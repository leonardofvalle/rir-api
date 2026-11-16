"""Schemas (Pydantic) de los endpoints de utilidades (M3)."""

from enum import StrEnum

from pydantic import BaseModel, Field


class SmoothingMethod(StrEnum):
    """Metodos de suavizado disponibles para obtener la envolvente."""

    HILBERT = "hilbert"
    MOVING_AVERAGE = "moving_average"


class SmoothingResponse(BaseModel):
    """Envolvente de una senal, decimada para el JSON."""

    method: SmoothingMethod
    window_ms: float = Field(description="Ventana de la media movil en ms.")
    sample_rate: int = Field(description="Frecuencia de muestreo del archivo en Hz.")
    time_step: float = Field(description="Segundos entre dos valores de envelope.")
    envelope: list[float] = Field(description="Envolvente en amplitud, decimada.")


class SchroederResponse(BaseModel):
    """Curva de decaimiento de Schroeder en dB, decimada para el JSON."""

    sample_rate: int = Field(description="Frecuencia de muestreo del archivo en Hz.")
    num_samples: int = Field(description="Largo de la RI original en muestras.")
    lundeby_applied: bool = Field(default=False, description="Si se trunco con Lundeby.")
    time_step: float = Field(description="Segundos entre dos valores de edc_db.")
    edc_db: list[float] = Field(description="Curva de Schroeder en dB, decimada y sin -inf.")
