"""
app/routers/leads.py — CRM Pipeline: CRUD de leads y cambio de etapa.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from typing import List, Optional
from datetime import datetime, timezone

from app.database import get_session
from app.models.lead import Lead, LeadCreate, LeadRead, LeadUpdateStage, LeadUpdateNotes, PIPELINE_STAGES

router = APIRouter()


@router.get("/", response_model=List[LeadRead])
async def get_leads(
    session: AsyncSession = Depends(get_session),
    stage: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
):
    """Listar leads del CRM. Filtrar por etapa con ?stage=received"""
    query = select(Lead).order_by(Lead.created_at.desc()).offset(skip).limit(limit)  # type: ignore
    if stage:
        query = select(Lead).where(Lead.pipeline_stage == stage).order_by(Lead.created_at.desc()).offset(skip).limit(limit)  # type: ignore
    result = await session.execute(query)
    return result.scalars().all()


@router.post("/", response_model=LeadRead, status_code=201)
async def create_lead(
    lead_in: LeadCreate,
    session: AsyncSession = Depends(get_session),
):
    """Crear un lead manualmente (también se crea automáticamente al crear quotation)."""
    lead = Lead.model_validate(lead_in)
    session.add(lead)
    await session.commit()
    await session.refresh(lead)
    return lead


@router.get("/{lead_id}", response_model=LeadRead)
async def get_lead(lead_id: int, session: AsyncSession = Depends(get_session)):
    lead = await session.get(Lead, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")
    return lead


@router.patch("/{lead_id}/stage", response_model=LeadRead)
async def update_lead_stage(
    lead_id: int,
    stage_update: LeadUpdateStage,
    session: AsyncSession = Depends(get_session),
):
    """Cambiar la etapa del pipeline de un lead (trigger del select picker en iPhone)."""
    if stage_update.pipeline_stage not in PIPELINE_STAGES:
        raise HTTPException(
            status_code=400,
            detail=f"Etapa inválida. Opciones: {', '.join(PIPELINE_STAGES)}"
        )

    lead = await session.get(Lead, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")

    lead.pipeline_stage = stage_update.pipeline_stage
    lead.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
    session.add(lead)
    await session.commit()
    await session.refresh(lead)

    # Etapa 'accepted' sin notificación por ahora o implementar via Telegram si se requiere

    return lead


@router.patch("/{lead_id}/notes", response_model=LeadRead)
async def update_lead_notes(
    lead_id: int,
    notes_update: LeadUpdateNotes,
    session: AsyncSession = Depends(get_session),
):
    """Actualizar notas de seguimiento de un lead."""
    lead = await session.get(Lead, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")

    lead.notes = notes_update.notes
    lead.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
    session.add(lead)
    await session.commit()
    await session.refresh(lead)
    return lead


@router.delete("/{lead_id}", status_code=204)
async def delete_lead(lead_id: int, session: AsyncSession = Depends(get_session)):
    """Eliminar un lead del CRM."""
    lead = await session.get(Lead, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado")
    await session.delete(lead)
    await session.commit()
