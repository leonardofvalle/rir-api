"""Servicio de calculo de parametros acusticos segun ISO 3382.

Milestone 3: Producto final.
"""

import numpy as np

from app.services.filter import filter_single_band

OCTAVE_BANDS = (125, 250, 500, 1000, 2000, 4000)
"""Frecuencias centrales (Hz) de las bandas de octava que se analizan."""

DECAY_RANGES = {
    "EDT": (0.0, -10.0),
    "T10": (-5.0, -15.0),
    "T20": (-5.0, -25.0),
    "T30": (-5.0, -35.0),
}
"""Tramo de la curva de Schroeder (inicio, fin en dB) de cada tiempo."""

PRE_PADDING_S = 0.005
"""Ceros que se agregan antes de la RI para filtrar (s)."""

NOISE_TAIL_FRACTION = 0.1
"""Fraccion final de la banda que se toma como ruido de fondo."""

ENVELOPE_WINDOW_S = 0.01
"""Ventana para promediar la energia al medir el rango dinamico (s)."""

DYNAMIC_RANGE_MARGIN_DB = 10.0
"""Margen sobre el ruido que exige ISO 3382 por encima del fin del tramo (dB)."""


def apply_smoothing(
    signal: np.ndarray, fs: int, method: str = "hilbert", window_ms: float = 10
) -> np.ndarray:
    """Suaviza una senal y devuelve su envolvente en **amplitud**.

    - ``method='hilbert'`` (recomendado): envolvente de Hilbert,
      ``np.abs(scipy.signal.hilbert(signal))``. Ignora ``window_ms``.
    - ``method='moving_average'``: media movil de ``window_ms`` milisegundos
      (``int(window_ms * fs / 1000)`` muestras, al menos 1). Para que la salida
      quede en amplitud (comparable con Hilbert), devolver la raiz de la media
      movil de ``signal**2`` (envolvente RMS) o, alternativamente, la media
      movil de ``|signal|``. Documentar cual se eligio.

    Parameters
    ----------
    signal : np.ndarray
        Senal de entrada (tipicamente una RI filtrada por banda, array 1D).
    fs : int
        Frecuencia de muestreo en Hz (para convertir ``window_ms`` a muestras).
    method : str, optional
        ``'hilbert'`` (por defecto) o ``'moving_average'``.
    window_ms : float, optional
        Largo de la ventana de media movil en milisegundos (por defecto 10 ms).

    Returns
    -------
    np.ndarray
        Envolvente en amplitud (no negativa), de la misma longitud que ``signal``.

    Raises
    ------
    ValueError
        Si ``method`` no es ``'hilbert'`` ni ``'moving_average'``, o si
        ``window_ms`` no es positivo.
    """

    if method not in ["hilbert", "moving_average"]:
        raise ValueError("Metodo invalido. Debe usar 'hilbert' o 'moving_average'")

    if window_ms <= 0:
        raise ValueError("El largo de la ventana debe ser positivo")

    if method == "hilbert":
        from scipy.signal import hilbert

        # Envolvente de Hilbert
        envelope = np.abs(hilbert(signal))

    elif method == "moving_average":
        # Convertir milisegundos a cantidad de muestras
        window_samples = max(1, int(window_ms * fs / 1000))

        # Ventana de media movil promediada
        window = np.ones(window_samples) / window_samples

        # Calcular la media movil del cuadrado de la senal al cuadrado
        mean_squared = np.convolve(signal**2, window, mode="same")

        # Envolvente RMS
        envelope = np.sqrt(mean_squared)

    return envelope


def apply_schroeder_integral(ir: np.ndarray) -> np.ndarray:
    """Calcula la integral de Schroeder (Energy Decay Curve) en dB.

    ``E[n] = sum_{k=n}^{N-1} h[k]**2`` y ``L[n] = 10*log10(E[n] / E[0])``.

    Parameters
    ----------
    ir : np.ndarray
        Respuesta al impulso (o RI filtrada por banda, array 1D).

    Returns
    -------
    np.ndarray
        Curva de decaimiento en dB, normalizada a 0 dB en la primera muestra,
        de la misma longitud que ``ir``.

    References
    ----------
    .. [1] Schroeder, M. R. (1965). "New method of measuring reverberation
       time." JASA 37(3), 409-412.
    """

    # Calculo de la integral de Schroeder
    schroeder = np.cumsum(ir[::-1] ** 2)[::-1]

    # Evitar logaritmo de cero
    schroeder = np.maximum(schroeder, np.finfo(float).eps)

    # Curva de decaimiento normalizada a 0 dB
    schroeder_db = 10 * np.log10(schroeder / schroeder[0])

    return schroeder_db


