"""
app/models/settings.py — Modelo para configuración dinámica del sitio (CMS).
"""
from sqlmodel import SQLModel, Field
from datetime import datetime, timezone
from typing import Optional

def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)

class SiteSettingsBase(SQLModel):
    # Identidad de Marca
    studio_name: str = Field(default="RAWPOKEZ")
    logo_url: Optional[str] = None
    contact_whatsapp: str = Field(default="+573175607784")
    contact_email: Optional[str] = None
    instagram_url: Optional[str] = None
    
    # Textos Principales
    hero_title: str = Field(default="RAWPOKEZ")
    hero_subtitle: str = Field(default="Handpoke Tattoo Studio")
    about_text: Optional[str] = None

class SiteSettings(SiteSettingsBase, table=True):
    __tablename__ = "site_settings"
    id: Optional[int] = Field(default=None, primary_key=True)
    updated_at: datetime = Field(default_factory=utc_now)

class SiteSettingsUpdate(SQLModel):
    studio_name: Optional[str] = None
    logo_url: Optional[str] = None
    contact_whatsapp: Optional[str] = None
    contact_email: Optional[str] = None
    instagram_url: Optional[str] = None
    hero_title: Optional[str] = None
    hero_subtitle: Optional[str] = None
    about_text: Optional[str] = None

class SiteSettingsRead(SiteSettingsBase):
    id: int
    updated_at: datetime
