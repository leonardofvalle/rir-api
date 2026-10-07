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