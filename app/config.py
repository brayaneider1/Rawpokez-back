"""
app/config.py — Settings centralizadas usando pydantic-settings.

Estrategia de configuración:
  - LOCAL (APP_ENV=development): Lee variables del archivo .env
  - PRODUCCIÓN (APP_ENV=production): Lee secretos de Azure Key Vault
    usando Managed Identity (sin contraseñas, sin .env en el servidor)

Lección AZ-104 — Managed Identity:
  DefaultAzureCredential prueba credenciales en este orden:
  1. EnvironmentCredential   ← variables de entorno (CI/CD)
  2. ManagedIdentityCredential ← Managed Identity del App Service ✓ (producción)
  3. AzureCliCredential      ← `az login` en tu máquina local (desarrollo)
  Si ninguna funciona, lanza una excepción clara.
"""
import logging
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


def _load_from_keyvault(vault_url: str) -> dict:
    """
    Lee secretos críticos de Azure Key Vault usando Managed Identity.

    Esto funciona en producción (Azure App Service) sin NINGUNA credencial
    en el código. Azure inyecta el token automáticamente al App Service
    gracias a la System-Assigned Managed Identity.

    Lección AZ-104: Los guiones (-) en Key Vault se convierten en guiones
    bajos (_) al leerlos como variables de entorno en Azure App Service.
    """
    try:
        # Estos imports solo se usan en producción para no cargar el SDK en dev
        from azure.keyvault.secrets import SecretClient
        from azure.identity import DefaultAzureCredential

        credential = DefaultAzureCredential()
        client = SecretClient(vault_url=vault_url, credential=credential)

        # Mapeamos: nombre en Key Vault → nombre en Settings
        secret_map = {
            "DATABASE-URL":      "database_url",
            "DATABASE-URL-SYNC": "database_url_sync",
            "TELEGRAM-BOT-TOKEN": "telegram_bot_token",
            "TELEGRAM-CHAT-ID":   "telegram_chat_id",
            "GEMINI-API-KEY":     "gemini_api_key",
            "ADMIN-PASSWORD":     "admin_password",
            "APP-SECRET-KEY":     "app_secret_key",
        }

        secrets = {}
        for kv_name, setting_name in secret_map.items():
            try:
                secret = client.get_secret(kv_name)
                secrets[setting_name] = secret.value
                logger.info(f"✅ Secreto '{kv_name}' cargado desde Key Vault.")
            except Exception as e:
                # Si un secreto no existe en KV, no fallamos toda la app
                logger.warning(f"⚠️  Secreto '{kv_name}' no encontrado en Key Vault: {e}")

        return secrets

    except Exception as e:
        logger.error(f"❌ No se pudo conectar a Key Vault '{vault_url}': {e}")
        return {}


class Settings(BaseSettings):
    # ─── App ──────────────────────────────────────────────────────────────────
    app_env: str = "development"
    app_secret_key: str = "change_me_in_production"
    allowed_origins: str = "http://localhost:3000"
    frontend_url: str = "http://localhost:3000"
    backend_url: str = "http://localhost:8000"

    # ─── Azure Key Vault ──────────────────────────────────────────────────────
    # URL del Key Vault. En producción se configura como App Setting en Azure.
    # Formato: https://<nombre-del-vault>.vault.azure.net/
    # En local se deja vacío y se usa el .env directamente.
    azure_key_vault_url: str = ""

    # ─── Database ─────────────────────────────────────────────────────────────
    database_url: str = ""
    database_url_sync: str = ""

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

    # ─── Gemini AI ────────────────────────────────────────────────────────────
    gemini_api_key: str = ""

    # ─── MercadoPago ──────────────────────────────────────────────────────────
    mp_access_token: str = ""

    # ─── Web Push (VAPID) ─────────────────────────────────────────────────────
    vapid_public_key: str = ""
    vapid_private_key: str = ""
    vapid_claim_email: str = "maria@rawpokez.com"

    # ─── Azure Blob Storage ─────────────────────────────────────────────
    # Reemplaza Cloudinary. Connection String se guarda en Key Vault en prod.
    azure_storage_account_name: str = ""
    azure_storage_connection_string: str = ""
    azure_storage_container: str = "tattoo-assets"

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",")]

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    def load_keyvault_secrets(self) -> None:
        """
        Si estamos en producción y hay una URL de Key Vault configurada,
        sobreescribe los valores de las settings con los secretos del vault.
        Llamar este método DESPUÉS de crear la instancia de Settings.
        """
        if self.is_production and self.azure_key_vault_url:
            logger.info(f"🔐 Cargando secretos desde Azure Key Vault: {self.azure_key_vault_url}")
            secrets = _load_from_keyvault(self.azure_key_vault_url)
            for attr, value in secrets.items():
                if hasattr(self, attr) and value:
                    object.__setattr__(self, attr, value)
        else:
            logger.info("📄 Usando configuración local (.env) — modo desarrollo.")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """
    Singleton de configuración.
    En producción: lee .env básico primero, luego sobreescribe con Key Vault.
    En desarrollo: solo lee el .env local.
    """
    settings = Settings()
    settings.load_keyvault_secrets()
    return settings
