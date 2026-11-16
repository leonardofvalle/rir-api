"""Casos de error de los endpoints de M3: siempre 422, nunca 500.

Estos casos se rechazan antes de llamar a los servicios, asi que funcionan
aunque los servicios de M3 todavia no esten implementados.
"""

import io

import numpy as np
import pytest
import soundfile as sf
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

ENDPOINTS_M3 = [
    "/api/v1/acoustics/parameters",
    "/api/v1/utils/schroeder",
    "/api/v1/utils/smoothing",
]


def _wav_corto() -> bytes:
    """WAV valido de 0.1 s a 8 kHz para probar los parametros de formulario."""
    buffer = io.BytesIO()
    sf.write(buffer, np.zeros(800), 8000, format="WAV", subtype="PCM_16")
    return buffer.getvalue()


@pytest.mark.parametrize("endpoint", ENDPOINTS_M3)
def test_archivo_que_no_es_audio_da_422(endpoint):
    """Un archivo de texto con extension .wav no rompe el servidor."""
    archivo = {"file": ("ri.wav", b"esto no es un audio", "audio/wav")}
    response = client.post(endpoint, files=archivo)
    assert response.status_code == 422
    assert "audio" in response.json()["detail"].lower()


@pytest.mark.parametrize("endpoint", ENDPOINTS_M3)
def test_sin_archivo_da_422(endpoint):
    """Si falta el archivo, FastAPI responde 422."""
    assert client.post(endpoint).status_code == 422


@pytest.mark.parametrize(
    "form",
    [
        {"method": "gaussiano"},
        {"window_ms": "0"},
        {"window_ms": "-5"},
        {"window_ms": "500"},
    ],
)
def test_smoothing_parametros_invalidos_dan_422(form):
    """Metodo inexistente o ventana fuera de (0, 100] ms da 422."""
    archivo = {"file": ("ri.wav", _wav_corto(), "audio/wav")}
    response = client.post("/api/v1/utils/smoothing", files=archivo, data=form)
    assert response.status_code == 422
