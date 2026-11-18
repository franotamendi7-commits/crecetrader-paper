# B4 — Correcciones previas a la anotación humana

Fecha: 2026-11-16
Alcance: `benchmark_vision_b1/` only. Sin inferencias, sin B4/B5, sin cambios en producción.
Copia de seguridad previa: `benchmark_vision_b1/B4_pre_correccion_backup/`.

---

## 1. Problemas detectados

De la auditoría nocturna y de esta revisión:

- **C1 — Contradicción en la guía.** La sección 7 permitía "anotar el valor más probable con confianza baja", mientras el protocolo exige `NO LEGIBLE` ante dígitos dudosos.
- **C2 — Métricas incompletas.** El comparador cubría 6 de 11 métricas (faltaban niveles horizontales, directrices, liquidez, abstención y acuerdo entre anotadores).
- **C3 — Sin precisión de precios** ni detección explícita de números inventados.
- **C4 — Sin validación de formato de la referencia** (podían colarse filas desalineadas o separadores distintos).
- **C5 — Solape de campos** (`visible_price_labels` vs `horizontal_levels` vs `trendlines`).
- **C6 — Plantilla sin legibilidad por campo** (solo una nota genérica).
- **C7 — Redundancia de los 20 frames** (nuevo, ver punto 7).

## 2. Correcciones realizadas

- **C1**: reescrita la sección 7 de la guía con el criterio definitivo (claro → transcribir; duda → `NO LEGIBLE`; inexistente → `NO PRESENTE`). Actualizado el protocolo para referenciar la guía y el esquema.
- **C2/C3/C4**: reescrito `scripts/b4_comparar.py` (v2): 14 métricas con numerador/denominador/resultado/excluidos/no evaluables; precisión y exhaustividad de precios; niveles horizontales; directrices; liquidez; indicadores (F1 aprox.); abstención correcta; acuerdo entre anotadores; validación de formato que **aborta** si la referencia es inválida.
- **Alucinaciones**: un número ausente en la referencia **no** se marca como inventado; se registra como `pendiente_de_verificacion_visual` (requiere comprobar la imagen).
- **C5**: nuevo `B4_ESQUEMA_ANOTACION.md` con reglas de asignación no ambiguas (línea horizontal vs directriz, línea con etiqueta, etc.).
- **C6**: nueva plantilla `B4_referencia_humana_template_v2.csv` con 8 columnas `legibility_*` (1-4). La v1 se conserva.
- **C7**: análisis de redundancia (punto 7) + recomendación, sin alterar la selección oficial.

## 3. Archivos modificados / creados

| Archivo | Cambio |
|---|---|
| `B4_GUIA_ANOTACION_HUMANA.md` | modificado (sección 7) |
| `B4_PROTOCOLO_EVALUACION.md` | modificado (sección 4) |
| `B4_ESQUEMA_ANOTACION.md` | nuevo |
| `B4_referencia_humana_template_v2.csv` | nuevo (v1 intacta) |
| `scripts/b4_comparar.py` | reescrito (v2) |
| `scripts/b4_pruebas_sinteticas.py` | nuevo |
| `B4_pre_correccion_backup/` | copia de seguridad de los 6 archivos previos |

No se modificaron las 20 fichas (ya eran coherentes) ni B1/B3/B6.

## 4. Pruebas sintéticas ejecutadas

`scripts/b4_pruebas_sinteticas.py` → **13/13 OK** (sin llamadas a modelos):

| Caso | Resultado |
|---|---|
| coincidencia exacta | OK |
| precio omitido | recall 50 / precision 100 |
| precio inventado | precision 50 + `pendiente_de_verificacion_visual` |
| precio ilegible en referencia | denominador 0, no evaluable |
| instrumento incorrecto | 0% |
| temporalidad incorrecta | 0% |
| indicador incorrecto | F1 0 |
| abstención correcta | 100% |
| abstención incorrecta | 0% |
| formato CSV inválido | rc=2, aborta sin métricas |
| campos vacíos | no evaluable |
| datos duplicados | deduplicado |
| acuerdo entre anotadores | 100% |

## 5. Resultados esperados vs obtenidos

