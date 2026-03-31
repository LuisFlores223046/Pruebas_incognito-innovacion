"""Lógica de negocio para reportes."""
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.reporte import Reporte
from app.schemas.reporte import ReporteCreate


def crear_reporte(db: Session, datos: ReporteCreate) -> Reporte:
    reporte = Reporte(**datos.model_dump())
    db.add(reporte)
    db.commit()
    db.refresh(reporte)
    return reporte


def listar_reportes(
    db: Session,
    resuelto: bool | None = None,
    espacio_id: int | None = None,
) -> list[Reporte]:
    q = db.query(Reporte)
    if resuelto is not None:
        q = q.filter(Reporte.resuelto == resuelto)
    if espacio_id is not None:
        q = q.filter(Reporte.espacio_id == espacio_id)
    return q.order_by(Reporte.creado_en.desc()).all()


def resolver_reporte(db: Session, reporte_id: int) -> Reporte:
    reporte = db.query(Reporte).filter(Reporte.id == reporte_id).first()
    if not reporte:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reporte no encontrado")
    reporte.resuelto = True
    reporte.resuelto_en = datetime.now(timezone.utc)
    db.commit()
    db.refresh(reporte)
    return reporte
