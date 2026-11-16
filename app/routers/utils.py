"""Endpoints de utilidades: envolvente y curva de Schroeder (M3)."""

from typing import Annotated

import numpy as np
from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.routers.audio_http import uploaded_file
from app.schemas.utils import SchroederResponse, SmoothingMethod, SmoothingResponse
from app.services.acoustic_parameters import apply_schroeder_integral, apply_smoothing
from app.services.signal_utils import load_audio

router = APIRouter()

PISO_DB = -150.0  # JSON no admite -inf: la curva se recorta en este nivel


def _leer_audio(file: UploadFile) -> tuple[np.ndarray, int]:
    """Lee el archivo subido; si no es un audio valido responde 422."""
    with uploaded_file(file) as path:
        try:
            return load_audio(path)
        except ValueError as e:
            raise HTTPException(status_code=422, detail=f"No es un audio valido: {e}") from e


def _paso_decimacion(fs: int) -> int:
    """Cantidad de muestras entre dos valores del JSON (cerca de uno por ms)."""
    return max(1, round(fs / 1000))


@router.post("/smoothing", response_model=SmoothingResponse)
def smoothing(
    file: Annotated[UploadFile, File(description="Respuesta al impulso (WAV o FLAC).")],
    method: Annotated[SmoothingMethod, Form(description="Metodo de suavizado.")] = (
        SmoothingMethod.HILBERT
    ),
    window_ms: Annotated[float, Form(gt=0, le=100, description="Ventana en ms.")] = 10,
) -> SmoothingResponse:
    """Devuelve la envolvente (en amplitud) de la senal subida."""
    signal, fs = _leer_audio(file)
    envelope = apply_smoothing(signal, fs, method=method.value, window_ms=window_ms)
    paso = _paso_decimacion(fs)
    return SmoothingResponse(
        method=method,
        window_ms=window_ms,
        sample_rate=fs,
        time_step=paso / fs,
        envelope=envelope[::paso].tolist(),
    )


@router.post("/schroeder", response_model=SchroederResponse)
def schroeder(
    file: Annotated[UploadFile, File(description="Respuesta al impulso (WAV o FLAC).")],
) -> SchroederResponse:
    """Devuelve la curva de decaimiento de Schroeder (en dB) de la RI subida."""
    ir, fs = _leer_audio(file)
    edc = apply_schroeder_integral(ir)
    edc = np.nan_to_num(edc, nan=PISO_DB, neginf=PISO_DB)
    edc = np.maximum(edc, PISO_DB)
    paso = _paso_decimacion(fs)
    return SchroederResponse(
        sample_rate=fs,
        num_samples=len(ir),
        time_step=paso / fs,
        edc_db=edc[::paso].tolist(),
    )
