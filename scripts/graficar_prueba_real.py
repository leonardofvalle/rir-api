"""Grafico de una prueba real de play_and_record (issue #3).

Lee ``docs/m1/prueba_<nombre>_grabacion.wav`` y ``prueba_<nombre>_ri.wav``
(generados por ``scripts/prueba_play_and_record.py``) y guarda
``docs/m1/prueba_<nombre>.png`` con cuatro paneles:

1. La senal emitida (el sweep, regenerado con los mismos parametros).
2. La grabacion, en el mismo eje de tiempo: se ven la latencia y si hay clipping o cortes.
3. El espectrograma de la grabacion: el barrido del sweep, la cola y el ruido de fondo.
4. La respuesta al impulso obtenida por deconvolucion, en dB.

Uso (desde la raiz del repositorio)::

    uv run python -m scripts.graficar_prueba_real auricular
    uv run python -m scripts.graficar_prueba_real parlante
"""

import sys

import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf

from app.services.signal_utils import logarithmic_scale_conversion
from app.services.sine_sweep import generate_sine_sweep_pair
from scripts.prueba_play_and_record import (
    CARPETA,
    DURACION_SWEEP,
    F_FINAL,
    F_INICIAL,
    NIVEL_SWEEP,
)

TITULOS = {
    "auricular": "fuente: auricular pegado al micrófono",
    "parlante": "fuente: parlante en la sala",
}


def main() -> None:
    nombre = sys.argv[1] if len(sys.argv) > 1 else "parlante"
    grabacion, fs = sf.read(CARPETA / f"prueba_{nombre}_grabacion.wav")
    ri, fs_ri = sf.read(CARPETA / f"prueba_{nombre}_ri.wav")

    sweep, _ = generate_sine_sweep_pair(DURACION_SWEEP, F_INICIAL, F_FINAL, fs)
    emitida = np.zeros(len(grabacion))
    emitida[: len(sweep)] = sweep * NIVEL_SWEEP
    t = np.arange(len(grabacion)) / fs

    fig, axes = plt.subplots(4, 1, figsize=(10, 12))
    fig.suptitle(f"Prueba de play_and_record · {TITULOS.get(nombre, nombre)}", fontsize=13, y=0.995)

    axes[0].plot(t, emitida, linewidth=0.4, color="tab:gray")
    axes[0].set_title("Señal emitida: sine sweep de 20 Hz a 20 kHz (−6 dBFS)")
    axes[1].plot(t, grabacion, linewidth=0.4, color="tab:blue")
    pico_db = 20 * np.log10(np.max(np.abs(grabacion)) + 1e-12)
    axes[1].set_title(f"Señal grabada (pico {pico_db:.1f} dBFS)")
    for ax in axes[:2]:
        ax.set_xlim(0, t[-1])
        ax.set_ylim(-1.05, 1.05)
        ax.set_xlabel("Tiempo [s]")
        ax.set_ylabel("Amplitud [FS]")
        ax.grid(True, alpha=0.3)

    nperseg = 2048
    _, _, _, imagen = axes[2].specgram(
        grabacion, NFFT=nperseg, Fs=fs, noverlap=nperseg * 3 // 4, cmap="magma", vmin=-140
    )
    axes[2].set_yscale("log")
    axes[2].set_ylim(20, fs / 2)
    axes[2].set_xlabel("Tiempo [s]")
    axes[2].set_ylabel("Frecuencia [Hz]")
    axes[2].set_title("Espectrograma de la grabación")
    fig.colorbar(imagen, ax=axes[2], label="Nivel [dB]", pad=0.01)

    t_ri = np.arange(len(ri)) / fs_ri * 1000
    axes[3].plot(t_ri, logarithmic_scale_conversion(ri), linewidth=0.6, color="tab:blue")
    axes[3].set_title("Respuesta al impulso (deconvolución con el filtro inverso)")
    axes[3].set_xlabel("Tiempo [ms]")
    axes[3].set_ylabel("Nivel [dB, 0 dB = pico]")
    axes[3].set_xlim(0, t_ri[-1])
    axes[3].set_ylim(-90, 5)
    axes[3].grid(True, alpha=0.3)

    fig.tight_layout()
    salida = CARPETA / f"prueba_{nombre}.png"
    fig.savefig(salida, dpi=150)
    print(f"Guardado: {salida}")


if __name__ == "__main__":
    main()
