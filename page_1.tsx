import Link from "next/link";

const cards = [
  {
    href: "/academia",
    accent: "#b40000",
    bg: "from-[#1a0000] to-[#140000]",
    nameColor: "text-white",
    iconColor: "text-[#b40000]",
    icon: "🥊",
    name: "Área de Treino",
    desc: "C.T.M. Cabapuã · Only for Warriors",
  },
  {
    href: "/clinica",
    accent: "#8b44b0",
    bg: "from-[#1a0f1e] to-[#120a18]",
    nameColor: "text-[#e8caf5]",
    iconColor: "text-[#b06ad8]",
    icon: "🌙",
    name: "Clínica Selene",
    desc: "Estética · Massoterapia · Terapias Holísticas",
  },
  {
    href: "/loja",
    accent: "#d4a017",
    bg: "from-[#1a1500] to-[#100d00]",
    nameColor: "text-[#ffd84d]",
    iconColor: "text-[#d4a017]",
    icon: "👊",
    name: "Loja Uracan",
    desc: "Uracan Fight Wear · Uniformes & Equipamentos",
  },
];

export default function HomePage() {
  return (
    <main
      className="relative min-h-screen bg-[#0a0a0a] flex flex-col items-center justify-start overflow-hidden"
      style={{
        backgroundImage:
          "repeating-linear-gradient(45deg,rgba(180,0,0,0.03) 0,rgba(180,0,0,0.03) 1px,transparent 1px,transparent 50%)",
        backgroundSize: "32px 32px",
      }}
    >
      {/* Header */}
      <header className="w-full max-w-md px-6 pt-10 pb-4 text-center animate-fade-up">
        <span className="inline-block bg-[#b40000] text-white font-mono text-[10px] tracking-[3px] uppercase px-3 py-1 rounded-sm mb-4">
          Since 2018
        </span>

        <h1
          className="text-white leading-none tracking-wide"
          style={{ fontFamily: "'Bebas Neue', sans-serif", fontSize: "clamp(2.8rem,10vw,4.5rem)" }}
        >
          Bem-vindo ao{" "}
          <span className="text-[#b40000]">Cabapuã</span>
        </h1>

        <p className="text-[#666] text-xs tracking-[4px] uppercase mt-1">
          Connect — Sua plataforma completa
        </p>

        <div className="w-14 h-[3px] bg-[#b40000] mx-auto mt-5 rounded-sm" />
      </header>

      {/* Cards */}
      <section className="w-full max-w-md px-5 pb-10 flex flex-col gap-3.5 mt-2">
        {cards.map((card, i) => (
          <Link
            key={card.href}
            href={card.href}
            className={`
              relative flex items-stretch min-h-[108px] rounded-md overflow-hidden
              border border-white/[0.06] transition-all duration-200
              bg-gradient-to-br ${card.bg}
              hover:-translate-y-[3px] hover:scale-[1.01] hover:shadow-2xl
              active:scale-[0.98]
            `}
            style={{ animationDelay: `${0.15 + i * 0.13}s` }}
          >
            {/* Accent bar */}
            <div
              className="w-[6px] flex-shrink-0"
              style={{ background: card.accent }}
            />

            {/* Content */}
            <div className="flex-1 px-5 py-4 flex flex-col justify-center">
              <span className={`text-2xl mb-1 ${card.iconColor}`}>
                {card.icon}
              </span>
              <p
                className={`text-[1.45rem] leading-none tracking-wide mb-1 ${card.nameColor}`}
                style={{ fontFamily: "'Bebas Neue', sans-serif" }}
              >
                {card.name}
              </p>
              <p className="text-[11px] tracking-widest uppercase text-white/50">
                {card.desc}
              </p>
            </div>

            {/* Arrow */}
            <div className="flex items-center pr-5 pl-2 text-white/30 text-xl">
              ›
            </div>
          </Link>
        ))}
      </section>

      {/* Footer */}
      <footer className="text-[11px] text-[#333] tracking-[2px] uppercase pb-6">
        Cabapuã Connect · Campinas, SP
      </footer>
    </main>
  );
}
