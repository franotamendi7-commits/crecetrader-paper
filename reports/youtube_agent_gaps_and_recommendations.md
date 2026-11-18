# YouTube Agent Gaps and Recommendations — FASE 3.2.4

## 1. Problemas de extracción

| Problema | Evidencia | Impacto | Causa probable | Solución | Prioridad | Coste |
|----------|-----------|---------|----------------|----------|-----------|-------|
| 1 frame por escena | 17 frames para 17 escenas | Cobertura visual insuficiente | PySceneDetect + extracción simple | Muestreo adaptativo (1 frame/10s en escenas largas) | Alta | $0 |
| Escenas largas sin cobertura | scene_3: 293.7s con 1 frame | Se pierden cambios de gráfico | Umbral de detección de escenas muy alto | Reducir umbral de ContentDetector | Alta | $0 |
| Frames duplicados | No detectados explícitamente | Desperdicio de procesamiento | No hay deduplicación | Hash perceptual de frames | Media | $0 |

## 2. Problemas de transcripción

| Problema | Evidencia | Impacto | Causa probable | Solución | Prioridad | Coste |
|----------|-----------|---------|----------------|----------|-----------|-------|
| Números mal transcritos | 476 → 74.476 (inferido) | Niveles incorrectos | Whisper small, español | Usar modelo larger o corrección post-transcripción | Media | $0 |
| Separadores decimales confundidos | 1890 → 1.890 (ETH) | Niveles incorrectos | Transcripción numérica ambigua | Normalización contextual mejorada | Media | $0 |
| Artefactos | 898, 2628400 | Falsos positivos | Whisper genera artefactos | Filtrado de artefactos con regex | Baja | $0 |

## 3. Problemas de cobertura visual

| Problema | Evidencia | Impacto | Causa probable | Solución | Prioridad | Coste |
|----------|-----------|---------|----------------|----------|-----------|-------|
| 47% frames sin texto | 8/17 frames sin OCR | Información visual perdida | Texto muy pequeño o no texto | Pre-procesamiento de imagen (resize, sharpen) | Alta | $0 |
| 7 niveles ilegibles | scene_15 precios cortados | 7 niveles no verificables | OCR sobre imagen de baja resolución | Pre-procesamiento + OCR mejorado (EasyOCR) | Alta | $0 |

## 4. Problemas de OCR

| Problema | Evidencia | Impacto | Causa probable | Solución | Prioridad | Coste |
|----------|-----------|---------|----------------|----------|-----------|-------|
| Tesseract exactitud ~56% | Solo 9/17 frames con texto | Texto no extraído | Tesseract no optimizado para gráficos | EasyOCR (open source) o PaddleOCR | Media | $0 |
| Sin pre-procesamiento | No se aplica resize/sharpen | OCR de baja calidad | Pipeline no incluye pre-procesamiento | Agregar OpenCV pre-processing | Media | $0 |

## 5. Problemas de comprensión semántica

| Problema | Evidencia | Impacto | Causa probable | Solución | Prioridad | Coste |
|----------|-----------|---------|----------------|----------|-----------|-------|
| No hay comprensión visual | Solo OCR, no visión | No se entienden gráficos | No hay modelo de visión | Moondream 2 (open weights) o Qwen-VL | Alta | $0 (local) |
| No hay interpretación de velas | No se identifican velas | No se entiende estructura | No hay detección de objetos | YOLOv8 (open source) para velas/líneas | Media | $0 |

## 6. Problemas de interpretación de gráficos

| Problema | Evidencia | Impacto | Causa probable | Solución | Prioridad | Coste |
|----------|-----------|---------|----------------|----------|-----------|-------|
| No se identifican indicadores | No hay detección de RSI, MACD, etc. | Metodología no verificable | No hay análisis de imagen | Visión semántica con Moondream | Alta | $0 |
| No se identifican líneas de tendencia | No hay detección de líneas | Soportes/resistencias no verificables | No hay análisis de imagen | Visión semántica con Moondream | Alta | $0 |

## 7. Problemas de datos OHLCV

| Problema | Evidencia | Impacto | Causa probable | Solución | Prioridad | Coste |
|----------|-----------|---------|----------------|----------|-----------|-------|
| CME no buscado | 8 niveles sin datos | 8 niveles no evaluables | No hay fuente gratuita para CME | Buscar fuente gratuita (Yahoo Finance futures) | Media | $0 |
| Otros instrumentos no buscados | 12 niveles sin datos | 12 niveles no evaluables | No se buscaron fuentes | Yahoo Finance (ETFs: GLD, SPY, QQQ) | Media | $0 |
| 0/24 verificados | 0 niveles coinciden exactamente | No se puede confirmar ningún nivel | Temporalidad incompatible (spot vs futuros) | Comparar con temporalidad correcta | Alta | $0 |

## 8. Problemas de reconciliación

| Problema | Evidencia | Impacto | Causa probable | Solución | Prioridad | Coste |
|----------|-----------|---------|----------------|----------|-----------|-------|
| Sin auditor independiente | INDEPENDENCIA_NO_DISPONIBLE | No se puede confiar en la auditoría | Un solo sistema (Hermes) | Usar un segundo modelo (Qwen local) como revisor | Media | $0 |
| Solo 1 video | n=1 | No se puede generalizar | Alcance limitado | Procesar 2-3 videos adicionales | Alta | $0 |

## 9. Problemas de validación

| Problema | Evidencia | Impacto | Causa probable | Solución | Prioridad | Coste |
|----------|-----------|---------|----------------|----------|-----------|-------|
| Sin ground truth independiente | Todas las métricas son del mismo sistema | No se puede confiar en métricas | No hay anotación manual | Crear anotación manual independiente | Alta | Tiempo humano |
| Sin validación cruzada | Un solo pipeline | No se detectan errores sistemáticos | No hay pipeline alternativo | Implementar pipeline alternativo (whisper.cpp) | Baja | $0 |

## Recomendaciones priorizadas

1. **Muestreo adaptativo** (Alta, $0) — Extraer más frames en escenas largas
2. **Pre-procesamiento de imagen** (Alta, $0) — Resize, sharpen, contrast para OCR
3. **Visión semántica** (Alta, $0) — Moondream 2 (open weights) o Qwen-VL
4. **Fuentes OHLCV adicionales** (Media, $0) — Yahoo Finance para ETFs y futuros
5. **OCR mejorado** (Media, $0) — EasyOCR o PaddleOCR
6. **Auditor independiente** (Media, $0) — Qwen local como revisor
7. **Más videos** (Alta, $0) — Validar con 2-3 videos adicionales
8. **Anotación manual** (Alta, tiempo) — Ground truth independiente

## Coste recurrente total: USD 0

Todas las soluciones propuestas son open source, open weights, o freeware. No se requieren servicios pagos.
EOF