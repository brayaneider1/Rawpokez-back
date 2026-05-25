"""
app/models/design.py — Modelo SQLModel para los diseños del portafolio.
"""
from sqlmodel import SQLModel, Field
from datetime import datetime, timezone
from typing import Optional

# Evita el problema del timezone ingenuo:
def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)

class DesignBase(SQLModel):
    title: str
    style: str  # e.g., "hand-poke", "fine-line", "custom"
    image_url: str
    price: Optional[float] = None
    available: bool = True
    expires_at: Optional[datetime] = None   # Flash de la semana — None = sin expiración
    is_flash: bool = Field(default=False)   # True = aparece en la sección Flash Week

class Design(DesignBase, table=True):
    """Modelo real en la base de datos (Tabla)"""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=utc_now)

class DesignCreate(DesignBase):
    """Payload para crear un nuevo diseño (POST)"""
    pass

class DesignRead(DesignBase):
    """Payload de respuesta al consultar un diseño (GET)"""
    id: int
    created_at: datetime

class DesignUpdate(SQLModel):
    """Payload para actualizar un diseño (PATCH)"""
    title: Optional[str] = None
    style: Optional[str] = None
    image_url: Optional[str] = None
    price: Optional[float] = None
    available: Optional[bool] = None
