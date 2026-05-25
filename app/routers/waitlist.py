"""
app/routers/waitlist.py — Endpoints para la lista de espera (suscripción email).
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from typing import List

from app.database import get_session
from app.models.waitlist import WaitlistEntry, WaitlistEntryCreate, WaitlistEntryRead

router = APIRouter()


@router.post("/", response_model=WaitlistEntryRead, status_code=201)
async def subscribe_waitlist(
    entry_in: WaitlistEntryCreate,
    session: AsyncSession = Depends(get_session),
):
    """Suscribir un email a la lista de espera. Retorna 409 si ya existe."""
    # Verificar si el email ya existe
    query = select(WaitlistEntry).where(WaitlistEntry.email == entry_in.email)
    result = await session.execute(query)
    existing = result.scalar_one_or_none()

    if existing:
        # Retornamos el registro existente (idempotente, no falla)
        return existing

    entry = WaitlistEntry(email=entry_in.email)
    session.add(entry)
    await session.commit()
    await session.refresh(entry)
    return entry


@router.get("/", response_model=List[WaitlistEntryRead])
async def get_waitlist(
    session: AsyncSession = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
):
    """Obtener lista de suscriptores (admin)."""
    query = select(WaitlistEntry).offset(skip).limit(limit)
    result = await session.execute(query)
    return result.scalars().all()
