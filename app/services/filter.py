"""Servicio de filtrado por bandas de octava.

Milestone 2: Procesamiento de la respuesta al impulso.
"""

import numpy as np


def filter_single_band(
    signal: np.ndarray, fs: int, center_freq: float, order: int = 4
) -> np.ndarray:
    """Aplica un filtro pasabanda de una octava centrado en ``center_freq`` (IEC 61260).

    Filtro Butterworth pasabanda (``scipy.signal.butter`` con ``output='sos'``)
    con frecuencias de corte:

    - inferior: ``center_freq / sqrt(2)``
    - superior: ``center_freq * sqrt(2)``

    Aplicarlo con ``scipy.signal.sosfiltfilt`` (fase cero), importante para no
    distorsionar EDT y T60. La forma ``(b, a)`` con ``filtfilt`` es inestable en
    las bandas graves.

    Parameters
    ----------
    signal : np.ndarray
        Senal de entrada (array 1D).
    fs : int
        Frecuencia de muestreo en Hz.
    center_freq : float
        Frecuencia central de la banda de octava en Hz.
    order : int, optional
        Orden del filtro Butterworth (por defecto 4).

    Returns
    -------
    np.ndarray
        Senal filtrada (array 1D, misma longitud que ``signal``).
    """
    import scipy.signal

    # Frecuencia de corte inferior
    lower_freq = center_freq / np.sqrt(2)

    # Frecuencia de corte superior
    upper_freq = center_freq * np.sqrt(2)

    # Filtro Butterworth
    butterworth = scipy.signal.butter(
        order, [lower_freq, upper_freq], btype="bandpass", fs=fs, output="sos"
    )

    # Filtro aplicado a la señal
    filtered_signal = scipy.signal.sosfiltfilt(butterworth, signal)

    return filtered_signal
