"""Rutas para reportes de problemas."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth.dependencies import get_current_admin
from app.models.administrador import Administrador
from app.schemas.reporte import ReporteCreate, ReporteOut
from app.services.reportes import crear_reporte, listar_reportes, resolver_reporte

router = APIRouter(prefix="/reportes", tags=["Reportes"])


@router.post("", response_model=ReporteOut, status_code=status.HTTP_201_CREATED)
def crear(datos: ReporteCreate, db: Session = Depends(get_db)):
    """Cualquier usuario puede reportar un problema (ruta pública)."""
    return crear_reporte(db, datos)


@router.get("", response_model=list[ReporteOut])
def listar(
    resuelto: bool | None = None,
    db: Session = Depends(get_db),
    _: Administrador = Depends(get_current_admin),
):
    return listar_reportes(db, resuelto=resuelto)


@router.patch("/{reporte_id}/resolver", response_model=ReporteOut)
def resolver(
    reporte_id: int,
    db: Session = Depends(get_db),
    _: Administrador = Depends(get_current_admin),
):
    return resolver_reporte(db, reporte_id)
