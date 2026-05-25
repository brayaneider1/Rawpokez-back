"""
app/routers/bookings.py — Endpoints para gestionar las citas con Google Calendar.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List
from datetime import datetime

from app.database import get_session
from app.models.booking import Booking, BookingCreate, BookingRead
# from app.services.calendar_service import get_available_slots, create_calendar_event

router = APIRouter()

@router.get("/available")
async def get_availability(start_date: str, end_date: str):
    """
    Obtener slots disponibles desde Google Calendar.
    Ejemplo: /available?start_date=2024-05-01&end_date=2024-05-31
    """
    # Lógica que llamará a calendar_service.py
    # return await get_available_slots(start_date, end_date)
    return {"message": "Not implemented yet", "slots": []}

@router.post("/", response_model=BookingRead, status_code=201)
async def create_booking(booking_in: BookingCreate, session: AsyncSession = Depends(get_session)):
    """
    Crear una reserva:
    1. Valida disponibilidad (doble check).
    2. Crea evento en Google Calendar.
    3. Guarda en BD.
    4. Manda WhatsApp (opcional).
    """
    # 1. Lógica de calendario
    # event_id = await create_calendar_event(booking_in)
    
    # 2. Guardar en BD
    booking = Booking.model_validate(booking_in)
    # booking.google_event_id = event_id
    
    session.add(booking)
    await session.commit()
    await session.refresh(booking)
    
    return booking
