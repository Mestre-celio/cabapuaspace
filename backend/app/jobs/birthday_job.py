from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import logging
from app.services import email_service, whatsapp_service
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.user import User

def _sync_dsn(dsn: str) -> str:
    dsn = dsn.replace("+asyncpg", "").replace("+aiosqlite", "").replace("+psycopg", "").replace("+psycopg2", "")
    return dsn

sync_engine = create_engine(_sync_dsn(settings.DATABASE_URL))
SyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

logger = logging.getLogger("BirthdayJob")

def get_users_by_birthday(month_day: str):
    with SyncSessionLocal() as session:
        users = session.query(User).filter(User.birth_date.like(f"%{month_day}")).all()
        return users

def birthday_check():
    logger.info("Executando Birthday Check...")
    today = datetime.now().strftime("-%m-%d") # e.g. -06-04
    
    # Busca alunos cujo aniversário é hoje
    alunnos = get_users_by_birthday(today) 
    
    for aluno in alunnos:
        msg = f"Mestre Célio D'Lua parabeniza você, {aluno.full_name or 'Aluno'}, por mais um ciclo de vida. Que sua força se renove no tatame."
        email_service.send(aluno.email, "Feliz Aniversário!", msg)
        if aluno.phone:
            whatsapp_service.send(aluno.phone, msg)
            
    logger.info(f"Birthday Check concluído. Notificados {len(alunnos)} alunos.")

scheduler = BackgroundScheduler()
scheduler.add_job(birthday_check, 'cron', hour=8, minute=0) # Disparo às 08:00
# Don't start it globally here to avoid thread issues, we'll start it in main.py lifespan
