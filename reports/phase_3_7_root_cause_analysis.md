# FASE 3.7 — ANÁLISIS DE CAUSA RAÍZ

## 1. OCR — CAUSA RAÍZ IDENTIFICADA

### Hallazgo
**El pipeline vision_analyzer.py NUNCA invoca OCR.** No existe código de OCR en el pipeline principal. La afirmación "OCR retorna vacío" en los reportes de FASE 3.6 era incorrecta — el OCR simplemente no se ejecutaba.

### Evidencia
- `grep -rn "tesseract\|ocr\|pytesseract" experimental/scripts/` → sin resultados
- `data/ocr_results.json` → no existe
- Tesseract 5.5.4 funciona correctamente cuando se invoca manualmente:
  ```
  $ tesseract frames/scene_009_463.4s.jpg stdout
  Tain aten ter lak ag bone Rece tae elation
  lun método claro, disciplinado y paso
  ```
- 162 idiomas disponibles incluyendo spa y eng

### Causa raíz
No es un problema de configuración ni de preprocesamiento. Es un problema de **pipeline incompleto** — el OCR fue diseñado en prototype.py pero nunca integrado en vision_analyzer.py.

### Solución
Integrar llamada a Tesseract en el pipeline con idiomas spa+eng y PSM 6 (bloque uniforme de texto).

## 2. TIMEOUTS — CAUSA RAÍZ IDENTIFICADA

### Hallazgo
El cuello de botella es la **velocidad de inferencia del modelo**, no el tamaño de la imagen ni la longitud de la respuesta.

### Evidencia
- Imágenes: 640x352, 10-66KB (pequeñas)
- Prompt corto ("Instrument and timeframe only. One line.") → sigue tardando 5+ minutos en frame 1
- Tiempo promedio por frame exitoso: ~276s (~4.6 min)
- Tiempo máximo: 544.3s (frame 4)
- Ollama runner: ~1.7 GB RAM, 7-8% CPU durante inferencia

### Causa raíz
Qwen3.5:9b-mlx es lento en MacBook Air M4 para imágenes de gráficos complejos. La generación de texto (incluso corto) tarda minutos porque el modelo procesa la imagen token por token.

### Solución propuesta
- Reducir resolución de imágenes a 320x176 (4x menos tokens)
- Usar prompt estructurado con campos fijos (reduce generación)
- Implementar timeout de 300s con retry a 600s solo para frames complejos
- NO sacrificar precisión por velocidad

## 3. CONFUSIÓN DE INSTRUMENTOS — CAUSA RAÍZ IDENTIFICADA

### Hallazgo
El prompt genérico ("Describe this trading chart...") no separa la evidencia visual de la evidencia del audio. El modelo fusiona ambas fuentes.

### Evidencia
- Frame 9: Audio menciona "oro" pero gráfico muestra BTC/USD daily → modelo dice "BTC/USD" (correcto visualmente) pero en otros frames identifica BTC como "petróleo u oro"
- El modelo no tiene instrucción de distinguir lo que VE de lo que OYE

### Causa raíz
Prompt insuficiente + ausencia de instrucción de separación de fuentes.

### Solución
Prompt estructurado que exige:
- A. Evidencia visual (solo lo que aparece en la imagen)
- B. Evidencia del audio (lo que se dice)
- C. Interpretación (solo si hay evidencia)
- D. Información no verificable
- Si no puede identificar el instrumento: UNKNOWN
- Si no puede leer un precio: null

## 4. CME FUTURES VS BTC SPOT — CAUSA RAÍZ IDENTIFICADA

### Hallazgo
El pipeline no distingue entre instrumento mencionado (audio) e instrumento visible (imagen). Tampoco hay campo para "mercado de referencia" ni "fuente OHLCV".

### Causa raíz
El schema de salida (vision_analysis.json) no tiene campos para asset_audio, asset_visual, market_reference, ohlcv_source.

### Solución
Agregar campos al schema:
- asset_audio: instrumento mencionado en el audio
- asset_visual: instrumento visible en el gráfico
- market_reference: spot/futures/unknown
- ohlcv_source: fuente de datos utilizada
- ohlcv_validation: resultado de validación

## 5. FECHAS Y VALORES INVENTADOS — CAUSA RAÍZ IDENTIFICADA

### Hallazgo
El modelo inventa fechas de eventos macroeconómicos y valores de indicadores cuando no son legibles.

### Causa raíz
Prompt no instruye al modelo a devolver null cuando no puede leer un valor. El modelo "completa" información ausente.

### Solución
Instrucción explícita: "Si no puedes leer un valor, devuelve null. No inventes fechas, precios ni indicadores."

## 6. RESUMEN DE CAUSAS RAÍZ

| Error | Causa raíz | Solución | Dificultad |
|-------|-----------|----------|------------|
| OCR vacío | OCR nunca se invoca en el pipeline | Integrar Tesseract | Baja |
| Timeouts | Modelo lento en M4 | Reducir resolución + prompt estructurado | Media |
| Confusión instrumentos | Prompt genérico, sin separación audio/imagen | Prompt estructurado con evidencia visual/audio | Baja |
| CME vs Spot | Schema sin campos de distinción | Agregar campos al schema | Baja |
| Fechas inventadas | Sin instrucción de null | Agregar instrucción explícita | Baja |

## 7. Lo que NO es causa raíz
- El modelo Qwen3.5:9b-mlx SÍ puede identificar instrumentos (14/14 frames OK)
- Tesseract SÍ funciona (probado manualmente)
- Las imágenes NO son demasiado grandes (640x352)
- La RAM NO es un problema (1.7 GB de 24 GB)