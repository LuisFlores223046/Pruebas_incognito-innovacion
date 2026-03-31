from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, TIMESTAMP, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Reporte(Base):
    __tablename__ = "reportes"
    __table_args__ = (
        CheckConstraint(
            "tipo IN ('cerrado', 'sucio', 'danado', 'lleno', 'otro')",
            name="ck_reporte_tipo",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    espacio_id = Column(Integer, ForeignKey("espacios.id"), nullable=False, index=True)
    tipo = Column(String(20), nullable=False)  # cerrado | sucio | danado | lleno | otro
    descripcion = Column(Text, nullable=True)
    resuelto = Column(Boolean, default=False, nullable=False)
    creado_en = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    resuelto_en = Column(TIMESTAMP(timezone=True), nullable=True)

    espacio = relationship("Espacio", back_populates="reportes")
