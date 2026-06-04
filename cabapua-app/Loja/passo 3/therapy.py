"""
Módulo 2 — Segurança LGPD (Clínica Selene)
Decorador @require_clinical_access + rotas de therapy_sessions.
"""

import functools
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.auth import get_current_user, TokenData  # seu módulo de auth JWT

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/therapy-sessions", tags=["therapy"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class TherapySessionCreate(BaseModel):
    patient_id: int
    therapist_id: int
    session_date: datetime
    notes: str | None = None
    duration_minutes: int = 50


class TherapySessionResponse(TherapySessionCreate):
    id: int
    created_at: datetime


# ---------------------------------------------------------------------------
# Decorador @require_clinical_access
# ---------------------------------------------------------------------------

def require_clinical_access(func):
    """
    Decorador LGPD para rotas clínicas.

    Regra de acesso:
      - Usuários com role='terapeuta' têm acesso a qualquer registro.
      - Demais usuários só podem acessar registros cujo patient_id == seu próprio id.

    Também grava um log de auditoria em `audit_logs` com:
      - accessed_by  (user_id do solicitante)
      - patient_id   (extraído do parâmetro de path ou body)
      - endpoint     (nome da função)
      - timestamp
    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        # Extrai dependências injetadas via kwargs pelo FastAPI
        current_user: TokenData = kwargs.get("current_user")
        db: AsyncSession = kwargs.get("db")
        patient_id: int | None = kwargs.get("patient_id")  # path param

        if current_user is None or db is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Dependências de segurança não injetadas corretamente.",
            )

        # ── Verificação de acesso ────────────────────────────────────────
        is_terapeuta = current_user.role == "terapeuta"
        is_owner = patient_id is not None and current_user.user_id == patient_id

        if not (is_terapeuta or is_owner):
            logger.warning(
                "Acesso negado: user_id=%s role=%s tentou acessar patient_id=%s",
                current_user.user_id,
                current_user.role,
                patient_id,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso não autorizado a este prontuário.",
            )

        # ── Log de auditoria (LGPD) ──────────────────────────────────────
        try:
            await db.execute(
                text(
                    """
                    INSERT INTO audit_logs
                        (accessed_by, patient_id, endpoint, ip_address, accessed_at)
                    VALUES
                        (:accessed_by, :patient_id, :endpoint, :ip, :now)
                    """
                ),
                {
                    "accessed_by": current_user.user_id,
                    "patient_id": patient_id,
                    "endpoint": func.__name__,
                    "ip": current_user.client_ip or "unknown",
                    "now": datetime.utcnow(),
                },
            )
            await db.commit()
        except Exception as exc:  # noqa: BLE001
            # Falha no log não deve bloquear o acesso legítimo, mas deve ser alertada
            logger.error("Falha ao gravar audit_log: %s", exc)

        return await func(*args, **kwargs)

    return wrapper


# ---------------------------------------------------------------------------
# Rotas — therapy_sessions
# ---------------------------------------------------------------------------

@router.post("/", response_model=TherapySessionResponse, status_code=status.HTTP_201_CREATED)
@require_clinical_access
async def create_session(
    payload: TherapySessionCreate,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Cria uma nova sessão terapêutica."""
    row = await db.execute(
        text(
            """
            INSERT INTO therapy_sessions
                (patient_id, therapist_id, session_date, notes, duration_minutes, created_at)
            VALUES
                (:patient_id, :therapist_id, :session_date, :notes, :duration, :now)
            RETURNING id, created_at
            """
        ),
        {
            "patient_id": payload.patient_id,
            "therapist_id": payload.therapist_id,
            "session_date": payload.session_date,
            "notes": payload.notes,
            "duration": payload.duration_minutes,
            "now": datetime.utcnow(),
        },
    )
    await db.commit()
    result = row.mappings().first()
    return TherapySessionResponse(**payload.dict(), **result)


@router.get("/{patient_id}", response_model=list[TherapySessionResponse])
@require_clinical_access
async def list_sessions(
    patient_id: int,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Lista todas as sessões de um paciente."""
    rows = await db.execute(
        text(
            """
            SELECT id, patient_id, therapist_id, session_date,
                   notes, duration_minutes, created_at
            FROM therapy_sessions
            WHERE patient_id = :patient_id
            ORDER BY session_date DESC
            """
        ),
        {"patient_id": patient_id},
    )
    return [TherapySessionResponse(**r) for r in rows.mappings().all()]


@router.get("/{patient_id}/{session_id}", response_model=TherapySessionResponse)
@require_clinical_access
async def get_session(
    patient_id: int,
    session_id: int,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retorna uma sessão específica."""
    row = await db.execute(
        text(
            """
            SELECT id, patient_id, therapist_id, session_date,
                   notes, duration_minutes, created_at
            FROM therapy_sessions
            WHERE id = :session_id AND patient_id = :patient_id
            """
        ),
        {"session_id": session_id, "patient_id": patient_id},
    )
    session = row.mappings().first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sessão não encontrada.")
    return TherapySessionResponse(**session)


@router.patch("/{patient_id}/{session_id}", response_model=TherapySessionResponse)
@require_clinical_access
async def update_session(
    patient_id: int,
    session_id: int,
    payload: TherapySessionCreate,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Atualiza notas e dados de uma sessão (apenas terapeuta responsável)."""
    await db.execute(
        text(
            """
            UPDATE therapy_sessions
            SET notes = :notes, duration_minutes = :duration
            WHERE id = :session_id AND patient_id = :patient_id
            """
        ),
        {
            "notes": payload.notes,
            "duration": payload.duration_minutes,
            "session_id": session_id,
            "patient_id": patient_id,
        },
    )
    await db.commit()
    return await get_session(
        patient_id=patient_id,
        session_id=session_id,
        current_user=current_user,
        db=db,
    )


@router.delete("/{patient_id}/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_clinical_access
async def delete_session(
    patient_id: int,
    session_id: int,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Exclui uma sessão (hard delete — considere soft delete em produção LGPD)."""
    await db.execute(
        text(
            "DELETE FROM therapy_sessions WHERE id = :session_id AND patient_id = :patient_id"
        ),
        {"session_id": session_id, "patient_id": patient_id},
    )
    await db.commit()
