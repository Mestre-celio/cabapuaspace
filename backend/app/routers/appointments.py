from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from pydantic import BaseModel
from typing import Annotated

from app.db import get_async_db
from app.models.user import User
from app.models.appointment import Appointment, AppointmentStatus
from app.models.class_slot import ClassSlot
from app.core.deps import get_current_user
import uuid

router = APIRouter(prefix="/api/v1/appointments", tags=["Appointments"])

class AppointmentCreate(BaseModel):
    slot_id: str

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_appointment(
    appointment_data: AppointmentCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_async_db)
):
    # Validação crítica de adimplência
    if not current_user.is_adimplent:
        raise HTTPException(
            status_code=403, 
            detail="Acesso negado: pendência financeira detectada. Entre em contato com a administração."
        )
    
    # Valida slot
    slot_query = select(ClassSlot).where(ClassSlot.id == appointment_data.slot_id)
    result = await db.execute(slot_query)
    slot = result.scalar_one_or_none()
    
    if not slot:
        raise HTTPException(status_code=404, detail="Aula não encontrada.")
    
    if slot.booked_count >= slot.capacity:
        raise HTTPException(status_code=400, detail="A aula já está lotada.")
        
    # Checa se já está agendado
    existing_query = select(Appointment).where(
        Appointment.user_id == current_user.id,
        Appointment.slot_id == appointment_data.slot_id,
        Appointment.status == AppointmentStatus.SCHEDULED
    )
    existing_result = await db.execute(existing_query)
    if existing_result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Você já está agendado para esta aula.")
    
    # Cria o agendamento
    new_appointment = Appointment(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        slot_id=slot.id,
        status=AppointmentStatus.SCHEDULED
    )
    db.add(new_appointment)
    
    # Atualiza vagas
    slot.booked_count += 1
    
    await db.commit()
    
    return {"message": "Agendamento realizado com sucesso", "appointment_id": new_appointment.id}
