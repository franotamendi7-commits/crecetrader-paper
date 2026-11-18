# Video Visual Analysis Audit — FASE 3.2.4

## 1. Evaluación de gráficos

| Elemento | Estado | Evidencia |
|----------|--------|-----------|
| Instrumento visible | PARCIAL | Solo 5/17 frames con texto claro |
| Temporalidad visible | PARCIAL | Solo scene_4 (semanal), scene_6 (4H) |
| Tipo de gráfico | NO_OBSERVADO | No se identificó tipo de gráfico en frames |
| Estructura de precios | NO_OBSERVADO | No se identificó estructura de velas |
| Soportes/resistencias | NO_OBSERVADO | No se identificaron líneas horizontales |
| Indicadores | NO_OBSERVADO | No se identificaron indicadores |
| Anotaciones | PARCIAL | scene_5 "Fase de Acumulación", scene_13 "CALENDARIO" |
| Zonas de liquidez | NO_OBSERVADO | No se identificaron zonas |
| Patrones | NO_OBSERVADO | No se identificaron patrones |

## 2. Evaluación de OCR

| Métrica | Valor |
|---------|-------|
| Frames con texto detectado | 9/17 (53%) |
| Frames con texto claro | 5/17 (29%) |
| Frames con texto parcial/ruidoso | 4/17 (24%) |
| Frames sin texto | 8/17 (47%) |
| Frames con precios ilegibles | 1/17 (6%) — scene_15 |
| Exactitud de lectura | ~56% (solo frames con texto) |

## 3. Evaluación de instrumentos

| Instrumento | Mencionado verbalmente | Visible en frames | Identificado por OCR |
|-------------|----------------------|-------------------|---------------------|
| BTC | ✅ (múltiples segmentos) | Parcial (scene_3, 4, 5, 6, 9) | Parcial |
| ETH | ✅ (segmentos 558-595s) | Parcial (scene_10) | ✅ "ETHEREUM" |
| Oro | ✅ (segmentos 680-710s) | No | No |
| S&P 500 | ✅ (segmentos 757-781s) | No | No |
| NASDAQ | ✅ (segmentos 765-781s) | No | No |

## 4. Evaluación de temporalidades

| Temporalidad | Mencionada verbalmente | Visible en frames |
|--------------|----------------------|-------------------|
| Semanal | ✅ | Parcial (scene_4) |
| Diario | ✅ | No |
| 4H | ✅ | Parcial (scene_6) |
| Intradía (5 min) | ✅ | No |

## 5. Evaluación de niveles

| Aspecto | Estado |
|---------|--------|
| Precios mencionados verbalmente | 44 identificados |
| Precios visibles en pantalla | 7 (ilegibles) |
| Precios verificados con OHLCV | 0 |
| Coincidencias aproximadas | 18 |
| Sin coincidencia en rango | 6 |
| No evaluables | 20 |
| Ilegibles | 7 |

## 6. Conclusión visual

El sistema **NO comprende los gráficos** del video. Solo extrae texto mediante OCR (56% de exactitud). No identifica velas, indicadores, líneas, patrones ni estructura de precios. La cobertura visual es insuficiente (1 frame por escena, 7 escenas con cobertura inadecuada).

**[VERIFICADO]** — OCR funciona para texto claro (5 frames)
**[VERIFICADO]** — 7 niveles ilegibles (scene_15)
**[NO_DEMOSTRADO]** — Comprensión de gráficos
**[NO_DEMOSTRADO]** — Identificación de velas, indicadores, patrones
**[PENDIENTE]** — Visión semántica de gráficos (requiere Moondream o similar)
EOF