"""Servicio de reproduccion y grabacion simultanea.

Milestone 1: Generacion de senales.

``sounddevice`` se importa **dentro** de la funcion (import perezoso): asi el
resto de la API, los tests y el CI funcionan en maquinas sin placa de audio.
"""

import numpy as np


def play_and_record(signal: np.ndarray, fs: int, record_duration: float) -> np.ndarray:
    """Reproduce una senal y graba simultaneamente (``sounddevice.playrec``).

    Consideraciones:

    - ``record_duration`` debe ser mayor o igual a la duracion de la senal
      para capturar la cola de reverberacion del recinto.
    - Aceptar senales mono (array 1D) y estereo (array 2D ``(muestras, canales)``)
      sin asumir la forma.
    - Se recomienda un silencio inicial (pre-roll) de 0.5-1 s para compensar la
      latencia del sistema de audio.
    - Documentar en el README la configuracion usada (dispositivo, canales, fs,
      buffer size).

    Parameters
    ----------
    signal : np.ndarray
        Senal a reproducir (1D mono o 2D ``(muestras, canales)``).
    fs : int
        Frecuencia de muestreo en Hz.
    record_duration : float
        Duracion total de la grabacion en segundos.

    Returns
    -------
    np.ndarray
        Senal grabada, con ``int(record_duration * fs)`` muestras.

    Raises
    ------
    RuntimeError
        Si no hay un dispositivo de audio disponible (con un mensaje informativo).
    """
    import sounddevice as sd

    # Cantidad de muestras que tiene que durar la grabacion
    n_total = int(record_duration * fs)
    signal = np.asarray(signal)

    # La grabacion no puede ser mas corta que la señal
    if signal.shape[0] > n_total:
        raise ValueError(
            f"record_duration ({record_duration} s) debe ser mayor o igual "
            f"a la duracion de la senal ({signal.shape[0] / fs:.2f} s)."
        )

    # Agregar silencio al final para grabar la cola de reverberacion.
    faltan = n_total - signal.shape[0]
    ancho = [(0, faltan)] + [(0, 0)] * (signal.ndim - 1)
    signal_con_cola = np.pad(signal, ancho, mode="constant")

    # Reproducir y grabar al mismo tiempo; si no hay placa, error
    try:
        recording = sd.playrec(signal_con_cola, samplerate=fs, channels=1)
        sd.wait()
    except sd.PortAudioError as e:
        raise RuntimeError(
            "No se encontro un dispositivo de audio disponible. "
            "Revisar que la placa este conectada y configurada."
        ) from e

    return recording
