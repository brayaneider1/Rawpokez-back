"""
app/models/push_subscription.py — Modelo para suscripciones Web Push.
"""
from sqlmodel import SQLModel, Field
from datetime import datetime, timezone
from typing import Optional


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class PushSubscriptionBase(SQLModel):
    endpoint: str = Field(unique=True)
    p256dh: str       # Clave pública del cliente
    auth: str         # Auth secret del cliente
    user_agent: Optional[str] = None


class PushSubscription(PushSubscriptionBase, table=True):
    __tablename__ = "push_subscription"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=utc_now)


class PushSubscriptionCreate(PushSubscriptionBase):
    pass


class PushSubscriptionRead(PushSubscriptionBase):
    id: int
    created_at: datetime
