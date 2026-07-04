from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload
from pydantic import BaseModel
from typing import Annotated, Optional
from datetime import datetime

from app.db import get_async_db
from app.models.user import User, Student, Role
from app.core.deps import get_current_user

router = APIRouter(prefix="/api/v1/students", tags=["Students"])

# === Schemas ===

class StudentResponse(BaseModel):
    id: int
    user_id: int
    email: str
    full_name: str
    phone: Optional[str] = None
    role: str
    enrollment_date: Optional[str] = None
    master_comment: Optional[str] = None
    is_adimplent: bool
    is_active: bool

    class Config:
        from_attributes = True

class StudentListResponse(BaseModel):
    students: list[StudentResponse]
    total: int
    page: int
    per_page: int

class StudentUpdate(BaseModel):
    enrollment_date: Optional[str] = None
    master_comment: Optional[str] = None

class CommentUpdate(BaseModel):
    comment: str

# === Helpers ===

async def _build_student_response(student: Student) -> StudentResponse:
    return StudentResponse(
        id=student.id,
        user_id=student.user_id,
        email=student.user.email,
        full_name=student.user.full_name,
        phone=student.user.phone,
        role=student.user.role.value,
        enrollment_date=student.enrollment_date,
        master_comment=student.master_comment,
        is_adimplent=student.user.is_adimplent,
        is_active=student.user.is_active,
    )

async def _get_student_or_404(db: AsyncSession, student_id: int) -> Student:
    result = await db.execute(
        select(Student).where(Student.id == student_id)
    )
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Aluno nao encontrado")
    return student

# === Endpoints ===

@router.get("/", response_model=StudentListResponse)
async def list_students(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: AsyncSession = Depends(get_async_db),
):
    query = select(Student).join(User)
    count_query = select(func.count(Student.id)).select_from(Student).join(User)

    if search:
        like = f"%{search}%"
        query = query.where(
            User.full_name.ilike(like) | User.email.ilike(like)
        )
        count_query = count_query.where(
            User.full_name.ilike(like) | User.email.ilike(like)
        )

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    offset = (page - 1) * per_page
    result = await db.execute(
        query.order_by(User.full_name).offset(offset).limit(per_page)
    )
    students = result.scalars().all()

    return StudentListResponse(
        students=[await _build_student_response(s) for s in students],
        total=total,
        page=page,
        per_page=per_page,
    )

@router.get("/me", response_model=StudentResponse)
async def get_my_student(
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_async_db),
):
    result = await db.execute(
        select(Student).where(Student.user_id == current_user.id)
    )
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Perfil de aluno nao encontrado")
    return await _build_student_response(student)

@router.get("/{student_id}", response_model=StudentResponse)
async def get_student(
    student_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: Annotated[User, Depends(get_current_user)] = None,
):
    result = await db.execute(
        select(Student).where(Student.id == student_id)
    )
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Aluno nao encontrado")
    return await _build_student_response(student)

@router.post("/", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
async def create_student(
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_async_db),
):
    if current_user.role not in [Role.ALUNO, Role.ADMIN]:
        raise HTTPException(status_code=403, detail="Apenas alunos podem criar perfil de aluno")

    result = await db.execute(
        select(Student).where(Student.user_id == current_user.id)
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Voce ja possui um perfil de aluno")

    student = Student(
        user_id=current_user.id,
        enrollment_date=datetime.now().strftime("%Y-%m-%d"),
    )
    db.add(student)
    await db.commit()
    await db.refresh(student)
    return await _build_student_response(student)

@router.put("/{student_id}", response_model=StudentResponse)
async def update_student(
    student_id: int,
    data: StudentUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_async_db),
):
    student = await _get_student_or_404(db, student_id)

    if current_user.id != student.user_id and current_user.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="Voce nao tem permissao para editar este aluno")

    if data.enrollment_date is not None:
        student.enrollment_date = data.enrollment_date
    if data.master_comment is not None and current_user.role in [Role.INSTRUTOR, Role.ADMIN]:
        student.master_comment = data.master_comment

    await db.commit()
    await db.refresh(student)
    return await _build_student_response(student)

@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_student(
    student_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_async_db),
):
    if current_user.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="Apenas administradores podem remover alunos")

    student = await _get_student_or_404(db, student_id)
    await db.delete(student)
    await db.commit()

@router.patch("/{student_id}/comment")
async def update_master_comment(
    student_id: int,
    data: CommentUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_async_db),
):
    if current_user.role not in [Role.INSTRUTOR, Role.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: apenas instrutores podem adicionar comentarios."
        )

    student = await _get_student_or_404(db, student_id)
    student.master_comment = data.comment
    await db.commit()
    return {"message": "Comentario atualizado com sucesso"}
