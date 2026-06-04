'use client';

import { useState } from 'react';

// Simple cart icon (Unicode) – can be replaced with an SVG later
const CartIcon = () => (
  <span className="inline-block align-text-bottom" style={{ fontSize: '1.2rem' }}>🛒</span>
);

// Dummy product list – in a real app this would come from an API
const PRODUCTS = [
  {
    id: 1,
    name: 'Luva Profissional',
    price: 149.99,
    img: 'https://via.placeholder.com/300x200?text=Luva+Profissional',
  },
  {
    id: 2,
    name: 'Camiseta Uracan',
    price: 79.9,
    img: 'https://via.placeholder.com/300x200?text=Camiseta+Uracan',
  },
  {
    id: 3,
    name: 'Shorts de Luta',
    price: 99.5,
    img: 'https://via.placeholder.com/300x200?text=Shorts+de+Luta',
  },
];

export default function LojaPage() {
  const [status, setStatus] = useState<string | null>(null);
  const [loadingIds, setLoadingIds] = useState<number[]>([]);
  const [cart, setCart] = useState<Array<{id: number; name: string; price: number}>>([]);
  const [checkoutLoading, setCheckoutLoading] = useState<boolean>(false);

  const addToCart = async (productId: number) => {
    setLoadingIds((prev) => [...prev, productId]);
    setStatus(null);
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE}/api/v1/shop/cart`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ product_id: productId, quantity: 1 }),
        }
      );
      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail ?? 'Erro ao adicionar ao carrinho');
      }
      // Add product to local cart state
      const product = PRODUCTS.find((p) => p.id === productId);
      if (product) {
        setCart((prev) => [...prev, { id: product.id, name: product.name, price: product.price }]);
      }
      setStatus('✅ Produto adicionado ao carrinho!');
    } catch (e: any) {
      setStatus(`❌ ${e.message}`);
    } finally {
      setLoadingIds((prev) => prev.filter((id) => id !== productId));
    }
  };

  const checkout = async () => {
    if (cart.length === 0) return;
    setCheckoutLoading(true);
    setStatus(null);
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE}/api/v1/shop/checkout`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ items: cart }),
        }
      );
      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail ?? 'Erro ao finalizar compra');
      }
      setStatus('✅ Compra finalizada com sucesso!');
      setCart([]);
    } catch (e: any) {
      setStatus(`❌ ${e.message}`);
    } finally {
      setCheckoutLoading(false);
    }
  };
  return (
    <div className="relative min-h-screen bg-black text-white">
      {/* Fixed header */}
      <header className="fixed inset-x-0 top-0 z-10 flex items-center justify-between bg-[#111] px-4 py-3 shadow-md">
        <h1 className="text-xl font-bold">Loja Uracan</h1>
        <button aria-label="Carrinho" className="text-2xl">
          <CartIcon />
        </button>
      </header>

      {/* Main content – add top padding to avoid header overlap */}
      <main className="pt-16 max-w-5xl mx-auto px-4 py-8">
        <section className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {PRODUCTS.map((p) => (
            <article
              key={p.id}
              className="flex flex-col rounded-lg overflow-hidden bg-[#1a1a1a] shadow-lg"
            >
              <img src={p.img} alt={p.name} className="w-full h-48 object-cover" />
              <div className="p-4 flex flex-col flex-1">
                <h2 className="text-lg font-semibold mb-2 text-white">{p.name}</h2>
                <p className="text-sm text-gray-300 mb-4">R$ {p.price.toFixed(2)}</p>
                <button
                  disabled={loadingIds.includes(p.id)}
                  onClick={() => addToCart(p.id)}
                  className={`mt-auto py-2 px-4 rounded transition-colors ${
                    loadingIds.includes(p.id)
                      ? 'bg-gray-600 cursor-not-allowed'
                      : 'bg-[#d4a017] hover:bg-[#c19115]'
                  }`}
                >
                  {loadingIds.includes(p.id) ? 'Adicionando...' : 'Adicionar ao Carrinho'}
                </button>
              </div>
            </article>
          ))}
        </section>
        {/* Cart Section */}
        <section className="mt-8 bg-[#111] p-4 rounded-lg">
          <h2 className="text-xl font-bold mb-4 text-white">Carrinho</h2>
          {cart.length === 0 ? (
            <p className="text-gray-400">Seu carrinho está vazio.</p>
          ) : (
            <>
              <ul className="space-y-2 mb-4">
                {cart.map((item, idx) => (
                  <li key={idx} className="flex justify-between text-white">
                    <span>{item.name}</span>
                    <span>R$ {item.price.toFixed(2)}</span>
                  </li>
                ))}
              </ul>
              <p className="font-bold text-white mb-2">
                Total: R$ {cart.reduce((sum, i) => sum + i.price, 0).toFixed(2)}
              </p>
              <button
                onClick={checkout}
                disabled={checkoutLoading}
                className={`py-2 px-4 rounded transition-colors ${checkoutLoading ? 'bg-gray-600 cursor-not-allowed' : 'bg-[#d4a017] hover:bg-[#c19115]'}`}
              >
                {checkoutLoading ? 'Finalizando...' : 'Finalizar Compra'}
              </button>
            </>
          )}
        </section>
        {status && (
          <p className="mt-6 text-center font-medium text-white">
            {status}
          </p>
        )}
      </main>
    </div>
  );
}
