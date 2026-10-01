"""Contratos Pydantic de argumentos de herramientas."""
from __future__ import annotations

from pydantic import BaseModel, Field, model_validator


class ListarActividadesArgs(BaseModel):
    desde: str | None = None
    hasta: str | None = None


class BuscarAsociadosArgs(BaseModel):
    query: str | None = None
    ciudad: str | None = None


class ConsultarDisponibilidadArgs(BaseModel):
    asociado_email: str | None = None
    ciudad: str | None = None
    fecha: str | None = None
    ventana: str | None = None

    @model_validator(mode="after")
    def validate_target(self):
        if not self.asociado_email and not self.ciudad:
            raise ValueError("Se requiere asociado_email o ciudad.")
        return self


class CrearActividadArgs(BaseModel):
    titulo: str
    descripcion: str = ""
    fecha: str
    duracion_minutos: int = Field(gt=0)
    asociado_email: str


class ActualizarActividadArgs(BaseModel):
    id: int
    descripcion: str | None = None
    fecha: str | None = None
    duracion_minutos: int | None = Field(default=None, gt=0)


class EliminarActividadArgs(BaseModel):
    id: int
