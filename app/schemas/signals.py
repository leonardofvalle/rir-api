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


class SyntheticIRRequest(BaseModel):
    """Parametros para sintetizar una respuesta al impulso con T60 conocidos por banda."""

    duration: float = Field(gt=0, le=30, description="Duracion de la RI en segundos.")
    t60_values: dict[float, float] = Field(
        min_length=1,
        description="T60 en segundos por frecuencia central en Hz, por ejemplo {'1000': 0.8}.",
    )
    sample_rate: int = Field(
        default=settings.fs_default, gt=0, le=192000, description="Frecuencia de muestreo en Hz."
    )

    @model_validator(mode="after")
    def check_t60_values(self) -> Self:
        """Valida que cada banda este por debajo de Nyquist y tenga un T60 positivo."""
        for center_freq, t60 in self.t60_values.items():
            if not 0 < center_freq < self.sample_rate / 2:
                raise ValueError(
                    f"La frecuencia central {center_freq} Hz debe estar entre 0 y "
                    f"Nyquist (sample_rate / 2)"
                )
            if t60 <= 0:
                raise ValueError(f"El T60 de la banda de {center_freq} Hz debe ser mayor a 0")
        return self
