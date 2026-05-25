"""
app/services/calendar_service.py — Integración con Google Calendar API v3.
"""
from typing import List, Dict, Any
# from google.oauth2.credentials import Credentials
# from googleapiclient.discovery import build
from app.config import get_settings

settings = get_settings()

async def get_available_slots(start_date: str, end_date: str) -> List[Dict[str, Any]]:
    """
    Consulta los eventos de la agenda principal de María.
    Retorna los "huecos libres" dentro del horario laboral.
    """
    # TODO: Implementar la llamada real a Google Calendar API
    # 1. Cargar credenciales desde BD o entorno
    # 2. Llamar a calendar.events().list(calendarId='primary', timeMin=start_date, timeMax=end_date)
    # 3. Restar eventos existentes de un horario laboral base (ej: 10:00 a 18:00)
    
    # Datos de prueba (Mock)
    return [
        {"date": "2024-05-01", "slots": ["10:00", "14:00", "16:00"]},
        {"date": "2024-05-02", "slots": ["11:00", "15:00"]},
    ]

async def create_calendar_event(booking_data: Any) -> str:
    """
    Crea un nuevo evento en Google Calendar cuando alguien reserva un tatuaje.
    Retorna el ID del evento de Google.
    """
    # TODO: Implementar creación en GCal
    # event = {
    #   'summary': f'Tatuaje - {booking_data.client_name}',
    #   'description': booking_data.notes,
    #   'start': {'dateTime': booking_data.start_time.isoformat()},
    #   'end': {'dateTime': booking_data.end_time.isoformat()},
    # }
    
    return "mock_gcal_event_id_12345"
