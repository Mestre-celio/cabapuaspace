"""
Módulo 1 — Automação de Fluxo de Compras (Loja Uracan)
FastAPI service que gerencia o fluxo completo de compra de uniforme.
"""

import asyncio
import logging
import uuid
from datetime import datetime
from enum import Enum
from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/checkout", tags=["checkout"])

# ---------------------------------------------------------------------------
# Enums & Schemas
# ---------------------------------------------------------------------------

class OrderStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    CANCELLED = "cancelled"


class CheckoutItem(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)
    size: str


class CheckoutPayload(BaseModel):
    customer_id: int
    items: list[CheckoutItem]
    payment_method: str
    card_token: str | None = None


class OrderResponse(BaseModel):
    order_id: str
    status: OrderStatus
    total_amount: float
    message: str


# ---------------------------------------------------------------------------
# Simulated payment gateway webhook
# ---------------------------------------------------------------------------

PAYMENT_GATEWAY_URL = "https://sandbox.gateway.uracan/v1/charge"  # simulado


async def _call_payment_gateway(order_id: str, amount: float, card_token: str | None) -> dict[str, Any]:
    """
    Dispara webhook simulado para o gateway de pagamento.
    Em produção substituir pela chamada HTTP real.
    """
    # Simulação: token inválido → falha; demais → sucesso
    if card_token == "FAIL_TOKEN":
        return {"success": False, "error": "card_declined"}

    # Simula latência de rede (~200 ms)
    await asyncio.sleep(0.2)
    return {
        "success": True,
        "transaction_id": f"txn_{uuid.uuid4().hex[:12]}",
        "charged_amount": amount,
    }


# ---------------------------------------------------------------------------
# Core service logic
# ---------------------------------------------------------------------------

async def _validate_and_reserve_stock(db: AsyncSession, items: list[CheckoutItem]) -> float:
    """
    Valida e reserva estoque usando transação atômica (SELECT … FOR UPDATE).
    Retorna o valor total do pedido.
    Levanta HTTPException em caso de estoque insuficiente.
    """
    total = 0.0

    for item in items:
        # Lock pessimista na linha do produto + tamanho
        row = await db.execute(
            text(
                """
                SELECT id, name, price, stock
                FROM products
                WHERE id = :product_id AND size = :size
                FOR UPDATE
                """
            ),
            {"product_id": item.product_id, "size": item.size},
        )
        product = row.mappings().first()

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Produto id={item.product_id} tamanho={item.size} não encontrado.",
            )

        if product["stock"] < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "error": "stock_insufficient",
                    "product_id": item.product_id,
                    "size": item.size,
                    "available": product["stock"],
                    "requested": item.quantity,
                },
            )

        total += product["price"] * item.quantity

    return round(total, 2)


async def _create_pending_order(
    db: AsyncSession, payload: CheckoutPayload, total: float
) -> str:
    order_id = str(uuid.uuid4())
    await db.execute(
        text(
            """
            INSERT INTO orders (id, customer_id, status, total_amount, payment_method, created_at)
            VALUES (:id, :customer_id, 'pending', :total, :payment_method, :now)
            """
        ),
        {
            "id": order_id,
            "customer_id": payload.customer_id,
            "total": total,
            "payment_method": payload.payment_method,
            "now": datetime.utcnow(),
        },
    )

    for item in payload.items:
        await db.execute(
            text(
                """
                INSERT INTO order_items (order_id, product_id, size, quantity)
                VALUES (:order_id, :product_id, :size, :quantity)
                """
            ),
            {
                "order_id": order_id,
                "product_id": item.product_id,
                "size": item.size,
                "quantity": item.quantity,
            },
        )

    return order_id


async def _finalize_paid_order(
    db: AsyncSession, order_id: str, items: list[CheckoutItem], transaction_id: str
) -> None:
    """Atualiza status para 'paid' e decrementa estoque — ainda dentro da mesma transação."""
    await db.execute(
        text(
            """
            UPDATE orders
            SET status = 'paid', transaction_id = :txn, paid_at = :now
            WHERE id = :order_id
            """
        ),
        {"txn": transaction_id, "now": datetime.utcnow(), "order_id": order_id},
    )

    for item in items:
        await db.execute(
            text(
                """
                UPDATE products
                SET stock = stock - :qty
                WHERE id = :product_id AND size = :size
                """
            ),
            {"qty": item.quantity, "product_id": item.product_id, "size": item.size},
        )


# ---------------------------------------------------------------------------
# Route
# ---------------------------------------------------------------------------

@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def process_checkout(
    payload: CheckoutPayload,
    db: AsyncSession = Depends(get_db),
) -> OrderResponse:
    """
    Fluxo completo de checkout:
      1. Valida estoque (transação atômica)
      2. Cria pedido como 'pending'
      3. Chama gateway de pagamento (webhook simulado)
      4. Em caso de sucesso → 'paid' + decrementa estoque
         Em caso de falha → cancela pedido e retorna erro
    """
    async with db.begin():  # transação atômica
        # ── Passo 1: validar e reservar estoque ──────────────────────────
        try:
            total = await _validate_and_reserve_stock(db, payload.items)
        except HTTPException:
            raise  # repassa stock_insufficient já formatado

        # ── Passo 2: criar pedido como pending ───────────────────────────
        order_id = await _create_pending_order(db, payload, total)
        logger.info("Pedido %s criado como 'pending' — R$ %.2f", order_id, total)

        # ── Passo 3: disparar gateway de pagamento ───────────────────────
        gw_result = await _call_payment_gateway(order_id, total, payload.card_token)

        if not gw_result["success"]:
            # Marca como cancelado antes de fazer rollback implícito
            await db.execute(
                text("UPDATE orders SET status = 'cancelled' WHERE id = :id"),
                {"id": order_id},
            )
            logger.warning("Pagamento recusado para pedido %s: %s", order_id, gw_result.get("error"))
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail={
                    "error": "payment_failed",
                    "order_id": order_id,
                    "reason": gw_result.get("error", "unknown"),
                },
            )

        # ── Passo 4: confirmar pagamento e decrementar estoque ───────────
        await _finalize_paid_order(db, order_id, payload.items, gw_result["transaction_id"])
        logger.info("Pedido %s confirmado — txn: %s", order_id, gw_result["transaction_id"])

    return OrderResponse(
        order_id=order_id,
        status=OrderStatus.PAID,
        total_amount=total,
        message="Compra realizada com sucesso!",
    )
