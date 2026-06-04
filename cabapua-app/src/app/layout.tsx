import './globals.css';
import { Cinzel, Inter } from 'next/font/google';
import Link from 'next/link';
import { AuthProvider } from '@/contexts/AuthContext';

const cinzel = Cinzel({ subsets: ['latin'], variable: '--font-cinzel' });
const inter = Inter({ subsets: ['latin'], variable: '--font-inter' });

export const metadata = {
  title: 'Cabapuã Connect',
  description: 'CT Cabapuã + Clínica Selene + Uracan Fight Wear',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt-BR" className={`${cinzel.variable} ${inter.variable}`}>
      <body className="bg-[#050505] text-white font-inter">
        <AuthProvider>
          <nav className="sticky top-0 z-50 bg-[#0A0A0A]/90 backdrop-blur-md border-b border-[#D4AF37]/30">
            <div className="container mx-auto px-6 py-4 flex justify-between items-center">
              <Link href="/" className="text-2xl font-cinzel font-bold text-[#D4AF37]">
                CABAPUÃ
              </Link>
              <div className="hidden md:flex gap-8 items-center">
                <Link href="/" className="hover:text-[#D4AF37] transition">Início</Link>
                <Link href="/academia" className="hover:text-[#D4AF37] transition">Academia</Link>
                <Link href="/clinica" className="hover:text-[#D4AF37] transition">Clínica</Link>
                <Link href="/loja" className="hover:text-[#D4AF37] transition">Loja</Link>
                <Link href="/login" className="px-4 py-2 border border-[#D4AF37] text-[#D4AF37] rounded hover:bg-[#D4AF37] hover:text-black transition">
                  Login
                </Link>
              </div>
            </div>
          </nav>
          
          <main className="min-h-screen">{children}</main>
          
          <footer className="border-t border-[#D4AF37]/30 py-6 text-center text-gray-500 text-sm">
            <p>© 2026 CT Cabapuã Brasil. Todos os direitos reservados.</p>
          </footer>
        </AuthProvider>
      </body>
    </html>
  );
}
