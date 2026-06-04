import logging

logger = logging.getLogger("WhatsAppService")

def send(to_phone: str, message: str):
    logger.info(f"[WHATSAPP MOCK] Enviando para {to_phone}")
    logger.info(f"[WHATSAPP MOCK] Mensagem: {message}")
