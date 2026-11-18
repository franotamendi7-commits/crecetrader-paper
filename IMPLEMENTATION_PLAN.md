# IMPLEMENTATION PLAN — YouTube Trading Agent

## Fecha: 2026-11-09

## 1. STACK MÍNIMO (Fase 1)

| Componente | Herramienta | Instalación |
|---|---|---|
| Descarga | yt-dlp | pip install yt-dlp |
| Multimedia | ffmpeg | brew install ffmpeg (si no está) |
| Transcripción | faster-whisper | pip install faster-whisper |
| Escenas | PySceneDetect | pip install scenedetect |
| Frames | OpenCV | pip install opencv-python |
| Charts | chart-vision-mcp | git clone + pip install |
| OCR | Tesseract | brew install tesseract |
| Visión | Moondream 2 | pip install transformers (o Ollama) |
| Gráficos | Lightweight Charts | npm/pip (JS library) |
| Indicadores | pandas-ta | pip install pandas-ta |
| DB | SQLite + FTS5 | Built-in (Python) |

## 2. ORDEN DE DESARROLLO

### Paso 1: Descarga y transcripción (1-2 días)
1. Instalar yt-dlp, ffmpeg, faster-whisper
2. Descargar audio de un video del canal
3. Transcribir con timestamps
4. Validar calidad en español

### Paso 2: Extracción de frames (1 día)
1. Instalar PySceneDetect, OpenCV
2. Detectar escenas en el video
3. Extraer 1 frame por escena
4. Validar que los frames capturan los gráficos

### Paso 3: Análisis estructural de charts (1-2 días)
1. Instalar chart-vision-mcp, Tesseract
2. Analizar frames con chart-vision-mcp
3. Extraer texto con Tesseract
4. Validar que se detectan niveles, velas, indicadores

### Paso 4: Visión semántica (1-2 días)
1. Instalar Moondream 2 (o Qwen2.5-VL)
2. Analizar frames con el modelo de vision
3. Relacionar con la transcripción
4. Clasificar: [DICHO], [OBSERVADO], [INFERIDO]

### Paso 5: Persistencia y memoria (1 día)
1. Crear base de datos SQLite + FTS5
2. Implementar cola de procesamiento
3. Implementar memoria de metodología
4. Implementar generación de informes

### Paso 6: Validación del primer video (1 día)
1. Procesar video completo
2. Generar informe
3. Validación manual por Francisco
4. Iterar según feedback

## 3. DELEGACIÓN DE MODELOS (OpenCode)

| Tarea | Modelo recomendado | Razón |
|---|---|---|
| Instalación y setup | Beam / DeepSeek | Programación general |
| Pipeline de descarga/transcripción | DeepSeek | Código Python |
| Análisis de charts | Beam | Razonamiento + visión |
| Persistencia y DB | DeepSeek | SQL + Python |
| Auditoría independiente | GLM | Revisión de código |
| Documentación | Beam | Redacción técnica |

## 4. PRUEBA DE ACEPTACIÓN (Primer Video)

### Video seleccionado
El video más reciente del canal CreceTrader / Bitcoin Hoy

### Criterios de validación manual

| Criterio | Peso | Validación |
|---|---|---|
| Transcripción en español (calidad) | Alto | Francisco lee y compara |
| Sincronización audio-video | Medio | Timestamps correctos |
| Detección de cambios visuales | Medio | Frames capturan gráficos |
| Reconocimiento de instrumentos | Alto | BTC, ETH, etc. identificados |
| Reconocimiento de temporalidades | Alto | 1D, 4H, etc. identificadas |
| Lectura de precios y niveles | Alto | Números correctos |
| Identificación de indicadores | Alto | RSI, MACD, etc. identificados |
| Comprensión de metodología | Alto | Escenarios, condiciones, invalidaciones |
| Clasificación [DICHO]/[OBSERVADO]/[INFERIDO] | Alto | Correcta clasificación |
| Calidad de reconstrucción gráfica | Medio | Gráfico se parece al original |

### Rúbrica de puntuación

- 9-10: Excelente — listo para automatización
- 7-8: Bueno — necesita ajustes menores
- 5-6: Aceptable — necesita mejoras
- 3-4: Deficiente — revisar approach
- 1-2: Fallido — reevaluar stack

### Objetivo mínimo: 7/10 en criterios de peso Alto

## 5. RECURSOS ESTIMADOS

| Recurso | Estimación |
|---|---|
| RAM (pico) | 4-6 GB |
| CPU | Alto durante procesamiento |
| Disco por video | ~500 MB |
| Disco por 100 videos | ~50 GB |
| Tiempo por video | 5-15 minutos |
| Coste recurrente | $0 |

## 6. COSTE RECURRENTE PREVISTO

**$0** — Todo el stack es gratuito y open source.

Sin suscripciones. Sin APIs pagas. Sin servicios comerciales.

## 7. RIESGOS PRINCIPALES

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|---|
| Transcripción en español de baja calidad | Media | Alto | Probar modelo medium, validar manualmente |
| Vision local insuficiente para charts | Media | Alto | Arquitectura híbrida, servicio remoto gratuito como respaldo |
| yt-dlp se rompe con cambios de YouTube | Baja | Medio | Actualizar frecuentemente |
| Modelos locales lentos en CPU | Alta | Medio | Procesamiento secuencial, modelos pequeños |
| Free tiers cambian | Media | Bajo | No depender de un solo proveedor |

## 8. CLASIFICACIÓN

- [VERIFICADO]: ffmpeg, Ollama, Kraken API, Hermes Memory Vault (SQLite+FTS5)
- [PROPUESTO]: Stack completo, arquitectura, plan de implementación
- [PENDIENTE]: Todas las pruebas de validación (Fase 1)
