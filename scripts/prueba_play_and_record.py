"""Prueba real de play_and_record con placa de audio y microfono (issue #3).

Reproduce un sine sweep, graba con el microfono, obtiene la respuesta al impulso
con get_impulse_response y guarda en ``docs/m1/``:

- ``prueba_<nombre>_grabacion.wav``: la grabacion (mono, 48 kHz).
- ``prueba_<nombre>_ri.wav``: los primeros 2 s de la RI.

``<nombre>`` identifica la fuente: ``auricular`` o ``parlante``.

Uso (desde la raiz del repositorio)::

    uv run python -m scripts.prueba_play_and_record parlante

Despues, el grafico: ``uv run python -m scripts.graficar_prueba_real parlante``.
"""

import sys
from pathlib import Path

import numpy as np
import soundfile as sf

from app.services.audio_io import play_and_record
from app.services.signal_utils import get_impulse_response
from app.services.sine_sweep import generate_sine_sweep_pair

# Configuracion: numeros de `uv run python -m sounddevice` (misma API de Windows en ambos)
DISPOSITIVO_ENTRADA = 1  # Microfono (USB Audio CODEC), MME
DISPOSITIVO_SALIDA = 13  # Parlantes del monitor ASUS VG249QL3A (NVIDIA HDMI), MME
FS = 48000
DURACION_SWEEP = 5.0  # segundos
DURACION_GRABACION = 7.0  # sweep + 2 s de cola de reverberacion
NIVEL_SWEEP = 0.5  # -6 dBFS, para no saturar
F_INICIAL, F_FINAL = 20.0, 20000.0
CARPETA = Path("docs/m1")


def main() -> None:
    import sounddevice as sd  # solo aca: el grafico importa esta config sin placa de audio

    nombre = sys.argv[1] if len(sys.argv) > 1 else "parlante"

    sd.default.device = (DISPOSITIVO_ENTRADA, DISPOSITIVO_SALIDA)
    entrada = sd.query_devices(DISPOSITIVO_ENTRADA)
    salida = sd.query_devices(DISPOSITIVO_SALIDA)
    api = sd.query_hostapis(entrada["hostapi"])["name"]

    print(f"=== Prueba: {nombre} ===")
    print(f"Entrada: [{DISPOSITIVO_ENTRADA}] {entrada['name']}")
    print(f"Salida:  [{DISPOSITIVO_SALIDA}] {salida['name']}")
    print(f"API de audio: {api}")
    print(f"fs: {FS} Hz | canales grabados: 1")
    print(f"Latencia de entrada: {entrada['default_high_input_latency'] * 1000:.1f} ms")
    print(f"Latencia de salida:  {salida['default_high_output_latency'] * 1000:.1f} ms")

    sweep, inverse_filter = generate_sine_sweep_pair(DURACION_SWEEP, F_INICIAL, F_FINAL, FS)
    print(f"\nReproduciendo sweep de {DURACION_SWEEP} s y grabando {DURACION_GRABACION} s...")
    recording = play_and_record(sweep * NIVEL_SWEEP, FS, DURACION_GRABACION)
    recording = np.asarray(recording).reshape(len(recording), -1)[:, 0]

    pico = np.max(np.abs(recording))
    print(f"Muestras grabadas: {len(recording)} (esperadas {int(DURACION_GRABACION * FS)})")
    print(f"Pico de la grabacion: {20 * np.log10(pico + 1e-12):.1f} dBFS")
    if pico >= 0.99:
        print("ATENCION: la grabacion satura. Baja la ganancia del microfono y repeti.")
    elif pico < 0.01:
        print("ATENCION: la grabacion es casi silencio. Revisa conexiones, phantom y ganancia.")

    ir = get_impulse_response(recording, inverse_filter)

    CARPETA.mkdir(parents=True, exist_ok=True)
    sf.write(CARPETA / f"prueba_{nombre}_grabacion.wav", recording, FS, subtype="PCM_16")
    sf.write(CARPETA / f"prueba_{nombre}_ri.wav", ir[: int(2 * FS)], FS, subtype="PCM_24")
    print(f"\nGuardado: {CARPETA}/prueba_{nombre}_grabacion.wav y prueba_{nombre}_ri.wav")


if __name__ == "__main__":
    main()
