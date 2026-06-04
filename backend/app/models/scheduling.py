'''Python
"""SQLAlchemy models for the scheduling subsystem of Cabapua Connect.
Includes:
- User with role, active flag, and payment status.
- LGPDConsent with granular scopes and audit fields.
- ClassType, ClassSlot (optional room), Appointment with status enum.
- Enumerations for role, consent scope, appointment status.
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

# ---------------------------- Enums ---------------------------------

class UserRole(str, enum.Enum):
    ALUNO = "aluno"
    INSTRUTOR = "instrutor"
    TERAPEUTA = "terapeuta"
    ADMIN = "admin"

class ConsentScope(str, enum.Enum):
    THERAPY_DATA = "therapy_data"
    PERFORMANCE_SHARE = "performance_share"
    MARKETING = "marketing"

class AppointmentStatus(str, enum.Enum):
    BOOKED = "booked"
    CANCELED = "canceled"
    NO_SHOW = "no_show"
    COMPLETED = "completed"

# ---------------------------- Models ---------------------------------

class User(Base):
    __tablename__ = "users"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, server_default=text("'aluno'"))
    is_active = Column(Boolean, nullable=False, server_default=text("true"))
    is_adimplent = Column(Boolean, nullable=False, server_default=text("true"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    consents = relationship("LGPDConsent", back_populates="user", cascade="all, delete-orphan")
    appointments = relationship("Appointment", back_populates="user", cascade="all, delete-orphan")
    slots = relationship("ClassSlot", back_populates="instructor")

class LGPDConsent(Base):
    __tablename__ = "lgpd_consents"
    __table_args__ = (
        UniqueConstraint("user_id", "scope", name="uq_user_scope"),
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    scope = Column(Enum(ConsentScope), nullable=False)
    consented = Column(Boolean, nullable=False, server_default=text("false"))
    ip_address = Column(String(45))  # IPv4/IPv6
    user_agent = Column(String)
    signed_at = Column(DateTime(timezone=True), server_default=func.now())
    version = Column(String(10), nullable=False, server_default=text("'1.0'"))
    expires_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="consents")

class ClassType(Base):
    __tablename__ = "class_types"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    is_private = Column(Boolean, nullable=False, server_default=text("false"))

    slots = relationship("ClassSlot", back_populates="class_type", cascade="all, delete-orphan")

class Room(Base):
    __tablename__ = "rooms"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)
    capacity = Column(Integer, nullable=False, server_default=text("20"))

    slots = relationship("ClassSlot", back_populates="room")

class ClassSlot(Base):
    __tablename__ = "class_slots"
    __table_args__ = (
        # Index to speed up time‑range queries
        Index("idx_slots_time", "start_time", "duration_min"),
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    class_type_id = Column(PGUUID(as_uuid=True), ForeignKey("class_types.id"), nullable=False)
    instructor_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    room_id = Column(PGUUID(as_uuid=True), ForeignKey("rooms.id"), nullable=True)
    start_time = Column(DateTime(timezone=True), nullable=False)
    duration_min = Column(Integer, nullable=False)
    capacity = Column(Integer, nullable=False, server_default=text("20"))
    booked_count = Column(Integer, nullable=False, server_default=text("0"))

    class_type = relationship("ClassType", back_populates="slots")
    instructor = relationship("User", back_populates="slots")
    room = relationship("Room", back_populates="slots")
    appointments = relationship("Appointment", back_populates="slot", cascade="all, delete-orphan")

class Appointment(Base):
    __tablename__ = "appointments"
    __table_args__ = (
        Index("idx_appt_user_time", "user_id", "slot_id"),
    )

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    slot_id = Column(PGUUID(as_uuid=True), ForeignKey("class_slots.id", ondelete="CASCADE"), nullable=False)
    status = Column(Enum(AppointmentStatus), nullable=False, server_default=text("'booked'"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    canceled_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="appointments")
    slot = relationship("ClassSlot", back_populates="appointments")
'''
