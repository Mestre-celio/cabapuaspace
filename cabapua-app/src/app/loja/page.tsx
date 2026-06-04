import Link from 'next/link';

export default function LojaPage() {
  const produtos = [
    {
      nome: 'Kimono Uracan Premium',
      categoria: 'Uniformes',
      preco: 299.90,
      imagem: '🥋',
      descricao: 'Tecido reforçado, costura dupla, ideal para treinos intensivos.'
    },
    {
      nome: 'Luvas de Muay Thai',
      categoria: 'Equipamentos',
      preco: 189.90,
      imagem: '🥊',
      descricao: 'Couro sintético de alta qualidade, proteção máxima.'
    },
    {
      nome: 'Livro: A Jornada do Guerreiro',
      categoria: 'Livros',
      preco: 79.90,
      imagem: '📚',
      descricao: 'Obra exclusiva do Mestre Célio sobre disciplina e superação.'
    },
    {
      nome: 'Camiseta Uracan Fight',
      categoria: 'Roupas',
      preco: 89.90,
      imagem: '👕',
      descricao: 'Algodão premium, estampa exclusiva da marca.'
    },
    {
      nome: 'Shorts de Treino',
      categoria: 'Roupas',
      preco: 119.90,
      imagem: '🩳',
      descricao: 'Tecido leve e respirável, mobilidade total.'
    },
    {
      nome: 'Faixa Graduação',
      categoria: 'Acessórios',
      preco: 39.90,
      imagem: '🎖️',
      descricao: 'Disponível em todas as cores e tamanhos.'
    }
  ];

  return (
    <div className="min-h-screen bg-[#050505]">
      {/* Hero Section */}
      <section className="bg-gradient-to-b from-[#0A0A0A] to-[#050505] py-20">
        <div className="container mx-auto px-6 text-center">
          <p className="text-[#D4AF37] uppercase tracking-[0.3em] text-sm font-bold mb-4">
            Equipamentos Profissionais
          </p>
          <h1 className="font-cinzel text-5xl md:text-6xl font-bold text-white mb-6">
            URACAN <span className="text-[#DC2626]">FIGHT WEAR</span>
          </h1>
          <p className="text-gray-400 text-lg max-w-2xl mx-auto mb-8">
            Equipamentos de alta performance para artes marciais. 
            Qualidade profissional para atletas exigentes.
          </p>
          <div className="flex flex-col md:flex-row gap-4 justify-center">
            <Link 
              href="#produtos" 
              className="px-8 py-4 bg-[#D4AF37] text-black font-bold rounded-lg hover:bg-white transition-all duration-300"
            >
              Ver Produtos
            </Link>
            <Link 
              href="/login" 
              className="px-8 py-4 border-2 border-[#DC2626] text-[#DC2626] font-bold rounded-lg hover:bg-[#DC2626] hover:text-white transition-all duration-300"
            >
              Área do Cliente
            </Link>
          </div>
        </div>
      </section>

      {/* Benefícios */}
      <section className="py-12 bg-[#0A0A0A] border-y border-[#D4AF37]/20">
        <div className="container mx-auto px-6">
          <div className="grid md:grid-cols-4 gap-6 text-center">
            {[
              { icon: '', title: 'Frete Grátis', desc: 'Para compras acima de R$ 300' },
              { icon: '💳', title: 'Parcelamento', desc: 'Até 12x no cartão' },
              { icon: '🔒', title: 'Compra Segura', desc: 'Ambiente 100% protegido' },
              { icon: '↩️', title: 'Troca Fácil', desc: '7 dias para devolução' }
            ].map((item, index) => (
              <div key={index} className="flex flex-col items-center gap-2">
                <div className="text-3xl">{item.icon}</div>
                <h3 className="font-bold text-white">{item.title}</h3>
                <p className="text-gray-400 text-sm">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Produtos */}
      <section id="produtos" className="py-20 bg-[#050505]">
        <div className="container mx-auto px-6">
          <h2 className="font-cinzel text-4xl font-bold text-center text-white mb-4">
            PRODUTOS <span className="text-[#D4AF37]">URACAN</span>
          </h2>
          <p className="text-gray-400 text-center mb-12">Qualidade profissional para seu treino</p>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {produtos.map((produto, index) => (
              <div key={index} className="bg-[#121212] border border-[#D4AF37]/20 rounded-xl overflow-hidden hover:border-[#D4AF37] hover:shadow-2xl hover:shadow-[#D4AF37]/10 transition-all duration-300 group">
                <div className="h-64 bg-gradient-to-br from-[#1a1a1a] to-[#0a0a0a] flex items-center justify-center text-8xl group-hover:scale-110 transition-transform duration-300">
                  {produto.imagem}
                </div>
                <div className="p-6">
                  <div className="text-[#DC2626] text-xs font-bold uppercase tracking-wider mb-2">{produto.categoria}</div>
                  <h3 className="font-cinzel text-xl font-bold text-white mb-2">{produto.nome}</h3>
                  <p className="text-gray-400 text-sm mb-4">{produto.descricao}</p>
                  <div className="flex items-center justify-between">
                    <div className="text-2xl font-bold text-[#D4AF37]">
                      R$ {produto.preco.toFixed(2).replace('.', ',')}
                    </div>
                    <button className="px-4 py-2 bg-[#DC2626] text-white text-sm font-bold rounded hover:bg-[#B91C1C] transition-colors">
                      Comprar
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Livros do Mestre Célio */}
      <section className="py-20 bg-[#0A0A0A]">
        <div className="container mx-auto px-6">
          <div className="bg-gradient-to-r from-[#D4AF37]/10 to-[#DC2626]/10 border border-[#D4AF37]/30 rounded-2xl p-8 md:p-12">
            <div className="grid md:grid-cols-2 gap-12 items-center">
              <div>
                <p className="text-[#D4AF37] text-sm font-bold uppercase tracking-wider mb-4">Coleção Exclusiva</p>
                <h2 className="font-cinzel text-4xl font-bold text-white mb-6">
                  LIVROS DO <span className="text-[#DC2626]">MESTRE CÉLIO</span>
                </h2>
                <p className="text-gray-400 text-lg mb-6 leading-relaxed">
                  Conhecimento ancestral e moderno sobre artes marciais, 
                  disciplina mental e o caminho do guerreiro.
                </p>
                <ul className="space-y-3 mb-8">
                  <li className="text-gray-300 flex items-center gap-2">
                    <span className="text-[#D4AF37]">▸</span> A Jornada do Guerreiro
                  </li>
                  <li className="text-gray-300 flex items-center gap-2">
                    <span className="text-[#D4AF37]">▸</span> Disciplina e Superação
                  </li>
                  <li className="text-gray-300 flex items-center gap-2">
                    <span className="text-[#D4AF37]">▸</span> Técnicas Avançadas de Muay Thai
                  </li>
                </ul>
                <Link 
                  href="#produtos" 
                  className="inline-block px-6 py-3 bg-[#D4AF37] text-black font-bold rounded hover:bg-white transition-colors"
                >
                  Ver Coleção Completa
                </Link>
              </div>
              <div className="flex justify-center">
                <div className="text-9xl animate-pulse">📚</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Final */}
      <section className="py-20 bg-[#DC2626]">
        <div className="container mx-auto px-6 text-center">
          <h2 className="font-cinzel text-4xl font-bold text-white mb-4">
            ALUNOS CABAPUÃ TÊM DESCONTO
          </h2>
          <p className="text-white/90 text-xl mb-8">10% de desconto em toda a loja para alunos ativos</p>
          <Link 
            href="/login" 
            className="inline-block px-10 py-4 bg-black text-white font-bold rounded-lg hover:bg-gray-900 transition-all duration-300"
          >
            ACESSAR MINHA CONTA
          </Link>
        </div>
      </section>
    </div>
  );
}
