"""
app/routers/ai.py — Endpoints para generación de cotizaciones con IA (Groq).
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
from app.services.ai_service import chat_quotation

router = APIRouter()


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    quiz_style: Optional[str] = None


@router.post("/chat")
async def chat_endpoint(req: ChatRequest):
    """
    Endpoint de chat que procesa el historial y responde con una pregunta o el ticket final.
    """
    try:
        messages_dict = [{"role": msg.role, "content": msg.content} for msg in req.messages]
        response_json = await chat_quotation(
            messages=messages_dict,
            style_hint=req.quiz_style,
        )
        return {"success": True, "data": response_json}
    except Exception as e:
        import traceback
        traceback.print_exc() # Imprime el error completo en los logs de Docker
        raise HTTPException(status_code=503, detail=f"Error en chat IA: {str(e)}")

