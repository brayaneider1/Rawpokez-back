"""
app/config.py — Settings centralizadas usando pydantic-settings.
Todas las variables se leen del .env automáticamente.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    # ─── App ──────────────────────────────────────────────────────────────────
    app_env: str = "development"
    app_secret_key: str = "change_me_in_production"
    allowed_origins: str = "http://localhost:3000"
    frontend_url: str = "http://localhost:3000"
    backend_url: str = "http://localhost:8000"

    # ─── Database ─────────────────────────────────────────────────────────────
    database_url: str
    database_url_sync: str

    # ─── Cloudinary ───────────────────────────────────────────────────────────
    cloudinary_cloud_name: str = ""
    cloudinary_api_key: str = ""
    cloudinary_api_secret: str = ""

    # ─── Google (Calendar + OAuth) ────────────────────────────────────────────
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/auth/google/callback"
    google_calendar_id: str = "primary"

    # ─── Telegram Bot ─────────────────────────────────────────────────────────
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

    # ─── Admin ────────────────────────────────────────────────────────────────
    admin_username: str = "maria"
    admin_password: str = "change_me"

    # ─── Groq AI (gratis) ─────────────────────────────────────────────────────
    gemini_api_key: str = ""

    # ─── MercadoPago ──────────────────────────────────────────────────────────
    mp_access_token: str = ""          # TEST-... en sandbox, APP_USR-... en producción

    # ─── Web Push (VAPID) ─────────────────────────────────────────────────────
    vapid_public_key: str = ""
    vapid_private_key: str = ""
    vapid_claim_email: str = "maria@rawpokez.com"

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",")]

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Singleton — llama get_settings() en cualquier parte del proyecto."""
    return Settings()
