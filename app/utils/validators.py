"""
app/utils/validators.py — Funciones comunes para validaciones.
"""
import re

def validate_phone(phone: str) -> bool:
    """
    Valida un número de teléfono genérico (internacional).
    Debe empezar con + y tener entre 10 y 15 dígitos.
    """
    pattern = re.compile(r"^\+\d{10,15}$")
    return bool(pattern.match(phone))

def format_phone_for_baileys(phone: str) -> str:
    """
    Elimina el '+' y cualquier espacio. Baileys espera algo como '573001234567@s.whatsapp.net'.
    """
    clean_phone = re.sub(r"[^\d]", "", phone)
    return f"{clean_phone}@s.whatsapp.net"
