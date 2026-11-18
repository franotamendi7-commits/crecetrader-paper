# FASE 3.7 — INFORME FINAL

## Resumen ejecutivo

Se identificaron las causas raíz de los 5 errores críticos de FASE 3.6:

1. **OCR vacío**: El OCR nunca se invocaba en el pipeline (no es un problema de configuración)
2. **Confusión de instrumentos**: Prompt genérico sin separación audio/imagen
3. **Timeouts**: Velocidad de inferencia del modelo (no tamaño de imagen)
4. **CME vs Spot**: Schema sin campos de distinción
5. **Fechas inventadas**: Sin instrucción de null para valores no legibles

Se diseñó un pipeline optimizado con prompt estructurado, OCR integrado y schema mejorado. **La implementación y pruebas comparativas quedan pendientes de delegación a OpenCode.**

**Estado: PENDIENTE DE IMPLEMENTACIÓN.**

## Lo que se hizo en FASE 3.7
1. Auditoría técnica del pipeline (causas raíz identificadas)
2. Diagnóstico de OCR (Tesseract funciona, pipeline no lo invoca)
3. Diseño de pipeline optimizado (prompt estructurado, OCR, schema)
4. Comparación antes/después documentada
5. Matriz de validación generada

## Lo que se verificó
- [VERIFICADO] OCR funciona manualmente (Tesseract 5.5.4, spa+eng)
- [VERIFICADO] Pipeline NO invoca OCR (grep sin resultados)
- [VERIFICADO] Imágenes pequeñas (640x352) — no causa de timeout
- [VERIFICADO] Modelo tarda 5+ min con prompt corto — bottleneck es inferencia
- [VERIFICADO] Causas raíz de los 5 errores identificadas
- [VERIFICADO] Soluciones diseñadas para todos los errores

## Lo que NO se hizo (pendiente)
1. Implementación del pipeline optimizado
2. Integración de OCR en vision_analyzer.py
3. Ejecución de pruebas comparativas
4. Validación de resultados
5. Generación de evidencia de mejora

## Lo que falló
- No se pudo implementar el pipeline optimizado (requiere delegación a OpenCode)
- No se pudo ejecutar pruebas comparativas (proceso de retry interrumpido)
- No se pudo recuperar los 5 frames fallidos

## Evidencia
- `reports/phase_3_7_root_cause_analysis.md` — Análisis de causas raíz
- `reports/phase_3_7_ocr_diagnostics.md` — Diagnóstico de OCR
- `reports/phase_3_7_pipeline_comparison.md` — Comparación antes/después
- `reports/phase_3_7_validation_matrix.md` — Matriz de validación

## Recomendación concreta
1. **Delegar implementación a OpenCode** — crear pipeline optimizado con prompt estructurado, OCR integrado y schema mejorado
2. **Ejecutar pruebas comparativas** en los 10 frames seleccionados
3. **Validar resultados** antes de declarar FASE 3.7 como aprobada
4. **Si Qwen3.5 sigue confundiendo activos** después de optimizar, usar la evidencia para decidir si incorporar Qwen3-VL
5. **No instalar Qwen3-VL** hasta tener evidencia de que el pipeline optimizado no es suficiente

## Principio central
Precisión antes que velocidad, evidencia antes que inferencia y confiabilidad antes que automatización.