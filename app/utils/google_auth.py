"""
app/utils/google_auth.py — Helpers para la autenticación OAuth con Google.
"""
# from google_auth_oauthlib.flow import Flow
from app.config import get_settings

settings = get_settings()

SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_auth_url() -> str:
    """Genera la URL para que María inicie sesión y dé permisos al calendario."""
    # flow = Flow.from_client_secrets_file(
    #     'client_secret.json',
    #     scopes=SCOPES,
    #     redirect_uri=settings.google_redirect_uri
    # )
    # auth_url, _ = flow.authorization_url(prompt='consent')
    # return auth_url
    return "https://accounts.google.com/o/oauth2/auth?..."

def process_callback(code: str) -> dict:
    """Intercambia el código por tokens y los guarda."""
    # flow.fetch_token(code=code)
    # credentials = flow.credentials
    # return {"token": credentials.token, "refresh_token": credentials.refresh_token}
    return {"status": "success"}
