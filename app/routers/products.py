"""
app/routers/products.py — CRUD de productos de la tienda Handpoke.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from typing import List, Optional

from app.database import get_session
from app.models.product import Product, ProductCreate, ProductRead, ProductUpdate

router = APIRouter()


@router.get("/", response_model=List[ProductRead])
async def get_products(
    session: AsyncSession = Depends(get_session),
    category: Optional[str] = None,
    active_only: bool = True,
):
    """Listar productos. Filtrar por categoría y/o solo activos."""
    query = select(Product)
    if active_only:
        query = query.where(Product.active == True)  # noqa: E712
    if category:
        query = query.where(Product.category == category)
    result = await session.execute(query)
    return result.scalars().all()


@router.post("/", response_model=ProductRead, status_code=201)
async def create_product(
    product_in: ProductCreate,
    session: AsyncSession = Depends(get_session),
):
    product = Product.model_validate(product_in)
    session.add(product)
    await session.commit()
    await session.refresh(product)
    return product


@router.patch("/{product_id}", response_model=ProductRead)
async def update_product(
    product_id: int,
    updates: ProductUpdate,
    session: AsyncSession = Depends(get_session),
):
    product = await session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    session.add(product)
    await session.commit()
    await session.refresh(product)
    return product


@router.delete("/{product_id}", status_code=204)
async def delete_product(product_id: int, session: AsyncSession = Depends(get_session)):
    product = await session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    await session.delete(product)
    await session.commit()
