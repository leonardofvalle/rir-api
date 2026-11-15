"""Grafico de la prueba real de play_and_record (issue #3).

Lee data/prueba_grabacion.wav y data/prueba_ri.wav (generados por
prueba_play_and_record.py) y guarda docs/m1/prueba_real_play_and_record.png.

Uso: uv run python graficar_prueba_real.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf

from app.services.signal_utils import logarithmic_scale_conversion

grabacion, fs = sf.read("data/prueba_grabacion.wav")
ri, fs_ri = sf.read("data/prueba_ri.wav")

t_grabacion = np.arange(len(grabacion)) / fs
ri_db = logarithmic_scale_conversion(ri)
t_ri = np.arange(len(ri)) / fs_ri * 1000  # ms

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6.5))

ax1.plot(t_grabacion, grabacion, linewidth=0.4)
ax1.set_title("Grabacion del sine sweep (UMC22 + AT2020, fuente: auricular)")
ax1.set_xlabel("Tiempo [s]")
ax1.set_ylabel("Amplitud [FS]")
ax1.grid(True, alpha=0.3)

ax2.plot(t_ri, ri_db, linewidth=0.6)
ax2.set_title("Respuesta al impulso obtenida con get_impulse_response")
ax2.set_xlabel("Tiempo [ms]")
ax2.set_ylabel("Nivel [dB, 0 dB = pico]")
ax2.set_xlim(0, 300)
ax2.set_ylim(-80, 5)
ax2.grid(True, alpha=0.3)

fig.tight_layout()
Path("docs/m1").mkdir(parents=True, exist_ok=True)
fig.savefig("docs/m1/prueba_real_play_and_record.png", dpi=150)
print("Guardado: docs/m1/prueba_real_play_and_record.png")
