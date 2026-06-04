"""
Módulo 3 — Sistema de Presença (Academia Cabapuã)
Função backend de check-in com validação de plano ativo.
"""

import logging
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/attendance", tags=["attendance"])

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

PLAN_EXPIRY_DAYS = 30  # dias sem pagamento → plano vencido


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class CheckInRequest(BaseModel):
    student_id: int
    class_code: str


class CheckInResponse(BaseModel):
    success: bool
    message: str
    attendance_id: int | None = None
    attendance_total: int | None = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _plan_is_expired(last_payment_date: datetime | None) -> bool:
    """Retorna True se o último pagamento for mais antigo que PLAN_EXPIRY_DAYS."""
    if last_payment_date is None:
        return True  # nunca pagou → considera vencido
    cutoff = datetime.utcnow() - timedelta(days=PLAN_EXPIRY_DAYS)
    return last_payment_date < cutoff


# ---------------------------------------------------------------------------
# Lógica principal de check-in
# ---------------------------------------------------------------------------

async def process_checkin(
    student_id: int,
    class_code: str,
    db: AsyncSession,
) -> CheckInResponse:
    """
    Processa o check-in de um aluno:
      1. Verifica se o aluno existe.
      2. Verifica se o plano está 'active' e dentro do prazo de pagamento.
      3. Se ativo → registra presença + incrementa attendance_total.
      4. Se vencido → retorna mensagem amigável sem registrar presença.
    """
    # ── 1. Buscar aluno ──────────────────────────────────────────────────
    row = await db.execute(
        text(
            """
            SELECT id, name, plan_status, last_payment_date, attendance_total
            FROM students
            WHERE id = :student_id
            FOR UPDATE
            """
        ),
        {"student_id": student_id},
    )
    student = row.mappings().first()

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Aluno id={student_id} não encontrado.",
        )

    # ── 2. Verificar validade do plano ───────────────────────────────────
    plan_active = student["plan_status"] == "active"
    payment_expired = _plan_is_expired(student["last_payment_date"])

    if not plan_active or payment_expired:
        reason = (
            "plano inativo" if not plan_active
            else f"pagamento vencido há mais de {PLAN_EXPIRY_DAYS} dias"
        )
        logger.info(
            "Check-in bloqueado — aluno_id=%s motivo=%s", student_id, reason
        )
        return CheckInResponse(
            success=False,
            message=(
                f"Olá, {student['name']}! 😊 Identificamos que seu plano está com "
                f"pendência ({reason}). Por favor, regularize sua situação na recepção "
                "para continuar aproveitando as aulas. Aguardamos você!"
            ),
        )

    # ── 3. Verificar se a turma existe ───────────────────────────────────
    class_row = await db.execute(
        text("SELECT id FROM classes WHERE code = :code AND is_active = true"),
        {"code": class_code},
    )
    class_obj = class_row.mappings().first()

    if not class_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Aula com código '{class_code}' não encontrada ou inativa.",
        )

    # ── 4. Verificar duplicidade (aluno já fez check-in hoje nesta aula) ─
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    dup = await db.execute(
        text(
            """
            SELECT id FROM attendance
            WHERE student_id = :student_id
              AND class_id = :class_id
              AND checked_in_at >= :today
            """
        ),
        {"student_id": student_id, "class_id": class_obj["id"], "today": today_start},
    )
    if dup.mappings().first():
        return CheckInResponse(
            success=False,
            message=f"Check-in já registrado hoje para a aula '{class_code}'.",
        )

    # ── 5. Registrar presença ────────────────────────────────────────────
    att_row = await db.execute(
        text(
            """
            INSERT INTO attendance (student_id, class_id, checked_in_at)
            VALUES (:student_id, :class_id, :now)
            RETURNING id
            """
        ),
        {
            "student_id": student_id,
            "class_id": class_obj["id"],
            "now": datetime.utcnow(),
        },
    )
    attendance_id = att_row.scalar_one()

    # ── 6. Incrementar contador de presenças ─────────────────────────────
    upd = await db.execute(
        text(
            """
            UPDATE students
            SET attendance_total = attendance_total + 1
            WHERE id = :student_id
            RETURNING attendance_total
            """
        ),
        {"student_id": student_id},
    )
    new_total = upd.scalar_one()
    await db.commit()

    logger.info(
        "Check-in confirmado — aluno_id=%s aula=%s total=%s",
        student_id, class_code, new_total,
    )

    return CheckInResponse(
        success=True,
        message=f"Presença registrada! Bom treino, {student['name']}! 💪",
        attendance_id=attendance_id,
        attendance_total=new_total,
    )


# ---------------------------------------------------------------------------
# Route
# ---------------------------------------------------------------------------

@router.post("/checkin", response_model=CheckInResponse)
async def checkin(
    payload: CheckInRequest,
    db: AsyncSession = Depends(get_db),
) -> CheckInResponse:
    """Endpoint de check-in de aluno em aula."""
    return await process_checkin(
        student_id=payload.student_id,
        class_code=payload.class_code,
        db=db,
    )
