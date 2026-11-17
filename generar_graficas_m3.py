"""Graficas y tabla de validacion de M3 (issue #15).

Genera en ``docs/m3/``:

- ``ri_sintetica.wav``: RI sintetica con T60 conocidos, para medirla tambien en REW.
- ``schroeder_regresiones.png``: grafica 1, curva de Schroeder con las rectas
  de EDT, T20 y T30 (banda de 1 kHz de la RI real).
- ``filtros_octava.png``: grafica 2, respuesta en frecuencia de los filtros de octava.
- ``rew.csv``: planilla para completar con los valores de REW (se crea si no existe).
- ``validacion_rew.png`` y ``tabla_validacion.md``: grafica 3 y tabla comparativa,
  solo cuando ``rew.csv`` ya tiene los valores de REW.

Uso (desde la raiz del repositorio)::

    uv run python generar_graficas_m3.py

Para elegir la RI real, ``--ranking CARPETA`` lista los WAV de una carpeta
ordenados por su T30 en 1 kHz (de mayor a menor)::

    uv run python generar_graficas_m3.py --ranking ruta/a/Audio
"""

import csv
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf

from app.services.acoustic_parameters import (
    DECAY_RANGES,
    OCTAVE_BANDS,
    PRE_PADDING_S,
    _energy_envelope,
    _noise_floor,
    _truncation_index,
    apply_schroeder_integral,
    calculate_parameters_from_ir,
    linear_regression,
)
from app.services.filter import filter_single_band
from app.services.signal_utils import generate_synthetic_ir, load_audio

CARPETA = Path("docs/m3")
RI_REAL = CARPETA / "ri_real.wav"
RI_SINTETICA = CARPETA / "ri_sintetica.wav"
REW_CSV = CARPETA / "rew.csv"

FS_SINTETICA = 44100
T60_SINTETICA = {125: 1.8, 250: 1.6, 500: 1.4, 1000: 1.2, 2000: 1.0, 4000: 0.8}
PARAMETROS = ("EDT", "T20", "T30", "C80")
BANDA_GRAFICA_1 = 1000
NOMBRES = {"sintetica": "sintética", "real": "real"}


def tolerancia(parametro: str, referencia: float) -> float:
    """Tolerancia del criterio de aceptacion: +-10 % (tope 0,5 s) o +-1 dB en C80."""
    if parametro == "C80":
        return 1.0
    return min(0.1 * abs(referencia), 0.5)


def preparar_ris() -> dict[str, tuple[np.ndarray, int]]:
    """Genera la RI sintetica (si falta) y carga las RI que existan."""
    CARPETA.mkdir(parents=True, exist_ok=True)
    if not RI_SINTETICA.exists():
        ir = generate_synthetic_ir(3.0, T60_SINTETICA, FS_SINTETICA)
        sf.write(RI_SINTETICA, ir, FS_SINTETICA, subtype="PCM_24")
        print(f"Generada {RI_SINTETICA}")
    ris = {"sintetica": load_audio(RI_SINTETICA)}
    if RI_REAL.exists():
        ris["real"] = load_audio(RI_REAL)
    else:
        print(f"AVISO: falta {RI_REAL}. Las graficas usan solo la RI sintetica.")
    return ris


def grafica_schroeder(ir: np.ndarray, fs: int, nombre_ri: str) -> None:
    """Grafica 1: curva de Schroeder de una banda con las rectas de cada tiempo."""
    padded = np.concatenate([np.zeros(int(PRE_PADDING_S * fs)), ir])
    banda = filter_single_band(padded, fs, BANDA_GRAFICA_1)
    envolvente = _energy_envelope(banda, fs)
    fin = _truncation_index(envolvente, _noise_floor(envolvente))
    edc_db = apply_schroeder_integral(banda[:fin])
    t = np.arange(len(edc_db)) / fs

    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.plot(t, edc_db, color="black", linewidth=2, label="Curva de Schroeder")
    colores = {"EDT": "tab:orange", "T20": "tab:green", "T30": "tab:blue"}
    for nombre, color in colores.items():
        inicio_db, fin_db = DECAY_RANGES[nombre]
        tramo = (edc_db <= inicio_db) & (edc_db >= fin_db)
        if np.count_nonzero(tramo) < 2:
            continue
        pendiente, ordenada, r2 = linear_regression(t[tramo], edc_db[tramo])
        t_recta = np.array([0.0, (-65 - ordenada) / pendiente])
        ax.plot(
            t_recta,
            pendiente * t_recta + ordenada,
            "--",
            color=color,
            label=f"{nombre}: tramo {inicio_db:g} a {fin_db:g} dB, "
            f"T = {-60 / pendiente:.2f} s (R² = {r2:.3f})",
        )
        ax.axhspan(fin_db, inicio_db, color=color, alpha=0.06)
    ax.set_xlim(0, t[-1])
    ax.set_ylim(-70, 3)
    ax.set_xlabel("Tiempo [s]")
    ax.set_ylabel("Nivel [dB]")
    ax.set_title(
        f"Curva de Schroeder y regresiones · RI {NOMBRES[nombre_ri]}, banda de {BANDA_GRAFICA_1} Hz"
    )
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(CARPETA / "schroeder_regresiones.png", dpi=150)
    plt.close(fig)
    print(f"Guardada {CARPETA / 'schroeder_regresiones.png'}")


