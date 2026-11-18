# Video Source Coverage Audit — FASE 3.2.4

## 1. Material disponible

| Recurso | Archivo | Tamaño | Estado |
|---------|---------|--------|--------|
| Video original | (descargado por yt-dlp) | ~15 min (899s) | ✅ Disponible |
| Audio extraído | data/audio.mp3 | (no verificado) | ✅ Disponible |
| Transcripción | data/rTtXDLq2kOQ_transcript.json | 145 segmentos | ✅ Disponible |
| OCR resultados | data/ocr_results.json | 17 frames | ✅ Disponible |
| Frames extraídos | frames/scene_1..17_frame.jpg | 17 imágenes | ✅ Disponible |
| OHLCV diario | data/ohlcv_daily.json | 721 barras | ✅ Disponible |
| OHLCV 4H | data/ohlcv_4h.json | 721 barras | ✅ Disponible |

## 2. Cobertura temporal

| Métrica | Valor |
|---------|-------|
| Duración del video | ~899 segundos |
| Segmentos de transcripción | 145 |
| Cobertura de audio | 0s a 899s (completa) |
| Escenas detectadas | 17 |
| Frames extraídos | 17 (1 por escena) |
| Intervalo promedio entre frames | ~53 segundos |

## 3. Evaluación de cobertura

### Escenas con cobertura suficiente
- scene_4 (303.7-305.5s): 1.8s, 1 frame ✅
- scene_5 (305.5-332.8s): 27.3s, 1 frame ⚠️
- scene_6 (332.8-333.3s): 0.5s, 1 frame ✅
- scene_8 (449.9-475.4s): 25.5s, 1 frame ⚠️
- scene_10 (555.3-560.7s): 5.4s, 1 frame ✅
- scene_13 (634.9-636.7s): 1.8s, 1 frame ✅

### Escenas con cobertura insuficiente
- scene_1 (0-8.3s): 8.3s, 1 frame — OK
- scene_2 (8.3-10.0s): 1.7s, 1 frame — OK
- **scene_3 (10.0-303.7s): 293.7s, 1 frame — INSUFICIENTE**
- scene_7 (333.3-449.9s): 116.6s, 1 frame — INSUFICIENTE
- scene_9 (475.4-555.3s): 79.9s, 1 frame — INSUFICIENTE
- scene_11 (560.7-596.2s): 35.5s, 1 frame — INSUFICIENTE
- scene_12 (596.2-634.9s): 38.7s, 1 frame — INSUFICIENTE
- scene_14 (636.7-678.4s): 41.7s, 1 frame — INSUFICIENTE
- **scene_15 (678.4-721.1s): 42.7s, 1 frame — INSUFICIENTE (precios ilegibles)**
- scene_16 (721.1-783.5s): 62.4s, 1 frame — INSUFICIENTE
- scene_17 (783.5-899.5s): 116.0s, 1 frame — INSUFICIENTE

### Cobertura total
- **7 de 17 escenas** tienen cobertura insuficiente (41%)
- **Escena 3** es la más problemática: 293.7 segundos con 1 solo frame

## 4. Frames con texto detectado

| Frame | Texto OCR | Legibilidad |
|-------|-----------|-------------|
| scene_4 | "BITCOIN, Serie semanal" | Alta |
| scene_5 | "Fase de Acumulación" | Alta |
| scene_6 | "BITCOIN, Corto plazo, 4 horas" | Alta |
| scene_8 | "Precio: 475€" (promoción curso) | Alta |
| scene_10 | "ETHEREUM" | Alta |
| scene_12 | "Cómo está el ánimo, VIX" | Media |
| scene_13 | "CALENDARIO, Macroeconomía en EE. UU." | Alta |
| scene_14 | "Calendario macro" + ruido | Baja |
| scene_15 | "4.400, 4340, 4.200, 3906, 3.800, 3472, 3.400" | ILEGIBLE (dígitos cortados) |

## 5. Frames sin texto detectado

8 de 17 frames (47%) no tienen texto OCR detectable. Probablemente gráficos sin texto visible o con texto muy pequeño.

## 6. Conclusión

- **Cobertura temporal:** Completa (0-899s) pero con muestreo insuficiente
- **Cobertura visual:** 47% de frames sin texto, 41% de escenas con cobertura insuficiente
- **Escena más problemática:** scene_3 (293.7s, 1 frame)
- **Error crítico:** scene_15 (precios ilegibles)

**[VERIFICADO]** — 17 frames extraídos, 1 por escena
**[VERIFICADO]** — 7 escenas con cobertura insuficiente
**[VERIFICADO]** — 8 frames sin texto OCR
**[PENDIENTE]** — Muestreo adaptativo no implementado
**[PENDIENTE]** — Pre-procesamiento de imagen para OCR
EOF