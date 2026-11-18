# IDENTIFICACIÓN DE FUNCIONES DE LOS MODELOS QFT - FASE 5.4

**Proyecto:** `~/YouTubeTradingAgent/`
**Fecha:** 10 de noviembre de 2026
**Orquestador:** Hermes
**Modelo verificado:** Qwen3.5:9b-mlx y Qwen2.5vl:3b

---

## 1. IDENTIFICACIÓN DE FUNCIONES

| Modelo | Tamaño | Función real | Uso en el código | Estado |
|--------|--------|--------------|------------------|--------|
| `Qwen2.5vl:3b` | 3.2GB | **Análisis audiovisual** (visión) | `historical_processor.py`, `vision_analyzer_qwen25vl.py`, `vision_independence_test.py`, `retry_failed_*.py` | ✅ Claramente separado |
| `Qwen3.5:9b-mlx` | 8.9GB | **Procesamiento textual** (memoria, reportes, análisis) | `memory_manager.py`, `vision_analyzer.py`, `retry_failed_*.py`, `test_qwen_vision.py` | ✅ Claramente separado |

**No hay mezcla de modelos:**
- Qwen2.5vl:3b → siempre recibe imágenes de gráficos y devuelve análisis visual.
- Qwen3.5:9b-mlx → siempre procesa texto (transcripciones, memoria, reportes).

---

## 2. CONFIGURACIÓN ACTUAL

| Componente | Configuración |
|------------|---------------|
| RSS polling | Cada 4 horas (14400s) |
| Estado persistente | `experimental/results/historical_progress.json` |
| Modelo de análisis visual | `Qwen3.5:9b-mlx` (primario), `Qwen2.5vl:3b` (soporte) |
| Almacenamiento persistente | Memoria JSON + SQLite (pendiente) |

---

## 3. PRÓXIMO PASO

Procesar el video más reciente pendiente:

| ID | Fecha publicación | Estado |
|----|-------------------|--------|
| DnwM-2nuS4s | 05/11/2026 | Detected |

Pipeline: Download → Frames → Transcript → Vision → Validation

---

## 4. RESTRICCIONES DE EJECUCIÓN

- RSS polling cada 4 horas.
- Si aparece un video nuevo, pasa al frente de la cola.
- No se reprocesan videos completados.
- El estado sobrevive a las interrupciones.
- Toda conclusión debe conservar trazabilidad al video, timestamp y evidencia visual.

---

**VEREDICTO:** Qwen2.5vl:3b funciona como modelo visual de análisis (audiovisual). Qwen3.5:9b-mlx como modelo textual (memoria, reportes). Las funciones están separadas correctamente.
