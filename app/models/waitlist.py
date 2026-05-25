"""
app/models/waitlist.py — Modelo para suscriptores a la lista de espera.
"""
from sqlmodel import SQLModel, Field
from datetime import datetime, timezone
from typing import Optional


def utc_now() -> datetime:
    """Returns naive UTC datetime to avoid asyncpg timezone mismatch."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class WaitlistEntryBase(SQLModel):
    email: str = Field(index=True, unique=True)


class WaitlistEntry(WaitlistEntryBase, table=True):
    __tablename__ = "waitlist_entry"

    id: Optional[int] = Field(default=None, primary_key=True)
    discount_used: bool = Field(default=False)
    created_at: datetime = Field(default_factory=utc_now)


class WaitlistEntryCreate(SQLModel):
    email: str


class WaitlistEntryRead(WaitlistEntryBase):
    id: int
    discount_used: bool
    created_at: datetime
