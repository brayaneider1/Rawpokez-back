"""
app/services/cloudinary_service.py — Integración con Cloudinary.
"""
from fastapi import UploadFile
import cloudinary # type: ignore
import cloudinary.uploader # type: ignore
from app.config import get_settings

settings = get_settings()

# Configuración lazy-loaded (se ejecuta solo si hay keys, para evitar crashes en dev)
if settings.cloudinary_api_key:
    cloudinary.config(
        cloud_name=settings.cloudinary_cloud_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )

async def upload_image(file: UploadFile) -> str:
    """
    Sube un archivo a Cloudinary asíncronamente y retorna la URL pública (Secure URL).
    """
    if not settings.cloudinary_api_key:
        print("WARNING: Cloudinary no configurado. Usando imagen de prueba.")
        return "https://res.cloudinary.com/demo/image/upload/sample.jpg"

    try:
        # FastAPI UploadFile usa SpooledTemporaryFile, hay que leer los bytes
        contents = await file.read()
        
        # Cloudinary uploader bloquea el thread, en un entorno hiper-optimizado 
        # usaríamos asyncio.to_thread, pero para este caso está bien así.
        result = cloudinary.uploader.upload(
            contents,
            folder="rawpokez_designs",
            # Auto format y auto quality (optimización SEO nativa)
            format="webp",
            transformation=[
                {"quality": "auto", "fetch_format": "auto"}
            ]
        )
        return result.get("secure_url")
    except Exception as e:
        print(f"Error subiendo imagen a Cloudinary: {e}")
        raise
