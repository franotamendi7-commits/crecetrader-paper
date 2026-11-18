# FASE 3.3 — Auditoría del Pipeline Visual Actual

## 1. Archivos auditados

- src/prototype.py (563 líneas)
- src/fetch_ohlcv.py
- src/generate_visual_report.py
- data/rTtXDLq2kOQ_transcript.json (145 segmentos)
- data/ocr_results.json (17 frames)
- frames/scene_1..17_frame.jpg

## 2. Pipeline actual

### Paso 1: Descarga de video
- yt-dlp con formato "best"
- Descarga video completo (~899s, MP4)
- ✅ Funciona

### Paso 2: Extracción de audio
- yt-dlp con formato WAV
- ✅ Funciona

### Paso 3: Transcripción
- faster-whisper, modelo "small", español
- 145 segmentos con timestamps
- ✅ Funciona (con errores numéricos conocidos)

### Paso 4: Detección de escenas
- PySceneDetect ContentDetector, threshold 30.0
- 17 escenas detectadas
- ⚠️ Muchas escenas largas (scene_3: 293.7s)
- ⚠️ Umbral alto = pocas escenas en momentos de cambio visual

### Paso 5: Extracción de frames
- 1 frame por escena, en el centro de la escena
- OpenCV VideoCapture
- ✅ Funciona técnicamente
- ⚠️ 1 frame por escena es insuficiente para escenas largas

### Paso 6: OCR
- Tesseract (spa+eng)
- Pre-procesamiento: Otsu threshold + morfología
- PSM 6 (bloque de texto)
- ✅ Funciona para texto claro
- ⚠️ 56% exactitud, 7 niveles ilegibles

### Paso 7: Generación de informe
- Markdown con transcripción + OCR + clasificación
- Clasificación por keywords (heurística)
- ⚠️ Clasificación no semántica

## 3. Limitaciones identificadas

### 3.1 Muestreo visual
- 1 frame por escena = insuficiente
- Escenas largas (293.7s) con 1 solo frame
- No detecta cambios de gráfico dentro de una escena
- No prioriza momentos importantes

### 3.2 OCR
- Tesseract exactitud ~56%
- Sin pre-procesamiento avanzado (resize, sharpen, contrast)
- PSM 6 no es óptimo para gráficos
- No distingue entre texto y estructura visual

### 3.3 Comprensión visual
- NO hay comprensión semántica de gráficos
- No se identifican velas, indicadores, líneas, patrones
- No se distingue entre instrumentos visualmente
- No se identifican temporalidades en gráficos
- No se relaciona audio con video

### 3.4 Hardware
- MacBook Air M4, 24 GB RAM
- Ollama: qwen3.5:9b-mlx (8.9 GB)
- No hay GPU dedicada (Apple Silicon)
- ~15 GB RAM disponible para nuevos modelos

### 3.5 Dependencias actuales
- yt-dlp, faster-whisper, scenedetect, opencv-python, pytesseract, numpy, Pillow
- NO: torch, transformers, moondream, easyocr, paddleocr

## 4. Componentes reutilizables

- ✅ Descarga de video (yt-dlp)
- ✅ Extracción de audio (yt-dlp)
- ✅ Transcripción (faster-whisper)
- ✅ Detección de escenas (PySceneDetect)
- ✅ Extracción de frames (OpenCV)
- ✅ Generación de informes (Markdown)
- ⚠️ OCR (Tesseract) — reutilizable pero mejorable
- ❌ Comprensión visual — NO existe

## 5. Componentes necesarios

1. **Muestreo adaptativo** — Extraer múltiples frames por escena larga
2. **Pre-procesamiento de imagen** — Resize, sharpen, contrast para OCR
3. **Modelo de visión** — Para comprensión semántica de gráficos
4. **Sincronización audiovisual** — Relacionar audio con frames
5. **Estructuración de resultados** — Formato JSON para análisis visual

## 6. Diagnóstico técnico

El pipeline actual es un sistema de procesamiento audiovisual básico:
- Transcribe audio ✅
- Detecta escenas ✅
- Extrae frames ✅
- Ejecuta OCR ✅
- Genera informes ✅

Pero NO comprende visualmente:
- No identifica gráficos ❌
- No reconoce velas ❌
- No detecta indicadores ❌
- No identifica soportes/resistencias ❌
- No relaciona audio con video ❌

**El principal gap es la ausencia de un modelo de visión que pueda interpretar gráficos financieros.**

## 7. Recomendación

Investigar modelos de visión open source/open weights que puedan ejecutarse en Apple Silicon M4 con 24 GB RAM. Priorizar Moondream 2 (2.2 GB, open weights) o Qwen-VL (requiere transformers+torch, mayor consumo).

**[VERIFICADO]** — Pipeline actual auditado
**[VERIFICADO]** — Limitaciones identificadas
**[VERIFICADO]** — Hardware: M4, 24GB RAM, ~15GB disponible
**[PENDIENTE]** — Selección de modelo de visión
**[PENDIENTE]** — Implementación de muestreo adaptativo
EOF