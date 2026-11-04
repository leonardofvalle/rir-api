"""Endpoints de filtrado por bandas de octava (M2)."""

from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, Response, UploadFile

from app.routers.audio_http import uploaded_file, wav_response
from app.services.filter import filter_single_band
from app.services.signal_utils import load_audio

router = APIRouter()


@router.post("/single-band", response_class=Response)
def single_band(
    file: Annotated[UploadFile, File(description="Archivo de audio (WAV o FLAC).")],
    center_freq: Annotated[float, Form(gt=0, description="Frecuencia central en Hz.")],
    order: Annotated[int, Form(ge=1, le=10, description="Orden del Butterworth.")] = 4,
) -> Response:
    """Filtra un audio subido en una banda de octava y devuelve el resultado como WAV."""
    with uploaded_file(file) as path:
        try:
            signal, fs = load_audio(path)
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e)) from e

    if center_freq * 2**0.5 >= fs / 2:
        raise HTTPException(
            status_code=422,
            detail=f"La banda de {center_freq} Hz supera la frecuencia de Nyquist ({fs / 2} Hz)",
        )

    filtered = filter_single_band(signal, fs, center_freq, order)
    return wav_response(filtered, fs, filename=f"band_{center_freq:g}hz.wav")
