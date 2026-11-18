# Investigacion — YouTube Agent

## DIRECTIVA: GRATUIDAD Y OPEN SOURCE

Prioridad absoluta a herramientas gratuitas y open source. Sin suscripciones pagas. Sin dependencias obligatorias de APIs comerciales. Free tiers son referencia, no dependencia.

## Repositorios candidatos verificados

### 1. yt-dlp (ADOPTAR)
- **URL:** https://github.com/yt-dlp/yt-dlp
- **Funcion:** Descarga de video y audio de YouTube (y 1000+ sitios)
- **Licencia:** Unlicense (dominio publico)
- **Open source:** Si (completo)
- **Coste:** $0
- **Compatibilidad Apple Silicon:** Si
- **Recomendacion:** ADOPTAR COMO CANDIDATO

### 2. faster-whisper (ADOPTAR)
- **URL:** https://github.com/SYSTRAN/faster-whisper
- **Funcion:** Transcripcion de audio con timestamps (CTranslate2)
- **Licencia:** MIT
- **Open source:** Si (completo)
- **Coste:** $0
- **Compatibilidad Apple Silicon:** Si (CPU mode)
- **Recomendacion:** ADOPTAR COMO CANDIDATO (modelo small/medium)

### 3. PySceneDetect (ADOPTAR)
- **URL:** https://github.com/Breakthrough/PySceneDetect
- **Funcion:** Deteccion de cambios de escena en video
- **Licencia:** BSD 3-Clause
- **Open source:** Si (completo)
- **Coste:** $0
- **Compatibilidad Apple Silicon:** Si
- **Recomendacion:** ADOPTAR COMO CANDIDATO

### 4. chart-vision-mcp (ADOPTAR — NUEVO)
- **URL:** https://github.com/nessos666/chart-vision-mcp
- **Funcion:** Analisis estructural de graficos TradingView con OpenCV + Tesseract OCR
- **Licencia:** MIT
- **Open source:** Si (completo)
- **Coste:** $0 (sin API keys, sin GPU, offline)
- **Compatibilidad Apple Silicon:** Si
- **Ventajas:** Analisis estructural instantaneo (colores de velas, niveles, zonas, volumen, OCR), sin alucinaciones de LLM, MCP server integrable con Hermes
- **Limitaciones:** Analisis estructural, no semantico (no "entiende" el grafico como un LLM)
- **Recomendacion:** ADOPTAR COMO CANDIDATO — complementa a un modelo de vision

### 5. Financial-Chart-Understanding-System (INVESTIGAR — NUEVO)
- **URL:** https://github.com/VT69/Financial-Chart-Understanding-System
- **Funcion:** Deteccion de patrones de velas con YOLOv8 + fusion OHLCV
- **Licencia:** (verificar)
- **Open source:** Si (codigo disponible)
- **Coste:** $0
- **Compatibilidad Apple Silicon:** Parcial (YOLOv8, CPU posible)
- **Ventajas:** 13 patrones de velas, 89.4% mAP, dashboard XAI
- **Limitaciones:** Requiere entrenamiento, dependencias pesadas (conda, torch)
- **Recomendacion:** INVESTIGAR MAS (para deteccion de patrones de velas)

### 6. EasyOCR (PROBAR)
- **URL:** https://github.com/JaidedAI/EasyOCR
- **Funcion:** OCR (reconocimiento de texto en imagenes)
- **Licencia:** Apache 2.0
- **Open source:** Si (completo)
- **Coste:** $0
- **Compatibilidad Apple Silicon:** Si (CPU mode)
- **Recomendacion:** PROBAR EN FASE POSTERIOR (vs Tesseract)

### 7. Qwen2.5-VL (INVESTIGAR)
- **URL:** https://github.com/QwenLM/Qwen2.5-VL
- **Funcion:** Modelo de vision multimodal local
- **Licencia:** Apache 2.0
- **Open source:** Si (pesos abiertos)
- **Coste:** $0 (pero requiere 8-16 GB RAM)
- **Compatibilidad Apple Silicon:** Parcial (sin GPU NVIDIA, CPU only)
- **Recomendacion:** INVESTIGAR MAS (considerar servicio remoto gratuito en su lugar)

