from enum import Enum

from sqlalchemy import Column, Enum as SQLEnum, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Role(str, Enum):
    ALUNO = "aluno"
    INSTRUTOR = "instrutor"
    TERAPEUTA = "terapeuta"
    ADMIN = "admin"
    CLIENTE = "cliente"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_adimplent = Column(Boolean, default=True)
    full_name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    birth_date = Column(String, nullable=True) # Format: YYYY-MM-DD
    role = Column(SQLEnum(Role), nullable=False)
    
    # Financial job tracking
    due_date = Column(String, nullable=True) # or DateTime
    last_notified_at = Column(String, nullable=True) # or DateTime

    # Relationships for extensions
    student = relationship("Student", uselist=False, back_populates="user")
    therapist = relationship("Therapist", uselist=False, back_populates="user")
    appointments = relationship("Appointment", back_populates="user")
    invoices = relationship("Invoice", back_populates="user")

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    # Additional student-specific fields
    enrollment_date = Column(String, nullable=True)
    master_comment = Column(String, nullable=True)
    user = relationship("User", back_populates="student")

class Therapist(Base):
    __tablename__ = "therapists"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    # Additional therapist-specific fields
    license_number = Column(String, nullable=True)
    user = relationship("User", back_populates="therapist")
