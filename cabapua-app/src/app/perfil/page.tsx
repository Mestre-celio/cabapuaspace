'use client';

import { useAuth } from '@/contexts/AuthContext';
import Link from 'next/link';

// Tipagem mockada para faturas (isso seria buscado de uma API /api/v1/invoices)
const mockInvoices = [
  { id: 1, mes: "Fevereiro/2026", valor: 150.00, status: "pago", link: "#" },
  { id: 2, mes: "Março/2026", valor: 150.00, status: "pago", link: "#" },
  { id: 3, mes: "Abril/2026", valor: 150.00, status: "pago", link: "#" },
  { id: 4, mes: "Maio/2026", valor: 150.00, status: "pendente", link: "#" }, // A fatura atual
];

export default function PerfilPage() {
  const { user } = useAuth();
  
  // Em produção, faremos um fetch das Invoices do aluno
  const invoices = mockInvoices;
  
  if (!user) return <div className="text-white p-8">Carregando perfil...</div>;

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h1 className="font-cinzel text-4xl font-bold text-white mb-2">Seu Perfil</h1>
      <p className="text-gray-400 mb-8">Gerencie suas informações e verifique seu status no CT.</p>
      
      {/* Estrutura do Painel de Perfil (Status Financeiro) */}
      <div className="bg-[#050505] border-l-4 border-[#D4AF37] p-8 mt-6 shadow-[0_0_15px_rgba(212,175,55,0.1)]">
        <h2 className="font-cinzel text-3xl text-white mb-6 tracking-wider">Status Financeiro</h2>
        
        {/* Card de Status */}
        <div className={`p-6 rounded-lg ${user.is_adimplent ? 'bg-green-900/20 border border-green-700' : 'bg-red-900/20 border border-red-700'}`}>
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <div>
              <p className="text-gray-400 uppercase tracking-widest text-sm">Situação Atual</p>
              <p className={`text-2xl font-bold ${user.is_adimplent ? 'text-green-500' : 'text-red-500'}`}>
                {user.is_adimplent ? 'Regular' : 'Pendente de Regularização'}
              </p>
            </div>
            {!user.is_adimplent && (
              <button className="px-6 py-3 bg-[#D4AF37] text-black font-bold uppercase hover:bg-yellow-600 transition shadow-[0_0_15px_rgba(212,175,55,0.4)]">
                Resolver Pendência
              </button>
            )}
          </div>
        </div>
        
        {/* Histórico Financeiro */}
        <div className="mt-8">
          <h3 className="text-white font-bold mb-4 uppercase tracking-widest border-b border-gray-800 pb-2">Últimas Faturas</h3>
          <div className="space-y-3">
            {invoices.map((inv) => (
              <div key={inv.id} className="flex justify-between items-center p-4 bg-[#121212] border border-gray-800 hover:border-[#D4AF37] transition">
                <div>
                  <p className="text-white font-bold">{inv.mes}</p>
                  <p className="text-gray-400 text-sm">R$ {inv.valor.toFixed(2)}</p>
                </div>
                <div className="flex items-center gap-4">
                  <span className={`px-3 py-1 text-xs font-bold uppercase ${inv.status === 'pago' ? 'bg-green-900/50 text-green-500' : 'bg-red-900/50 text-red-500'}`}>
                    {inv.status}
                  </span>
                  <a href={inv.link} className="text-[#D4AF37] hover:text-white transition text-sm font-bold uppercase">
                    {inv.status === 'pago' ? 'Recibo' : 'Pagar via PIX'}
                  </a>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
      
      {/* Link para o histórico de graduação */}
      <div className="mt-8 flex justify-end">
        <Link href="/perfil/historico" className="text-[#D4AF37] hover:text-white transition uppercase font-bold text-sm tracking-widest">
          Ver Trajetória do Discípulo →
        </Link>
      </div>
    </div>
  );
}
