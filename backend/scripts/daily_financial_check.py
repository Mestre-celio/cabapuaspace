import asyncio
import sys
import os
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import select, update, and_
import logging

# Ensure we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.user import User
from app.models.invoice import Invoice, InvoiceStatus
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FinancialCheckJob")

async def mock_send_email(to_email: str, subject: str, body: str):
    logger.info(f"[EMAIL MOCK] Enviando email para {to_email} | Assunto: {subject}")
    logger.info(f"[EMAIL MOCK] Corpo: {body}")
    await asyncio.sleep(0.5)

async def mock_push_notification(user_id: int, message: str):
    logger.info(f"[PUSH MOCK] Notificando UserID {user_id}: {message}")
    await asyncio.sleep(0.1)

async def run_daily_financial_check():
    logger.info("Iniciando Job de Verificação Financeira Diária...")
    
    # Configure DB Session
    engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    now_utc = datetime.now(timezone.utc)
    cutoff_5_days = now_utc - timedelta(days=5)

    async with async_session() as session:
        # Busca todas as faturas pendentes que já venceram
        overdue_invoices_query = select(Invoice).where(
            and_(
                Invoice.status == InvoiceStatus.PENDING,
                Invoice.due_date < now_utc
            )
        )
        result = await session.execute(overdue_invoices_query)
        invoices = result.scalars().all()
        
        for invoice in invoices:
            # Pega o usuário associado
            user_result = await session.execute(select(User).where(User.id == invoice.user_id))
            user = user_result.scalar_one_or_none()
            
            if not user:
                continue
            
            # Se atrasou, set status para OVERDUE se não estiver
            if invoice.status != InvoiceStatus.OVERDUE:
                invoice.status = InvoiceStatus.OVERDUE
            
            # Calcula dias de atraso
            days_overdue = (now_utc - invoice.due_date).days
            
            if days_overdue >= 5:
                # Bloqueia agendamento (Bloqueio Gradual)
                if user.is_adimplent:
                    user.is_adimplent = False
                    logger.warning(f"Usuário {user.email} bloqueado por atraso de {days_overdue} dias.")
                    await mock_send_email(
                        user.email,
                        "Aviso de Bloqueio de Agendamento - Uracan",
                        f"Olá {user.full_name}, seu acesso foi temporariamente bloqueado por falta de pagamento. Regularize no portal."
                    )
            elif days_overdue > 0:
                # Dispara notificação multicanal
                await mock_send_email(
                    user.email,
                    "Pendência Financeira Detectada - Uracan",
                    f"Olá {user.full_name}, identificamos uma fatura pendente. Por favor, regularize no seu Perfil."
                )
                await mock_push_notification(user.id, "Você possui uma pendência. Regularize para evitar bloqueios.")
        
        await session.commit()
    
    logger.info("Job finalizado com sucesso.")

if __name__ == "__main__":
    asyncio.run(run_daily_financial_check())
