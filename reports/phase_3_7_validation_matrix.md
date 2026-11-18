# FASE 3.7 — MATRIZ DE VALIDACIÓN

## Matriz de evaluación

| # | Criterio | Estado actual | Estado propuesto | Evidencia | Estado |
|---|----------|---------------|------------------|-----------|--------|
| 1 | OCR funcional | No se ejecuta en pipeline | Integrar Tesseract | phase_3_7_ocr_diagnostics.md | PENDIENTE |
| 2 | Confusión de instrumentos | Sí (BTC→oro) | Prompt estructurado | phase_3_7_root_cause_analysis.md | PENDIENTE |
| 3 | Timeouts | 5/19 (26%) | Reducir resolución | phase_3_7_root_cause_analysis.md | PENDIENTE |
| 4 | CME/Spot distinción | No implementado | Campos en schema | phase_3_7_pipeline_comparison.md | PENDIENTE |
| 5 | Fechas inventadas | Sí | Instrucción null | phase_3_7_root_cause_analysis.md | PENDIENTE |
| 6 | Separación audio/imagen | No implementado | Prompt estructurado | phase_3_7_pipeline_comparison.md | PENDIENTE |
| 7 | Expresión de incertidumbre | Parcial | Sistemática | phase_3_7_pipeline_comparison.md | PENDIENTE |
| 8 | Validación de precios | No implementado | OHLCV cross-reference | — | PENDIENTE |
| 9 | Reproducibilidad | No verificada | Ejecutar 2x | — | PENDIENTE |
| 10 | Rendimiento | ~276s/frame | ~180-276s/frame | — | PENDIENTE |

## Lo que se verificó en FASE 3.7

### [VERIFICADO]
1. OCR funciona cuando se invoca manualmente (Tesseract 5.5.4, spa+eng)
2. El pipeline NO invoca OCR (grep sin resultados)
3. Las imágenes son pequeñas (640x352, 10-66KB) — no es causa de timeout
4. El modelo tarda 5+ min incluso con prompt corto — bottleneck es inferencia
5. Tesseract tiene 162 idiomas incluyendo spa y eng
6. Las causas raíz de los 5 errores están identificadas

### [NO VERIFICADO]
1. Si el prompt estructurado reduce la confusión de instrumentos
2. Si la integración de OCR mejora la extracción de niveles
3. Si la reducción de resolución reduce timeouts sin perder precisión
4. Si el pipeline optimizado procesa los 5 frames fallidos

### [PENDIENTE]
1. Implementación del pipeline optimizado (delegar a OpenCode)
2. Ejecución de pruebas comparativas
3. Validación de resultados
4. Generación de informe final con evidencia

## Errores críticos que persisten

| Error | Causa raíz | Solución diseñada | Estado |
|-------|-----------|-------------------|--------|
| OCR vacío | OCR no invocado | Integrar Tesseract | Diseñado, no implementado |
| Confusión instrumentos | Prompt genérico | Prompt estructurado | Diseñado, no implementado |
| Timeouts | Modelo lento | Reducir resolución | Diseñado, no implementado |
| CME vs Spot | Schema incompleto | Campos de distinción | Diseñado, no implementado |
| Fechas inventadas | Sin instrucción null | Instrucción explícita | Diseñado, no implementado |

## Recomendación
Implementar el pipeline optimizado y ejecutar pruebas comparativas antes de declarar FASE 3.7 como aprobada. Los cambios son reversibles y no requieren instalaciones nuevas.