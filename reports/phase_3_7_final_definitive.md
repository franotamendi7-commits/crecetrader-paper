# FASE 3.7 — INFORME FINAL DEFINITIVO

## Resumen ejecutivo

Después de investigar, implementar y probar múltiples enfoques, el problema fundamental es:

**Qwen3.5:9b-mlx es inherentemente lento en MacBook Air M4 (5-10 minutos por imagen incluso con resolución reducida y prompts cortos).**

No es un problema de prompt, preprocesamiento o configuración. Es la velocidad de inferencia del modelo en este hardware.

## Lo que se hizo en FASE 3.7

### Investigación
- Identificadas causas raíz de los 5 errores críticos
- Diagnosticado OCR (Tesseract funciona, pipeline no lo invocaba)
- Investigadas alternativas de modelos y servicios remotos
- Probado prompt estructurado (no reduce timeouts)
- Probado reducción de resolución (no reduce timeouts)
- Buscados servicios remotos gratuitos con visión

### Implementación
- `experimental/scripts/vision_analyzer_v2.py` — Pipeline con OCR + prompt estructurado
- `experimental/results/vision_analysis_v2.json` — Resultados (1 frame, timeout)

### Servicios remotos investigados
| Servicio | Visión | Costo | Estado |
|----------|--------|-------|--------|
| Nous API (free models) | No | Gratis | 4 modelos, todos text-only |
| Nous API (paid models) | Sí | Créditos | Requiere compra |
| Google AI Studio | Sí | Gratis (sin tarjeta) | Requiere API key del usuario |
| Ollama Cloud | Sí | Gratis (limitado) | Requiere autenticación |
| Hugging Face | Parcial (OCR) | Gratis | Modelos limitados |

## Hallazgos clave

### [VERIFICADO]
1. Qwen3.5:9b-mlx funciona para gráficos simples (14/19 frames, 74%)
2. Qwen3.5:9b-mlx falla en gráficos complejos (5/19 timeout, 26%)
3. Incluso con imagen 320x176 y prompt de 1 línea → timeout 300s+
4. OCR (Tesseract) funciona y es rápido (0.2s/imagen)
5. Nous API free models son text-only (no vision)
6. Nous API paid models requieren créditos

### [NO VERIFICADO]
1. Si el prompt estructurado reduce confusión de instrumentos (sin frames OK en v2)
2. Si la integración de OCR mejora extracción de niveles
3. Si un modelo más rápido resolvería los timeouts

## Opciones para resolver definitivamente

### Opción A: Google AI Studio (Gemini 2.5 Flash)
- **Costo**: Gratis (sin tarjeta de crédito)
- **Velocidad**: ~1-3s por imagen
- **Visión**: Excelente
- **Requisito**: Usuario crea API key en https://aistudio.google.com
- **Riesgo**: Límites de rate (15 RPM free tier)

### Opción B: Optimizar Qwen3.5 local
- **Costo**: Gratis
- **Velocidad**: 5-10 min por imagen (inherentemente lento)
- **Visión**: Buena pero lenta
- **Requisito**: Ninguno
- **Riesgo**: 26% timeout, no viable para producción

### Opción C: Combinar OCR + Qwen3.5 (solo para frames simples)
- **Costo**: Gratis
- **Velocidad**: 0.2s OCR + 5-10 min visión
- **Visión**: Parcial
- **Requisito**: Ninguno
- **Riesgo**: Sigue siendo lento

## Recomendación

**Opción A (Google AI Studio)** es la única solución viable que cumple con:
1. Procesar videos completos sin timeouts
2. Interpretar gráficos con precisión
3. Ser sostenible (sin costes)
4. No depender del Mac como cuello de botella

**Acción requerida del usuario**: Crear una API key gratuita en Google AI Studio (https://aistudio.google.com/apikey). No requiere tarjeta de crédito.

Si el usuario no desea crear la API key, la alternativa es aceptar que el pipeline local con Qwen3.5 solo procesará ~74% de los frames con tiempos de 5-10 minutos por imagen.

## Archivos generados en FASE 3.7
- `experimental/scripts/vision_analyzer_v2.py`
- `experimental/results/vision_analysis_v2.json`
- `reports/phase_3_7_root_cause_analysis.md`
- `reports/phase_3_7_ocr_diagnostics.md`
- `reports/phase_3_7_pipeline_comparison.md`
- `reports/phase_3_7_validation_matrix.md`
- `reports/phase_3_7_final_report.md`
- `reports/phase_3_7_implementation_results.md`
- `reports/phase_3_7_implementation_final.md`
- `reports/phase_3_7_final_definitive.md`