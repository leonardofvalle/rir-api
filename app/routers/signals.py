"""Endpoints de generacion de senales (M1)."""

from fastapi import APIRouter, Response

from app.routers.audio_http import wav_response
from app.schemas.signals import PinkNoiseRequest, SineSweepRequest, SyntheticIRRequest
from app.services.pink_noise import generate_pink_noise
from app.services.signal_utils import generate_synthetic_ir
from app.services.sine_sweep import generate_sine_sweep_pair

router = APIRouter()


@router.post("/pink-noise", response_class=Response)
def pink_noise(request: PinkNoiseRequest) -> Response:
    """Genera ruido rosa y lo devuelve como archivo WAV."""
    signal = generate_pink_noise(request.duration, request.sample_rate)
    return wav_response(signal, request.sample_rate, filename="pink_noise.wav")


@router.post("/sine-sweep", response_class=Response)
def sine_sweep(request: SineSweepRequest) -> Response:
    """Genera un sine sweep logaritmico (o su filtro inverso) como archivo WAV."""
    sweep, inverse_filter = generate_sine_sweep_pair(
        request.duration, request.start_freq, request.end_freq, request.sample_rate
    )
    if request.inverse:
        return wav_response(inverse_filter, request.sample_rate, filename="inverse_filter.wav")
    return wav_response(sweep, request.sample_rate, filename="sine_sweep.wav")


@router.post("/synthetic-ir", response_class=Response)
def synthetic_ir(request: SyntheticIRRequest) -> Response:
    """Sintetiza una respuesta al impulso con T60 conocidos y la devuelve como WAV."""
    ir = generate_synthetic_ir(request.duration, request.t60_values, request.sample_rate)
    return wav_response(ir, request.sample_rate, filename="synthetic_ir.wav")
