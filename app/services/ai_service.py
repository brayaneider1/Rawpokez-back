"""
app/services/ai_service.py — Servicio de IA para cotizaciones usando Google Gemini API.

Modelo: gemini-1.5-flash (gratis en Google AI Studio, rápido y accesible en Colombia)
Dependencia: httpx (ya instalado) — sin SDK extra necesario.
"""
import json
import httpx
from typing import Optional
from app.config import get_settings

settings = get_settings()

# La URL requiere la API key en el querystring
GEMINI_MODEL = "gemini-1.5-flash"

# ─── System prompt de Agente Conversacional ────────────────────────────────────
QUOTE_SYSTEM_PROMPT = """Eres María, la asistente experta de RAWPOKEZ Tattoo Studio.
Tu objetivo es asesorar al cliente y generar una cotización técnica basada en su idea de tatuaje Handpoke.

REGLAS DE ORO:
1. Si falta información, pregunta con brevedad y estilo.
2. Si tienes suficiente información, genera una cotización técnica.
3. SI EL USUARIO PIDE CORRECCIONES (ej: cambiar tamaño, zona o estilo), RE-CALCULA los precios y emite un NUEVO ticket actualizado de inmediato.

PRECIOS DE REFERENCIA (COP):
- XS (1-3cm): $80k - $120k
- S (3-6cm): $120k - $180k
- M (6-10cm): $200k - $350k
- L (10-20cm): $350k - $600k
- XL (+20cm): $600k+

RESPONDE SIEMPRE EN FORMATO JSON:
{
  "type": "chat" | "ticket",
  "message": "Respuesta textual para el chat",
  "quote": {
    "precio_min": number,
    "precio_max": number,
    "tiempo_sesion": "X horas",
    "sesiones": number,
    "zona_mapeada": "antebrazo" | "brazo" | "pierna" | "espalda" | "pecho" | "costillas" | "cuello" | "mano" | "tobillo",
    "descripcion": "Breve resumen técnico",
    "recomendacion": "Consejo experto"
  }
}
"""


async def chat_quotation(messages: list[dict], style_hint: Optional[str] = None) -> dict:
    """
    Toma un historial de mensajes y genera una respuesta de chat o el ticket final.
    """
    
    # Construir el array 'contents' para Gemini
    gemini_contents = []
    
    if style_hint:
        gemini_contents.append({
            "role": "user", 
            "parts": [{"text": f"[CONTEXTO OCULTO: El usuario seleccionó este estilo o diseño base: {style_hint}. Úsalo para la cotización final.]"}]
        })
        
    # Estructura ultra-compatible: Metemos el system prompt como el primer mensaje del "user"
    # para evitar errores de versión v1/v1beta con el campo system_instruction
    contents = [
        {
            "role": "user",
            "parts": [{"text": f"INSTRUCCIÓN DEL SISTEMA:\n{QUOTE_SYSTEM_PROMPT}\n\nENTENDIDO. Ahora responderé a la siguiente conversación siguiendo estrictamente el formato JSON solicitado."}]
        },
        {
            "role": "model",
            "parts": [{"text": "Entendido. Estoy listo para procesar la cotización en formato JSON."}]
        }
    ]
    
    for msg in messages:
        role = "model" if msg["role"] == "assistant" else "user"
        contents.append({
            "role": role,
            "parts": [{"text": msg["content"]}]
        })

    payload = {
        "contents": contents,
        "generationConfig": {
            "temperature": 0.7,
        }
    }

    # Usamos el modelo que ya te estaba funcionando y que aparece en tu consola: Gemini 3.1 Flash Lite
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite:generateContent?key={settings.gemini_api_key}"

    async with httpx.AsyncClient(timeout=20.0) as client:
        try:
            print(f"DEBUG IA: Intentando con Gemini 3.1 Flash Lite...")
            response = await client.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            content_text = result["candidates"][0]["content"]["parts"][0]["text"]
            
            # Limpiar posibles bloques de código markdown si la IA los pone
            if "```json" in content_text:
                content_text = content_text.split("```json")[1].split("```")[0].strip()
            elif "```" in content_text:
                content_text = content_text.split("```")[1].split("```")[0].strip()
                
            return json.loads(content_text)
        except Exception as e:
            print(f"DEBUG IA ERROR: {str(e)}")
            if 'response' in locals(): print(f"DETALLE: {response.text}")
            raise e
