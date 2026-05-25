"""
app/models/order.py — Modelo para órdenes de compra con MercadoPago.
"""
from sqlmodel import SQLModel, Field
from datetime import datetime, timezone
from typing import Optional


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class OrderBase(SQLModel):
    client_name: str
    client_email: str
    client_phone: Optional[str] = None
    items_json: str                             # JSON serializado de los items del carrito
    total_cop: int                              # Total en pesos colombianos


class Order(OrderBase, table=True):
    __tablename__ = "order"

    id: Optional[int] = Field(default=None, primary_key=True)
    status: str = Field(default="pending")      # pending, approved, rejected, cancelled
    mp_preference_id: Optional[str] = None      # ID de la preferencia de MercadoPago
    mp_payment_id: Optional[str] = None         # ID del pago confirmado por MP
    created_at: datetime = Field(default_factory=utc_now)


class OrderCreate(OrderBase):
    pass


class OrderRead(OrderBase):
    id: int
    status: str
    mp_preference_id: Optional[str]
    mp_payment_id: Optional[str]
    created_at: datetime
