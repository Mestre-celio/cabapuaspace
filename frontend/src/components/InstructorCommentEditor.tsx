'use client';

import { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { api } from '@/lib/api';

interface InstructorCommentEditorProps {
  alunoId: number;
  currentComment: string;
}

export default function InstructorCommentEditor({ alunoId, currentComment }: InstructorCommentEditorProps) {
  const [comment, setComment] = useState(currentComment || "");
  const { user } = useAuth(); // Contexto de autenticação

  // Role check: Only instructor or admin
  if (!user || (user.role !== 'instrutor' && user.role !== 'admin')) return null;

  const handleSave = async () => {
    try {
      await api.patch(`/api/v1/students/${alunoId}/comment`, { comment });
      alert("Nota de evolução registrada com sucesso.");
    } catch (err) {
      alert("Erro ao registrar nota de evolução.");
    }
  };

  return (
    <div className="bg-[#121212] p-6 border-l-4 border-[#DC2626]">
      <h4 className="text-[#D4AF37] font-bold uppercase text-sm mb-2">Comentário do Mestre (Privado)</h4>
      <textarea 
        className="w-full bg-black text-white p-3 border border-gray-700 focus:border-[#D4AF37] outline-none"
        value={comment}
        onChange={(e) => setComment(e.target.value)}
        rows={4}
        placeholder="Escreva a nota de evolução do aluno aqui..."
      />
      <button onClick={handleSave} className="mt-4 bg-[#D4AF37] text-black font-bold px-6 py-2 hover:bg-yellow-600 transition">
        Atualizar Registro
      </button>
    </div>
  );
}
