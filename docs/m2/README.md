# Validación de la Milestone 2 (M2) — RIR-API

Este documento resume la validación experimental y las evidencias gráficas correspondientes a la **Milestone 2 (M2)** del proyecto `rir-api`.

---

## 1. Ida y Vuelta Sintética (Deconvolución Espectral)
Se validó el método de deconvolución en el dominio de la frecuencia (`get_impulse_response`) mediante la prueba completa de ida y vuelta:
1. Generación de una RI sintética ($T_{60} = 1.0\text{ s}$).
2. Convolución con un *sine sweep* logarítmico (3 segundos, 20 Hz – 20 kHz).
3. Deconvolución con el filtro inverso.
4. **Alineación de picos:** Se alinearon los picos máximos de la RI original y la recuperada previo al cálculo de correlación.

* **Resultado:** Coeficiente de correlación de Pearson entre la RI original alineada y la recuperada: **`0.99999`** (objetivo > 0.99).

![Ida y Vuelta Sintética](./ida_y_vuelta_sintetica_correlacion.png)

---

## 2. Filtrado por Bandas de Octava (IEC 61260)
Se implementó `filter_single_band` aplicando filtros Butterworth de orden 4 con `sosfiltfilt` para filtrado de fase cero en **7 bandas de octava** (125 Hz a 8 kHz).

---

## 3. Análisis de Respuestas al Impulso (RIRs Sintéticas Controladas)
Para la evaluación del comportamiento temporal, espectral y de decaimiento por octavas en esta etapa (M2), se utilizaron respuestas al impulso sintéticas generadas algorítmicamente (`generate_synthetic_ir`), lo que permite un control preciso y reproducible de los tiempos de reverberación objetivo ($T_{60}$):

### A. RIR Sintética Corta ($T_{60}$ de 0.6 s a 0.25 s según la banda — Recinto Pequeño / Estudio)
Respuesta al impulso representativa de un espacio con baja reverberación. Se evalúan 3 paneles:
1. **Forma de onda:** Decaimiento temporal rápido y limpio.
2. **Espectro de frecuencia:** Representado en escala logarítmica (20 Hz a 20 kHz).
3. **Decaimiento por bandas de octava:** Curvas de Schroeder diferenciadas trazadas para las 7 bandas estándar (125 Hz a 8 kHz).

![Análisis RIR Corta](./rir_corta_analisis.png)

### B. RIR Sintética Larga ($T_{60}$ de 2.6 s a 1.2 s según la banda — Sala Reverberante / Aula Magna)
Respuesta al impulso representativa de un espacio altamente reverberante:
1. **Forma de onda:** Envolvente de decaimiento prolongado.
2. **Espectro de frecuencia:** Representado en escala logarítmica (20 Hz a 20 kHz).
3. **Decaimiento por bandas de octava:** Integrales de Schroeder correspondientes a las 7 bandas de octava trazadas con decaimientos individuales visibles.

![Análisis RIR Larga](./rir_larga_analisis.png)
