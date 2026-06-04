'use client';

// Tipagem mockada para demonstração (em produção buscaríamos via api.get('/api/v1/users/historico'))
const mockAluno = {
  nome: "Lucas Mendes",
  graduacoes: [
    {
      data: "15 de Janeiro, 2026",
      titulo: "Faixa Branca - 1º Grau",
      comentario_mestre: "Ótima evolução na postura e nos fundamentos básicos. Mantenha a disciplina."
    },
    {
      data: "05 de Agosto, 2025",
      titulo: "Início no CT Cabapuã",
      comentario_mestre: "O primeiro passo na jornada do guerreiro."
    }
  ]
};

export default function HistoricoGraduacao() {
  const aluno = mockAluno; // MOCK

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <div className="bg-[#0A0A0A] p-8 border border-[#D4AF37] shadow-[0_0_15px_rgba(212,175,55,0.1)]">
        <h2 className="font-cinzel text-3xl text-[#D4AF37] mb-8 uppercase tracking-widest text-center">Trajetória do Discípulo</h2>
        
        <div className="space-y-8 pl-4">
          {aluno.graduacoes.map((grad, index) => (
            <div key={index} className="relative pl-8 border-l-2 border-red-800 pb-4">
              <div className="absolute -left-[9px] top-1 w-4 h-4 bg-[#D4AF37] rotate-45 shadow-[0_0_10px_rgba(212,175,55,0.8)]"></div>
              <p className="text-gray-500 text-sm font-bold uppercase tracking-widest">{grad.data}</p>
              <h3 className="text-xl font-bold text-white mt-1 mb-2">{grad.titulo}</h3>
              <p className="text-gray-400 italic">"{grad.comentario_mestre}"</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
