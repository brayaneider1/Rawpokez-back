"""
app/routers/orders.py — Órdenes de compra con integración MercadoPago.
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from typing import List
import json
import httpx

from app.database import get_session
from app.models.order import Order, OrderCreate, OrderRead
from app.models.lead import Lead
from app.config import get_settings

router = APIRouter()
settings = get_settings()

MP_API_BASE = "https://api.mercadopago.com/checkout/preferences"


@router.post("/", response_model=OrderRead, status_code=201)
async def create_order(
    order_in: OrderCreate,
    session: AsyncSession = Depends(get_session),
):
    """
    Crea la orden en BD y una preferencia en MercadoPago.
    Retorna el init_point (URL de pago) para redirigir al usuario.
    """
    # 1. Guardar orden en BD
    order = Order.model_validate(order_in)
    session.add(order)
    await session.commit()
    await session.refresh(order)

    # 2. Crear preferencia en MercadoPago
    items = json.loads(order_in.items_json)
    mp_items = [
        {
            "title": item["name"],
            "quantity": item["quantity"],
            "unit_price": item["price_cop"] / 100,  # MP usa pesos con decimales
            "currency_id": "COP",
        }
        for item in items
    ]

    mp_payload = {
        "items": mp_items,
        "payer": {
            "name": order_in.client_name,
            "email": order_in.client_email,
        },
        "back_urls": {
            "success": f"{settings.frontend_url}/tienda/gracias",
            "failure": f"{settings.frontend_url}/tienda",
            "pending": f"{settings.frontend_url}/tienda/pendiente",
        },
        "auto_return": "approved",
        "external_reference": str(order.id),
        "notification_url": f"{settings.backend_url}/api/v1/orders/webhook",
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            mp_response = await client.post(
                MP_API_BASE,
                headers={
                    "Authorization": f"Bearer {settings.mp_access_token}",
                    "Content-Type": "application/json",
                },
                json=mp_payload,
            )
            mp_response.raise_for_status()
            mp_data = mp_response.json()

        # 3. Actualizar orden con preference_id de MP
        order.mp_preference_id = mp_data["id"]
        session.add(order)
        await session.commit()
        await session.refresh(order)

        # 4. Crear Lead en CRM
        lead = Lead(
            source="store_purchase",
            client_name=order_in.client_name,
            client_phone=order_in.client_phone or "",
            client_email=order_in.client_email,
            pipeline_stage="received",
            ref_id=order.id,
        )
        session.add(lead)
        await session.commit()

        return {**order.model_dump(), "init_point": mp_data.get("init_point")}

    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Error con MercadoPago: {str(e)}")


@router.post("/webhook")
async def mercadopago_webhook(request: Request, session: AsyncSession = Depends(get_session)):
    """Webhook de MercadoPago para actualizar el estado del pago."""
    data = await request.json()
    if data.get("type") == "payment":
        payment_id = data.get("data", {}).get("id")
        order_ref = data.get("external_reference")
        if order_ref:
            order = await session.get(Order, int(order_ref))
            if order:
                order.mp_payment_id = str(payment_id)
                order.status = "approved"
                session.add(order)
                await session.commit()
    return {"status": "ok"}


@router.get("/", response_model=List[OrderRead])
async def get_orders(
    session: AsyncSession = Depends(get_session),
    skip: int = 0,
    limit: int = 50,
):
    """Listar órdenes (admin)."""
    query = select(Order).order_by(Order.created_at.desc()).offset(skip).limit(limit)  # type: ignore
    result = await session.execute(query)
    return result.scalars().all()
