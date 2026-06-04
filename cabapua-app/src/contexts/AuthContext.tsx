'use client';

import {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
  useCallback,
} from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';

// === TYPES ===
export type UserRole = 'aluno' | 'instrutor' | 'terapeuta' | 'admin';

export interface User {
  id: string;
  email: string;
  full_name: string;
  phone?: string;
  role: UserRole;
  is_active: boolean;
  is_adimplent: boolean;
  created_at: string;
}

export interface RegisterData {
  email: string;
  password: string;
  full_name: string;
  phone?: string;
}

export interface AuthContextType {
  user: User | null;
  loading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  register: (data: RegisterData) => Promise<void>;
  refreshUser: () => Promise<void>;
}

// === CONTEXT ===
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// === PROVIDER ===
export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  // Carregar usuário ao iniciar (se tiver token salvo)
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      loadUser();
    } else {
      setLoading(false);
    }
  }, []);

  // Função para buscar dados do usuário logado
  const loadUser = useCallback(async () => {
    try {
      const response = await api.get<User>('/api/v1/auth/me');
      setUser(response.data);
      setError(null);
    } catch (err: any) {
      console.error('Erro ao carregar usuário:', err);
      // Token inválido ou expirado → limpar e redirecionar
      localStorage.removeItem('token');
      setUser(null);
      if (err.response?.status !== 401) {
        setError('Falha ao carregar dados do usuário');
      }
    } finally {
      setLoading(false);
    }
  }, []);

  // Login com email/senha
  const login = async (email: string, password: string) => {
    setError(null);
    setLoading(true);
    try {
      const response = await api.post('/api/v1/auth/login', { email, password });
      const { access_token, user: userData } = response.data;
      
      // Salvar token
      localStorage.setItem('token', access_token);
      
      // Atualizar estado
      setUser(userData);
      
      // Redirecionar conforme role
      const redirectPath = getRedirectPath(userData.role);
      router.push(redirectPath);
    } catch (err: any) {
      console.error('Erro no login:', err);
      const message = err.response?.data?.detail || 'Email ou senha inválidos';
      setError(message);
      throw new Error(message);
    } finally {
      setLoading(false);
    }
  };

  // Registro de novo usuário
  const register = async (data: RegisterData) => {
    setError(null);
    setLoading(true);
    try {
      const response = await api.post('/api/v1/auth/register', data);
      const { access_token, user: userData } = response.data;
      
      localStorage.setItem('token', access_token);
      setUser(userData);
      
      const redirectPath = getRedirectPath(userData.role);
      router.push(redirectPath);
    } catch (err: any) {
      console.error('Erro no registro:', err);
      const message = err.response?.data?.detail || 'Erro ao criar conta';
      setError(message);
      throw new Error(message);
    } finally {
      setLoading(false);
    }
  };

  // Logout: limpa token e estado
  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
    setError(null);
    router.push('/');
  };

  // Refresh manual dos dados do usuário
  const refreshUser = async () => {
    await loadUser();
  };

  // Helper: redirecionamento por role
  const getRedirectPath = (role: UserRole): string => {
    const paths: Record<UserRole, string> = {
      aluno: '/dashboard/aluno',
      instrutor: '/dashboard/instrutor',
      terapeuta: '/dashboard/clinica',
      admin: '/dashboard/admin',
    };
    return paths[role] || '/dashboard/aluno';
  };

  // Valor do contexto
  const value: AuthContextType = {
    user,
    loading,
    error,
    login,
    logout,
    register,
    refreshUser,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

// === HOOK ===
export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth deve ser usado dentro de AuthProvider');
  }
  return context;
}
