"""
app/routers/designs.py — Endpoints para gestionar los diseños del portafolio.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from typing import List

from app.database import get_session
from app.models.design import Design, DesignCreate, DesignRead, DesignUpdate

router = APIRouter()

@router.get("/", response_model=List[DesignRead])
async def get_designs(
    session: AsyncSession = Depends(get_session),
    skip: int = 0,
    limit: int = Query(default=100, le=100),
    available_only: bool = False
):
    """Obtener catálogo de diseños."""
    query = select(Design)
    if available_only:
        query = query.where(Design.available == True)
    
    query = query.offset(skip).limit(limit)
    result = await session.execute(query)
    designs = result.scalars().all()
    return designs

@router.get("/{design_id}", response_model=DesignRead)
async def get_design(design_id: int, session: AsyncSession = Depends(get_session)):
    """Obtener un diseño específico por ID."""
    design = await session.get(Design, design_id)
    if not design:
        raise HTTPException(status_code=404, detail="Design not found")
    return design

@router.post("/", response_model=DesignRead, status_code=201)
async def create_design(design_in: DesignCreate, session: AsyncSession = Depends(get_session)):
    """Crear un nuevo diseño (Admin)."""
    # TODO: Add auth dependency later
    design = Design.model_validate(design_in)
    session.add(design)
    await session.commit()
    await session.refresh(design)
    return design

@router.patch("/{design_id}", response_model=DesignRead)
async def update_design(
    design_id: int, 
    design_in: DesignUpdate, 
    session: AsyncSession = Depends(get_session)
):
    """Actualizar un diseño existente (Admin)."""
    # TODO: Add auth dependency later
    design = await session.get(Design, design_id)
    if not design:
        raise HTTPException(status_code=404, detail="Design not found")
    
    update_data = design_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(design, key, value)
        
    session.add(design)
    await session.commit()
    await session.refresh(design)
    return design

@router.delete("/{design_id}", status_code=204)
async def delete_design(design_id: int, session: AsyncSession = Depends(get_session)):
    """Eliminar un diseño (Admin)."""
    # TODO: Add auth dependency later
    design = await session.get(Design, design_id)
    if not design:
        raise HTTPException(status_code=404, detail="Design not found")
    
    await session.delete(design)
    await session.commit()
    return None
