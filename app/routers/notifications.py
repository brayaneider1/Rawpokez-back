"""
app/routers/notifications.py — Web Push Notifications (subscribe + send).
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from typing import List
from pydantic import BaseModel

from app.database import get_session
from app.models.push_subscription import PushSubscription, PushSubscriptionCreate, PushSubscriptionRead
from app.services.push_service import send_push_notification
from app.config import get_settings

router = APIRouter()
settings = get_settings()


class SendNotificationRequest(BaseModel):
    title: str
    body: str
    url: str = "/"
    tag: str = "rawpokez-notification"


@router.post("/subscribe", response_model=PushSubscriptionRead, status_code=201)
async def subscribe(
    sub_in: PushSubscriptionCreate,
    session: AsyncSession = Depends(get_session),
):
    """Registrar suscripción push de un cliente (idempotente por endpoint)."""
    query = select(PushSubscription).where(PushSubscription.endpoint == sub_in.endpoint)
    result = await session.execute(query)
    existing = result.scalar_one_or_none()
    if existing:
        return existing

    sub = PushSubscription.model_validate(sub_in)
    session.add(sub)
    await session.commit()
    await session.refresh(sub)
    return sub


@router.post("/send")
async def send_notification_to_all(
    req: SendNotificationRequest,
    session: AsyncSession = Depends(get_session),
):
    """
    Enviar notificación push a TODOS los suscriptores activos.
    Solo para uso admin.
    """
    query = select(PushSubscription)
    result = await session.execute(query)
    subscriptions = result.scalars().all()

    if not subscriptions:
        return {"sent": 0, "failed": 0, "message": "No hay suscriptores"}

    sent = 0
    failed = 0
    dead_endpoints = []

    for sub in subscriptions:
        success = send_push_notification(
            endpoint=sub.endpoint,
            p256dh=sub.p256dh,
            auth=sub.auth,
            title=req.title,
            body=req.body,
            url=req.url,
            tag=req.tag,
        )
        if success:
            sent += 1
        else:
            failed += 1
            dead_endpoints.append(sub.id)

    # Limpiar endpoints muertos (que ya no existen en el browser)
    if dead_endpoints:
        for sub_id in dead_endpoints:
            sub = await session.get(PushSubscription, sub_id)
            if sub:
                await session.delete(sub)
        await session.commit()

    return {"sent": sent, "failed": failed, "total": len(subscriptions)}


@router.get("/vapid-public-key")
async def get_vapid_public_key():
    """Retorna la clave pública VAPID para el frontend (service worker)."""
    return {"public_key": settings.vapid_public_key}


@router.get("/test-telegram")
async def test_telegram():
    """Envía un mensaje de prueba al bot de Telegram de María. Solo para diagnóstico admin."""
    from app.services.telegram_service import send_telegram_message
    success = await send_telegram_message(
        "🧪 <b>Test de Conexión</b>\n\n"
        "✅ El bot de Telegram de RAWPOKEZ está correctamente configurado.\n"
        "Los mensajes de cotización llegarán aquí."
    )
    if success:
        return {"ok": True, "message": "Mensaje enviado correctamente a Telegram."}
    return {"ok": False, "message": "Falló el envío. Verifica TELEGRAM_BOT_TOKEN y TELEGRAM_CHAT_ID en el .env."}