### 8. pine-script-builder (REFERENCIA)
- **URL:** https://github.com/learngermanbd/pine-script-builder
- **Funcion:** Generacion de Pine Script para TradingView
- **Licencia:** (verificar)
- **Open source:** Si (codigo disponible)
- **Coste:** $0
- **Recomendacion:** INVESTIGAR MAS (para reconstruccion de graficos)

### 9. Lightweight Charts (ADOPTAR — NUEVO)
- **URL:** https://github.com/nicholasgasior/lightweight-charts (o TradingView oficial)
- **Funcion:** Graficos financieros interactivos open source
- **Licencia:** Apache 2.0
- **Open source:** Si (completo)
- **Coste:** $0
- **Ventajas:** Graficos OHLCV profesionales, sin dependencias de TradingView
- **Recomendacion:** ADOPTAR COMO CANDIDATO (para reconstruccion de graficos desde datos)

### 10. Chart Pattern Analyzer (DESCARTAR)
- **URL:** https://github.com/raulduke9119/chart-pattern-analyzer
- **Funcion:** Analisis de patrones en graficos
- **Licencia:** (verificar)
- **Limitaciones:** Depende de OpenRouter Vision (API paga) y Binance API
- **Recomendacion:** DESCARTAR (dependencia de API paga)

## Modelos de vision gratuitos (local)

| Modelo | Tipo | RAM | Coste | Open source | Compatibilidad Mac |
|---|---|---|---|---|---|
| Qwen2.5-VL 7B | Multimodal | 8-16 GB | $0 | Si (Apache 2.0) | Parcial (CPU) |
| LLaVA 7B | Multimodal | 8-16 GB | $0 | Si (Apache 2.0) | Parcial (CPU) |
| Moondream 2 | Multimodal | 2-4 GB | $0 | Si (Apache 2.0) | Si |
| BLIP-2 | Vision+Language | 4-8 GB | $0 | Si (BSD) | Si |

## Hallazgo importante: Vision LLMs para charts

Segun audit empirico (roman-rr/trading-skills):
- 4 modelos de vision (Anthropic, Google) en 40 senales crypto
- Resultado: 51% de precision direccional, 1/215 patrones, 100% long-bias en Gemini
- Conclusion: Ningun vision LLM es confiable para analisis direccional de patrones en charts
- Recomendacion: Usar analisis estructural (chart-vision-mcp) + LLM para interpretacion semantica

## Stack tecnologico recomendado (V1, 100% gratuito)

| Componente | Herramienta | Coste | Alternativa |
|---|---|---|---|
| Descarga video/audio | yt-dlp | $0 | — |
| Procesamiento multimedia | ffmpeg | $0 | — |
| Transcripcion | faster-whisper (small) | $0 | whisper.cpp |
| Deteccion de escenas | PySceneDetect | $0 | ffmpeg scenedetect |
| Extraccion de frames | OpenCV / ffmpeg | $0 | — |
| Analisis estructural de charts | chart-vision-mcp | $0 | — |
| OCR | Tesseract (vs EasyOCR) | $0 | EasyOCR |
| Vision semantica | Qwen2.5-VL (local) o Moondream | $0 | Servicio remoto gratuito |
| Reconstruccion graficos | Lightweight Charts | $0 | — |
| Orquestacion | Scripts Python simples | $0 | — |

## Clasificacion final

- **ADOPTAR:** yt-dlp, ffmpeg, faster-whisper, PySceneDetect, chart-vision-mcp, Tesseract, Lightweight Charts
- **PROBAR:** Moondream 2 (vision ligero), EasyOCR, stable-ts
- **INVESTIGAR MAS:** Qwen2.5-VL, Financial-Chart-Understanding-System, pine-script-builder
- **DESCARTAR:** Chart Pattern Analyzer (depende de API paga), Celery (excesivo), pytube (menos mantenido)

## Licencias (todas gratuitas y open source)

- yt-dlp: Unlicense (dominio publico)
- faster-whisper: MIT
- PySceneDetect: BSD 3-Clause
- chart-vision-mcp: MIT
- EasyOCR: Apache 2.0
- Qwen2.5-VL: Apache 2.0
- Moondream: Apache 2.0
- Lightweight Charts: Apache 2.0
- Tesseract: Apache 2.0
