# YouTubeTradingAgent — Contratos y Arquitectura

## 1. Model Manager Contract

### Responsabilidad exclusiva
Controlar carga, descarga y disponibilidad de modelos Ollama. Garantizar exclusión mutua.

### Entrada
```json
{
  "action": "ensure|load|unload|status",
  "model_key": "youtube_analyst|memory_manager",
  "model_name": "qwen2.5vl:3b|qwen3.5:9b-mlx"
}
```

### Salida
```json
{
  "success": true,
  "model_loaded": "qwen2.5vl:3b",
  "ram_before_gb": 13.9,
  "ram_after_gb": 15.5,
  "ram_freed_gb": 0.0,
  "elapsed_seconds": 1.2,
  "error": null
}
```

### Validaciones
- Solo un modelo cargado a la vez
- Verificar liberación de RAM después de unload
- Timeout de 120s para carga
- Timeout de 30s para descarga

### Estados
- `idle`: ningún modelo cargado
- `loading`: modelo en proceso de carga
- `loaded`: modelo disponible
- `unloading`: modelo en proceso de descarga
- `error`: fallo en carga/descarga

## 2. YouTube Analyst Contract

### Responsabilidad exclusiva
Análisis audiovisual de videos de CreceTrader. Interpretación de gráficos.

### Entrada
```json
{
  "video_id": "subONxt5iag",
  "frame_path": "frames_new/frame_0001.jpg",
  "transcript_text": "texto de transcripción...",
  "timestamp_start": 0.0,
  "timestamp_end": 15.0
}
```

### Salida
```json
{
  "scene_idx": 0,
  "start": 0.0,
  "end": 15.0,
  "frame": "frame_0001.jpg",
  "vision_analysis": "A_VISUAL: instrument=..., timeframe=..., prices=[...]",
  "ocr_text": "texto extraído por Tesseract",
  "ocr_time_seconds": 0.2,
  "vision_time_seconds": 17.5,
  "total_time_seconds": 17.7,
  "model": "qwen2.5vl:3b",
  "pipeline": "qwen2.5vl:3b"
}
```

### Validaciones
- vision_analysis no vacío
- No inventar precios (usar null)
- Distinguir NOT_A_CHART
- Registrar tiempo por etapa

## 3. Memory Manager Contract

### Responsabilidad exclusiva
Persistencia, recuperación y consolidación de memoria.

### Entrada
```json
{
  "action": "store|retrieve|consolidate",
  "data_type": "analysis|methodology|decision",
  "content": "...",
  "source": "youtube_analyst",
  "timestamp": "2026-11-10T12:00:00Z"
}
```

### Salida
```json
{
  "success": true,
  "stored_id": "mem_001",
  "data_type": "analysis",
  "timestamp": "2026-11-10T12:00:00Z"
}
```

### Validaciones
- No analizar imágenes ni videos
- No modificar resultados del YouTube Analyst
- Conservar procedencia y trazabilidad

## 4. Pipeline Audiovisual Contract

### Responsabilidad exclusiva
Orquestar el procesamiento completo de un video.

### Entrada
```json
{
  "video_id": "subONxt5iag",
  "video_path": "data_new/subONxt5iag.mp4",
  "transcript_path": "data_new/subONxt5iag_transcript.json",
  "frames_dir": "frames_new/",
  "model": "qwen2.5vl:3b"
}
```

### Salida
```json
{
  "video_id": "subONxt5iag",
  "frames_processed": 18,
  "frames_ok": 18,
  "frames_error": 0,
  "total_time_seconds": 315.7,
  "avg_time_per_frame": 17.5,
  "results_path": "experimental/results/vision_analysis_subONxt5iag.json"
}
```

## 5. Persistencia de Resultados Contract

### Responsabilidad exclusiva
Almacenar y recuperar resultados de análisis.

### Entrada
```json
{
  "result_type": "vision_analysis|transcript|frame_selection",
  "video_id": "subONxt5iag",
  "data": {...},
  "overwrite": false
}
```

### Salida
```json
{
  "success": true,
  "file_path": "experimental/results/vision_analysis_subONxt5iag.json",
  "bytes_written": 12345,
  "timestamp": "2026-11-10T12:00:00Z"
}
```

### Validaciones
- No sobrescribir resultados existentes sin confirmación
- Conservar historial de versiones
- Verificar integridad de datos

## 6. Comunicación con Hermes Contract

### Responsabilidad exclusiva
Interfaz entre Hermes (orquestador) y los módulos.

### Entrada
```json
{
  "command": "process_video|analyze_frame|consolidate_memory|get_status",
  "params": {...},
  "timeout_seconds": 300
}
```

### Salida
```json
{
  "status": "success|error|timeout",
  "result": {...},
  "elapsed_seconds": 12.3,
  "error": null
}
```

### Validaciones
- Timeout configurable
- Manejo de errores graceful
- Logging de todas las operaciones

## Versionado
- Contratos: v1.0
- Model Manager: v1.0
- YouTube Analyst: v1.0 (qwen2.5vl:3b)
- Memory Manager: v1.0 (qwen3.5:9b-mlx)
- Pipeline: v1.0

## Procedencia y trazabilidad
- Cada resultado incluye: model, pipeline, timestamp, video_id
- Historial de resultados conservado (no sobrescribir)
- Logs en experimental/logs/