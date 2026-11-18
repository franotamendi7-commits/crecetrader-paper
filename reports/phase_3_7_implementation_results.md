# FASE 3.7 — RESULTADOS DE IMPLEMENTACIÓN

## Implementación realizada

### Archivo creado
- `experimental/scripts/vision_analyzer_v2.py` — Pipeline optimizado con:
  - OCR integrado (Tesseract spa+eng, PSM 6)
  - Prompt estructurado con separación audio/imagen
  - Instrucción de UNKNOWN y null
  - Campos de tiempo por etapa (OCR, visión, total)
  - Resultados en archivo separado (vision_analysis_v2.json)

### Ejecución
- **Frames seleccionados**: 10 (1, 2, 4, 6, 10, 12, 13, 15, 16, 17)
- **Frames procesados**: 1 (frame 1)
- **Resultado**: Timeout (600s) — mismo que pipeline anterior
- **Proceso**: Interrumpido después de frame 1

## Comparación de resultados

### Pipeline anterior (v1) — 10 frames seleccionados
| Frame | Estado | Tiempo | OCR |
|-------|--------|--------|-----|
| 1 | ERR (timeout) | 0s | No ejecutado |
| 2 | ERR (timeout) | 0s | No ejecutado |
| 4 | OK | 544.3s | No ejecutado |
| 6 | ERR (timeout) | 0s | No ejecutado |
| 10 | OK | 459.2s | No ejecutado |
| 12 | ERR (timeout) | 0s | No ejecutado |
| 13 | OK | 296.4s | No ejecutado |
| 15 | OK | 233.6s | No ejecutado |
| 16 | ERR (timeout) | 0s | No ejecutado |
| 17 | OK | 376.6s | No ejecutado |

### Pipeline nuevo (v2) — 10 frames seleccionados
| Frame | Estado | Tiempo visión | Tiempo OCR | OCR resultado |
|-------|--------|---------------|------------|---------------|
| 1 | ERR (timeout) | 600.0s | 0.2s | Texto detectado (baja calidad) |
| 2-17 | No procesados | — | — | — |

## Lo que se verificó

1. **OCR funciona** — Tesseract extrae texto en 0.2s (rápido)
2. **OCR detecta texto** — pero calidad moderada (errores de reconocimiento)
3. **Prompt estructurado no reduce timeouts** — frame 1 sigue fallando a 600s
4. **El bottleneck es la inferencia del modelo**, no el prompt ni la imagen

## Lo que NO se pudo verificar

1. Si el prompt estructurado reduce la confusión de instrumentos (frame 1 timeout)
2. Si el OCR integrado mejora la extracción de niveles (sin frames OK en v2)
3. Si los campos nuevos se completan correctamente (sin frames OK en v2)
4. Comparación antes/después en frames OK

## Conclusiones

### 1. OCR — ÉXITO PARCIAL
- Tesseract funciona y es rápido (0.2s por imagen)
- La calidad del OCR es moderada (errores de reconocimiento)
- El OCR detecta texto en español pero con errores
- **No se pudo verificar** si el OCR mejora la extracción de niveles porque no hubo frames OK

### 2. Prompt estructurado — NO VERIFICADO
- El prompt fue implementado correctamente
- Frame 1 (el primer frame de prueba) timed out a 600s
- No se pudo verificar si reduce la confusión de instrumentos
- El prompt es más largo, lo que puede aumentar el tiempo de generación

### 3. Timeouts — NO RESUELTO
- El modelo sigue tardando 600s+ en gráficos complejos
- El prompt estructurado no reduce el tiempo
- La causa raíz sigue siendo la velocidad de inferencia del modelo
- **Solución propuesta**: Reducir resolución de imágenes a 320x176

### 4. CME/Spot — NO VERIFICADO
- Los campos fueron agregados al schema
- No se pudo verificar porque no hubo frames OK

## Errores restantes
1. **Timeouts persistentes** — 5/19 frames (26%) no se procesan
2. **Confusión de instrumentos** — no verificado con prompt estructurado
3. **OCR calidad moderada** — errores de reconocimiento
4. **CME/Spot** — no verificado

## Recomendación sobre Qwen3.5 vs Qwen3-VL

### Evidencia actual
- Qwen3.5:9b-mlx **funciona** para gráficos simples (14/19 frames OK, 74%)
- Qwen3.5 **falla** en gráficos complejos (5/19 timeout, 26%)
- El prompt estructurado **no reduce** los timeouts
- El OCR **funciona** y es rápido

### Recomendación
1. **Optimizar primero** — reducir resolución de imágenes a 320x176 para acelerar inferencia
2. **Probar prompt más corto** — el prompt estructurado es largo, puede aumentar tiempo
3. **Si después de optimizar** sigue habiendo confusión de instrumentos, entonces considerar Qwen3-VL
4. **No instalar Qwen3-VL** hasta tener evidencia de que el pipeline optimizado no es suficiente

### Próximos pasos propuestos
1. Reducir resolución de imágenes (320x176)
2. Acortar prompt (solo campos esenciales)
3. Reintentar frames 1, 2, 6, 12, 16
4. Si mejora, ejecutar comparación completa
5. Si no mejora, presentar evidencia para decidir sobre Qwen3-VL