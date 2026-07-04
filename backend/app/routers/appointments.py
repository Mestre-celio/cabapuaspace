from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from pydantic import BaseModel
from typing import Annotated, Optional
from datetime import datetime, timezone
import uuid

from app.db import get_async_db
from app.models.user import User, Role
from app.models.appointment import Appointment, AppointmentStatus
from app.models.class_slot import ClassSlot
from app.core.deps import get_current_user

router = APIRouter(prefix="/api/v1/appointments", tags=["Appointments"])

# === Schemas ===

class AppointmentCreate(BaseModel):
    slot_id: str

class AppointmentResponse(BaseModel):
    id: str
    user_id: int
    slot_id: str
    status: str
    class_name: Optional[str] = None
    instructor_name: Optional[str] = None
    start_time: Optional[str] = None
    duration_minutes: Optional[int] = None
    room_name: Optional[str] = None
    checkin_time: Optional[str] = None
    created_at: Optional[str] = None

    class Config:
        from_attributes = True

class AppointmentListResponse(BaseModel):
    appointments: list[AppointmentResponse]
    total: int

# === Helpers ===

async def _build_appointment_response(appointment: Appointment) -> AppointmentResponse:
    resp = AppointmentResponse(
        id=appointment.id,
        user_id=appointment.user_id,
        slot_id=appointment.slot_id,
        status=appointment.status.value,
        checkin_time=appointment.checkin_time.isoformat() if appointment.checkin_time else None,
        created_at=appointment.created_at.isoformat() if appointment.created_at else None,
    )
    if appointment.slot:
        resp.class_name = appointment.slot.class_type.name if appointment.slot.class_type else None
        resp.instructor_name = appointment.slot.instructor.full_name if appointment.slot.instructor else None
        resp.start_time = appointment.slot.start_time.isoformat() if appointment.slot.start_time else None
        resp.duration_minutes = appointment.slot.duration_minutes
        resp.room_name = appointment.slot.room.name if appointment.slot.room else None
    return resp

def _check_403(condition: bool, detail: str):
    if condition:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)

# === Endpoints ===

@router.get("/", response_model=AppointmentListResponse)
async def list_appointments(
    status_filter: Optional[str] = Query(None, alias="status"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_async_db),
):
    query = select(Appointment).where(Appointment.user_id == current_user.id)
    count_query = select(Appointment.id).where(Appointment.user_id == current_user.id)

    if status_filter:
        query = query.where(Appointment.status == status_filter)

    total_result = await db.execute(count_query)
    total = len(total_result.scalars().all())

    result = await db.execute(
        query.order_by(Appointment.created_at.desc()).offset(offset).limit(limit)
    )
    appointments = result.scalars().all()

    return AppointmentListResponse(
        appointments=[await _build_appointment_response(a) for a in appointments],
        total=total,
    )

@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(
    appointment_id: str,
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_async_db),
):
    result = await db.execute(
        select(Appointment).where(Appointment.id == appointment_id)
    )
    appointment = result.scalar_one_or_none()
    if not appointment:
        raise HTTPException(status_code=404, detail="Agendamento nao encontrado")
    _check_403(appointment.user_id != current_user.id and current_user.role != Role.ADMIN,
               "Voce nao tem permissao para ver este agendamento")
    return await _build_appointment_response(appointment)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_appointment(
    appointment_data: AppointmentCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_async_db)
):
    if not current_user.is_adimplent:
        raise HTTPException(
            status_code=403,
            detail="Acesso negado: pendencia financeira detectada. Entre em contato com a administracao."
        )

    slot_query = select(ClassSlot).where(ClassSlot.id == appointment_data.slot_id)
    result = await db.execute(slot_query)
    slot = result.scalar_one_or_none()

    if not slot:
        raise HTTPException(status_code=404, detail="Aula nao encontrada.")

    if slot.booked_count >= slot.capacity:
        raise HTTPException(status_code=400, detail="A aula ja esta lotada.")

    existing_query = select(Appointment).where(
        Appointment.user_id == current_user.id,
        Appointment.slot_id == appointment_data.slot_id,
        Appointment.status == AppointmentStatus.SCHEDULED
    )
    existing_result = await db.execute(existing_query)
    if existing_result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Voce ja esta agendado para esta aula.")

    new_appointment = Appointment(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        slot_id=slot.id,
        status=AppointmentStatus.SCHEDULED
    )
    db.add(new_appointment)
    slot.booked_count += 1
    await db.commit()

    return {"message": "Agendamento realizado com sucesso", "appointment_id": new_appointment.id}

@router.patch("/{appointment_id}/cancel")
async def cancel_appointment(
    appointment_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_async_db),
):
    result = await db.execute(
        select(Appointment).where(Appointment.id == appointment_id)
    )
    appointment = result.scalar_one_or_none()
    if not appointment:
        raise HTTPException(status_code=404, detail="Agendamento nao encontrado")

    _check_403(appointment.user_id != current_user.id and current_user.role != Role.ADMIN,
               "Voce nao tem permissao para cancelar este agendamento")
    _check_403(appointment.status == AppointmentStatus.CANCELED,
               "Este agendamento ja foi cancelado")

    appointment.status = AppointmentStatus.CANCELED
    appointment.canceled_at = datetime.now(timezone.utc)

    if appointment.slot:
        appointment.slot.booked_count = max(0, appointment.slot.booked_count - 1)

    await db.commit()
    return {"message": "Agendamento cancelado com sucesso"}

@router.patch("/{appointment_id}/checkin")
async def checkin_appointment(
    appointment_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_async_db),
):
    _check_403(current_user.role not in [Role.INSTRUTOR, Role.ADMIN],
               "Apenas instrutores ou administradores podem fazer check-in")

    result = await db.execute(
        select(Appointment).where(Appointment.id == appointment_id)
    )
    appointment = result.scalar_one_or_none()
    if not appointment:
        raise HTTPException(status_code=404, detail="Agendamento nao encontrado")
    _check_403(appointment.status != AppointmentStatus.SCHEDULED,
               "Este agendamento nao pode ter check-in (ja foi cancelado ou concluido)")

    appointment.status = AppointmentStatus.COMPLETED
    appointment.checkin_time = datetime.now(timezone.utc)
    await db.commit()

    return {"message": "Check-in realizado com sucesso"}
