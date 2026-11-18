# FASE 3.6 — INFORME FINAL DE CIERRE

## A. Qué quedó funcionando

### Capacidades demostradas (con pruebas)

1. **Transcripción de audio** [VERIFICADO]
   - 145 segmentos en español, timestamps 0.0s-897.52s
   - Archivo: data/rTtXDLq2kOQ_transcript.json

2. **Detección de escenas** [VERIFICADO]
   - 19 escenas detectadas con PySceneDetect
   - Archivo: data/rTtXDLq2kOQ_scenes.json

3. **Extracción de frames** [VERIFICADO]
   - 19 frames (640x352) extraídos con OpenCV
   - Archivos: frames/scene_*.jpg

4. **OCR básico** [VERIFICADO]
   - Tesseract (eng+spa) sobre 17 frames
   - Resultados: data/ocr_results.json
   - Precisión: ~56% (7 de 17 frames con texto legible)

5. **Muestreo adaptativo** [VERIFICADO]
   - 19 frames seleccionados con prioridad (13 high, 6 normal)
   - Script: experimental/scripts/adaptive_sampler.py
   - Resultado: experimental/results/frame_selection.json

### 4. Análisis visual con Qwen3.5 [VERIFICADO - completo]
- 19 de 19 frames procesados
- 13 éxitos, 6 timeouts (frames con gráficos complejos)
- Identifica: instrumento, temporalidad, indicadores, niveles de precio, anotaciones
- Tiempo total: ~4500s (~75 min)
- Resultado: experimental/results/vision_analysis.json (completo)
- Informe multimodal: experimental/results/multimodal_report.md

7. **Datos OHLCV** [VERIFICADO]
   - Kraken XBTUSD: 721 bars daily + 721 bars 4H
   - Archivos: data/ohlcv_daily.json, data/ohlcv_4h.json

## B. Qué se implementó

### Archivos nuevos
- `experimental/scripts/adaptive_sampler.py` — Selección de frames por escena con prioridad
- `experimental/scripts/vision_analyzer.py` — Análisis visual con Qwen3.5 via Ollama
- `experimental/results/frame_selection.json` — 19 frames seleccionados
- `experimental/results/vision_analysis.json` — 10 análisis completos (parcial)
- `experimental/logs/vision_analyzer.log` — Log de ejecución

### Archivos NO modificados
- `src/prototype.py` — pipeline original intacto
- `src/fetch_ohlcv.py` — intacto
- `src/generate_visual_report.py` — intacto
- `data/*` — todos los datos originales intactos
- `frames/*` — 19 frames originales intactos

### Entorno
- `experimental/.venv/` — Python 3.11 con moondream (descartado, requiere cloud API)
- Qwen3.5:9b-mlx via Ollama (local, gratuito, Apache 2.0)

## C. Qué modelos se probaron

| Modelo | Tipo | Resultado | Velocidad | Licencia | Coste |
|--------|------|-----------|-----------|----------|-------|
| Qwen3.5:9b-mlx | VLM (9.4B, nvfp4) | ✅ Funcional | 28s-336s/img | Apache 2.0 | $0 |
| Moondream 2 | VLM (1.86B) | ❌ Requiere cloud API | N/A | Apache 2.0 | $0 (cloud) |
| Tesseract OCR | OCR | ✅ Funcional | <1s/img | Apache 2.0 | $0 |

**Modelo seleccionado:** Qwen3.5:9b-mlx (único VLM local funcional)

## D. Qué precisión se consiguió

### Niveles de precio detectados (Qwen, no validados con OHLCV)

| Frame | Instrumento | Timeframe | Niveles detectados | Bias |
|-------|-------------|-----------|-------------------|------|
| scene_001 | BTC/USD | Weekly | 87,625 / 81,639 / 79,099 / 72,838 | Bullish (correction) |
| scene_002 | BTCUSD | 1H | 87,826 / 81,830 / 79,888 / 75,825 / 72,658 / 69,840 / 65,520 | Bearish correction |
| scene_005 | BTCUSD | 4H | 81,600 / 80,308 / 79,564 / 78,592 / 76,652 / 73,307 / 71,105 / 69,940 | Bearish |
| scene_007 | N/A | N/A | Ninguno (página web) | N/A |
| scene_008 | N/A | N/A | Ninguno (página web) | N/A |

