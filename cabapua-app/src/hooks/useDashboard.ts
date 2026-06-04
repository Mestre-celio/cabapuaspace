import { useQuery, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';

export interface NextClass {
  id: string;
  class_name: string;
  instructor: string;
  start_time: string; // ISO string
  duration_minutes: number;
  room?: string;
  status: 'scheduled' | 'completed' | 'canceled';
}

export interface DashboardStats {
  total_classes: number;
  attended_classes: number;
  attendance_rate: number; // 0-100
  next_class: NextClass | null;
  is_adimplent: boolean;
  last_updated: string;
}

export function useDashboard(userId?: string) {
  const queryClient = useQueryClient();

  const statsQuery = useQuery<DashboardStats>({
    queryKey: ['dashboard', 'stats', userId],
    queryFn: async () => {
      const { data } = await api.get<DashboardStats>('/api/v1/dashboard/stats');
      return data;
    },
    enabled: !!userId,
    staleTime: 2 * 60 * 1000, // 2 minutos
    retry: 1,
  });

  const appointmentsQuery = useQuery<NextClass[]>({
    queryKey: ['dashboard', 'appointments', userId],
    queryFn: async () => {
      const { data } = await api.get<NextClass[]>('/api/v1/dashboard/appointments?status=scheduled&limit=5');
      return data;
    },
    enabled: !!userId,
    staleTime: 5 * 60 * 1000, // 5 minutos
  });

  const refresh = async () => {
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: ['dashboard', 'stats'] }),
      queryClient.invalidateQueries({ queryKey: ['dashboard', 'appointments'] }),
    ]);
  };

  return {
    stats: statsQuery.data,
    appointments: appointmentsQuery.data,
    isLoading: statsQuery.isLoading || appointmentsQuery.isLoading,
    isError: statsQuery.isError || appointmentsQuery.isError,
    error: statsQuery.error || appointmentsQuery.error,
    refresh,
  };
}
