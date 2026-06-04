import Link from 'next/link';

export default function ClinicaPage() {
  return (
    <div className="min-h-screen bg-[#050505]">
      {/* Hero Section */}
      <section className="bg-gradient-to-b from-[#0A0A0A] to-[#050505] py-20">
        <div className="container mx-auto px-6 text-center">
          <p className="text-[#D4AF37] uppercase tracking-[0.3em] text-sm font-bold mb-4">
            Saúde Integral & Performance
          </p>
          <h1 className="font-cinzel text-5xl md:text-6xl font-bold text-white mb-6">
            CLÍNICA <span className="text-[#DC2626]">SELENE</span>
          </h1>
          <p className="text-gray-400 text-lg max-w-2xl mx-auto mb-8">
            Terapia especializada para atletas e praticantes de artes marciais. 
            Cuide da sua mente com a mesma dedicação do seu corpo.
          </p>
          <div className="flex flex-col md:flex-row gap-4 justify-center">
            <Link 
              href="/login" 
              className="px-8 py-4 bg-[#DC2626] text-white font-bold rounded-lg hover:bg-[#B91C1C] transition-all duration-300"
            >
              Agendar Sessão
            </Link>
            <Link 
              href="#servicos" 
              className="px-8 py-4 border-2 border-[#D4AF37] text-[#D4AF37] font-bold rounded-lg hover:bg-[#D4AF37] hover:text-black transition-all duration-300"
            >
              Conhecer Serviços
            </Link>
          </div>
        </div>
      </section>

      {/* Serviços */}
      <section id="servicos" className="py-20 bg-[#0A0A0A]">
        <div className="container mx-auto px-6">
          <h2 className="font-cinzel text-4xl font-bold text-center text-white mb-16">
            SERVIÇOS <span className="text-[#D4AF37]">TERAPÊUTICOS</span>
          </h2>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Terapia Individual */}
            <div className="bg-[#121212] border border-[#DC2626]/30 rounded-xl p-8 hover:border-[#DC2626] hover:shadow-2xl hover:shadow-[#DC2626]/10 transition-all duration-300">
              <div className="w-16 h-16 bg-[#DC2626]/20 rounded-full flex items-center justify-center mb-6">
                <svg className="w-8 h-8 text-[#DC2626]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                </svg>
              </div>
              <h3 className="font-cinzel text-2xl font-bold text-white mb-4">Terapia Individual</h3>
              <p className="text-gray-400 mb-6 leading-relaxed">
                Sessões personalizadas focadas em ansiedade, performance atlética, 
                gestão emocional e desenvolvimento pessoal.
              </p>
              <div className="text-[#D4AF37] font-bold text-lg">R$ 150,00<span className="text-gray-500 text-sm font-normal">/sessão</span></div>
            </div>

            {/* Acompanhamento Esportivo */}
            <div className="bg-[#121212] border border-[#DC2626]/30 rounded-xl p-8 hover:border-[#DC2626] hover:shadow-2xl hover:shadow-[#DC2626]/10 transition-all duration-300">
              <div className="w-16 h-16 bg-[#DC2626]/20 rounded-full flex items-center justify-center mb-6">
                <svg className="w-8 h-8 text-[#DC2626]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 className="font-cinzel text-2xl font-bold text-white mb-4">Preparação Mental</h3>
              <p className="text-gray-400 mb-6 leading-relaxed">
                Treinamento psicológico para competições, controle de pressão, 
                foco e resiliência mental no tatame e na vida.
              </p>
              <div className="text-[#D4AF37] font-bold text-lg">R$ 200,00<span className="text-gray-500 text-sm font-normal">/sessão</span></div>
            </div>

            {/* Terapia de Casal */}
            <div className="bg-[#121212] border border-[#DC2626]/30 rounded-xl p-8 hover:border-[#DC2626] hover:shadow-2xl hover:shadow-[#DC2626]/10 transition-all duration-300">
              <div className="w-16 h-16 bg-[#DC2626]/20 rounded-full flex items-center justify-center mb-6">
                <svg className="w-8 h-8 text-[#DC2626]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
              <h3 className="font-cinzel text-2xl font-bold text-white mb-4">Terapia de Casal</h3>
              <p className="text-gray-400 mb-6 leading-relaxed">
                Mediação de conflitos, melhoria da comunicação e fortalecimento 
                de relacionamentos com abordagem prática.
              </p>
              <div className="text-[#D4AF37] font-bold text-lg">R$ 250,00<span className="text-gray-500 text-sm font-normal">/sessão</span></div>
            </div>
          </div>
        </div>
      </section>

      {/* Benefícios */}
      <section className="py-20 bg-[#050505]">
        <div className="container mx-auto px-6">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="font-cinzel text-4xl font-bold text-white mb-6">
                POR QUE A <span className="text-[#DC2626]">MENTE</span> É TÃO IMPORTANTE?
              </h2>
              <p className="text-gray-400 text-lg mb-8 leading-relaxed">
                Atletas de alta performance sabem que o sucesso é 80% mental. 
                Na Clínica Selene, integramos técnicas terapêuticas com o universo 
                das artes marciais para potencializar seus resultados.
              </p>
              <ul className="space-y-4">
                {[
                  'Controle da ansiedade pré-competição',
                  'Gestão do estresse e pressão',
                  'Melhoria do foco e concentração',
                  'Desenvolvimento de resiliência mental',
                  'Equilíbrio entre treino, trabalho e vida pessoal'
                ].map((item, index) => (
                  <li key={index} className="flex items-center gap-3 text-gray-300">
                    <svg className="w-6 h-6 text-[#D4AF37] flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    {item}
                  </li>
                ))}
              </ul>
            </div>
            <div className="bg-gradient-to-br from-[#DC2626]/20 to-[#D4AF37]/20 rounded-2xl p-8 border border-[#DC2626]/30">
              <div className="bg-[#0A0A0A] rounded-xl p-6 mb-6">
                <p className="font-cinzel text-2xl text-[#D4AF37] mb-2">"A força da superação constrói o sucesso."</p>
                <p className="text-gray-400">— Mestre Célio</p>
              </div>
              <p className="text-gray-400 text-sm leading-relaxed">
                Com mais de 20 anos de experiência em artes marciais e terapia, 
                ofereço um atendimento que entende suas necessidades como atleta 
                e como pessoa.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Final */}
      <section className="py-20 bg-[#DC2626]">
        <div className="container mx-auto px-6 text-center">
          <h2 className="font-cinzel text-4xl font-bold text-white mb-4">
            INVISTA NA SUA SAÚDE MENTAL
          </h2>
          <p className="text-white/90 text-xl mb-8">Primeira sessão com 20% de desconto para alunos do CT Cabapuã</p>
          <Link 
            href="/login" 
            className="inline-block px-10 py-4 bg-black text-white font-bold rounded-lg hover:bg-gray-900 transition-all duration-300"
          >
            AGENDAR MINHA SESSÃO
          </Link>
        </div>
      </section>
    </div>
  );
}
