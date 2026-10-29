# AI_LOG

Registro del uso de herramientas de IA durante el desarrollo de RIR-API.
Cada integrante agrega sus propias entradas.

---

## 2026-10-01 · Leonardo Valle · Claude (claude.ai)

**Contexto:** Configuración del entorno y apertura de los notebooks de clase.

**Qué pregunté:** Por qué me daba `ModuleNotFoundError: No module named 'marimo'` al
abrir `clase_01/contenido.py`, si tenía marimo instalado.

**Qué obtuve:** La explicación de que el botón Run de VSCode ejecuta el archivo con el
Python general, donde marimo no está instalado, porque lo instalé como herramienta
aislada con `uv tool install`. Los notebooks se abren con `marimo edit`.

**Qué aprendí:** La diferencia entre una herramienta instalada con `uv tool` y una
librería del entorno de Python, y qué es el sandbox de marimo (un entorno aislado con
las dependencias que declara cada notebook).

**Verificación:** El notebook abrió correctamente con `marimo edit`.

---

## 2026-10-02 · Leonardo Valle · Claude (claude.ai)

**Contexto:** M0, creación del repositorio del grupo.

**Qué pregunté:** Cómo crear el repo del grupo a partir del template, subirlo a GitHub
y verificar que la API funcione.

**Qué obtuve:** Los pasos para inicializar Git, conectar con GitHub y subir el template;
cómo correr `uv sync`, levantar la API y los tests.

**Qué aprendí:** La diferencia entre Git y GitHub, para qué sirve `uv.lock`, por qué hay
que revisar que se copien los archivos ocultos (`.github/`, `.gitignore`) y que los tests
"xfailed" son los de milestones futuros, no errores.

**Error / limitación:** Cuando `localhost:8000/health` no respondía, la IA primero supuso
que el servidor no había terminado de arrancar. El problema real era la dirección:
funcionó con `127.0.0.1:8000`.

**Verificación:** `/health` respondió con `"status": "healthy"` y `pytest` dio
6 passed y 44 xfailed.

---

## 2026-10-07 · Leonardo Valle · Claude (claude.ai)

**Contexto:** M0, organización del trabajo en grupo.

**Qué pregunté:** Qué son el CI, los endpoints, los issues, los labels y la branching
strategy; cómo se coordina el trabajo en paralelo; y una propuesta de reparto de roles
e issues según el nivel de Python de cada integrante.

**Qué obtuve:** Explicaciones con ejemplos (el flujo rama → pull request → CI → merge),
la configuración para proteger `main` y una primera propuesta de roles.

**Qué aprendí:** Por qué los stubs del template permiten trabajar en paralelo (la firma
de cada función ya está acordada) y cómo el CI evita que entre código roto a `main`.

**Decisión propia:** La primera propuesta me dejaba con 8 de los 16 issues. Pedí una
distribución más pareja y elegí la segunda.

**Verificación:** El check `lint-and-test` quedó como requisito en la regla de protección
de `main`.

---

## 2026-10-07 · Leonardo Valle · Claude (claude.ai)

**Contexto:** M0 y diagrama de arquitectura.

**Qué pregunté:** Cómo armar el diagrama de arquitectura.

**Qué obtuve:** Un diagrama en Mermaid con las capas
routers → schemas → services y los módulos de M1 a M3.

**Qué aprendí:** Cómo se organiza la API en capas y qué endpoint de cada milestone llama
a qué función.

**Verificación:** Revisé el diagrama renderizado en GitHub antes de hacer merge del PR.

---

## 2026-10-07 · Leonardo Valle · Claude (claude.ai)

**Contexto:** M0, revisión del diagrama de arquitectura.

**Qué pregunté:** Si la flecha "llama a" debía salir de los schemas, ya que solo se
llama al service si la validación pasa; y si faltaba detalle en la caja de schemas.

**Qué obtuve:** La explicación de que los schemas no ejecutan nada: FastAPI valida
contra ellos y, si falla, responde 422 sin llegar al router. El que llama al service
es el router. Además, una propuesta para detallar los schemas por archivo.

**Qué aprendí:** El diagrama muestra quién usa a quién, no un paso a paso en el tiempo.

**Decisión propia:** Detecté que la caja de schemas tenía menos detalle que el resto y
pedí completarla; agregué también la etiqueta del error 422 y la dependencia del filtro inverso.

---

## 2026-10-24 · Marcelo Flores · Gemini Notebook 

**Contexto:** Issue #2 - Implementación de generate_sine_sweep_pair. 

**Qué pregunté:** Cómo implementar la generación de sine sweep logarítmico y su filtro inverso según Farina (2000).

**Qué obtuve:** Explicación matemática y código en NumPy con inversión temporal, envolvente de -6 dB/octava y normalización al pico. 