def grafica_filtros(fs: int = 48000) -> None:
    """Grafica 2: respuesta en frecuencia de los filtros de octava.

    Se filtra un impulso centrado (``sosfiltfilt`` no es causal) y se toma su FFT,
    asi la grafica muestra el filtro tal como lo aplica ``filter_single_band``.
    """
    n = 2**16
    impulso = np.zeros(n)
    impulso[n // 2] = 1.0
    f = np.fft.rfftfreq(n, 1 / fs)

    fig, ax = plt.subplots(figsize=(10, 5))
    for fc in OCTAVE_BANDS:
        respuesta = np.abs(np.fft.rfft(filter_single_band(impulso, fs, fc)))
        ax.semilogx(f[1:], 20 * np.log10(respuesta[1:] + 1e-12), label=f"{fc} Hz")
    ax.axhline(-6, color="gray", linestyle=":", label="-6 dB (cortes fc/√2 y fc·√2)")
    ax.set_xlim(50, 10000)
    ax.set_ylim(-60, 5)
    ax.set_xlabel("Frecuencia [Hz]")
    ax.set_ylabel("Magnitud [dB]")
    ax.set_title("Filtros de octava: Butterworth orden 4 con sosfiltfilt (fase cero)")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(loc="lower center", ncol=4)
    fig.tight_layout()
    fig.savefig(CARPETA / "filtros_octava.png", dpi=150)
    plt.close(fig)
    print(f"Guardada {CARPETA / 'filtros_octava.png'}")


def leer_o_crear_csv(resultados: dict[str, dict]) -> list[dict]:
    """Crea la planilla de REW con los valores de RIR-API, o la lee si ya existe."""
    if not REW_CSV.exists():
        with REW_CSV.open("w", newline="", encoding="utf-8") as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow(["ri", "parametro", "banda_hz", "rew"])
            for nombre_ri in resultados:
                for parametro in PARAMETROS:
                    for fc in OCTAVE_BANDS:
                        escritor.writerow([nombre_ri, parametro, fc, ""])
        print(f"Creada {REW_CSV}: completar la columna 'rew' con los valores de REW.")
        return []
    with REW_CSV.open(encoding="utf-8") as archivo:
        return [fila for fila in csv.DictReader(archivo) if fila["rew"].strip()]


def tabla_y_grafica_validacion(resultados: dict[str, dict], filas_rew: list[dict]) -> None:
    """Grafica 3 y tabla comparativa contra REW."""
    lineas = [
        "| RI | Parámetro | Banda (Hz) | RIR-API | REW | Diferencia | Tolerancia | Dentro |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    rew: dict[str, dict[str, dict[float, float]]] = {}
    dentro_total = 0
    for fila in filas_rew:
        nombre_ri, parametro = fila["ri"], fila["parametro"]
        fc, valor_rew = float(fila["banda_hz"]), float(fila["rew"].replace(",", "."))
        rew.setdefault(nombre_ri, {}).setdefault(parametro, {})[fc] = valor_rew
        valor_api = resultados.get(nombre_ri, {}).get(parametro, {}).get(fc)
        unidad = "dB" if parametro == "C80" else "s"
        if valor_api is None:
            lineas.append(
                f"| {nombre_ri} | {parametro} | {fc:g} | sin rango | "
                f"{valor_rew:.2f} {unidad} | - | - | - |"
            )
            continue
        diferencia = valor_api - valor_rew
        tol = tolerancia(parametro, valor_rew)
        dentro = abs(diferencia) <= tol
        dentro_total += dentro
        lineas.append(
            f"| {nombre_ri} | {parametro} | {fc:g} | {valor_api:.2f} {unidad} | "
            f"{valor_rew:.2f} {unidad} | {diferencia:+.2f} {unidad} | "
            f"±{tol:.2f} {unidad} | {'sí' if dentro else 'no'} |"
        )
    (CARPETA / "tabla_validacion.md").write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print(f"Guardada {CARPETA / 'tabla_validacion.md'} ({dentro_total} de {len(filas_rew)} dentro)")

    nombres = [nombre for nombre in resultados if "T30" in rew.get(nombre, {})]
    if not nombres:
        print("AVISO: rew.csv no tiene valores de T30; no se genera la grafica 3.")
        return
    fig, axes = plt.subplots(1, len(nombres), figsize=(6 * len(nombres), 4.8), squeeze=False)
    for ax, nombre_ri in zip(axes[0], nombres, strict=True):
        bandas = sorted(rew[nombre_ri]["T30"])
        x = np.arange(len(bandas))
        ref = np.array([rew[nombre_ri]["T30"][fc] for fc in bandas])
        tol = np.array([tolerancia("T30", r) for r in ref])
        api = [resultados[nombre_ri]["T30"].get(fc) for fc in bandas]
        api = np.array([np.nan if v is None else v for v in api])
        ax.fill_between(
            x, ref - tol, ref + tol, color="tab:gray", alpha=0.2, label="Tolerancia ±10 %"
        )
        ax.plot(x, ref, "s-", color="tab:gray", label="REW")
        ax.plot(x, api, "o--", color="tab:blue", label="RIR-API")
        if nombre_ri == "sintetica":
            pedido = [T60_SINTETICA.get(int(fc), np.nan) for fc in bandas]
            ax.plot(x, pedido, "x", color="black", label="T60 pedido")
        ax.set_xticks(x, [f"{fc:g}" for fc in bandas])
        ax.set_xlabel("Banda de octava [Hz]")
        ax.set_ylabel("T30 [s]")
        ax.set_title(f"T30 por banda · RI {NOMBRES[nombre_ri]}")
        ax.grid(True, alpha=0.3)
        ax.legend()
    fig.suptitle("Validación: RIR-API contra REW")
    fig.tight_layout()
    fig.savefig(CARPETA / "validacion_rew.png", dpi=150)
    plt.close(fig)
    print(f"Guardada {CARPETA / 'validacion_rew.png'}")


def ranking(carpeta: Path) -> None:
    """Lista los WAV de una carpeta ordenados por T30 en 1 kHz, para elegir la RI real."""
    filas = []
    for ruta in sorted(carpeta.glob("*.wav")):
        try:
            ir, fs = load_audio(ruta)
            params = calculate_parameters_from_ir(ir, fs)
        except ValueError as error:
            print(f"  salteado {ruta.name}: {error}")
            continue
        filas.append((params["T30"].get(1000.0), params["EDT"].get(1000.0), fs, ruta.name))
    filas.sort(key=lambda fila: -1 if fila[0] is None else fila[0], reverse=True)
    print(f"{'T30 1k':>7} {'EDT 1k':>7} {'fs':>6}  archivo")
    for t30, edt, fs, nombre in filas:
        t30_txt = "-" if t30 is None else f"{t30:.2f}"
        edt_txt = "-" if edt is None else f"{edt:.2f}"
        print(f"{t30_txt:>7} {edt_txt:>7} {fs:>6}  {nombre}")


def main() -> None:
    if len(sys.argv) == 3 and sys.argv[1] == "--ranking":
        ranking(Path(sys.argv[2]))
        return
    ris = preparar_ris()
    resultados = {nombre: calculate_parameters_from_ir(ir, fs) for nombre, (ir, fs) in ris.items()}

    print("\nValores de RIR-API:")
    for nombre_ri, params in resultados.items():
        print(f"  RI {nombre_ri}:")
        for parametro in PARAMETROS:
            valores = "  ".join(
                f"{fc:g}: {'-' if v is None else f'{v:.2f}'}" for fc, v in params[parametro].items()
            )
            print(f"    {parametro:4s} {valores}")
    print()

    nombre_g1 = "real" if "real" in ris else "sintetica"
    grafica_schroeder(*ris[nombre_g1], nombre_g1)
    grafica_filtros()
    filas_rew = leer_o_crear_csv(resultados)
    if filas_rew:
        tabla_y_grafica_validacion(resultados, filas_rew)


if __name__ == "__main__":
    main()
