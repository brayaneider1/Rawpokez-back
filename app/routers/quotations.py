"""
app/routers/quotations.py — Endpoints para cotizaciones con IA y envío a WhatsApp de María.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from typing import List, Optional

from app.database import get_session
from app.models.quotation import Quotation, QuotationCreate, QuotationRead
from app.models.design import Design
from app.models.lead import Lead
from app.services.telegram_service import notify_new_quotation
from pydantic import BaseModel
from datetime import datetime

class ConfirmPayload(BaseModel):
    appointment_date: Optional[datetime] = None

router = APIRouter()


@router.post("/", response_model=QuotationRead, status_code=201)
async def create_quotation(
    quotation_in: QuotationCreate,
    session: AsyncSession = Depends(get_session),
):
    """
    1. Valida el diseño asociado (si aplica).
    2. Guarda la cotización en BD.
    3. Crea un Lead en el CRM automáticamente (stage: received).
    4. Envía mensaje formateado al WhatsApp de María (async, no bloquea).
    """
    # 1. Verificar diseño
    if quotation_in.design_id:
        design = await session.get(Design, quotation_in.design_id)
        if not design:
            quotation_in.design_id = None

    # 2. Guardar cotización
    quotation = Quotation.model_validate(quotation_in)
    
    # Strip tzinfo from appointment_date to avoid asyncpg naive vs aware mismatch
    if quotation.appointment_date and quotation.appointment_date.tzinfo:
        quotation.appointment_date = quotation.appointment_date.replace(tzinfo=None)

    session.add(quotation)
    await session.commit()
    await session.refresh(quotation)

    # 3. Crear Lead automático en CRM
    import json
    ai_snapshot = None
    if quotation.ai_quote_min:
        ai_snapshot = json.dumps({
            "precio_min": quotation.ai_quote_min,
            "precio_max": quotation.ai_quote_max,
            "tiempo_sesion": quotation.ai_session_time,
            "sesiones": quotation.ai_sessions_count,
            "descripcion": quotation.ai_description,
            "recomendacion": quotation.ai_recommendation,
        }, ensure_ascii=False)

    lead = Lead(
        source="quotation_form",
        client_name=quotation.client_name,
        client_phone=quotation.client_phone,
        client_email=quotation.client_email,
        pipeline_stage="received",
        ref_id=quotation.id,
        ai_quote_snapshot=ai_snapshot,
    )
    session.add(lead)
    await session.commit()

    # 4. Notificar via Telegram (no bloquea el flujo si falla)
    try:
        await notify_new_quotation(quotation)
    except Exception as tg_err:
        import logging
        logging.getLogger(__name__).error(f"Telegram notification failed: {tg_err}")

    return quotation


@router.get("/", response_model=List[QuotationRead])
async def get_quotations(
    session: AsyncSession = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
):
    """Historial de cotizaciones (admin)."""
    query = (
        select(Quotation)
        .offset(skip)
        .limit(limit)
        .order_by(Quotation.created_at.desc())  # type: ignore
    )
    result = await session.execute(query)
    return result.scalars().all()


@router.get("/{quotation_id}", response_model=QuotationRead)
async def get_quotation(quotation_id: int, session: AsyncSession = Depends(get_session)):
    quotation = await session.get(Quotation, quotation_id)
    if not quotation:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")
    return quotation

@router.get("/slots/booked", response_model=List[str])
async def get_booked_slots(session: AsyncSession = Depends(get_session)):
    """Retorna las fechas ISO de todas las citas confirmadas."""
    query = select(Quotation.appointment_date).where(Quotation.appointment_status == "confirmed", Quotation.appointment_date != None)
    result = await session.execute(query)
    dates = result.scalars().all()
    return [d.isoformat() for d in dates if d]

@router.post("/{quotation_id}/confirm", response_model=QuotationRead)
async def confirm_quotation(
    quotation_id: int,
    payload: ConfirmPayload,
    session: AsyncSession = Depends(get_session)
):
    """Admin endpoint: Confirma una cotización y (opcionalmente) actualiza la fecha."""
    quotation = await session.get(Quotation, quotation_id)
    if not quotation:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")
    
    quotation.appointment_status = "confirmed"
    if payload.appointment_date:
        if payload.appointment_date.tzinfo:
            quotation.appointment_date = payload.appointment_date.replace(tzinfo=None)
        else:
            quotation.appointment_date = payload.appointment_date
        
    session.add(quotation)
    await session.commit()
    await session.refresh(quotation)
    return quotation
