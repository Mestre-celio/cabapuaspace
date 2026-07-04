from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
from typing import Annotated

from app.db import get_async_db
from app.models.user import User
from app.schemas.auth import (
    UserRegister, UserLogin, TokenResponse,
    RefreshRequest,
    UserResponse, MessageResponse
)
from app.core.security import (
    verify_password, get_password_hash,
    create_access_token, decode_access_token,
    create_refresh_token, decode_refresh_token,
)

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])
security = HTTPBearer()

# === Dependency: Extrair token do header ===
async def get_token_header(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
) -> str:
    return credentials.credentials

# === Dependency: Validar usuário ativo ===
async def get_current_user(
    token: Annotated[str, Depends(get_token_header)],
    db: AsyncSession = Depends(get_async_db)
) -> User:
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token malformado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado ou inativo",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

# === POST /register ===
@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_async_db)
) -> TokenResponse:
    # Verificar email duplicado
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado"
        )
    
    # Criar usuário
    new_user = User(
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        phone=user_data.phone,
        is_active=True,
        is_adimplent=True,  # Novo usuário começa adimplente
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    # Gerar tokens
    token_data = {"sub": str(new_user.id), "role": new_user.role}
    access_token = create_access_token(data=token_data)
    refresh_token = create_refresh_token(data=token_data)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(new_user)
    )

# === POST /login ===
@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_async_db)
) -> TokenResponse:
    # Buscar usuário
    result = await db.execute(select(User).where(User.email == credentials.email))
    user = result.scalar_one_or_none()
    
    # Validar credenciais
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha inválidos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verificar status
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta desativada. Contate o suporte."
        )
    
    # Atualizar last_login (se o campo existir no modelo)
    if hasattr(user, 'last_login'):
        user.last_login = datetime.now(timezone.utc)
        await db.commit()
    
    # Gerar tokens
    token_data = {"sub": str(user.id), "role": user.role}
    access_token = create_access_token(data=token_data)
    refresh_token = create_refresh_token(data=token_data)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user)
    )

# === POST /refresh (renovar access_token) ===
@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    body: RefreshRequest,
    db: AsyncSession = Depends(get_async_db)
) -> TokenResponse:
    payload = decode_refresh_token(body.refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido ou expirado",
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token malformado",
        )
    
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado ou inativo",
        )
    
    token_data = {"sub": str(user.id), "role": user.role}
    access_token = create_access_token(data=token_data)
    refresh_token = create_refresh_token(data=token_data)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user)
    )

# === GET /me (perfil do usuário logado) ===
@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: Annotated[User, Depends(get_current_user)]
) -> UserResponse:
    return UserResponse.model_validate(current_user)

# === POST /logout (invalidar token no frontend) ===
@router.post("/logout", response_model=MessageResponse)
async def logout() -> MessageResponse:
    # Obs: JWT é stateless, o "logout" é feito no frontend removendo o token
    return MessageResponse(message="Logout realizado com sucesso")
