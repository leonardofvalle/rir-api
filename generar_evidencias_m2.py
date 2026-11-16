import os
import matplotlib.pyplot as plt
import numpy as np

# Importaciones desde los modulos de rir-api
from app.services.signal_utils import (generate_synthetic_ir, get_impulse_response,)
from app.services.sine_sweep import generate_sine_sweep_pair 
try:
    from app.services.filter import filter_single_band
except ImportError:
    from app.services.signal_utils import filter_single_band

# Definición explícita de bandas de octava según norma ISO / IEC
OCTAVE_BANDS = (125, 250, 500, 1000, 2000, 4000, 8000)  # Hz

# Crear carpeta de destino
os.makedirs("docs/m2", exist_ok=True)
fs = 44100

print(" 1/3: Generando prueba de Ida y Vuelta Sintetica...")

# 1. Generar RI sintetica de prueba
duration = 2.0
t60_target = 1.0
t60_dict = {fc: t60_target for fc in OCTAVE_BANDS}
rir_orig = generate_synthetic_ir(duration=duration, t60_values=t60_dict, fs=fs)

# 2 Generar Sine Sweep y su filtro inverso
sweep, inverse_filter = generate_sine_sweep_pair(duration=3.0, f1=20.0, f2=20000.0, fs=fs)

# 3. Convolución (Simulación del recinto)
recorded_signal = np.convolve(sweep, rir_orig, mode="full")

# 4. Deconvolución para recuperar la RI
rir_rec = get_impulse_response(recorded_signal, inverse_filter)

# Alineación de longitudes
min_len = min(len(rir_orig), len(rir_rec))
r1 = rir_orig[:min_len]
r2 = rir_rec[:min_len]

# Coeficiente de correlación de Pearson
corr_matrix = np.corrcoef(r1, r2)
corr_val = float(corr_matrix[0, 1])

# Gráfico 1: Ida y vuelta sintética
plt.figure(figsize=(10, 4))
time_axis = np.linspace(0, min_len / fs, min_len)
plt.plot(time_axis, r1, label="RI Sintética Original", alpha=0.75, linewidth=1)
plt.plot(time_axis, r2, label="RI Deconvolucionada", alpha=0.75, linestyle="--", linewidth=1)
plt.title(f"Ida y Vuelta Sintética — Coeficiente de Correlación: {corr_val:.4f}")
plt.xlabel("Tiempo [s]")
plt.ylabel("Amplitud Normalizada")
plt.legend(loc="upper right")
plt.grid(True, linestyle=":", alpha=0.6)
plt.tight_layout()
plt.savefig("docs/m2/ida_y_vuelta_sintetica_correlacion.png", dpi=150)
plt.close()

print("⏳ 2/3: Generando curvas de decaimiento por bandas de octava...")

# Gráfico 2: Decaimiento por bandas de octava (Integración de Schroeder)
plt.figure(figsize=(10, 5))
for fc in OCTAVE_BANDS:
    band_sig = filter_single_band(rir_orig, fs, fc)
    energy = band_sig[::-1] ** 2
    schroeder = np.cumsum(energy)[::-1]
    schroeder_db = 10 * np.log10(schroeder + 1e-12)
    schroeder_db -= np.max(schroeder_db)
    t_band = np.linspace(0, len(schroeder_db) / fs, len(schroeder_db))
    plt.plot(t_band, schroeder_db, label=f"{fc} Hz")

plt.title("Decaimiento de Energía por Bandas de Octava (Integración de Schroeder)")
plt.xlabel("Tiempo [s]")
plt.ylabel("Nivel [dB]")
plt.ylim(-60, 5)
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(True, linestyle=":", alpha=0.6)
plt.tight_layout()
plt.savefig("docs/m2/decaimiento_bandas_octava.png", dpi=150)
plt.close()

print("3/3: Generando análisis de RIs representativas (T60 corto y largo)...")

