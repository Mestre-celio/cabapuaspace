from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.db import create_db_and_tables
from app.routers import auth, dashboard, appointments, students

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: criar tabelas se necessário
    await create_db_and_tables()
    
    # Iniciar jobs agendados
    try:
        from app.jobs.birthday_job import scheduler
        scheduler.start()
    except Exception as e:
        print(f"Erro ao iniciar scheduler: {e}")
        
    yield
    
    # Shutdown: limpar conexões se necessário
    try:
        from app.jobs.birthday_job import scheduler
        scheduler.shutdown()
    except Exception:
        pass

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API para CT Cabapuã + Clínica Selene + Uracan Fight Wear",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(appointments.router)
app.include_router(students.router)

# Health check & Test routes
@app.get("/api/v1/test/birthday-trigger")
async def trigger_birthday():
    from app.jobs.birthday_job import birthday_check
    birthday_check()
    return {"message": "Job de aniversário disparado com sucesso."}

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "cabapua-api"}

@app.get("/")
async def root():
    return {
        "message": f"{settings.APP_NAME} v{settings.APP_VERSION}",
        "docs": "/docs",
        "redoc": "/redoc"
    }
