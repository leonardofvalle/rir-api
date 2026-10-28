"""Schemas (Pydantic) de los endpoints de generacion de senales (M1)."""

from typing import Self

from pydantic import BaseModel, Field, model_validator

from app.settings import settings


class PinkNoiseRequest(BaseModel):
    """Parametros para generar ruido rosa."""

    duration: float = Field(gt=0, le=60, description="Duracion en segundos.")
    sample_rate: int = Field(
        default=settings.fs_default, gt=0, le=192000, description="Frecuencia de muestreo en Hz."
    )


class SineSweepRequest(BaseModel):
    """Parametros para generar un sine sweep logaritmico o su filtro inverso."""

    duration: float = Field(gt=0, le=60, description="Duracion en segundos.")
    start_freq: float = Field(default=20.0, gt=0, description="Frecuencia inicial en Hz.")
    end_freq: float = Field(default=20000.0, gt=0, description="Frecuencia final en Hz.")
    sample_rate: int = Field(
        default=settings.fs_default, gt=0, le=192000, description="Frecuencia de muestreo en Hz."
    )
    inverse: bool = Field(
        default=False, description="Si es True, devuelve el filtro inverso en lugar del sweep."
    )

    @model_validator(mode="after")
    def check_frequencies(self) -> Self:
        """Valida que el rango de frecuencias tenga sentido."""
        if self.start_freq >= self.end_freq:
            raise ValueError("start_freq debe ser menor que end_freq")
        if self.end_freq > self.sample_rate / 2:
            raise ValueError("end_freq no puede superar la frecuencia de Nyquist (sample_rate / 2)")
        return self
