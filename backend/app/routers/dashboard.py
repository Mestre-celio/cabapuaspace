from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, timezone, timedelta
from typing import Annotated, Optional

from app.db import get_async_db
from app.models.user import User, Role
from app.core.deps import get_current_user

router = APIRouter(prefix="/api/v1/dashboard", tags=["Dashboard"])

# === MODELS DE RESPOSTA (Pydantic v2) ===
from pydantic import BaseModel, Field
from enum import Enum

class ClassStatus(str, Enum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELED = "canceled"

class NextClassResponse(BaseModel):
    id: str
    class_name: str
    instructor: str
    start_time: str  # ISO format
    duration_minutes: int
    room: Optional[str] = None
    status: ClassStatus

class DashboardStatsResponse(BaseModel):
    total_classes: int
    attended_classes: int
    attendance_rate: float  # 0-100
    next_class: Optional[NextClassResponse]
    is_adimplent: bool
    last_updated: str

# === GET /stats ===
@router.get("/stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats(
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_async_db)
):
    from app.models.appointment import Appointment
    
    total_query = select(func.count(Appointment.id)).where(
        Appointment.user_id == current_user.id
    )
    total_result = await db.execute(total_query)
    total_classes = total_result.scalar_one() or 0
    
    attended_query = select(func.count(Appointment.id)).where(
        and_(
            Appointment.user_id == current_user.id,
            Appointment.status == ClassStatus.COMPLETED
        )
    )
    attended_result = await db.execute(attended_query)
    attended_classes = attended_result.scalar_one() or 0
    
    attendance_rate = round((attended_classes / total_classes * 100), 1) if total_classes > 0 else 0.0
    
    from app.models.class_slot import ClassSlot
    
    next_class_query = (
        select(Appointment, ClassSlot)
        .join(ClassSlot, Appointment.slot_id == ClassSlot.id)
        .where(
            Appointment.user_id == current_user.id,
            Appointment.status == ClassStatus.SCHEDULED,
            ClassSlot.start_time >= datetime.now(timezone.utc)
        )
        .order_by(ClassSlot.start_time.asc())
        .limit(1)
    )
    
    next_result = await db.execute(next_class_query)
    next_row = next_result.first()
    
    next_class_data = None
    if next_row:
        appointment, slot = next_row
        instructor_name = "Instrutor"
        class_name = "Aula"
        
        if slot.class_type:
            class_name = slot.class_type.name
        if slot.instructor and slot.instructor.full_name:
            instructor_name = slot.instructor.full_name
            
        next_class_data = NextClassResponse(
            id=str(appointment.id),
            class_name=class_name,
            instructor=instructor_name,
            start_time=slot.start_time.isoformat(),
            duration_minutes=slot.duration_minutes,
            room=slot.room.name if slot.room else None,
            status=ClassStatus.SCHEDULED
        )
    
    return DashboardStatsResponse(
        total_classes=total_classes,
        attended_classes=attended_classes,
        attendance_rate=attendance_rate,
        next_class=next_class_data,
        is_adimplent=current_user.is_adimplent,
        last_updated=datetime.now(timezone.utc).isoformat()
    )

@router.get("/appointments", response_model=list[NextClassResponse])
async def get_user_appointments(
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_async_db),
    status_filter: Optional[ClassStatus] = None,
    limit: int = 10,
    offset: int = 0
):
    from app.models.appointment import Appointment
    from app.models.class_slot import ClassSlot
    
    query = (
        select(Appointment, ClassSlot)
        .join(ClassSlot, Appointment.slot_id == ClassSlot.id)
        .where(Appointment.user_id == current_user.id)
        .order_by(ClassSlot.start_time.desc())
        .offset(offset)
        .limit(limit)
    )
    
    if status_filter:
        query = query.where(Appointment.status == status_filter)
    
    result = await db.execute(query)
    rows = result.all()
    
    appointments = []
    for appointment, slot in rows:
        instructor_name = slot.instructor.full_name if slot.instructor else "TBD"
        class_name = slot.class_type.name if slot.class_type else "Aula"
        
        appointments.append(
            NextClassResponse(
                id=str(appointment.id),
                class_name=class_name,
                instructor=instructor_name,
                start_time=slot.start_time.isoformat(),
                duration_minutes=slot.duration_minutes,
                room=slot.room.name if slot.room else None,
                status=appointment.status
            )
        )
    
    return appointments

