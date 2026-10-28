import numpy as np


def generate_pink_noise(duration: float, fs: int) -> np.ndarray:

    n = int(duration * fs)  # Número de muestras

    white_noise = np.random.randn(n)  # Generación de ruido blanco

    fft = np.fft.rfft(white_noise)  # Transformada rápida de Fourier
    # para pasar al dominio de la frecuencia

    freqs = np.fft.rfftfreq(n, d=1 / fs)  # Frecuencias correspondientes

    z = np.zeros_like(fft)  # Para evitar la división por cero se genera un array de ceros del mismo
    # tamaño que el espectro de ruido blanco

    z[1:] = 1 / np.sqrt(freqs[1:])  # Se aplica el filtro 1/sqrt(f) en todas las posiciones menos
    # la primera, que se deja en cero para evitar la división por cero

    filt = fft * z  # Se aplica el filtro al espectro de ruido blanco

    ifft = np.fft.irfft(filt, n=n)  # Transformada rápida de Fourier inversa

    pink_noise: np.ndarray = ifft / np.max(np.abs(ifft))  # Ruido rosa normalizado entre -1 y 1

    return pink_noise
