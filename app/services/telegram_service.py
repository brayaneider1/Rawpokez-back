import httpx
import logging
from app.config import get_settings
from app.models.quotation import Quotation

logger = logging.getLogger(__name__)
settings = get_settings()

async def send_telegram_message(text: str):
    """Envía un mensaje simple vía Telegram Bot API."""
    if not settings.telegram_bot_token or not settings.telegram_chat_id:
        logger.warning("Telegram Bot Token o Chat ID no configurados.")
        return False
    
    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
    payload = {
        "chat_id": settings.telegram_chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=10.0)
            if not response.is_success:
                logger.error(f"Telegram API error {response.status_code}: {response.text}")
                return False
            logger.info("Telegram notification sent successfully.")
            return True
    except Exception as e:
        logger.error(f"Error enviando mensaje a Telegram: {e}")
        return False

async def notify_new_quotation(quotation: Quotation):
    """Notifica a María sobre una nueva cotización recibida."""
    # appointment_date ahora es Optional[str] (ej: "Lunes", "Martes")
    fecha = quotation.appointment_date or "Por definir"
    
    msg = (
        f"<b>✨ ¡Nueva Cotización Recibida!</b>\n\n"
        f"👤 <b>Cliente:</b> {quotation.client_name}\n"
        f"📱 <b>WhatsApp:</b> {quotation.client_phone}\n"
        f"📍 <b>Zona:</b> {quotation.body_zone}\n"
        f"📏 <b>Tamaño:</b> {quotation.size_category or 'No especificado'}\n"
        f"⚠️ <b>Alergias:</b> {quotation.allergies or 'Ninguna'}\n"
        f"💡 <b>Idea:</b> {quotation.idea_description or 'Sin descripción'}\n"
        f"📅 <b>Fecha preferida:</b> {fecha}\n\n"
        f"🎨 <b>Diseño:</b> {'Flash #' + str(quotation.design_id) if quotation.design_id else 'Personalizado'}\n"
    )
    
    if quotation.ai_quote_min:
        msg += (
            f"\n--- <i>Sugerencia de IA</i> ---\n"
            f"💰 <b>Precio:</b> ${quotation.ai_quote_min:,} - ${quotation.ai_quote_max:,}\n"
            f"⏱️ <b>Tiempo:</b> {quotation.ai_session_time}\n"
        )
    
    msg += f"\n👉 <a href='{settings.frontend_url}/admin/quotations'>Ver en el Panel</a>"
    
    return await send_telegram_message(msg)
