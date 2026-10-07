# RIR-API

API REST para procesamiento y analisis de respuestas al impulso segun la norma ISO 3382.

![CI](https://github.com/leonardofvalle/rir-api/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.12+-blue.svg)

## Descripcion

RIR-API es el trabajo practico de Senales y Sistemas (UNTREF, 2C 2026): una API REST
(FastAPI) con la cadena completa de procesamiento acustico, desde la generacion de senales
de excitacion hasta el calculo de parametros acusticos (EDT, T20, T30, D50, C80) segun
ISO 3382-1.

- Consigna, especificaciones y ruta del TP: <https://maxiyommi.github.io/signal-systems/trabajo_practico/ruta/>
- API de referencia de la catedra (Swagger UI): <https://rir-api.onrender.com/docs>

> Este README es un punto de partida: el grupo lo completa en M0 (integrantes, roles,
> diagrama de arquitectura, branching strategy) y lo va actualizando hasta M3 (seccion
> "Validacion" con los resultados).

## Integrantes

| Nombre | Legajo | Rol |
|--------|--------|-----|
| Leonardo Valle | 76106 | Integración, API, adquisición de audio y cálculo de parámetros |
| Matías Archelli | 70479 | Ruido rosa, filtrado y curva de decaimiento; registro de IA |
| Marcelo Flores | 50004 | Sine sweep, respuesta al impulso y validación |

## Requisitos previos

- Python 3.12 o superior
- [uv](https://docs.astral.sh/uv/) (gestor de paquetes y entornos virtuales)
- git y una cuenta de GitHub

## Arranque: 
Clonar el repositorio e instalar (ver "Instalacion y ejecucion"):

    git clone https://github.com/leonardofvalle/rir-api.git
    cd rir-api

## Instalacion y ejecucion

```bash
# Crear el entorno e instalar dependencias (incluye las de desarrollo: pytest, ruff, ...)
uv sync

# Iniciar la API con hot-reload
uv run uvicorn app.main:app --reload

# Correr los tests
uv run pytest
```

La API queda disponible en `http://localhost:8000`. Documentacion interactiva:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

`uv sync` genera un `uv.lock` con las versiones exactas instaladas: **commitéenlo** en el
repositorio del grupo para que todos (y el CI) usen las mismas versiones.

## Estructura del proyecto

```
rir-api/
├── app/
│   ├── __init__.py
│   ├── main.py                    # Punto de entrada FastAPI (/ y /health)
│   ├── settings.py                # Configuracion (pydantic-settings, variables RIR_*)
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── health.py              # GET /health (M0)
│   │   └── audio_http.py          # wav_response y uploaded_file (ya resueltas)
│   ├── schemas/
│   │   └── __init__.py            # Modelos Pydantic de request/response (desde M1)
│   └── services/
│       ├── __init__.py
│       ├── pink_noise.py          # generate_pink_noise (M1)
│       ├── sine_sweep.py          # generate_sine_sweep_pair (M1)
│       ├── audio_io.py            # play_and_record (M1)
│       ├── signal_utils.py        # load_audio, generate_synthetic_ir, get_impulse_response,
│       │                          # logarithmic_scale_conversion (M2)
│       ├── filter.py              # filter_single_band (M2)
│       └── acoustic_parameters.py # apply_smoothing, apply_schroeder_integral, linear_regression,
│                                  # calculate_parameters_from_ir, apply_lundeby (M3)
├── tests/
│   ├── data/                      # WAV chicos de prueba (se versionan)
│   ├── test_placeholder.py        # Test trivial (M0)
│   ├── test_generacion.py         # Tests de M1
│   ├── test_procesamiento.py      # Tests de M2
│   ├── test_analisis.py           # Tests de M3 (services)
│   └── test_api.py                # Tests de endpoints, por milestone (M0 a M3)
├── data/                          # Mediciones y audios locales (ignorado por git)
├── docs/
│   └── README.md                  # Guia para la documentacion (graficas de validacion, etc.)
├── .github/workflows/ci.yml       # CI: ruff + pytest en cada push/PR
├── .gitignore
├── pyproject.toml                 # Dependencias y configuracion (ruff, pytest)
└── README.md
```

Cada milestone expone lo que construye: los routers y schemas de `signals` se agregan en M1
(y suman `synthetic-ir` en M2), los de `filters` en M2 y los de `acoustics` y `utils` en M3
(ver los `TODO` en `app/main.py`).

## Arquitectura

La API se organiza en tres capas: los **routers** reciben los pedidos HTTP, los
**schemas** (Pydantic) validan los datos de entrada y salida, y los **services**
hacen el procesamiento de señales.

```mermaid
flowchart TB
    Cliente["Cliente<br/>(Swagger UI /docs, scripts)"]

    subgraph API["app/main.py · FastAPI"]
        direction TB
        subgraph R["routers/"]
            Rh["health.py<br/>GET /health (M0)"]
            Rs["signals<br/>POST /signals/pink-noise · /signals/sine-sweep (M1)<br/>POST /signals/synthetic-ir (M2)"]
            Rf["filters<br/>POST /filters/single-band (M2)"]
            Ra["acoustics<br/>POST /acoustics/parameters (M3)"]
            Ru["utils<br/>POST /utils/schroeder · /utils/smoothing (M3)"]
            Rio["audio_http.py<br/>wav_response · uploaded_file"]
        end

        S["schemas/ (Pydantic)<br/>validacion de requests y responses"]

        subgraph SV["services/"]
            pn["pink_noise.py<br/>generate_pink_noise (M1)"]
            ss["sine_sweep.py<br/>generate_sine_sweep_pair (M1)"]
            io["audio_io.py<br/>play_and_record (M1)"]
            su["signal_utils.py<br/>load_audio · generate_synthetic_ir<br/>get_impulse_response · logarithmic_scale_conversion (M2)"]
            fi["filter.py<br/>filter_single_band (M2)"]
            ap["acoustic_parameters.py<br/>apply_smoothing · apply_schroeder_integral<br/>linear_regression · calculate_parameters_from_ir (M3)"]
        end
    end

    Cliente -->|"request HTTP"| R
    R -->|"valida con"| S
    R -->|"llama a"| SV
    SV -->|"resultado (WAV o JSON)"| R
    R -->|"response"| Cliente

    ap -.->|"usa"| fi
    ap -.->|"usa"| su
```

**Flujo de un pedido:** el cliente envía un request → el router lo recibe → Pydantic
valida los parámetros (si son inválidos responde con error 422) → el router llama al
service correspondiente → el resultado vuelve al cliente como WAV o JSON.

## Branching strategy

- **`main` protegida**: solo se modifica mediante pull request, con el CI
  (`lint-and-test`: ruff + pytest) en verde. No se permite push directo ni force push.
- **Ramas de trabajo**: una por tarea, creadas desde `main` actualizada:
  `feature/descripcion` para funcionalidades, `fix/descripcion` para correcciones y
  `docs/descripcion` para documentación (por ejemplo `feature/pink-noise`).
- **Commits**: siguiendo [Conventional Commits](https://www.conventionalcommits.org/):
  `feat:` funcionalidad nueva, `fix:` corrección, `docs:` documentación,
  `test:` tests, `refactor:` reorganización sin cambiar comportamiento, `chore:` mantenimiento.
- **Pull requests**: cada PR referencia su issue (por ejemplo "Closes #3") y lo revisa
  otro integrante antes del merge.
- **Entregas**: cada milestone se marca con un tag anotado en `main`
  (`v0.1.0`, `v0.2.0`, `v1.0.0`).

## Milestones y entregas (2C 2026)

| Milestone | Entrega | Tag | Evaluacion |
|-----------|---------|-----|------------|
| **M0 · El plano** (arquitectura) | mie 7/10 (asincronica, por Slack/GitHub) | — | Seguimiento, sin nota |
| **M1 · Generacion de senales** | mie 28/10 (en clase) | `v0.1.0` | Seguimiento, sin nota |
| **M2 · Procesamiento de la RI** | mie 4/11 | `v0.2.0` | Seguimiento, sin nota |
| **M3 · Producto final** + presentacion oral | mie 18/11 | `v1.0.0` | **Nota del TP: 60 % M3 + 40 % oral** |

- No hay informe escrito: la validacion de resultados va en una seccion **"Validacion"** de
  este README.
- **`AI_LOG.md`** en la raiz del repositorio es **obligatorio** (sin nota propia, pero sin
  `AI_LOG.md` M3 no se considera completo): registren el uso de herramientas de IA durante
  todo el proyecto.
- Detalle de cada milestone: <https://maxiyommi.github.io/signal-systems/trabajo_practico/ruta/>

### M0 · El plano

- [X] Repositorio del grupo creado a partir del template, con los docentes como colaboradores.
- [X] `uv sync`, `uv run uvicorn app.main:app --reload` y `uv run pytest` funcionan.
- [X] README con integrantes y roles, instalacion, estructura y branching strategy.
- [X] Diagrama de arquitectura (Mermaid o draw.io) con todos los modulos de M1, M2 y M3.
- [X] Al menos 10 issues con labels (`milestone-1`, `milestone-2`, `milestone-3`) y asignados.

### M1 · Generacion de senales (`v0.1.0`)

- [ ] `generate_pink_noise()` en `app/services/pink_noise.py` (Voss-McCartney recomendado).
- [ ] `generate_sine_sweep_pair()` (sweep + filtro inverso) en `app/services/sine_sweep.py`.
- [ ] `play_and_record()` en `app/services/audio_io.py`.
- [ ] Endpoints `POST /api/v1/signals/pink-noise` y `POST /api/v1/signals/sine-sweep` (devuelven WAV),
      con sus schemas en `app/schemas/signals.py`.
- [ ] Tests de `tests/test_generacion.py` y los de M1 en `tests/test_api.py` pasando;
      graficas de validacion en `docs/m1/`.

### M2 · Procesamiento de la RI (`v0.2.0`)

- [ ] `load_audio()`, `generate_synthetic_ir()`, `get_impulse_response()` y
      `logarithmic_scale_conversion()` en `app/services/signal_utils.py`.
- [ ] `filter_single_band()` en `app/services/filter.py`.
- [ ] Endpoints `POST /api/v1/signals/synthetic-ir` y `POST /api/v1/filters/single-band`
      (recibe un WAV subido).
- [ ] Tests de `tests/test_procesamiento.py` y los de M2 en `tests/test_api.py` pasando.

### M3 · Producto final (`v1.0.0`)

- [ ] `apply_smoothing()`, `apply_schroeder_integral()`, `linear_regression()` y
      `calculate_parameters_from_ir()` en `app/services/acoustic_parameters.py`.
- [ ] Endpoints `POST /api/v1/acoustics/parameters`, `POST /api/v1/utils/schroeder` y
      `POST /api/v1/utils/smoothing`: la API completa.
- [ ] Tests de `tests/test_analisis.py` y todos los de `tests/test_api.py` pasando.
- [ ] Seccion "Validacion" en este README, `AI_LOG.md` y presentacion oral.
- [ ] (Opcional) `apply_lundeby()`.

## Tests

Las funciones de `app/services/` vienen como *stubs* que lanzan `NotImplementedError`. Sus
tests estan marcados como `xfail` (fallo esperado), asi el CI queda en verde desde el
primer dia:

- Mientras la funcion no este implementada, el test aparece como `x` (xfailed).
- Cuando la implementen bien, aparece como `X` (xpassed). En ese momento conviene **borrar
  la marca `xfail`** del modulo de tests (`pytestmark = ...`) para que el test cuente como
  un test normal. En `tests/test_api.py` la marca va test por test (`@xfail_m1`,
  `@xfail_m2`, `@xfail_m3`): borren la de cada endpoint que implementen.
- Si la implementacion es incorrecta, el test **falla** (rojo) con el `AssertionError`.

```bash
uv run pytest                                  # todos los tests
uv run pytest -v tests/test_generacion.py      # un archivo, con detalle
uv run pytest -v -k pink_noise                 # tests cuyo nombre contiene "pink_noise"
uv run pytest -rxX                             # listar xfailed / xpassed
uv run pytest --cov=app                        # con cobertura
```

`play_and_record` se testea con un *mock* de `sounddevice`, por lo que el CI no necesita
placa de audio. Para probarla de verdad, corran la funcion localmente con un parlante y un
microfono y documenten la configuracion (dispositivo, canales, fs, buffer size).

## Linter y formato

```bash
uv run ruff check app/ tests/          # verificar estilo
uv run ruff check --fix app/ tests/    # corregir lo automatico
uv run ruff format app/ tests/         # formatear
```

El CI (`.github/workflows/ci.yml`) corre `ruff check`, `ruff format --check` y
`pytest --cov=app` en cada push a `main` y en cada pull request.

## Configuracion

`app/settings.py` define la configuracion con `pydantic-settings`. Cualquier valor se puede
sobreescribir con variables de entorno con prefijo `RIR_` (por ejemplo `RIR_FS_DEFAULT=44100`)
o con un archivo `.env` en la raiz (ignorado por git).

## Referencias

- ISO 3382-1:2009 — Acoustics — Measurement of room acoustic parameters.
- Farina, A. (2000). *Simultaneous measurement of impulse response and distortion with a
  swept-sine technique.* 108th AES Convention.
- Schroeder, M. R. (1965). *New method of measuring reverberation time.* JASA 37(3).
- [FastAPI](https://fastapi.tiangolo.com/) · [Pydantic](https://docs.pydantic.dev/) ·
  [uv](https://docs.astral.sh/uv/)
