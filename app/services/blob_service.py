"""
app/services/blob_service.py

Servicio de subida de imágenes a Azure Blob Storage.

ARQUITECTURA AZ-104:
────────────────────────────────────────────────────────────────────
Contenedor: tattoo-assets (acceso público Blob)
  └── flash/       → Diseños flash PNG subidos por el admin
  └── portfolio/   → Fotos del portafolio de María
  └── body-parts/  → Imágenes de referencia del cuerpo humano

El montaje de cotizaciones NO sube imágenes — solo guarda coordenadas
en la BD y el navegador renderiza el efecto con CSS transforms.

SEGURIDAD:
  - Local:       Usa AZURE_STORAGE_CONNECTION_STRING del .env
  - Producción:  La Connection String se guarda en Azure Key Vault.
                 El App Service la lee via Managed Identity.
────────────────────────────────────────────────────────────────────
"""

import uuid
import mimetypes
from typing import Literal

from fastapi import UploadFile, HTTPException
from azure.storage.blob import BlobServiceClient, ContentSettings
from azure.core.exceptions import AzureError

from app.config import get_settings

settings = get_settings()

# Prefijos de carpeta dentro del contenedor
FolderType = Literal["flash", "tatuajes-hechos", "body-parts"]

ALLOWED_CONTENT_TYPES = {
    "image/png",
    "image/jpeg",
    "image/jpg",
    "image/webp",
    "image/gif",
}


def _get_client() -> BlobServiceClient:
    """Retorna el cliente de Azure Blob Storage usando la connection string."""
    conn_str = getattr(settings, "azure_storage_connection_string", None)
    if not conn_str:
        raise HTTPException(
            status_code=503,
            detail="Azure Storage no configurado. Agrega AZURE_STORAGE_CONNECTION_STRING al entorno.",
        )
    return BlobServiceClient.from_connection_string(conn_str)


async def upload_image(
    file: UploadFile,
    folder: FolderType = "flash",
) -> str:
    """
    Sube un archivo de imagen a Azure Blob Storage.

    Args:
        file:   Archivo recibido desde el formulario multipart.
        folder: Subcarpeta virtual dentro del contenedor (flash | portfolio | body-parts).

    Returns:
        URL pública del blob subido.

    Raises:
        HTTPException 400: Si el archivo no es una imagen válida.
        HTTPException 503: Si Azure Storage no está configurado.
        HTTPException 502: Si falla la conexión con Azure.
    """
    # Validar tipo de archivo
    content_type = file.content_type or ""
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de archivo no permitido: {content_type}. Solo se aceptan imágenes PNG, JPEG, WebP o GIF.",
        )

    # Obtener extensión del archivo
    ext = mimetypes.guess_extension(content_type) or ".png"
    if ext == ".jpe":
        ext = ".jpg"  # Normalizar extensión de JPEG

    # Nombre único para el blob: folder/uuid.ext
    blob_name = f"{folder}/{uuid.uuid4().hex}{ext}"

    container_name = getattr(settings, "azure_storage_container", "tattoo-assets")

    try:
        client = _get_client()
        container_client = client.get_container_client(container_name)
        blob_client = container_client.get_blob_client(blob_name)

        # Leer contenido del archivo
        content = await file.read()

        # Subir con el Content-Type correcto para que el navegador lo renderice bien
        blob_client.upload_blob(
            content,
            overwrite=True,
            content_settings=ContentSettings(content_type=content_type),
        )

        # Construir URL pública
        account_name = getattr(settings, "azure_storage_account_name", "")
        url = f"https://{account_name}.blob.core.windows.net/{container_name}/{blob_name}"
        return url

    except AzureError as e:
        raise HTTPException(
            status_code=502,
            detail=f"Error al conectar con Azure Storage: {str(e)}",
        )


async def delete_image(blob_url: str) -> None:
    """
    Elimina un blob dado su URL pública.

    Args:
        blob_url: URL completa del blob a eliminar.
    """
    container_name = getattr(settings, "azure_storage_container", "tattoo-assets")
    try:
        # Extraer el nombre del blob desde la URL
        # URL format: https://{account}.blob.core.windows.net/{container}/{blob_name}
        parts = blob_url.split(f"{container_name}/")
        if len(parts) < 2:
            return  # URL inválida, ignorar silenciosamente

        blob_name = parts[-1]
        client = _get_client()
        blob_client = client.get_blob_client(container=container_name, blob=blob_name)
        blob_client.delete_blob()

    except AzureError:
        pass  # Si falla el borrado, no es crítico

async def list_images(folder: FolderType) -> list[dict]:
    """
    Lista todos los blobs dentro de una subcarpeta virtual.
    
    Args:
        folder: Subcarpeta a listar (flash | tatuajes-hechos | body-parts)
        
    Returns:
        Lista de diccionarios con 'url' y 'name'.
    """
    container_name = getattr(settings, "azure_storage_container", "tattoo-assets")
    account_name = getattr(settings, "azure_storage_account_name", "")
    base_url = f"https://{account_name}.blob.core.windows.net/{container_name}/"
    
    try:
        client = _get_client()
        container_client = client.get_container_client(container_name)
        
        # List blobs with the specified prefix (folder/)
        blob_list = container_client.list_blobs(name_starts_with=f"{folder}/")
        
        images = []
        for blob in blob_list:
            images.append({
                "url": f"{base_url}{blob.name}",
                "name": blob.name.split('/')[-1]
            })
            
        return images
    except AzureError as e:
        print(f"Error listando blobs: {e}")
        return []
