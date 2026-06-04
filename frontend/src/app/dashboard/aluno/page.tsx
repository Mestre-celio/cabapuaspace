'use client';

import { useAuth } from '@/contexts/AuthContext';
import { useDashboard } from '@/hooks/useDashboard';
import StatsCard from '@/components/dashboard/StatsCard';
import ClassCard from '@/components/dashboard/ClassCard';
import QuickAction from '@/components/dashboard/QuickAction';
import PaymentStatus from '@/components/dashboard/PaymentStatus';
import Link from 'next/link';

export default function AlunoDashboard() {
  const { user } = useAuth();
  const { stats, appointments, isLoading, error, refresh } = useDashboard(user?.id);

  // Fallback para desenvolvimento (remover em produção)
  const mockStats = {
    total_classes: 24,
    attended_classes: 18,
    attendance_rate: 75,
    next_class: {
      id: 'mock-1',
      class_name: 'Muay Thai',
      instructor: 'Mestre Célio',
      start_time: new Date(Date.now() + 2 * 60 * 60 * 1000).toISOString(), // +2h
      duration_minutes: 60,
      room: 'Sala 1',
      status: 'scheduled' as const,
    },
    is_adimplent: true,
    last_updated: new Date().toISOString(),
  };

  const displayStats = stats || mockStats;
  const upcomingClasses = appointments || (mockStats.next_class ? [mockStats.next_class] : []);

  if (isLoading && !stats) {
    return (
      <div className="min-h-screen bg-[#050505] flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-[#D4AF37] border-t-transparent" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-500/10 border border-red-500 text-red-400 p-4 rounded-lg">
          <p className="font-bold">Erro ao carregar dashboard</p>
          <p className="text-sm mt-1">{error.message}</p>
          <button 
            onClick={() => refresh()}
            className="mt-3 px-4 py-2 bg-red-500/20 hover:bg-red-500/30 rounded text-sm"
          >
            Tentar novamente
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="font-cinzel text-3xl font-bold text-white">
            Olá, <span className="text-[#D4AF37]">{user?.full_name?.split(' ')[0]}</span>
          </h1>
          <p className="text-gray-400 mt-1">
            Última atualização: {new Date(displayStats.last_updated).toLocaleTimeString('pt-BR')}
          </p>
        </div>
        <PaymentStatus isAdimplent={displayStats.is_adimplent} />
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatsCard
          title="Aulas Totais"
          value={displayStats.total_classes.toString()}
          icon="📚"
          trend={`${displayStats.attended_classes} frequentadas`}
        />
        <StatsCard
          title="Frequência"
          value={`${displayStats.attendance_rate}%`}
          icon="✅"
          trend={displayStats.attendance_rate >= 80 ? 'Excelente!' : 'Continue assim!'}
          variant={displayStats.attendance_rate >= 80 ? 'success' : 'default'}
        />
        <StatsCard
          title="Próxima Aula"
          value={displayStats.next_class ? 'Hoje' : '—'}
          icon="🥋"
          trend={displayStats.next_class?.class_name || 'Nenhuma agendada'}
        />
        <StatsCard
          title="Status"
          value={displayStats.is_adimplent ? 'Ativo' : 'Pendente'}
          icon={displayStats.is_adimplent ? '💚' : '⚠️'}
          trend={displayStats.is_adimplent ? 'Mensalidade em dia' : 'Regularize para agendar'}
          variant={displayStats.is_adimplent ? 'success' : 'warning'}
        />
      </div>

      {/* Próxima Aula em Destaque */}
      {displayStats.next_class && (
        <div className="bg-gradient-to-r from-[#DC2626]/20 to-[#D4AF37]/20 border border-[#DC2626]/30 rounded-2xl p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-cinzel text-xl font-bold text-white">🎯 PRÓXIMA AULA</h2>
            <button 
              onClick={() => refresh()}
              className="text-gray-400 hover:text-white text-sm flex items-center gap-1"
            >
              🔄 Atualizar
            </button>
          </div>
          
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <p className="text-2xl font-bold text-white">{displayStats.next_class.class_name}</p>
              <p className="text-gray-400">com {displayStats.next_class.instructor}</p>
              <p className="text-[#D4AF37] font-semibold mt-2">
                {new Date(displayStats.next_class.start_time).toLocaleDateString('pt-BR', {
                  weekday: 'long',
                  day: 'numeric',
                  month: 'long',
                  hour: '2-digit',
                  minute: '2-digit'
                })}
              </p>
              {displayStats.next_class.room && (
                <p className="text-gray-500 text-sm mt-1">📍 {displayStats.next_class.room}</p>
              )}
              <p className="text-gray-500 text-sm">⏱️ {displayStats.next_class.duration_minutes} min</p>
            </div>
            <div className="flex gap-3">
              <Link 
                href={`/academia/aula/${displayStats.next_class.id}`}
                className="px-6 py-3 bg-[#DC2626] text-white font-bold rounded-lg hover:bg-[#B91C1C] transition"
              >
                Ver Detalhes
              </Link>
              <button 
                className="px-6 py-3 border border-[#D4AF37] text-[#D4AF37] font-bold rounded-lg hover:bg-[#D4AF37] hover:text-black transition"
                onClick={() => {
                  if (confirm('Tem certeza que deseja cancelar esta aula?')) {
                    // Implementar cancelamento aqui
                    refresh();
                  }
                }}
              >
                Cancelar
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Ações Rápidas */}
      <div>
        <h2 className="font-cinzel text-xl font-bold text-white mb-4">⚡ AÇÕES RÁPIDAS</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <QuickAction icon="📅" title="Agendar Aula" href="/academia" description="Veja a grade e marque" />
          <QuickAction icon="🏥" title="Clínica Selene" href="/clinica" description="Sessão terapêutica" />
          <QuickAction icon="🛒" title="Loja Uracan" href="/loja" description="Uniformes e livros" />
          <QuickAction icon="📊" title="Histórico" href="/dashboard/aluno/historico" description="Sua evolução" />
        </div>
      </div>

      {/* Lista de Aulas Agendadas */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-cinzel text-xl font-bold text-white">📅 AULAS AGENDADAS</h2>
          <Link href="/academia" className="text-[#D4AF37] text-sm hover:underline">
            Ver grade completa →
          </Link>
        </div>

        <div className="space-y-4">
          {upcomingClasses.length > 0 ? (
            upcomingClasses.map((cls) => (
              <ClassCard key={cls.id} classData={cls} onRefresh={refresh} />
            ))
          ) : (
            <div className="text-center py-12 bg-[#0A0A0A] rounded-xl border border-dashed border-gray-700">
              <p className="text-4xl mb-4">🥋</p>
              <p className="text-gray-400 mb-4">Nenhuma aula agendada</p>
              <Link
                href="/academia"
                className="inline-block px-6 py-2 bg-[#D4AF37] text-black font-bold rounded hover:bg-white transition"
              >
                Agendar Agora
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
