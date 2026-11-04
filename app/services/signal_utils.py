"""Utilidades de procesamiento de senales.

Milestone 2: Procesamiento de la respuesta al impulso.
"""

from pathlib import Path

import numpy as np


def load_audio(path: str | Path) -> tuple[np.ndarray, int]:
    """Carga un archivo de audio (al menos WAV y FLAC) y retorna senal y fs.

    La senal se devuelve **mono**: si el archivo es estereo (o multicanal) se
    promedian los canales. Se convierte a ``float64`` normalizada entre -1 y 1
    independientemente de la profundidad de bits original (16, 24 o 32 bits).
    Usar ``soundfile`` (o ``scipy.io.wavfile``).

    Parameters
    ----------
    path : str | Path
        Ruta al archivo de audio a cargar.

    Returns
    -------
    signal : np.ndarray
        Senal de audio mono como array 1D ``float64`` en [-1, 1].
    fs : int
        Frecuencia de muestreo del archivo en Hz.

    Raises
    ------
    FileNotFoundError
        Si el archivo especificado no existe.
    ValueError
        Si el archivo no es un audio valido o el formato no es soportado
        (con un mensaje claro que indique el archivo y el motivo).
    """
    raise NotImplementedError("Implementar en Milestone 2")


import numpy as np
import scipy.signal as sps


def generate_synthetic_ir(duration: float, t60_values: dict[float, float], fs: int) -> np.ndarray:
    """Sintetiza una respuesta al impulso con valores de T60 conocidos por banda.

    Modelo: ``h(t) = n(t) * exp(-alpha * t)`` con ``alpha = 3 * ln(10) / T60``,
    donde ``n(t)`` es ruido blanco filtrado en la banda de octava. Se suman las
    componentes de todas las bandas y se normaliza.

    Parameters
    ----------
    duration : float
        Duracion de la respuesta al impulso en segundos.
    t60_values : dict[float, float]
        Diccionario ``{frecuencia_central_Hz: T60_segundos}``.
        Ejemplo: ``{125: 2.0, 250: 1.8, 500: 1.5, 1000: 1.2, 2000: 1.0, 4000: 0.8}``.
    fs : int
        Frecuencia de muestreo en Hz.

    Returns
    -------
    np.ndarray
        Respuesta al impulso sintetizada (array 1D de ``int(duration * fs)`` muestras).

    Raises
    ------
    ValueError
        Si `duration` es menor o igual a 0, o si `t60_values` esta vacio.
    """
    if duration <= 0:
        raise ValueError("La duracion debe ser mayor a 0 segundos.")
    if not t60_values:
        raise ValueError("El diccionario de valores T60_values no puede estar vacio.")

    num_samples = int(duration * fs)
    t = np.linspace(0, duration, num_samples, endpoint=False)
    ir_total = np.zeros(num_samples)

    rng = np.random.default_rng(42)

    for fc, t60 in t60_values.items():
        if t60 <= 0:
            raise ValueError(
                f"El valor de T60 para la frecuencia {fc} Hz debe ser mayor a 0 segundos."
            )

        # 1. Ruido blanco por banda
        white_noise = rng.normal(0, 1, num_samples)

        # 2. Filtrado pasa-banda por octava (f_low = fc / sqrt(2), f_high = fc * sqrt(2))
        f_low = fc / np.sqrt(2)
        f_high = fc * np.sqrt(2)

        # Asegurar que las frecuencias no superen el límite de Nyquist
        nyquist = fs / 2.0
        if f_high >= nyquist:
            f_high = nyquist * 0.99
        if f_low <= 0:
            f_low = 1.0

        sos = sps.butter(N=4, Wn=[f_low, f_high], btype="bandpass", fs=fs, output="sos")
        band_noise = sps.sosfilt(sos, white_noise)

        # 3. Envolvente de decaimiento exponencial
        alpha = (3.0 * np.log(10.0)) / t60
        envelope = np.exp(-alpha * t)

        # 4. Acumular la componente de la banda
        ir_total += band_noise * envelope

    # Normalización al pico máximo
    max_amp = np.max(np.abs(ir_total))
    if max_amp > 0:
        ir_total = (ir_total / max_amp) * 0.9

    return ir_total


def get_impulse_response(recording: np.ndarray, inverse_filter: np.ndarray) -> np.ndarray:
    """Obtiene la respuesta al impulso mediante deconvolucion de un sine sweep.

    ``h(t) = y(t) * x_inv(t)``, con ``y = recording`` y ``x_inv = inverse_filter``;
    usar ``scipy.signal.fftconvolve`` (``mode='full'``), recortar para que la RI
    comience en el pico (o ligeramente antes) y normalizar respecto del pico.

    Parameters
    ----------
    recording : np.ndarray
        Senal grabada que contiene la respuesta de la sala al sweep.
    inverse_filter : np.ndarray
        Filtro inverso del sweep utilizado.

    Returns
    -------
    np.ndarray
        Respuesta al impulso estimada, normalizada.
    """
    raise NotImplementedError("Implementar en Milestone 2")


def logarithmic_scale_conversion(signal: np.ndarray) -> np.ndarray:
    """Convierte una senal a escala logaritmica (dB) normalizada.

    ``L = 20 * log10(|x| / max(|x|))``. Evitar ``log(0)`` (usar un ``eps`` o
    un piso, por ejemplo -120 dB).

    Parameters
    ----------
    signal : np.ndarray
        Senal de entrada (valores lineales, array 1D).

    Returns
    -------
    np.ndarray
        Senal en dB, normalizada a 0 dB en el maximo.
    """
    raise NotImplementedError("Implementar en Milestone 2")
