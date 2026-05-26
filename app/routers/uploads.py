"""
app/routers/uploads.py — Endpoint para subir imágenes a Azure Blob Storage.
"""
from typing import Literal
from fastapi import APIRouter, UploadFile, File, Query

from app.services.blob_service import upload_image, delete_image, list_images

router = APIRouter()

FolderType = Literal["flash", "tatuajes-hechos", "body-parts"]

@router.get("/")
async def get_files(
    folder: FolderType = Query(default="flash", description="Subcarpeta a consultar")
):
    """
    Retorna la lista de imágenes subidas a la subcarpeta especificada.
    """
    images = await list_images(folder)
    return images

@router.post("/")
async def upload_file(
    file: UploadFile = File(...),
    folder: FolderType = Query(default="flash", description="Subcarpeta destino en Azure Blob Storage"),
):
    """
    Recibe una imagen multipart y la sube a Azure Blob Storage.

    Query params:
      - folder: flash | portfolio | body-parts  (default: flash)

    Retorna la URL pública del blob subido.
    """
    url = await upload_image(file, folder=folder)
    return {"url": url, "folder": folder}


@router.delete("/")
async def delete_file(url: str = Query(..., description="URL pública del blob a eliminar")):
    """
    Elimina un blob dado su URL pública.
    """
    await delete_image(url)
    return {"message": "Imagen eliminada correctamente"}
