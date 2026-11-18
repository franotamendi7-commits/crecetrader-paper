# Arquitectura del Agente Persistente — YouTube Trading Agent

## Objetivo

Construir un agente que vigile el canal CreceTrader/Bitcoin Hoy, detecte automáticamente cada publicación nueva, analice su contenido y prepare un informe diario para Francisco. Debe funcionar de forma continua, recuperar su estado después de reinicios y mantener memoria selectiva.

## A. MONITOR DEL CANAL

- Consultar el canal periódicamente (cada N minutos)
- Detectar publicaciones nuevas por ID único (video_id)
- Registrar fecha y hora de detección
- Evitar duplicados (comparar con lista de procesados)
- Recuperar publicaciones no procesadas después de reinicio
- Fuente: YouTube Data API v3 (free tier: 10,000 units/día) o yt-dlp --flat-playlist

## B. COLA DE PROCESAMIENTO

Estados posibles:
- PENDING: Video detectado, pendiente de procesar
- PROCESSING: En proceso de análisis
- COMPLETED: Análisis completado
- FAILED: Fallo en procesamiento (con reintentos)
- SKIPPED: Video no relevante (ej: shorts, no trading)

Persistencia: SQLite local (estado de la cola)

Campos por video:
- video_id (PK)
- title
- published_at
- detected_at
- status
- priority
- retry_count
- last_error
- completed_at

## C. PIPELINE DE PROCESAMIENTO

1. Descarga de audio (yt-dlp)
2. Transcripción (faster-whisper, con timestamps)
3. Detección de escenas (PySceneDetect)
4. Extracción de frames (ffmpeg, 1 por escena)
5. Análisis estructural de charts (chart-vision-mcp)
6. OCR de graficos (Tesseract)
7. Análisis de vision (modelo local o servicio gratuito)
8. Interpretación y clasificación ([DICE], [OBSERVADO], [INFERIDO])
9. Reconstrucción de graficos (Lightweight Charts, si hay datos)
10. Generación de informe (Markdown + JSON)

## D. MEMORIA SELECTIVA

Almacenamiento: SQLite + FTS5 (similar a Hermes Memory Vault)

Tablas:
- videos: Historial de videos analizados
- methodology: Metodología extraída (indicadores, parámetros, niveles)
- scenarios: Escenarios identificados
- criteria_changes: Cambios de criterio del analista
- contradictions: Contradicciones detectadas
- evidence: Evidencias originales (referencias a frames, timestamps)

Búsqueda: Por instrumento, temporalidad, fecha, concepto (FTS5)

## E. INFORMES

### Informe individual por video
- Resumen del video
- Instrumentos analizados
- Temporalidades
- Niveles y zonas
- Indicadores mencionados
- Escenarios propuestos
- Clasificación: [DICE], [OBSERVADO], [INFERIDO]
- Referencias temporales al video
- Nivel de confianza
- Datos desconocidos

### Resumen diario
- Videos procesados en el día
- Cambios importantes respecto a análisis anteriores
- Nuevos niveles o escenarios
- Contradicciones detectadas

## F. RECUPERACIÓN

- Persistir estado en SQLite (cola + memoria)
- Sobrevivir a reinicios (estado en disco)
- No perder videos pendientes (cola persistente)
- No duplicar informes (idempotencia por video_id)
- Registrar errores (log de fallos)
- Permitir reanudar procesos interrumpidos (checkpoint por paso)

## G. AUTOMATIZACIÓN FUTURA (después de validación)

1. Vigilar canal automáticamente
2. Detectar video nuevo
3. Añadir a cola
4. Procesar automáticamente
5. Actualizar memoria metodológica
6. Generar informe
7. Notificar por Discord
8. Conservar informe para consulta posterior

Frecuencia: Detectar y procesar publicaciones nuevas diariamente, idealmente poco después de publicación.

## H. RECURSOS ESTIMADOS

| Componente | RAM | CPU | Disco |
|---|---|---|---|
| Monitor (yt-dlp flat-playlist) | ~50 MB | Bajo | — |
| Cola (SQLite) | ~10 MB | Bajo | ~1 MB |
| Pipeline completo | ~4-6 GB | Alto | ~500 MB/video |
| Memoria (SQLite+FTS5) | ~20 MB | Bajo | ~10 MB/100 videos |
| Informes | ~10 MB | Bajo | ~50 KB/video |

## I. COSTE RECURRENTE

$0 — Todo el stack es gratuito y open source. Sin suscripciones.

## J. RIESGOS

- YouTube puede cambiar su estructura (yt-dlp se actualiza frecuentemente)
- Free tiers de APIs pueden cambiar (no dependemos de ellos)
- Modelos locales pueden ser lentos en CPU (Mac sin GPU NVIDIA)
- Calidad de vision local puede ser inferior a servicios comerciales
- Transcripción en español puede tener errores (requiere validación)