Todos los casos produjeron el resultado esperado. La validación de formato detectó la fila desalineada (caso 10) gracias a la comprobación de número de columnas añadida durante las pruebas.

## 6. Estado de las métricas

| Métrica | Implementada | num/den |
|---|---|---|
| instrument_accuracy | sí | sí |
| timeframe_accuracy | sí | sí |
| market_structure_accuracy | sí | sí |
| prices_recall / precision | sí | sí |
| horizontal_levels recall / precision | sí | sí |
| trendlines recall / precision | sí | sí |
| liquidity_zones recall / precision | sí | sí |
| indicators_f1_approx | sí | sí |
| abstencion_correcta | sí | sí |
| posibles_alucinaciones_precios | sí (con verificación visual pendiente) | sí |
| acuerdo_entre_anotadores | sí | sí |
| consistencia entre repeticiones | **no** (requiere 3 ejecuciones del modelo; se computará en B5) | — |

## 7. Análisis de redundancia de los 20 frames

Comparación por pares (PIL, diferencia media sobre 255, imágenes reescaladas a 320×176):

- **190/190 pares** con diferencia < 3.
- Diferencia **máxima: 0,24/255**; pares consecutivos entre 0,01 y 0,14.
- Los 20 frames son la **misma escena** (mismo gráfico, mismas líneas, mismas etiquetas); solo cambian detalles mínimos del precio actual y alguna vela.

**Conclusión**: los 20 frames aportan información **prácticamente duplicada**. Su **n efectivo** es de ~1-3 escenas, no 20.

**Recomendación (no aplicada; la selección oficial no se cambia sin tu autorización):**
1. **No anotar los 20 como muestra de 20.** Anotar un subconjunto representativo (p. ej., `3994`, `4006`, `4013`) o un máximo de 5 equidistantes.
2. Ampliar el benchmark con vídeos de mayor cobertura y escenas distintas: `LzPTdClLo_w` (91,5% del vídeo), `jeOFS1TZYQA` (73,7%), `scJ-ai2FRiE` (64,5%), `s3KxjqkzwKM` (57,4%).
3. Declarar siempre que LFHkc5dUoLw es **una escena única** (últimos 3,8 s), no el vídeo completo.

**Limitaciones estadísticas**: con n efectivo ≈ 1-3 no es posible ninguna inferencia poblacional; las métricas serían un resultado anclado a una única imagen.

## 8. Recomendación para la anotación humana

1. Elegir **2 anotadores independientes** y un tercero que adjudique.
2. Anotar el **subconjunto representativo** de LFHkc5dUoLw + un lote de los vídeos priorizados (empezando por `LzPTdClLo_w`).
3. Usar la **v2** de la plantilla y la guía corregida; registrar `NO LEGIBLE` ante cualquier duda de dígito.
4. Volcar a `anotador1.csv` / `anotador2.csv`; adjudicar; generar la referencia validada.
5. Solo entonces ejecutar `b4_ejecutar_evaluacion.py --ejecutar` y `b4_comparar.py`.

## 9. Problemas que continúan pendientes

- **No hay dos anotadores humanos** → B4/B5 siguen detenidos.
- **Consistencia entre repeticiones** no implementada (B5).
- **Verificación visual de posibles alucinaciones** requiere revisión humana de cada precio marcado.
- **El esquema de 4 estados de legibilidad** debe respetarse en el volcado; si el anotador lo omite, el comparador lo trata como vacío (no evaluable).
- **Las 20 fichas** habría que regenerarlas si se adopta el subconjunto recomendado.

## 10. Confirmación de integridad

- **Producción intacta**: no se tocó `scripts/rss_priority_processor.py`, `run_video.py`, `analyze_vision_batch.py`, prompts, modelos, proveedores, skills ni configuración de Hermes.
- **No se ejecutó B4/B5** ni ninguna inferencia (no se llamó a Ollama).
- **No se modificó B1, B3 ni B6** (solo lectura).
- **No se descargó material ni se usaron servicios externos.**
- Todos los cambios fueron documentados y con copia de seguridad en `B4_pre_correccion_backup/`.
- No se completó ninguna anotación humana ni se generó ground truth artificial.

**B4 sigue técnicamente preparado y detenido.** No se declara el modelo validado ni YouTubeTradingAgent aprobado.
