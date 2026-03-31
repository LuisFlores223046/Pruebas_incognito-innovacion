from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict


TipoReporte = Literal["cerrado", "sucio", "danado", "lleno", "otro"]


class ReporteCreate(BaseModel):
    espacio_id: int
    tipo: TipoReporte
    descripcion: str | None = None


class ReporteOut(ReporteCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    resuelto: bool
    creado_en: datetime
    resuelto_en: datetime | None = None
