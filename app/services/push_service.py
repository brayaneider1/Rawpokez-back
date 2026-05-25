"""
app/services/push_service.py — Servicio de Web Push Notifications usando pywebpush.
"""
import json
from typing import Optional
from pywebpush import webpush, WebPushException
from app.config import get_settings

settings = get_settings()


def _build_notification_payload(
    title: str,
    body: str,
    url: str = "/",
    icon: str = "/assets/rawlogo.svg",
    badge: str = "/assets/rawlogo.svg",
    tag: Optional[str] = None,
) -> str:
    """Construye el payload JSON de la notificación push."""
    payload = {
        "title": title,
        "body": body,
        "url": url,
        "icon": icon,
        "badge": badge,
    }
    if tag:
        payload["tag"] = tag
    return json.dumps(payload)


def send_push_notification(
    endpoint: str,
    p256dh: str,
    auth: str,
    title: str,
    body: str,
    url: str = "/",
    tag: Optional[str] = None,
) -> bool:
    """
    Envía una notificación push a un suscriptor específico.
    Retorna True si fue exitoso, False en caso de error.
    """
    try:
        webpush(
            subscription_info={
                "endpoint": endpoint,
                "keys": {"p256dh": p256dh, "auth": auth},
            },
            data=_build_notification_payload(title, body, url, tag=tag),
            vapid_private_key=settings.vapid_private_key,
            vapid_claims={
                "sub": f"mailto:{settings.vapid_claim_email}",
            },
        )
        return True
    except WebPushException as e:
        print(f"[Push] Error enviando a {endpoint[:50]}...: {e}")
        return False
    except Exception as e:
        print(f"[Push] Error inesperado: {e}")
        return False