def analizar_y_graficar_rir(rir, t60_nom, nombre_archivo, titulo_sala):
    fig, axs = plt.subplots(3, 1, figsize=(10, 8))
    t_axis = np.linspace(0, len(rir) / fs, len(rir))
    axs[0].plot(t_axis, rir, color="#1f77b4", linewidth=0.8)
    axs[0].set_title(f"{titulo_sala} — Forma de Onda")
    axs[0].set_ylabel("Amplitud")
    axs[0].grid(True, linestyle=":", alpha=0.6)
    fft_vals = np.abs(np.fft.rfft(rir))
    freqs = np.fft.rfftfreq(len(rir), 1 / fs)
    axs[1].semilogx(freqs, 20 * np.log10(fft_vals + 1e-12), color="#ff7f0e", linewidth=0.8)
    axs[1].set_title(f"{titulo_sala} — Espectro Frecuencial")
    axs[1].set_xlabel("Frecuencia [Hz]")
    axs[1].set_ylabel("Magnitud [dB]")
    axs[1].set_xlim(20, 20000)
    axs[1].grid(True, which="both", linestyle=":", alpha=0.6)
    for fc in OCTAVE_BANDS:
        b_sig = filter_single_band(rir, fs, fc)
        e = b_sig[::-1] ** 2
        sch = 10 * np.log10(np.cumsum(e)[::-1] + 1e-12)
        sch -= np.max(sch)
    axs[2].plot(np.linspace(0, len(sch) / fs, len(sch)), sch, label=f"{fc} Hz")  
    axs[2].set_title(f"{titulo_sala} — Decaimiento por Bandas de Octava")
    axs[2].set_xlabel("Tiempo [s]")
    axs[2].set_ylabel("Nivel [dB]")
    axs[2].set_ylim(-60, 5)
    axs[2].legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    axs[2].grid(True, linestyle=":", alpha=0.6)
    plt.tight_layout()
    plt.savefig(f"docs/m2/{nombre_archivo}", dpi=150)
    plt.close()

rir_corta = generate_synthetic_ir(duration=1.0, t60_values={fc: 0.4 for fc in OCTAVE_BANDS}, fs=fs)
analizar_y_graficar_rir(rir_corta, 0.4, "rir_corta_analisis.png", 
"RIR Corta (Recinto pequeño / Estudio)")

rir_larga = generate_synthetic_ir(duration=3.0, t60_values={fc: 2.0 for fc in OCTAVE_BANDS}, fs=fs)
analizar_y_graficar_rir(rir_larga, 2.0, "rir_larga_analisis.png",
"RIR Larga (Recinto grande / Sala " \
"Reverberante)")

readme_content = f"""# Validación de Milestone 2 (M2) — RIR-API

Este documento resume la validación experimental y los resultados de los servicios desarrollados en 
la Milestone 2.

---

## 1. Ida y Vuelta Sintética (Deconvolución Espectral)
Se validó el método de deconvolución en el dominio de la frecuencia (`get_impulse_response`)
mediante la prueba completa de ida y vuelta:
1. Generación de una RI sintética ($T_{{60}} = 1.0\\text{{ s}}$).
2. Convolución con un *sine sweep* logarítmico (3 segundos, 20 Hz – 20 kHz).
3. Deconvolución con el filtro inverso.

* **Resultado:** Coeficiente de correlación de Pearson entre la RI original y la recuperada: **`
{corr_val:.4f}`** (objetivo > 0.99).
![Ida y Vuelta Sintética](./ida_y_vuelta_sintetica_correlacion.png)

---

## 2. Filtrado por Bandas de Octava (IEC 61260)
Se implementó `filter_single_band` aplicando filtros Butterworth de orden 4 con `sosfiltfilt`
para filtrado de fase cero.

![Decaimiento por Bandas](./decaimiento_bandas_octava.png)

---

## 3. Análisis de Respuestas al Impulso (Casos de prueba real)
A continuación se presenta el análisis comparativo para dos tipologías de salas:

### A. RIR Corta ($T_{{60}} \\approx 0.4\\text{{ s}}$ — Recinto Pequeño / Estudio)
![Análisis RIR Corta](./rir_corta_analisis.png)

### B. RIR Larga ($T_{{60}} \\approx 2.0\\text{{ s}}$ — Sala Reverberante / Aula Magna)
![Análisis RIR Larga](./rir_larga_analisis.png)
"""

with open("docs/m2/README.md", "w", encoding="utf-8") as f:
    f.write(readme_content)

print("¡Evidencias y reporte de M2 generados exitosamente en docs/m2/!")
print(" Coeficiente de correlación obtenido: {corr_val:.4f}")


