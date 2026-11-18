# FASE 3.6 — INFORME FINAL

## Resumen ejecutivo

El YouTube Analyst puede identificar instrumentos (BTC/USD), temporalidades (Weekly/Daily/4H/1H) y estructura de mercado (soportes, resistencias, tendencias) en 14 de 19 frames (74%). Sin embargo, presenta errores críticos de confusión de instrumentos, OCR no funcional, y 26% de frames no procesados por timeout.

**Estado: NO APROBADO para siguiente fase.**

## Lo que se hizo
1. Se reconcilió el estado de 19 frames (14 OK, 5 ERR)
2. Se creó fuente de verdad canónica (vision_analysis_canonical.json)
3. Se generó informe de reconciliación (phase_3_6_frame_reconciliation.md)
4. Se generó auditoría de estado (phase_3_6_audit.md)
5. Se generó matriz de validación (phase_3_6_validation_matrix.md)

## Lo que se verificó
- [VERIFICADO] 14/19 frames procesados exitosamente con Qwen3.5:9b-mlx
- [VERIFICADO] Instrumento BTC/USD identificado en todos los gráficos OK
- [VERIFICADO] Temporalidades identificadas correctamente (Weekly, Daily, 4H, 1H)
- [VERIFICADO] 5 frames fallan por timeout (600s) incluso con reintentos
- [VERIFICADO] OCR (Tesseract) retorna texto vacío en todos los frames
- [VERIFICADO] Confusión de instrumentos: modelo identifica BTC como "oro/petróleo"
- [VERIFICADO] Tiempo promedio por frame: ~276s (~4.6 min)
- [VERIFICADO] Tiempo total de procesamiento exitoso: ~3,860s (~64 min)

## Lo que falló
1. **26% de frames no procesados** — 5/19 timeout (600s)
2. **Confusión de instrumentos** — BTC identificado como oro/petróleo
3. **OCR no funcional** — Tesseract retorna vacío
4. **CME vs Spot** — No se distingue futuros de spot
5. **Fechas inventadas** — Modelo inventa fechas de eventos macro
6. **Sin validación de precios** — No se contrasta con OHLCV
7. **Sin clasificación sistemática** — No implementa [DICHO]/[OBSERVADO]/[INFERIDO]/[NO VERIFICADO]

## Evidencia
- `experimental/results/vision_analysis_canonical.json` — 19 frames (14 OK, 5 ERR)
- `experimental/results/vision_analysis.json` — Análisis visual detallado
- `experimental/results/structured_scenes.json` — 18 escenas estructuradas
- `experimental/results/multimodal_report.md` — Informe correlacionado
- `experimental/logs/vision_analyzer3.log` — Log de ejecución completa
- `experimental/logs/retry_failed.log` — Log de reintentos
- `experimental/logs/retry_v2.log` — Log de reintentos v2

## Lo que queda pendiente
1. Recuperar 5 frames fallidos (1, 2, 6, 12, 16) — requiere modelo más rápido o timeout mayor
2. Implementar OCR funcional (easyOCR, paddleOCR, o Tesseract con preprocesamiento)
3. Corregir confusión de instrumentos (prompt mejorado, separación audio/imagen)
4. Implementar distinción CME futures vs BTC spot
5. Validar niveles de precio con OHLCV (Kraken)
6. Implementar clasificación sistemática [DICHO]/[OBSERVADO]/[INFERIDO]/[NO VERIFICADO]
7. Benchmark Qwen3.5 vs Qwen3-VL (requiere autorización para instalar)
8. Generar informe estructurado por escena

## Recomendación concreta
1. **Mantener Qwen3.5:9b-mlx** como modelo principal — funciona para gráficos simples
2. **Implementar preprocesamiento de imágenes** (resize, crop) para reducir timeouts
3. **Mejorar prompts** para separar audio de imagen y evitar confusión de instrumentos
4. **Investigar OCR alternativo** antes de declarar que no hay texto en las imágenes
5. **NO instalar Qwen3-VL** sin autorización — primero optimizar el pipeline actual
6. **NO pasar a siguiente fase** hasta resolver los 5 errores críticos

## Conclusión
El YouTube Analyst puede interpretar gráficos simples de BTC (instrumento, temporalidad, niveles) pero no es confiable para análisis completo. Los errores críticos (confusión de instrumentos, OCR no funcional, 26% timeout) deben resolverse antes de avanzar.