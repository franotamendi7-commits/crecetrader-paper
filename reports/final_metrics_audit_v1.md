# Final Metrics Audit v1 — FASE 3.2.1

## Métricas con referencias y denominadores explícitos

---

## 1. Extracción de afirmaciones

| Métrica | Definición | Numerador | Denominador | Fuente de referencia | Casos excluidos | Casos ambiguos |
|---------|-----------|-----------|-------------|---------------------|-----------------|----------------|
| Precisión de extracción | Niveles correctos / Total extraídos | 51 | 51 | Transcripción (145 segmentos) | 0 | 0 |
| Recall de extracción | Niveles extraídos / Total mencionados | 51 | 51 | Transcripción (145 segmentos) | 0 | 2 (898, 2628400 — artefactos) |
| F1 de extracción | 2*P*R/(P+R) | 100% | — | — | — | — |

**Limitación:** La referencia fue construida por el mismo sistema. No es independiente.

---

## 2. Identificación de instrumentos

| Métrica | Definición | Numerador | Denominador | Fuente | Casos excluidos |
|---------|-----------|-----------|-------------|--------|-----------------|
| Exactitud de instrumentos | Instrumentos correctos / Total | 5/5 | 5 | Transcripción | 0 |

**Limitación:** Solo 5 instrumentos. Muestra pequeña.

---

## 3. Identificación de mercados

| Métrica | Definición | Numerador | Denominador | Fuente | Casos excluidos |
|---------|-----------|-----------|-------------|--------|-----------------|
| Exactitud de mercados | Mercados correctos / Total | 4/5 | 5 | Transcripción | ETH (mercado no especificado) |

**Limitación:** ETH no tiene mercado especificado. Se asume spot.

---

## 4. Identificación de temporalidades

| Métrica | Definición | Numerador | Denominador | Fuente | Casos excluidos |
|---------|-----------|-----------|-------------|--------|-----------------|
| Exactitud de temporalidades | Temporalidades correctas / Total | 4/4 | 4 | Transcripción | 0 |

---

## 5. Extracción de precios

| Métrica | Definición | Numerador | Denominador | Fuente | Casos excluidos |
|---------|-----------|-----------|-------------|--------|-----------------|
| Precisión de precios | Precios correctos / Total | 44/44 | 44 | Transcripción | 7 (OCR ilegible) |
| Precisión de OCR | Precios legibles / Total OCR | 0/7 | 7 | Frames (scene_15) | 0 |

**Limitación:** OCR parcial. No se puede verificar sin procesamiento de imagen.

---

## 6. Clasificación de niveles

| Métrica | Definición | Numerador | Denominador | Fuente | Casos excluidos |
|---------|-----------|-----------|-------------|--------|-----------------|
| Clasificación correcta | Niveles correctamente clasificados / Total | 51/51 | 51 | Revisión manual | 0 |

**Limitación:** Clasificación realizada por el mismo sistema.

---

## 7. Validación OHLCV

| Métrica | Definición | Numerador | Denominador | Fuente | Casos excluidos |
|---------|-----------|-----------|-------------|--------|-----------------|
| Verificación BTC spot | Niveles verificados / Total BTC spot | 0/24 | 24 | Kraken (XBTUSD) | 0 |
| Verificación BTC CME | Niveles verificados / Total BTC CME | 0/8 | 8 | Sin datos CME | 8 (todos) |
| Verificación otros | Niveles verificados / Total otros | 0/12 | 12 | Sin datos | 12 (todos) |
| Verificación total | Niveles verificados / Total | 0/51 | 51 | Kraken + sin datos | 27 |

---

## 8. Resumen de métricas

| Métrica | Valor | Independiente? |
|---------|-------|----------------|
| Precisión de extracción | 100% (51/51) | NO — referencia construida por el mismo sistema |
| Recall de extracción | 100% (51/51) | NO — referencia construida por el mismo sistema |
| Exactitud de instrumentos | 100% (5/5) | NO — muestra pequeña |
| Exactitud de mercados | 80% (4/5) | NO — muestra pequeña |
| Exactitud de temporalidades | 100% (4/4) | NO — muestra pequeña |
| Precisión de precios (verbal) | 100% (44/44) | NO — referencia construida por el mismo sistema |
| Precisión de OCR | 0% (0/7) | NO — no se pudo verificar |
| Clasificación correcta | 100% (51/51) | NO — clasificación por el mismo sistema |
| Validación OHLCV | 0% (0/51) | SÍ — datos externos de Kraken |

**Única métrica independiente:** Validación OHLCV (0%) — porque usa datos externos (Kraken).

**Todas las demás métricas NO son independientes** porque la referencia fue construida por el mismo sistema.

---

## Conclusión

- **Precisión de extracción:** 100% (no independiente)
- **Validación OHLCV:** 0% (independiente)
- **NO DEMOSTRADO INDEPENDIENTEMENTE:** Todas las métricas excepto validación OHLCV

**[VERIFICADO]** — Métricas con referencias y denominadores explícitos
**[VERIFICADO]** — Única métrica independiente: validación OHLCV (0%)
**[PENDIENTE]** — Evaluación independiente real
**[PENDIENTE]** — Ground truth con más videos
