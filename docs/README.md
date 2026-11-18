# Documentacion de RIR-API

## Estructura

```
├── docs/
│   ├── m1/                        # Gráficos de validación de M1
│   │   ├── convolucion_sweep_filtro_inverso.png
│   │   ├── espectro_ruido_rosa.png
│   │   ├── espectrograma_sine_sweep.png
│   │   ├── prueba_auricular.png
│   │   ├── prueba_auricular_grabacion.wav
│   │   ├── prueba_auricular_ri.wav
│   │   ├── prueba_parlante.png
│   │   ├── prueba_parlante_grabacion.wav
│   │   └── prueba_parlante_ri.wav
│   ├── m2/                        # Gráficos de validación de M2
│   │   ├── README.md              # Resumen de la validación experimental
│   │   ├── decaimiento_bandas_octava.png
│   │   ├── ida_y_vuelta_sintetica_correlacion.png
│   │   ├── rir_corta_analisis.png
│   │   └── rir_larga_analisis.png
│   ├── m3/                        # Gráficos de validación de M3
│   │   ├── filtros_octava.png
│   │   ├── schroeder_regresiones.png
│   │   ├── validacion_rew.png
│   │   ├── ri_real.wav
│   │   ├── ri_sintetica.wav
│   │   ├── rew.csv
│   │   └── tabla_validacion.md
```

## API de referencia

Explorar la [documentacion interactiva de la API de la catedra](https://rir-api.onrender.com/docs)
para entender la estructura de endpoints, schemas y respuestas esperadas.

## Referencias utiles

- **ISO 3382-1:2009** — Acoustics — Measurement of room acoustic parameters.
- Farina, A. (2000). *Simultaneous measurement of impulse response and distortion
  with a swept-sine technique.*
- Schroeder, M. R. (1965). *New method of measuring reverberation time.*
  The Journal of the Acoustical Society of America.
- Lundeby, A. et al. (1995). *Uncertainties of measurements in room acoustics.*
  Acta Acustica.
- [FastAPI: documentacion oficial](https://fastapi.tiangolo.com/)
- [Pydantic: validacion de datos](https://docs.pydantic.dev/)

## Notas

Cada milestone deberia documentarse brevemente en este directorio, incluyendo:

1. Decisiones de diseno tomadas.
2. Resultados de validacion (graficos, tablas comparativas).
3. Problemas encontrados y como se resolvieron.
