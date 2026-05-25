"""
app/models/product.py — Modelo para productos de la tienda Handpoke.
"""
from sqlmodel import SQLModel, Field
from datetime import datetime, timezone
from typing import Optional


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class ProductBase(SQLModel):
    name: str
    description: str
    price_cop: int                          # Precio en pesos colombianos (sin decimales)
    image_url: str
    stock: int = Field(default=1)
    category: str = Field(default="handpoke")   # handpoke, joyeria, accesorios
    active: bool = Field(default=True)


class Product(ProductBase, table=True):
    __tablename__ = "product"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=utc_now)


class ProductCreate(ProductBase):
    pass


class ProductRead(ProductBase):
    id: int
    created_at: datetime


class ProductUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price_cop: Optional[int] = None
    image_url: Optional[str] = None
    stock: Optional[int] = None
    category: Optional[str] = None
    active: Optional[bool] = None
