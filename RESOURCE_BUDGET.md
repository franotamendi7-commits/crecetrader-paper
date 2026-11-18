# Presupuesto de Recursos — YouTube Trading Agent

## Hardware disponible

- MacBook Air M4
- 24 GB RAM
- 512 GB almacenamiento
- macOS 15.5

## Principios

1. Procesamiento bajo demanda (no cargar todos los modelos simultaneamente)
2. Modelos locales cuando tengan sentido (Whisper local, OCR local)
3. Servicios remotos cuando ofrezcan ventajas claras (vision LLM)
4. Liberar recursos despues del procesamiento
5. Limitar concurrencia
6. Evitar duplicacion de herramientas
7. Mantener checkpoints y recuperacion

## Estimacion de consumo por componente

| Componente | RAM estimada | CPU | Notas |
|---|---|---|---|
| yt-dlp (descarga) | ~100 MB | Bajo | Descarga de audio/video |
| ffmpeg (procesamiento) | ~200 MB | Medio | Conversion, extraccion de frames |
| Whisper (transcripcion) | ~2-4 GB | Alto | Modelo small/medium |
| faster-whisper | ~1-3 GB | Medio-Alto | Optimizado con CTranslate2 |
| PySceneDetect | ~500 MB | Medio | Deteccion de escenas |
| OpenCV (frames) | ~500 MB | Medio | Extraccion de frames |
| EasyOCR | ~1-2 GB | Medio | OCR de graficos |
| Qwen2.5-VL (local) | ~8-16 GB | Alto | Modelo de vision (si se usa) |
| LLaVA (local) | ~8-16 GB | Alto | Modelo de vision (si se usa) |

## Reglas de uso

- No cargar mas de 2 modelos pesados simultaneamente
- Liberar memoria despues de cada paso del pipeline
- Usar modelos small/medium para Whisper (no large)
- Preferir servicios remotos para vision (GPT-4o, Claude) si la calidad es superior
- Monitorear consumo de RAM durante procesamiento

## Almacenamiento estimado

| Dato | Tamaño estimado |
|---|---|
| Video (1 video, 30 min) | ~100-500 MB |
| Audio extraido | ~10-30 MB |
| Transcripcion | ~50-200 KB |
| Frames extraidos (100 frames) | ~10-50 MB |
| Analisis (JSON/Markdown) | ~10-50 KB por video |
| Total por video | ~120-580 MB |
| 100 videos | ~12-58 GB |
