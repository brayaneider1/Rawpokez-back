"""
app/models/lead.py — Modelo CRM para pipeline de seguimiento de clientes.
"""
from sqlmodel import SQLModel, Field
from datetime import datetime, timezone
from typing import Optional


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


# Etapas del pipeline
PIPELINE_STAGES = ["received", "quoted", "confirmed", "done", "followup"]
LEAD_SOURCES = ["quotation_form", "waitlist", "store_purchase", "manual"]


class LeadBase(SQLModel):
    source: str = Field(default="quotation_form")   # LEAD_SOURCES
    client_name: str
    client_phone: str
    client_email: Optional[str] = None
    pipeline_stage: str = Field(default="received") # PIPELINE_STAGES
    notes: Optional[str] = None
    ref_id: Optional[int] = None                    # ID de quotation/order relacionado
    ai_quote_snapshot: Optional[str] = None         # JSON de la cotización IA generada


class Lead(LeadBase, table=True):
    __tablename__ = "lead"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class LeadCreate(LeadBase):
    pass


class LeadRead(LeadBase):
    id: int
    created_at: datetime
    updated_at: datetime


class LeadUpdateStage(SQLModel):
    pipeline_stage: str


class LeadUpdateNotes(SQLModel):
    notes: str