def linear_regression(x: np.ndarray, y: np.ndarray) -> tuple[float, float, float]:
    """Calcula la regresion lineal por minimos cuadrados.

    Se recomienda implementarla a mano (formulas de minimos cuadrados) en lugar
    de ``np.polyfit``, para demostrar comprension del metodo.

    Parameters
    ----------
    x : np.ndarray
        Variable independiente (tipicamente tiempo en segundos).
    y : np.ndarray
        Variable dependiente (tipicamente curva de Schroeder en dB).

    Returns
    -------
    slope : float
        Pendiente de la recta ajustada ``m`` (dB/s en el contexto acustico).
    intercept : float
        Ordenada al origen ``b`` (dB).
    r2 : float
        Coeficiente de determinacion R^2.
    """

    x_mean = np.mean(x)
    y_mean = np.mean(y)

    numerator = np.sum((x - x_mean) * (y - y_mean))
    denominator = np.sum((x - x_mean) ** 2)

    slope = numerator / denominator
    intercept = y_mean - slope * x_mean

    ss_total = np.sum((y - y_mean) ** 2)
    ss_residual = np.sum((y - (slope * x + intercept)) ** 2)

    r2 = 1 - (ss_residual / ss_total)

    return slope, intercept, r2


def calculate_parameters_from_ir(ir: np.ndarray, fs: int) -> dict[str, dict[float, float | None]]:
    """Calcula los parametros acusticos ISO 3382 por banda de octava.

    Parametros: EDT (0 a -10 dB), T10 (-5 a -15 dB), T20 (-5 a -25 dB),
    T30 (-5 a -35 dB), D50 (%) y C80 (dB).

    Para cada banda de ``OCTAVE_BANDS`` que entra por debajo de Nyquist:
    se filtra la RI con ``filter_single_band``, se calcula la curva de
    Schroeder y se ajusta una recta en el tramo de cada tiempo de
    reverberacion; el tiempo es el que tarda esa recta en caer 60 dB.
    D50 y C80 se cuentan desde el pico de la banda filtrada.

    Parameters
    ----------
    ir : np.ndarray
        Respuesta al impulso (array 1D).
    fs : int
        Frecuencia de muestreo en Hz.

    Returns
    -------
    dict[str, dict[float, float | None]]
        ``{parametro: {frecuencia_central: valor}}``.
        Ejemplo: ``{'T30': {125.0: 1.5, 250.0: 1.3, ...}, 'EDT': {...},
        'D50': {...}, 'C80': {...}}``. Un tiempo de reverberacion vale
        ``None`` si la banda no tiene rango dinamico suficiente para su tramo.

    Raises
    ------
    ValueError
        Si ``ir`` esta vacia o es toda ceros, o si ``fs`` es tan baja que no
        entra ninguna banda.

    References
    ----------
    .. [1] ISO 3382-1:2009. "Acoustics -- Measurement of room acoustic
       parameters -- Part 1: Performance spaces."
    """
    ir = np.asarray(ir, dtype=float)
    if ir.size == 0 or not np.any(ir):
        raise ValueError("La respuesta al impulso esta vacia o es toda ceros.")

    bands = [fc for fc in OCTAVE_BANDS if fc * np.sqrt(2) < fs / 2]
    if not bands:
        raise ValueError(f"Con fs = {fs} Hz no entra ninguna banda de octava.")

    # get_impulse_response recorta justo en el pico: se agregan unos ms de
    # ceros adelante para que el filtro no se coma el comienzo de la RI.
    padding = np.zeros(int(PRE_PADDING_S * fs))
    ir_padded = np.concatenate([padding, ir])
    t = np.arange(len(ir_padded)) / fs

    results: dict[str, dict[float, float | None]] = {
        name: {} for name in (*DECAY_RANGES, "D50", "C80")
    }
    for fc in bands:
        band = filter_single_band(ir_padded, fs, fc)
        envelope = _energy_envelope(band, fs)
        noise = _noise_floor(envelope)
        dynamic_range = 10 * np.log10(np.max(envelope) / noise)
        end = _truncation_index(envelope, noise)
        edc_db = apply_schroeder_integral(band[:end])

        for name, (start_db, end_db) in DECAY_RANGES.items():
            if dynamic_range < abs(end_db) + DYNAMIC_RANGE_MARGIN_DB:
                results[name][float(fc)] = None
            else:
                results[name][float(fc)] = _decay_time(edc_db, t[:end], start_db, end_db)

        d50, c80 = _clarity_and_definition(band, fs)
        results["D50"][float(fc)] = d50
        results["C80"][float(fc)] = c80

    return results


