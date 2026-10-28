import os

import matplotlib.pyplot as plt
import numpy as np
import scipy.signal as sps

# Importamos las funciones desarrolladas en el proyecto
from app.services.pink_noise import generate_pink_noise
from app.services.sine_sweep import generate_sine_sweep_pair

# Crea la carpeta docs/m1 si aun no existe en el disco
os.makedirs("docs/m1", exist_ok=True)
fs = 44100  # Frecuencia de muestreo estandar (44.1 kHz)

print("Generando graficas de validacion para M1...")

# -----------------------------------------------------
# 1. Espectro del Ruido Rosa (-3 dB / octava)
# -----------------------------------------------------
try:
    pink = generate_pink_noise(5.0, fs)
    f, pxx = sps.welch(pink, fs=fs, nperseg=8192)

    # Filtrar la banda de 100 Hz a 20 kHz para calcular la pendiente de caida
    banda = (f >= 100) & (f <= 10000)
    f_banda = f[banda]
    pxx_banda_db = 10 * np.log10(pxx[banda])
    poly = np.polyfit(np.log2(f_banda), pxx_banda_db, 1)
    trend = np.polyval(poly, np.log2(f_banda))

    plt.figure(figsize=(9, 4.5))
    plt.semilogx(f, 10 * np.log10(pxx + 1e-12), label="PSD Ruido Rosa", color="#1f77b4", alpha=0.7)
    plt.semilogx(f_banda, trend, "r--", linewidth=2, label=f"Ajuste: {poly[0]:.2f} dB/octava")
    plt.title("Validacion M1: Espectro del Ruido Rosa (-3 dB/octava)", fontsize=12)
    plt.xlabel("Frecuencia [Hz]")
    plt.ylabel("PSD [dB/Hz]")
    plt.grid(True, which="both", linestyle="--", alpha=0.5)
    plt.legend()
    plt.tight_layout()
    plt.savefig("docs/m1/espectro_ruido_rosa.png", dpi=300)
    plt.close()
    print("✓ Creado: docs/m1/espectro_ruido_rosa.png")
except Exception as e:
    print(f"⚠ Nota sobre Ruido Rosa: {e}")

# -----------------------------------------------------
# 2. Espectrograma del Sine Sweep Logaritmico (20 Hz - 20 kHz)
# -----------------------------------------------------
sweep, inverse_filter = generate_sine_sweep_pair(3.0, 20.0, 20000.0, fs)
f_spec, t_spec, Sxx = sps.spectrogram(sweep, fs=fs, nperseg=2048, noverlap=1024)

plt.figure(figsize=(9, 4.5))
plt.pcolormesh(t_spec, f_spec, 10 * np.log10(Sxx + 1e-12), shading="gouraud", cmap="magma")
plt.title("Validacion M1: Espectrograma del Sine Sweep (20 Hz - 20 kHz)", fontsize=12)
plt.xlabel("Tiempo [s]")
plt.ylabel("Frecuencia [Hz]")
plt.colorbar(label="Potencia/Frecuencia [dB/Hz]")
plt.grid(True, which="both", linestyle="--", alpha=0.5)
plt.savefig("docs/m1/espectrograma_sine_sweep.png", dpi=300)
plt.close()
print("✓ Creado: docs/m1/espectrograma_sine_sweep.png")

# -----------------------------------------------------
# 3. Convolucion Sweep * Filtro Inverso (Impulso Delta)
# -----------------------------------------------------
impulso = sps.fftconvolve(sweep, inverse_filter, mode="full")
energia = impulso**2
energia_db = 10 * np.log10(energia / np.max(energia) + 1e-12)
t_imp = (np.arange(len(impulso)) - np.argmax(energia)) / fs

plt.figure(figsize=(9, 4.5))
plt.plot(t_imp, energia_db, color="#2ca02c")
plt.title("Validacion M1: Convolucion Sweep * Filtro Inverso (Impulso Delta)", fontsize=12)
plt.xlabel("Tiempo respecto al pico [s]")
plt.ylabel("Amplitud [dB]")
plt.xlim([-0.05, 0.05])
plt.ylim([-80, 5])
plt.grid(True, linestyle="--", alpha=0.5)
plt.tight_layout()
plt.savefig("docs/m1/convolucion_sweep_filtro_inverso.png", dpi=300)
plt.close()
print("✓ Creado: docs/m1/convolucion_sweep_filtro_inverso.png")

print("\n¡Proceso de generación finalizado con éxito!")
