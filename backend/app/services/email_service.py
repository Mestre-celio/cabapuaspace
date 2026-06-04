import logging

logger = logging.getLogger("EmailService")

def send(to_email: str, subject: str, message: str):
    logger.info(f"[EMAIL MOCK] Enviando para {to_email} | Assunto: {subject}")
    logger.info(f"[EMAIL MOCK] Mensagem: {message}")
