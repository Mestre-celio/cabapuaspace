'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';

// Tipagem da Grade
interface ClassSlot {
  id: string;
  class_name: string;
  instructor: string;
  start_time: string;
  duration: number;
  available_spots: number;
  total_spots: number;
}

export default function AcademiaPage() {
  const [filter, setFilter] = useState('Todas');
  const { user } = useAuth();
  
  // Fetch das aulas disponíveis
  const { data: slots, isLoading } = useQuery<ClassSlot[]>({
    queryKey: ['slots'],
    queryFn: async () => {
      const { data } = await api.get('/api/v1/slots');
      return data;
    }
  });

  const handleSchedule = (slotId: string) => {
    // TODO: Integrar agendamento
    alert('Agendamento em desenvolvimento para a aula: ' + slotId);
  };

  return (
    <div className="p-8 max-w-6xl mx-auto text-white">
      <h1 className="font-cinzel text-4xl font-bold mb-2">Grade de Horários</h1>
      <p className="text-gray-400 mb-8">Selecione a aula e marque sua presença no tatame.</p>

      {/* Filtros */}
      <div className="flex gap-4 mb-8">
        {['Todas', 'Jiu-Jitsu', 'Muay Thai', 'Capoeira', 'Hapkido'].map(cat => (
          <button 
            key={cat}
            onClick={() => setFilter(cat)}
            className={`px-4 py-2 rounded-full border ${filter === cat ? 'bg-[#D4AF37] text-black' : 'border-[#D4AF37] text-[#D4AF37]'}`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Grid de Aulas */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {slots?.filter(s => filter === 'Todas' || s.class_name === filter).map(slot => (
          <div key={slot.id} className="bg-gradient-to-br from-[#121212] to-[#050505] border-t-2 border-b-2 border-[#DC2626] p-6 rounded-none shadow-[0_0_15px_rgba(220,38,38,0.2)] hover:shadow-[0_0_25px_rgba(220,38,38,0.4)] transition-all">
            <h3 className="font-cinzel text-2xl font-bold tracking-wider text-[#E5E5E5]">{slot.class_name}</h3>
            <div className="h-1 w-16 bg-[#D4AF37] my-3"></div> {/* Detalhe Dourado */}
            <p className="text-gray-400 font-medium">Instrutor: <span className="text-[#D4AF37]">{slot.instructor}</span></p>
            <p className="text-[#D4AF37] my-2">{new Date(slot.start_time).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}</p>
            
            {/* Lógica de Adimplência (Bloqueio) */}
            <button 
              disabled={!user?.is_adimplent}
              onClick={() => handleSchedule(slot.id)}
              className={`w-full py-3 mt-4 font-bold uppercase tracking-widest transition-all ${
                user?.is_adimplent 
                  ? "bg-[#DC2626] text-white hover:bg-[#b91c1c] active:scale-95" 
                  : "bg-gray-800 text-gray-500 cursor-not-allowed border border-gray-700"
              }`}
            >
              {user?.is_adimplent ? `Agendar Vaga (${slot.available_spots}/${slot.total_spots})` : "Acesso Restrito: Regularize"}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
