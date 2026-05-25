"""
app/models/quotation.py — Modelo SQLModel para las solicitudes de cotización.
Extendido con campos para email, descripción libre y cotización generada por IA.
"""
from sqlmodel import SQLModel, Field
from datetime import datetime, timezone
from typing import Optional


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class QuotationBase(SQLModel):
    # Datos del cliente
    client_name: str
    client_phone: str
    client_email: Optional[str] = None
    # Datos del tatuaje
    body_zone: str
    body_zone_svg_id: Optional[str] = None     # ID del área tocada en el SVG de silueta
    size_cm: float
    notes: Optional[str] = None
    idea_description: Optional[str] = None     # Descripción libre de la idea (500 chars)
    colors: Optional[str] = None               # Preferencia de color (negro, color, etc)
    additional_details: Optional[str] = None    # Detalles extra (significado, etc)
    # Referencias
    design_id: Optional[int] = Field(default=None, foreign_key="design.id")
    custom_image_url: Optional[str] = None
    # Cotización generada por IA
    ai_quote_min: Optional[int] = None         # Precio mínimo COP
    ai_quote_max: Optional[int] = None         # Precio máximo COP
    ai_session_time: Optional[str] = None      # Ej: "2 horas"
    ai_sessions_count: Optional[int] = None    # Número de sesiones recomendadas
    ai_description: Optional[str] = None       # Descripción técnica IA
    ai_recommendation: Optional[str] = None    # Recomendación personalizada IA
    ai_preview_image_url: Optional[str] = None # URL imagen generada por Hugging Face
    # Estilo detectado por quiz
    quiz_style: Optional[str] = None           # naturaleza, misterio, minimalismo, tribu
    
    # Fotomontaje interactivo (Posicionamiento en canvas)
    mockup_x: Optional[float] = None
    mockup_y: Optional[float] = None
    mockup_scale: Optional[float] = None
    mockup_rotation: Optional[float] = None

    # Nuevos campos solicitados por María
    size_category: Optional[str] = None        # Pequeño, Mediano, Grande
    allergies: Optional[str] = None            # Condiciones de piel o alergias
    discount_code: Optional[str] = None        # Código o bono
    discount_evidence_url: Optional[str] = None # URL de la imagen del bono
    appointment_date: Optional[datetime] = None # Fecha y hora exacta elegida
    appointment_status: str = Field(default="pending") # pending, confirmed, cancelled


class Quotation(QuotationBase, table=True):
    """Modelo real en la BD"""
    __tablename__ = "quotation"

    id: Optional[int] = Field(default=None, primary_key=True)
    status: str = Field(default="pending")  # pending, quoted, accepted, rejected
    wa_sent: bool = Field(default=False)    # True si ya se envió a WhatsApp de María
    created_at: datetime = Field(default_factory=utc_now)


class QuotationCreate(QuotationBase):
    """Payload de creación (POST)"""
    pass


class QuotationRead(QuotationBase):
    """Payload de respuesta (GET)"""
    id: int
    status: str
    wa_sent: bool
    created_at: datetime
