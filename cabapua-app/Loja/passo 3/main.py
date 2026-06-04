"""
main.py — Entrypoint da aplicação FastAPI.
Registra todos os routers dos módulos desenvolvidos.
"""

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends
from sqlalchemy import text

from auth import verify_password, create_access_token, get_current_user, TokenData
from database import get_db as _get_db
from checkout import router as checkout_router
from therapy import router as therapy_router
from attendance import router as attendance_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Plataforma Multi-Negócios",
        description="APIs para Loja Uracan, Clínica Selene e Academia Cabapuã",
        version="1.0.0",
    )

    # ── CORS ────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # restringir em produção
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Routers ─────────────────────────────────────────────────────────
    app.include_router(checkout_router)
    app.include_router(therapy_router)
    app.include_router(attendance_router)

    # ── Auth login route ─────────────────────────────────────────────────
    @app.post("/auth/login")
    async def login(
        credentials: dict,
        db=Depends(_get_db),
    ):
        username = credentials.get("username")
        password = credentials.get("password")

        row = await db.execute(
            text("SELECT id, hashed_password, role FROM users WHERE email = :email"),
            {"email": username},
        )
        user = row.mappings().first()

        if not user or not verify_password(password, user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciais inválidas.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = create_access_token(data={"sub": str(user["id"]), "role": user["role"]})
        return {"access_token": token, "token_type": "bearer"}

    # ── Rota admin (exemplo protegida por role) ──────────────────────────


    @app.get("/admin/dashboard")
    async def admin_dashboard(current_user: TokenData = Depends(get_current_user)):
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso restrito a administradores.",
            )
        return {"message": "Bem-vindo ao painel admin."}

    # ── Handler global de erros ──────────────────────────────────────────
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        if isinstance(exc, HTTPException):
            raise exc
        return JSONResponse(
            status_code=500,
            content={"detail": "Erro interno do servidor. Tente novamente."},
        )

    return app


app = create_app()