**Qué aprendí:** Que A(t) atenúa los graves al multiplicar por la exponencial decreciente para compensar la densidad espectral del sweep. 

**Verificación:** `uv run pytest -v tests/test\_generacion.py -k "sine\_sweep"\` resultando en 3 tests pasados (XPASS).

## 2026-10-27 · Marcelo · Gemini Notebook 
**Contexto:** Issue #5 - Gráficas de validación de M1 y creación del script `generar_graficas.py`. 

**Qué pregunté:** Asistencia para escribir y depurar el script `generar_graficas.py` que genera las imágenes de validación de M1 (espectro del ruido rosa, espectrograma de sine sweep y la convolución con el filtro inverso). 

**Qué obtuve:** El código completo del script de generación y resolución paso a paso de errores de sintaxis (coma en `np.polyval`, corrección de `spectrogram` y parámetros de `plt.grid`).

**Qué aprendí:** A corregir errores de sintaxis/linter en Matplotlib/SciPy y la importancia de verificar que el archivo esté guardado correctamente antes de ejecutar con `uv run`.

**Verificación:** Ejecución exitosa con `uv run python generar_graficas.py`, comprobando la creación de `docs/m1/espectrograma_sine_sweep.png` y `docs/m1/convolucion_sweep_filtro_inverso.png`.

---

## 2026-10-27 · Matías Archelli · Microsoft Copilot

**Contexto:** Issue #1 - Implementar `generate_pink_noise`

**Qué pregunté:** Cómo aplicar un filtro a un ruido blanco para generar un ruido rosa

**Qué obtuve:** Se recomendó usar las funciones de numpy para la transformada rápida de Fourier y la transformada rápida inversa para generar el ruido rosa.

**Qué aprendí:** Cómo utilizar estas funciones así como su objetivo de transformar la señal en frecuencia para realizar el filtro y luego obtener nuevamente la señal temporal.

**Verificación:** Comprobación con Microsoft Copilot del código hasta el momento

---

## 2026-10-27 · Matías Archelli · Microsoft Copilot

**Contexto:** Issue #1 - Implementar `generate_pink_noise`

**Qué pregunté:** El código realizado es correcto para generar ruido rosa

**Qué obtuve:** Recomendación de generar un array de ceros para evitar a división por 0.

**Qué aprendí:** Aprendí una nueva técnica para evitar inconvenientes con la frecuencia de 0 Hz. Se genera un array de ceros del tamaño de la muestra para luego realizar un slicing de [1:] (dejando el primer valor como 0) de forma que no se realiza una division por 0 al realizar el filtro y luego solo se realiza una multiplicación por 0 cuando se aplica el filtro al espectro de ruido blanco.

**Verificación:** Pasó los tests para la funcion `generate_pink_noise` de `tests/generacion.py` (XPASS)

---

## 2026-10-28 · Leonardo Valle · Claude (claude.ai)

**Contexto:** Issue #3, implementacion de `play_and_record`.

**Qué pregunté:** Primero, una guia paso a paso para implementarla yo y chequeo del código por errores de sintaxis.

**Qué obtuve:** La implementacion completa: relleno con ceros para grabar la cola de
reverberacion, `sd.playrec` + `sd.wait`, y conversion de `PortAudioError` a `RuntimeError`.

**Qué aprendí:** Que `playrec` graba tantas muestras como reproduce (por eso se agrega
silencio al final), como funciona `np.pad` en 1D y 2D, y por que el import de
sounddevice va dentro de la funcion (para que el test pueda reemplazarlo por un mock).

**Verificación:** El test `test_play_and_record_shape` pasa (XPASS) y ruff no marca errores.

---

## 2026-10-28 · Leonardo Valle · Claude (claude.ai)

**Contexto:** Issue #4, endpoints de M1 (pink-noise y sine-sweep).

**Qué pregunté:** Como implementar los endpoints a partir de los tests de `tests/test_api.py`,
el router de ejemplo (`health.py`), `audio_http.py` y los services de mis compañeros.

**Qué obtuve:** El codigo de los schemas (`app/schemas/signals.py`), del router
(`app/routers/signals.py`) y el registro en `app/main.py`, con la explicacion de cada parte.

**Qué aprendí:** Que los tests definen el contrato de cada endpoint (nombres de los campos y
respuestas esperadas), que la validacion la hace FastAPI con el schema antes de llegar al
router (por eso una duracion negativa da 422 sin ejecutar codigo), y por que conviene
limitar `end_freq` a la frecuencia de Nyquist.

**Verificación:** Probe los endpoints a mano en `/docs` (200 con WAV descargable, y 422
con duracion negativa). Los tres tests de M1 en `test_api.py` pasan sin la marca xfail.