def _energy_envelope(band: np.ndarray, fs: int) -> np.ndarray:
    """Energia de la banda promediada en ventanas de ``ENVELOPE_WINDOW_S``."""
    window = max(1, int(ENVELOPE_WINDOW_S * fs))
    return np.convolve(band**2, np.ones(window) / window, mode="same")


def _noise_floor(envelope: np.ndarray) -> float:
    """Energia media del ultimo ``NOISE_TAIL_FRACTION`` de la envolvente."""
    tail = envelope[-max(1, int(NOISE_TAIL_FRACTION * len(envelope))) :]
    return float(np.mean(tail)) + np.finfo(float).tiny


def _truncation_index(envelope: np.ndarray, noise: float) -> int:
    """Primera muestra despues del pico donde la envolvente llega al ruido.

    Cortar ahi evita que la cola de ruido levante la curva de Schroeder.
    """
    peak = int(np.argmax(envelope))
    below = np.nonzero(envelope[peak:] <= noise)[0]
    return peak + int(below[0]) if below.size else len(envelope)


def _decay_time(edc_db: np.ndarray, t: np.ndarray, start_db: float, end_db: float) -> float | None:
    """Ajusta una recta a la curva de Schroeder entre ``start_db`` y ``end_db``.

    Devuelve el tiempo que tarda la recta en caer 60 dB (``-60 / pendiente``),
    o ``None`` si el tramo tiene menos de 2 muestras o la pendiente no es
    negativa.
    """
    in_range = (edc_db <= start_db) & (edc_db >= end_db)
    if np.count_nonzero(in_range) < 2:
        return None
    slope, _, _ = linear_regression(t[in_range], edc_db[in_range])
    if slope >= 0:
        return None
    return float(-60.0 / slope)


def _clarity_and_definition(band: np.ndarray, fs: int) -> tuple[float | None, float | None]:
    """Calcula D50 (%) y C80 (dB) contando desde el pico de la banda."""
    n0 = int(np.argmax(np.abs(band)))
    energy = band[n0:] ** 2
    total = np.sum(energy)
    n50 = int(0.05 * fs)
    n80 = int(0.08 * fs)
    early_80 = np.sum(energy[:n80])
    late_80 = total - early_80

    d50 = float(100 * np.sum(energy[:n50]) / total) if total > 0 else None
    c80 = float(10 * np.log10(early_80 / late_80)) if late_80 > 0 and early_80 > 0 else None
    return d50, c80


def apply_lundeby(ir: np.ndarray, fs: int) -> tuple[int, float]:
    """Estima el punto de truncamiento de la RI (metodo de Lundeby).

    Parameters
    ----------
    ir : np.ndarray
        Respuesta al impulso (array 1D).
    fs : int
        Frecuencia de muestreo en Hz.

    Returns
    -------
    index : int
        Indice de la muestra donde la RI se cruza con el ruido de fondo.
    noise_level_db : float
        Nivel estimado del ruido de fondo en dB.

    Notes
    -----
    Esta funcion es **opcional** (extra).

    References
    ----------
    .. [1] Lundeby, A. et al. (1995). "Uncertainties of measurements in
       room acoustics." Acustica 81(4), 344-355.
    """
    raise NotImplementedError("Implementar en Milestone 3 (opcional)")
