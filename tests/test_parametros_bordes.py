"""Casos de borde de calculate_parameters_from_ir (Milestone 3)."""

import numpy as np
import pytest

from app.services.acoustic_parameters import calculate_parameters_from_ir


def _ir_con_ruido(t60: float, fs: int, duration: float, noise_db: float) -> np.ndarray:
    """RI exponencial con un piso de ruido blanco a ``noise_db`` dB."""
    rng = np.random.default_rng(1)
    t = np.arange(int(duration * fs)) / fs
    decay = rng.standard_normal(len(t)) * np.exp(-3 * np.log(10) / t60 * t)
    return decay + 10 ** (noise_db / 20) * rng.standard_normal(len(t))


@pytest.mark.parametrize("ir", [np.array([]), np.zeros(1000)])
def test_ir_vacia_o_ceros_da_error(ir):
    """Una RI vacia o toda ceros no se puede analizar."""
    with pytest.raises(ValueError):
        calculate_parameters_from_ir(ir, 44100)


def test_fs_sin_bandas_da_error():
    """Con fs = 200 Hz no entra ni la banda de 125 Hz (su corte superior es 177 Hz)."""
    with pytest.raises(ValueError):
        calculate_parameters_from_ir(np.ones(100), 200)


@pytest.mark.xfail(raises=NotImplementedError, strict=False, reason="falta Schroeder (M3)")
def test_bandas_por_encima_de_nyquist_se_omiten():
    """Con fs = 8000 Hz la banda de 4 kHz queda afuera (su corte es 5657 Hz)."""
    params = calculate_parameters_from_ir(_ir_con_ruido(0.5, 8000, 1.0, -80), 8000)
    assert sorted(params["T30"]) == [125.0, 250.0, 500.0, 1000.0, 2000.0]


@pytest.mark.xfail(raises=NotImplementedError, strict=False, reason="falta Schroeder (M3)")
def test_poco_rango_dinamico_devuelve_none():
    """Con el ruido a -30 dB no hay rango para T20 ni T30, pero si para EDT."""
    params = calculate_parameters_from_ir(_ir_con_ruido(1.2, 48000, 2.5, -30), 48000)
    assert all(v is None for v in params["T30"].values())
    assert all(v is None for v in params["T20"].values())
    assert all(v is not None for v in params["EDT"].values())


@pytest.mark.xfail(raises=NotImplementedError, strict=False, reason="falta Schroeder (M3)")
def test_ruido_moderado_no_infla_t30():
    """Con el ruido a -60 dB, T30 sigue dentro de +-10 % del T60 real."""
    t60 = 1.2
    params = calculate_parameters_from_ir(_ir_con_ruido(t60, 48000, 2.5, -60), 48000)
    for fc, t30 in params["T30"].items():
        assert abs(t30 - t60) <= 0.1 * t60, f"T30({fc:.0f} Hz) = {t30:.2f} s"
