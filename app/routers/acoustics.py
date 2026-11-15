"""Endpoint principal: parametros acusticos ISO 3382 por banda (M3)."""

from typing import Annotated

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.routers.audio_http import uploaded_file
from app.schemas.responses import BandAnalysisResponse
from app.services.acoustic_parameters import calculate_parameters_from_ir
from app.services.signal_utils import load_audio

router = APIRouter()


@router.post("/parameters", response_model=BandAnalysisResponse)
def parameters(
    file: Annotated[UploadFile, File(description="Respuesta al impulso (WAV o FLAC).")],
) -> BandAnalysisResponse:
    """Calcula EDT, T10, T20, T30, D50 y C80 por banda de octava de la RI subida."""
    with uploaded_file(file) as path:
        try:
            ir, fs = load_audio(path)
        except ValueError as e:
            raise HTTPException(status_code=422, detail=f"No es un audio valido: {e}") from e

    try:
        params = calculate_parameters_from_ir(ir, fs)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e

    return BandAnalysisResponse(
        sample_rate=fs,
        duration=len(ir) / fs,
        center_frequencies=sorted(params["T30"]),
        parameters=params,
    )
