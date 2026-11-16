"""Schemas (Pydantic) de las respuestas del analisis acustico (M3)."""

from pydantic import BaseModel, Field


class BandAnalysisResponse(BaseModel):
    """Parametros acusticos ISO 3382 por banda de octava."""

    sample_rate: int = Field(description="Frecuencia de muestreo del archivo en Hz.")
    duration: float = Field(description="Duracion de la RI en segundos.")
    center_frequencies: list[float] = Field(description="Bandas de octava analizadas en Hz.")
    parameters: dict[str, dict[float, float | None]] = Field(
        description=(
            "{parametro: {banda: valor}}. EDT, T10, T20 y T30 en segundos, D50 en % "
            "y C80 en dB. Un tiempo sin rango dinamico suficiente vale null."
        )
    )
