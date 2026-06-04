import Link from 'next/link';

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-6 py-20">
      <div className="max-w-4xl text-center space-y-8 animate-fade-in">

        <p className="text-[#D4AF37] uppercase tracking-[0.4em] text-xs font-bold">
          Centro de Treinamento Cabapuã Brasil
        </p>

        <h1
          className="text-5xl md:text-7xl lg:text-8xl font-black text-white leading-tight"
          style={{ fontFamily: 'var(--font-cinzel)' }}
        >
          A FORÇA DA <br />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#D4AF37] to-[#F5C542]">
            SUPERAÇÃO
          </span>
        </h1>

        <p
          className="italic text-xl md:text-2xl text-gray-300 max-w-2xl mx-auto"
          style={{ fontFamily: 'var(--font-cinzel)' }}
        >
          &ldquo;Construímos campeões dentro e fora do tatame.&rdquo;
        </p>

        <div className="flex flex-col md:flex-row gap-4 pt-6 justify-center">
          <Link
            href="/academia"
            className="px-8 py-4 bg-[#D4AF37] text-black font-bold uppercase tracking-widest hover:bg-white hover:scale-105 transition-all duration-300 rounded-sm"
          >
            Conheça o CT
          </Link>
          <Link
            href="/clinica"
            className="px-8 py-4 border-2 border-[#D4AF37] text-[#D4AF37] font-bold uppercase tracking-widest hover:bg-[#D4AF37] hover:text-black hover:scale-105 transition-all duration-300 rounded-sm"
          >
            Saúde Selene
          </Link>
        </div>

        <p className="text-xs text-gray-600 pt-4">
          Agendamento online • Pagamento integrado • Prontuário seguro
        </p>
      </div>
    </div>
  );
}
