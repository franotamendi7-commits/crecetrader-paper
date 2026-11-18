# B4 — Auditoría nocturna (cierre)

Fecha: 2026-11-16
Alcance: solo lectura, análisis y preparación documental. **Sin inferencias, sin B4/B5, sin cambios en producción.**

---

## 1. Archivos revisados

- `benchmark_vision_b1/B4_fichas_anotacion/ficha_frame_*.md` (20)
- `benchmark_vision_b1/B4_referencia_humana_template.csv`
- `benchmark_vision_b1/B4_PROTOCOLO_EVALUACION.md`
- `benchmark_vision_b1/B4_INFORME_VALIDACION_VISUAL.md`
- `benchmark_vision_b1/scripts/b4_ejecutar_evaluacion.py`
- `benchmark_vision_b1/scripts/b4_comparar.py`
- `benchmark_vision_b1/scripts/b4_generar_fichas.py`
- (solo lectura) `inventory.json`, `temporal/timestamps.json`, `historical_progress.json`

## 2. Verificaciones que pasaron

| # | Comprobación | Resultado |
|---|---|---|
| 1 | Las 20 fichas tienen los mismos campos | **PASÓ** — una única cabecera, 12 campos, sin extras |
| 2 | Identificadores y timestamps correctos | **PASÓ** — 20/20 frame_id, idx y `pts_time` coinciden con `temporal/timestamps.json` |
| 3 | Plantilla CSV coherente con las fichas | **PASÓ** — las columnas cubren los campos de la ficha (ver E3) |
| 4 | Campos ambiguos o contradictorios | **PASÓ** con salvedades (ver E4) |
| 5 | El comparador interpreta la referencia | **PASÓ** — prueba con datos sintéticos en scratch: instrumento/timeframe/estructura/indicadores/precios calculados |
| 6 | El evaluador permanece bloqueado sin autorización | **PASÓ** — sin `--ejecutar` no crea salida ni llama al modelo |
| 7 | Ningún script ejecuta inferencias accidentales | **PASÓ** — el único con red es `b4_ejecutar_evaluacion.py` (líneas 52/57), protegido por flag |
| 8 | Métricas calculables con los datos disponibles | **PARCIAL** — 6 de 11 implementadas (ver E1) |

## 3. Errores y problemas encontrados

- **E1 — Métricas incompletas.** `b4_comparar.py` implementa 6 de las 11 propuestas. **Faltan**: niveles horizontales, directrices, zonas de liquidez, abstención correcta y consistencia entre repeticiones. B4/B5 no podrían reportar esas métricas sin ampliar el script.
- **E2 — Precisión de precios.** El comparador solo calcula `prices_recall`, no `prices_precision` (no se puede medir la tasa de números inventados por frame con el script actual).
- **E3 — Acoplamiento de formato.** El comparador asume `price_levels` e `indicators` separados por `;`. Si el anotador usa otro separador, las métricas degradan silenciosamente. Requiere validación de formato antes de comparar.
- **E4 — Campos con solape semántico.** `visible_price_labels` (precios con etiqueta) y `horizontal_levels` (líneas, opcionalmente etiquetadas) pueden solaparse. Las instrucciones lo aclaran, pero conviene que el anotador sea consistente.
- **E5 — Codificación de legibilidad.** La ficha usa 1-4 por campo, pero el CSV de referencia no incluye una columna `legibility` por campo (solo `legibility_notes`). Para métricas finas haría falta ampliar la plantilla.

Ninguno de estos errores fue corregido (la tarea prohíbe corregir automáticamente). Se dejan documentados.

## 4. Problemas que podrían bloquear mañana

1. **No hay dos anotadores humanos** → B4 no puede ejecutarse.
2. **Métricas E1/E2 incompletas** → el informe B5 quedaría parcial si no se amplía el comparador.
3. **Formato de la referencia (E3)** → riesgo de métricas inválidas si el volcado difiere del `;`.

## 5. Material útil para ampliar el benchmark

Cobertura real de los 157 frames existentes (sin reprocesamiento):

| vídeo | frames | t_min (s) | t_max (s) | dur (s) | cubre | inicio | final |
|---|---|---|---|---|---|---|---|
| LzPTdClLo_w | 17 | 0,0 | 480,0 | 524,5 | **91,5%** | SÍ | SÍ |
| jeOFS1TZYQA | 20 | 180,0 | 750,0 | 773,7 | 73,7% | no | SÍ |
| scJ-ai2FRiE | 20 | 270,0 | 840,0 | 884,2 | 64,5% | no | SÍ |
| s3KxjqkzwKM | 20 | 390,0 | 960,0 | 993,2 | 57,4% | no | SÍ |
| XLgPycsN0ls | 20 | 630,0 | 1200,0 | 1215,5 | 46,9% | no | SÍ |
| dPHvRw1wzYQ | 20 | 1410,0 | 1980,0 | 2015,0 | 28,3% | no | SÍ |
| EJoLhxbwYxo | 20 | 982,6 | 986,4 | 986,7 | 0,4% | no | SÍ |
| LFHkc5dUoLw | 20 | 798,6 | 802,4 | 802,6 | 0,5% | no | SÍ |

**Prioridad sugerida** (por cobertura y variedad de escenas, no por predicciones del modelo): `LzPTdClLo_w` (cobertura completa), `jeOFS1TZYQA`, `scJ-ai2FRiE`, `s3KxjqkzwKM`.
**No usar como muestras representativas**: `EJoLhxbwYxo` y `LFHkc5dUoLw` (0,4–0,5% del vídeo; solo el cierre).
**Cantidad aprovechable sin reprocesamiento**: **157 frames** (20 de LFHkc5dUoLw ya en B4).

## 6. Pendiente de intervención humana

1. Seleccionar **dos anotadores independientes** (y un tercero para adjudicar).
2. Completar las **20 fichas** (o el subconjunto acordado) y volcar a `anotador1.csv` / `anotador2.csv`.
3. Adjudicar desacuerdos y generar `B4_referencia_humana.csv` validada.
4. Recién entonces: ejecutar `b4_ejecutar_evaluacion.py --ejecutar`.

## 7. Confirmación

- **No ejecuté B4 ni B5.**
- **No llamé a Ollama ni a ningún modelo de visión.**
- **No realicé anotaciones automáticas** en nombre de los humanos.
- **No reprocesé videos ni descargué material.**
- **No modifiqué producción**, prompts, modelos, proveedores, skills ni configuración.
- **No modifiqué B1, B3 ni B6** (solo lectura).
- **No utilicé servicios externos** ni actualicé Hermes.
- Únicas escrituras: `B4_GUIA_ANOTACION_HUMANA.md` y este informe (documentación nueva, dentro del benchmark B4).

**B4 no está aprobado ni finalizado.** Queda detenido a la espera de las anotaciones humanas.
