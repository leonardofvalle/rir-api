import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import pearsonr

from app.services.signal_utils import (generate_synthetic_ir,get_impulse_response,filter_single_band,)
from app.services.sine_sweep import generate_sine_sweep_pair

# Definición local de bandas de octava estándar
OCTAVE_BANDS = {"125 Hz": 125.0,"250 Hz": 250.0,"500 Hz": 500.0,"1 kHz": 1000.0,"2 kHz": 2000.0,"4 kHz": 4000.0,"8 kHz": 8000.0,}

os.makedirs("docs/m2", exist_ok=True)

# ---------------------------------------------------------
# 1. PRUEBA DE IDA Y VUELTA SINTÉTICA (Con Alineación)
# ---------------------------------------------------------
fs = 44100
duration = 2.0
t60_target = 1.0
t60_dict = {freq: t60_target for freq in OCTAVE_BANDS.values()}

# Generar RIR sintética original (devuelve un único np.ndarray)
rir_orig = generate_synthetic_ir(duration=duration,t60_values=t60_dict,fs=fs)

# Generar Sine Sweep y su filtro inverso
sweep, inverse_filter = generate_sine_sweep_pair(3.0, 20.0, 20000.0, fs)

# Simulación de respuesta en recinto mediante convolución
recorded_signal = np.convolve(sweep, rir_orig, mode="full")

# Recalcular RI mediante deconvolución
rir_rec = get_impulse_response(recorded_signal, inverse_filter)

# ALINEACIÓN Y RECORTE (Corrección del desfasaje del pico)
rir_orig_aligned = rir_orig[np.argmax(np.abs(rir_orig)):]
rir_rec_aligned = rir_rec[np.argmax(np.abs(rir_rec)):]
min_len = min(len(rir_orig_aligned), len(rir_rec_aligned))
rir_orig_aligned = rir_orig_aligned[:min_len]
rir_rec_aligned = rir_rec_aligned[:min_len]

# Cálculo de correlación de Pearson
corr, _ = pearsonr(rir_orig_aligned, rir_rec_aligned)

# Graficar comparación alineada
plt.figure(figsize=(10, 4))
plt.plot(rir_orig_aligned, label="RI Original (Alineada)", alpha=0.7)
plt.plot(rir_rec_aligned, label="RI Recuperada", linestyle="--", alpha=0.7)
plt.title(f"Ida y Vuelta Sintética - Correlación de Pearson: {corr:.5f}")
plt.xlabel("Muestras")
plt.ylabel("Amplitud")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("docs/m2/ida_y_vuelta_sintetica_correlacion.png")
plt.close()

# ---------------------------------------------------------
# 2. ANÁLISIS POR BANDAS Y DECAIMIENTO DE SCHROEDER
# ---------------------------------------------------------
def analizar_y_graficar_rir(rir, fs, titulo_prefix, filename):
    fig, axs = plt.subplots(3, 1, figsize=(10, 10))
    
    # Subplot 1: Forma de onda
    t_val = np.arange(len(rir)) / fs
    axs[0].plot(t_val, rir, color='b')
    axs[0].set_title(f"{titulo_prefix} - Forma de Onda")
    axs[0].set_xlabel("Tiempo [s]")
    axs[0].set_ylabel("Amplitud")
    axs[0].grid(True)
    
    # Subplot 2: Espectro de Frecuencia
    fft_vals = np.abs(np.fft.rfft(rir))
    freqs = np.fft.rfftfreq(len(rir), 1/fs)
    axs[1].plot(freqs, 20 * np.log10(fft_vals + 1e-12), color='g')
    axs[1].set_title(f"{titulo_prefix} - Espectro de Frecuencia")
    axs[1].set_xlabel("Frecuencia [Hz]")
    axs[1].set_ylabel("Magnitud [dB]")
    axs[1].grid(True)
    
    # Subplot 3: Decaimiento por Bandas de Octava
    axs[2].set_title(f"{titulo_prefix} - Decaimiento por Bandas de Octava")
    axs[2].set_xlabel("Tiempo [s]")
    axs[2].set_ylabel("Energía [dB]")
    axs[2].grid(True)
    
    # Bucle por cada banda de octava
    for band_name, band_freq in OCTAVE_BANDS.items():
        filtered_band = filter_single_band(rir, fs, band_freq)
        
        # Integral de Schroeder
        energy = filtered_band[::-1]**2
        schroeder = np.cumsum(energy)[::-1]
        schroeder_db = 10 * np.log10(schroeder / (np.max(schroeder) + 1e-12) + 1e-12)
        t_band = np.arange(len(schroeder_db)) / fs
        
        # Trazar cada banda dentro del bucle for
        axs[2].plot(t_band, schroeder_db, label=f"{band_name}")
        
    axs[2].legend(loc="upper right", fontsize='small')
    plt.tight_layout()
    plt.savefig(f"docs/m2/{filename}")
    plt.close()

# Generar RIRs sintéticas representativas
t60_corta_dict = {freq: 0.4 for freq in OCTAVE_BANDS.values()}
rir_corta = generate_synthetic_ir(duration=2.0,t60_values=t60_corta_dict,fs=fs)

t60_larga_dict = {freq: 2.0 for freq in OCTAVE_BANDS.values()}
rir_larga = generate_synthetic_ir(duration=4.0,t60_values=t60_larga_dict,fs=fs)