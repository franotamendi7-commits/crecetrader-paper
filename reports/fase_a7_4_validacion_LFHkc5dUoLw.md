# FASE A.7.4 — Validación visual y temporal de LFHkc5dUoLw

Fecha: 2026-11-15
Video: `LFHkc5dUoLw` — "Bitcoin: la señal que hacía desconfiar del rebote" (publicado 2026-10-29T18:37:26+00:00)
Duración: 802,6 s (13:22) | Frames en disco: 20 (`frame_3994.jpg` … `frame_4013.jpg`) | Transcripción: 622 cues
Visión: 20/20 frames con resultado no vacío (`qwen2.5vl:3b` vía Ollama local)
Validación visual directa: 3 de 20 frames inspeccionados con visión real (3994, 4000, 4006). `frame_4013` no se pudo inspeccionar (429 del proveedor auxiliar de visión).

## Veredicto

`validation = false`. El procesamiento (descarga/frames/transcripción/visión) está completo, pero la validación visual/temporal **no es satisfactoria**: existen discrepancias concretas entre lo reportado por el modelo de visión y el contenido real de los gráficos, y no existe mapeo temporal que permita contrastar cada frame con su instante de transcripción.

## Evidencias que sí se verifican

| # | Comprobación | Resultado | Evidencia |
|---|---|---|---|
| 1 | Instrumento | **VERIFICADO** | Los 3 frames inspeccionados son `BTCUSD` (Coinbase / "Bolsa estadounidense"), marca de agua "BTCUSD, 1D" |
| 2 | Temporalidad | **VERIFICADO** | Velas diarias (1D) en los 3 frames inspeccionados |
| 3 | Niveles clave citados verbalmente | **PARCIAL** | 87.496 (frame_3994), 81.444≈81.446 (frame_4006), 78.748≈78.746 (frame_4006) visibles; 83.366 / 84.455 citados no coinciden con las etiquetas observadas (83.933 / 83.953) |
| 4 | Estructura | **VERIFICADO** | Máximo ~87–88k, corrección bajista, soportes 78,7k / 71,5k / 70k — coherente con el relato |
| 5 | Cobertura de visión | **VERIFICADO** | 20/20 frames con visión no vacía, sin duplicados por nombre |

## Defectos concretos (por qué no se valida)

**D1 — Precios reportados por la visión no corresponden a los niveles reales.**
- `frame_3994`: el modelo devolvió `PRICES: [87496, 87486, 87484, 87482, 87480, …]` (serie sintética descendente). El frame real muestra **87.496, 83.833, 73.458, 69.997, 67.534**.
- `frame_4006`: el modelo devolvió `PRICES: [78746, 78000, 77000, 76000, 75000, 7400…]`. El frame real muestra **87.996, 78.748, 83.933, 81.444, 71.466, 69.907, 68.348**.
- Conclusión: el modelo **fabrica/enumera precios** en lugar de transcribir los niveles etiquetados. Coincide con el defecto documentado en FASE 3.7 ("fechas inventadas", "validación de precios no implementada").

**D2 — Indicadores inconsistentes.**
- `INDICATORS: MA` en 12/20 frames. En `frame_3994` y `frame_4006` no se observan medias móviles (solo líneas de tendencia y niveles) → **falso positivo**.
- En `frame_3994` sí hay herramienta **Fibonacci** visible y el modelo no la reportó → **falso negativo**.

**D3 — Sin mapeo frame ↔ timestamp.**
- Los frames se numeran `3994–4013`. La extracción estándar del pipeline (`fps=1/30`, `frame_%04d`) produciría `0001–0027`; no hay ningún artefacto que registre el instante temporal de cada frame. Por tanto **no es posible contrastar cada frame con los timestamps de la transcripción** de forma estricta.

**D4 — Transcripción duplicada.**
- 622 cues → el texto aparece **triplicado** (dedup: 619 segmentos únicos consecutivos). No altera el contenido, pero duplica el volumen y degrada cualquier análisis automático.

**D5 — Cobertura de instrumentos insuficiente.**
- El transcript discute BTC, **ETH** (2.373 / 2.077), **oro** (5.000 / 3.906), **BX**, **SP500** y **Nasdaq**. Los 20 frames analizados son todos `BTCUSD 1D`. No hay evidencia de frames que cubran los tramos de ETH/oro/índices.

**D6 — frame_4013 no validado visualmente.**
- Rechazado dos veces con HTTP 429 (`retry_after` 1828 s y 2144 s) por el proveedor auxiliar de visión. No se cambió de modelo (requiere autorización).

## Criterios de validación aplicados

Se consideró que la validación exige: (a) correspondencia temporal frame↔transcripción, (b) correspondencia entre lo verbal y lo representado, (c) identificación correcta de instrumento/temporalidad, (d) niveles/precios/indicadores verificables contra la imagen, (e) evidencia por conclusión. No se cumplieron (a), (d) y parcialmente (b)/(e).

## NO VERIFICADO

- Los 17 frames restantes (no inspeccionados visualmente).
- Correspondencia temporal estricta (imposible sin mapeo).
- frame_4013.

## PENDIENTE

- Corregir el prompt de visión para transcribir niveles reales (no enumerar) y declarar `null` si no hay indicador.
- Registrar el timestamp de cada frame al extraer.
- Re-inspeccionar `frame_4013` cuando el proveedor auxiliar esté disponible.
