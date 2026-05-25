"""
app/models/booking.py — Modelo SQLModel para las reservas (Bookings) integradas con Calendar.
"""
from sqlmodel import SQLModel, Field
from datetime import datetime, timezone
from typing import Optional

def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)

class BookingBase(SQLModel):
    client_name: str
    client_phone: str
    start_time: datetime
    end_time: datetime
    notes: Optional[str] = None
    google_event_id: Optional[str] = None # ID del evento en Google Calendar

class Booking(BookingBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    status: str = Field(default="confirmed") # confirmed, cancelled
    created_at: datetime = Field(default_factory=utc_now)

class BookingCreate(BookingBase):
    pass

class BookingRead(BookingBase):
    id: int
    status: str
    created_at: datetime