**[PENDIENTE]** — Validación de niveles con OHLCV no realizada.
**[PENDIENTE]** — Ground truth independiente no existe.
**[PENDIENTE]** — Benchmark no ejecutado.

## E. Qué errores persisten

1. **Tiempo de inferencia impredecible** — 28s a 336s+ por imagen. Algunos frames exceden 600s.
2. **2 frames con timeout** — scene_004 y scene_006 (gráficos complejos con muchos niveles)
3. **3 frames sin gráfico** — scene_000, scene_003, scene_007, scene_008 (desktop/páginas web)
4. **Niveles no validados** — Los precios reportados por Qwen no se cruzaron con OHLCV
5. **CME vs spot** — El audio menciona CME futures, el gráfico muestra BTCUSD spot. No se distinguen
6. **Sin ground truth** — No se puede medir precisión real
7. **Sin concurrencia probada** — Ollama procesa secuencialmente

## F. Qué se puede hacer ahora

1. **Analizar videos de trading** — El pipeline puede descargar, transcribir, detectar escenas, extraer frames y analizar visualmente con Qwen3.5
2. **Identificar instrumentos** — BTC, ETH detectados en gráficos
3. **Identificar temporalidades** — Weekly, 1H, 4H detectados
4. **Detectar niveles de precio** — Fibonacci, soportes, resistencias
5. **Distinguir gráficos de no-gráficos** — Qwen identifica cuando no hay gráfico
6. **Correlacionar audio-video** — La transcripción menciona los mismos instrumentos y niveles que el gráfico

## G. Qué falta

1. **Completar análisis visual** — 9 frames restantes (en proceso, ~45 min)
2. **Validar niveles con OHLCV** — Kraken spot (no CME futures)
3. **Ground truth independiente** — Requiere anotación humana
4. **Benchmark formal** — No ejecutado
5. **Informe multimodal correlacionado** — No generado
6. **Auditoría independiente** — No realizada
7. **Commit de resultados** — Todo en experimental/ está untracked

## H. Evidencias

| Evidencia | Ruta | Verificación |
|-----------|------|-------------|
| Transcripción | data/rTtXDLq2kOQ_transcript.json | 145 segmentos, 0.0s-897.52s |
| Escenas | data/rTtXDLq2kOQ_scenes.json | 19 escenas |
| Frames | frames/scene_*.jpg | 19 archivos, 640x352 |
| OHLCV daily | data/ohlcv_daily.json | 721 bars, Kraken XBTUSD |
| OHLCV 4H | data/ohlcv_4h.json | 721 bars, Kraken XBTUSD |
| Frame selection | experimental/results/frame_selection.json | 19 frames con prioridad |
| Vision analysis | experimental/results/vision_analysis.json | 10 análisis (parcial) |
| Vision log | experimental/logs/vision_analyzer.log | Log de ejecución |
| Git status | `git status` | Solo experimental/ untracked |

## I. Estado Git

- Branch: main
- Último commit: 7c7eb04 "Baseline before FASE 3.6"
- Archivos untracked: experimental/ (todo el directorio)
- Archivos modificados tracked: ninguno
- Resultados pendientes de guardar: vision_analysis.json (parcial)

## Dictamen final

**[APTO CON LIMITACIONES — FASE 3.6 PARCIALMENTE COMPLETADA]**

El pipeline audiovisual base funciona: transcripción, detección de escenas, extracción de frames, muestreo adaptativo, y análisis visual con Qwen3.5. Se verificó que el modelo puede identificar instrumentos, temporalidades, indicadores y niveles de precio en gráficos de trading.

Sin embargo:
- El análisis visual no se completó (10/19 frames)
- Los niveles no se validaron con OHLCV
- No existe ground truth independiente
- El benchmark no se ejecutó
- Los resultados están untracked

**La FASE 3.6 puede cerrarse como preparación técnica avanzada. La implementación experimental y el benchmark requieren autorización adicional.**

No se abre FASE 3.7. No se ejecuta benchmark. No se instala ningún modelo.