"""Prueba real de play_and_record con placa de audio, parlante y microfono (issue #3).

Reproduce un sine sweep, graba la respuesta de la sala, obtiene la respuesta al
impulso con get_impulse_response y guarda los resultados en data/ (ignorada por git).

Uso: uv run python prueba_play_and_record.py
"""

from pathlib import Path

import numpy as np
import sounddevice as sd
import soundfile as sf

from app.services.audio_io import play_and_record
from app.services.signal_utils import get_impulse_response
from app.services.sine_sweep import generate_sine_sweep_pair

# Configuracion: numeros de `uv run python -m sounddevice` (misma API de Windows en ambos)
DISPOSITIVO_ENTRADA = 1  # Microfono (USB Audio CODEC), MME
DISPOSITIVO_SALIDA = 13  # Altavoces (USB Audio CODEC), MME
FS = 48000
DURACION_SWEEP = 5.0  # segundos
DURACION_GRABACION = 7.0  # sweep + 2 s de cola de reverberacion
NIVEL_SWEEP = 0.5  # -6 dBFS, para no saturar

sd.default.device = (DISPOSITIVO_ENTRADA, DISPOSITIVO_SALIDA)
entrada = sd.query_devices(DISPOSITIVO_ENTRADA)
salida = sd.query_devices(DISPOSITIVO_SALIDA)
api = sd.query_hostapis(entrada["hostapi"])["name"]

print("=== Configuracion ===")
print(f"Entrada: [{DISPOSITIVO_ENTRADA}] {entrada['name']}")
print(f"Salida:  [{DISPOSITIVO_SALIDA}] {salida['name']}")
print(f"API de audio: {api}")
print(f"fs: {FS} Hz | canales grabados: 1")
print(f"Buffer (blocksize): {sd.default.blocksize or 'automatico (0)'}")
print(f"Latencia de entrada: {entrada['default_high_input_latency'] * 1000:.1f} ms")
print(f"Latencia de salida:  {salida['default_high_output_latency'] * 1000:.1f} ms")

sweep, inverse_filter = generate_sine_sweep_pair(DURACION_SWEEP, 20, 20000, FS)
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

Path("data").mkdir(exist_ok=True)
sf.write("data/prueba_grabacion.wav", recording, FS)
sf.write("data/prueba_ri.wav", ir[: int(2 * FS)], FS)
print("\nGuardado: data/prueba_grabacion.wav y data/prueba_ri.wav")
