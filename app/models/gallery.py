"""
app/models/gallery.py — Modelo para las imágenes del portafolio (Galería).
"""
from sqlmodel import SQLModel, Field
from datetime import datetime, timezone
from typing import Optional

def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)

class GalleryImageBase(SQLModel):
    title: str
    image_url: str
    category: Optional[str] = Field(default="general")
    is_visible: bool = Field(default=True)
    display_order: int = Field(default=0)

class GalleryImage(GalleryImageBase, table=True):
    __tablename__ = "gallery_image"
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=utc_now)

class GalleryImageCreate(GalleryImageBase):
    pass

class GalleryImageUpdate(SQLModel):
    title: Optional[str] = None
    image_url: Optional[str] = None
    category: Optional[str] = None
    is_visible: Optional[bool] = None
    display_order: Optional[int] = None

class GalleryImageRead(GalleryImageBase):
    id: int
    created_at: datetime
