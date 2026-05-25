"""
app/routers/uploads.py — Endpoint para subir imágenes a Cloudinary (Diseños personalizados).
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
# from app.services.cloudinary_service import upload_image

router = APIRouter()

@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    """
    Recibe un multipart/form-data con la imagen.
    Sube a Cloudinary y retorna la URL pública.
    """
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # url = await upload_image(file)
    # return {"url": url}
    return {"message": "Not implemented yet", "url": "https://fake-cloudinary.com/img.png"}