# === ADMIN / INSTRUCTOR DASHBOARD ===

class AdminStatsResponse(BaseModel):
    total_students: int
    total_instructors: int
    total_appointments: int
    completed_appointments: int
    canceled_appointments: int
    scheduled_appointments: int
    today_appointments: int
    adimplent_percentage: float
    last_updated: str

@router.get("/admin/stats", response_model=AdminStatsResponse)
async def get_admin_stats(
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_async_db),
):
    if current_user.role not in [Role.INSTRUTOR, Role.ADMIN]:
        raise HTTPException(status_code=403, detail="Acesso restrito a instrutores e administradores")

    from app.models.appointment import Appointment, AppointmentStatus
    from app.models.user import Student

    students_count = await db.execute(select(func.count(User.id)).where(User.role == Role.ALUNO))
    total_students = students_count.scalar() or 0

    instructors_count = await db.execute(select(func.count(User.id)).where(User.role == Role.INSTRUTOR))
    total_instructors = instructors_count.scalar() or 0

    appointments_count = await db.execute(select(func.count(Appointment.id)))
    total_appointments = appointments_count.scalar() or 0

    completed_count = await db.execute(
        select(func.count(Appointment.id)).where(Appointment.status == AppointmentStatus.COMPLETED)
    )
    completed_appointments = completed_count.scalar() or 0

    canceled_count = await db.execute(
        select(func.count(Appointment.id)).where(Appointment.status == AppointmentStatus.CANCELED)
    )
    canceled_appointments = canceled_count.scalar() or 0

    scheduled_count = await db.execute(
        select(func.count(Appointment.id)).where(Appointment.status == AppointmentStatus.SCHEDULED)
    )
    scheduled_appointments = scheduled_count.scalar() or 0

    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    today_count = await db.execute(
        select(func.count(Appointment.id))
        .join(ClassSlot, Appointment.slot_id == ClassSlot.id)
        .where(
            Appointment.status == AppointmentStatus.SCHEDULED,
            ClassSlot.start_time >= today_start,
            ClassSlot.start_time < today_end,
        )
    )
    today_appointments = today_count.scalar() or 0

    adimplent_count = await db.execute(
        select(func.count(User.id)).where(User.is_adimplent == True, User.role == Role.ALUNO)
    )
    adimplent = adimplent_count.scalar() or 0
    adimplent_pct = round((adimplent / total_students * 100), 1) if total_students > 0 else 0.0

    return AdminStatsResponse(
        total_students=total_students,
        total_instructors=total_instructors,
        total_appointments=total_appointments,
        completed_appointments=completed_appointments,
        canceled_appointments=canceled_appointments,
        scheduled_appointments=scheduled_appointments,
        today_appointments=today_appointments,
        adimplent_percentage=adimplent_pct,
        last_updated=datetime.now(timezone.utc).isoformat(),
    )

@router.get("/admin/appointments", response_model=list[NextClassResponse])
async def get_all_appointments(
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_async_db),
    status_filter: Optional[ClassStatus] = None,
    limit: int = 50,
    offset: int = 0,
):
    if current_user.role not in [Role.INSTRUTOR, Role.ADMIN]:
        raise HTTPException(status_code=403, detail="Acesso restrito")

    from app.models.appointment import Appointment

    query = (
        select(Appointment, ClassSlot)
        .join(ClassSlot, Appointment.slot_id == ClassSlot.id)
        .order_by(ClassSlot.start_time.desc())
        .offset(offset)
        .limit(limit)
    )

    if status_filter:
        query = query.where(Appointment.status == status_filter)

    result = await db.execute(query)
    rows = result.all()

    items = []
    for appointment, slot in rows:
        instructor_name = slot.instructor.full_name if slot.instructor else "TBD"
        class_name = slot.class_type.name if slot.class_type else "Aula"
        items.append(
            NextClassResponse(
                id=str(appointment.id),
                class_name=class_name,
                instructor=instructor_name,
                start_time=slot.start_time.isoformat(),
                duration_minutes=slot.duration_minutes,
                room=slot.room.name if slot.room else None,
                status=appointment.status,
            )
        )
    return items
