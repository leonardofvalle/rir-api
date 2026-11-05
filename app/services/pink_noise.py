"""Servicio de generacion de ruido rosa.

Milestone 1: Generacion de senales.
"""

import numpy as np


def generate_pink_noise(duration: float, fs: int) -> np.ndarray:
    """Genera una senal de ruido rosa de la duracion especificada.

    El ruido rosa tiene una densidad espectral de potencia inversamente
    proporcional a la frecuencia (1/f): cae -3 dB/octava, de modo que cada
    octava contiene la misma energia. Por eso es util para mediciones acusticas.

    1. Se genera un ruido blaco con ``np.random.randn``,
    2. Se pasa el ruido generado al dominio de la frecuencia con ``np.fft.rfft``,
    3. Se debe crear el filtro ``H(f) = 1/sqrt(f)``
        3.1. Para evitar la división por cero se genera previamente un array de ceros
        3.2. Se reemplaza a partir de la segunda posición con el filtro dividiendo por ``sqrt(f)``
    4. Se aplica el filtro al espectro de ruido blanco
    5. Se retorna al dominio del tiempo con ``np.fft.irfft``
    6. Se normaliza el ruido rosa entre -1 y 1

    Parameters
    ----------
    duration : float
        Duracion de la senal en segundos.
    fs : int
        Frecuencia de muestreo en Hz.

    Returns
    -------
    np.ndarray
        Senal de ruido rosa normalizada entre -1 y 1, de longitud
        ``int(duration * fs)``.

    References
    ----------
    .. [1] https://www.firstpr.com.au/dsp/pink-noise/
    """
    # Número de muestras
    n = int(duration * fs)

    # Generación de ruido blanco
    white_noise = np.random.randn(n)

    # Transformada rápida de Fourier para pasar al dominio de la frecuencia
    fft = np.fft.rfft(white_noise)

    # Frecuencias correspondientes
    freqs = np.fft.rfftfreq(n, d=1 / fs)

    # Se genera un array de ceros del tamaño que el espectro de ruido blanco
    z = np.zeros_like(fft)

    # Se aplica el filtro 1/sqrt(f) en todas las posiciones dejando en cero la primera
    z[1:] = 1 / np.sqrt(freqs[1:])

    # Se aplica el filtro al espectro de ruido blanco
    filt = fft * z

    # Transformada rápida de Fourier inversa
    ifft = np.fft.irfft(filt, n=n)

    # Ruido rosa normalizado entre -1 y 1
    pink_noise: np.ndarray = ifft / np.max(np.abs(ifft))

    return pink_noise
