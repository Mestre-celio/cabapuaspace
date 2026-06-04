from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
import uuid

from app.models.user import Base

class ClassType(Base):
    __tablename__ = "class_types"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String)
    slots = relationship("ClassSlot", back_populates="class_type")

class Room(Base):
    __tablename__ = "rooms"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String)
    slots = relationship("ClassSlot", back_populates="room")

class ClassSlot(Base):
    __tablename__ = "class_slots"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    class_type_id = Column(String, ForeignKey("class_types.id"))
    instructor_id = Column(Integer, ForeignKey("users.id"))
    room_id = Column(String, ForeignKey("rooms.id"), nullable=True)
    
    start_time = Column(DateTime(timezone=True), nullable=False, index=True)
    duration_minutes = Column(Integer, default=60)
    capacity = Column(Integer, default=20)
    booked_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    class_type = relationship("ClassType", back_populates="slots")
    instructor = relationship("User", foreign_keys=[instructor_id])
    room = relationship("Room", back_populates="slots")
    appointments = relationship("Appointment", back_populates="slot")
