"""Lógica de subida / eliminación de fotos en Cloudinary."""
import re
import cloudinary
import cloudinary.uploader
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from app.config import settings
from app.models.espacio import Espacio
from app.models.foto_espacio import FotoEspacio
from app.schemas.foto_espacio import FotoCreate, FotoUpdate

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True,
)


def _public_id(espacio_codigo: str, orden: int) -> str:
    """Genera un public_id legible: mapacu/espacios/A-106_foto_1"""
    slug = re.sub(r"[^A-Za-z0-9\-]", "_", espacio_codigo)
    return f"mapacu/espacios/{slug}_foto_{orden}"


def subir_foto(db: Session, file: UploadFile, datos: FotoCreate) -> FotoEspacio:
    espacio = db.query(Espacio).filter(Espacio.id == datos.espacio_id).first()
    if not espacio:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Espacio no encontrado")

    public_id = _public_id(espacio.codigo, datos.orden)

    try:
        resultado = cloudinary.uploader.upload(
            file.file,
            public_id=public_id,
            folder=None,
            resource_type="image",
            overwrite=True,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error al subir imagen a Cloudinary: {exc}",
        )

    foto = FotoEspacio(
        espacio_id=datos.espacio_id,
        url=resultado["secure_url"],
        descripcion=datos.descripcion,
        es_principal=datos.es_principal,
        orden=datos.orden,
    )
    db.add(foto)
    db.commit()
    db.refresh(foto)
    return foto


def actualizar_foto(db: Session, foto_id: int, datos: FotoUpdate) -> FotoEspacio:
    foto = db.query(FotoEspacio).filter(FotoEspacio.id == foto_id).first()
    if not foto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Foto no encontrada")
    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(foto, campo, valor)
    db.commit()
    db.refresh(foto)
    return foto


def eliminar_foto(db: Session, foto_id: int) -> None:
    foto = db.query(FotoEspacio).filter(FotoEspacio.id == foto_id).first()
    if not foto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Foto no encontrada")

    # Extraer el public_id de la URL de Cloudinary
    try:
        partes = foto.url.split("/")
        # El public_id incluye la carpeta: mapacu/espacios/<nombre>
        nombre_archivo = partes[-1].split(".")[0]
        carpeta = "/".join(partes[-3:-1])
        public_id = f"{carpeta}/{nombre_archivo}"
        cloudinary.uploader.destroy(public_id)
    except Exception:
        pass  # Si falla la eliminación en Cloudinary, seguimos borrando de BD

    db.delete(foto)
    db.commit()
