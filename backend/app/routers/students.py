from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Annotated

from app.db.session import get_async_db
from app.models.user import User, Student, Role
from app.core.security import get_current_user

router = APIRouter(prefix="/api/v1/students", tags=["Students"])

class CommentUpdate(BaseModel):
    comment: str

@router.patch("/{student_id}/comment")
async def update_master_comment(
    student_id: int,
    data: CommentUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_async_db)
):
    # Verificação de segurança: apenas instrutor ou admin podem editar o comentário
    if current_user.role not in [Role.INSTRUTOR, Role.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Acesso negado: apenas instrutores podem adicionar comentários."
        )
        
    result = await db.execute(select(Student).where(Student.id == student_id))
    student = result.scalar_one_or_none()
    
    if not student:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
        
    student.master_comment = data.comment
    await db.commit()
    
    return {"message": "Comentário atualizado com sucesso"}
