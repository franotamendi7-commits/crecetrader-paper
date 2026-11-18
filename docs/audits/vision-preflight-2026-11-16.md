# Auditoría de preflight — estado de visión

Fecha: 2026-11-16 · Solo lectura · Sin inferencia, sin red, sin Ollama
Artefactos nuevos: `tools/vision_preflight.py`, `tests/test_vision_state.py`, este informe.

## 1. Estado de cada vídeo (frames totales / completos / pendientes / error)

Fuente: `experimental/results/historical_progress.json` + `frames_hist/` + `*_analysis.json`.

| vídeo | frames | completos | pendientes | error | vision |
|---|---|---|---|---|---|
| 0prmrS6nnRk | 27 | 20 | 0 | 0 | false |
| o6n6UDNVtCk | 41 | 20 | 0 | 0 | false |
| rTtXDLq2kOQ | 30 | 20 | 0 | 0 | false |
| subONxt5iag | 34 | 16 | 0 | 4 | true |
| DnwM-2nuS4s | 17 | 17 | 0 | 0 | true |
| j06_M-fADjM | 20 | 20 | 0 | 0 | true |
| 5KtjJ8kefQ4 | 16 | 16 | 0 | 0 | true |
| scJ-ai2FRiE | 20 | 20 | 0 | 0 | true |
| LzPTdClLo_w | 17 | 17 | 0 | 0 | true |
| s3KxjqkzwKM | 20 | 20 | 0 | 0 | true |
| jeOFS1TZYQA | 20 | 20 | 0 | 0 | true |
| EJoLhxbwYxo | 20 | 20 | 0 | 0 | true |
| dPHvRw1wzYQ | 20 | 20 | 0 | 0 | true |
| XLgPycsN0ls | 20 | 20 | 0 | 0 | true |
| LFHkc5dUoLw | 20 | 20 | 0 | 0 | true |
| mv2VdVtXvDw | 20 | 20 | 0 | 0 | true |
| bCc--rvyHpY | 0 | 0 | 0 | 0 | false |
| Vm7nUxLCMZQ | 0 | 0 | 0 | 0 | false |
| rX2wj_FXvT4 | 0 | 0 | 0 | 0 | false |
| s_GjovZxQqY | 20 | 0 | 0 | 0 | false |
| **TOTAL** | **382** | **306** | **0** | **4** | |

Observaciones:
- `0prmrS6nnRk`, `o6n6UDNVtCk`, `rTtXDLq2kOQ`: tienen más frames en disco que análisis (muestreo limitado a 20) y `vision=false`.
- `subONxt5iag`: 4 resultados con `ERROR` dentro de un `vision=true`.
- `s_GjovZxQqY`: 20 frames extraídos, sin análisis todavía.
- Preflight global: **20 vídeos · 7 `analysis_file`/`transcript_path` nulos · 32 rutas relativas · 0 artefactos ausentes · 0 discrepancias de transcripción · 0 errores de esquema**.

## 2. Causa raíz demostrada del fallo de persistencia

`save_state` (`scripts/rss_priority_processor.py:286-322`) **es atómico**: escribe `state.json.tmp`, `os.replace` y `fsync`. No es el culpable.

Causas demostradas:

1. **`artifacts.analysis_file = null`** → `_save_analysis` lanza `AttributeError: 'NoneType' object has no attribute 'parent'` y el checkpoint no se escribe. Evidencia: el fallo real de `proc_d0904ecc6af1` (2026-11-16) y 7 casos actuales detectados por el preflight.
2. **Checkpoint de visión por frame (CR4, ya corregido)**: antes `progress[vision]=True` se asignaba tras el primer frame; una interrupción a mitad dejaba la etapa sin completar en la reanudación. Evidencia: `reports/fase_a7_4_cierre_tecnico.md:67` y los 4 `ERROR` de `subONxt5iag`.
3. **Rutas relativas ambiguas**: 32 artefactos (`analysis_file`, `transcript_path`, `video_path`, `frames_dir`) son rutas relativas al *cwd*. Funcionan solo si el proceso arranca desde la raíz; desde otro directorio se pierden. Detectedas por el preflight.
4. **`transcript_path` sin `.json`** (solo `.vtt`) en `mv2VdVtXvDw`: el pipeline exige JSON; el preflight lo señala como relativa y el estado quedó con el `.vtt`.

## 3. Modelo configurado y modelos residentes

- **Configurado**: `VISION_MODELS = ["qwen3.5:9b-mlx", "qwen2.5vl:3b"]` (`rss_priority_processor.py:100`); `run_video.py:23` por defecto `qwen3.5:9b-mlx`. `choose_vision_model()` devuelve el primero disponible.
- **Instalados** (`ollama list`): `qwen2.5vl:3b` (3,2 GB), `moondream:latest` (1,7 GB), `qwen3.5:9b-mlx` (8,9 GB).
- **Residentes** (`ollama ps`): **ninguno** (tabla vacía). No se ejecutó ningún modelo.

## 4. Pruebas de persistencia

`python3 -m pytest -q tests/test_vision_state.py` → **8 passed**.

Cubren: `analysis_file=None`, directorio inexistente, `.vtt` sin `.json`, escritura atómica, interrupción antes del `replace` (el estado previo sigue legible), reanudación sin duplicar frames, y conservación de `frame`/`pts_time`.

## 5. Archivos nuevos / modificados

Nuevos (untracked; el repo no tiene baseline trackeado, por lo que `git diff` no los muestra):
- `tools/vision_preflight.py`
- `tests/test_vision_state.py`
- `docs/audits/vision-preflight-2026-11-16.md`

Comprobaciones: `git diff --check` sin errores; `git status --short tools tests` → `??`. Ningún archivo de producción modificado.

## 6. Manifiesto de validación propuesto (sin imágenes reales)

```json
{
  "frame_id": "video_id:timestamp_ms",
  "video_id": "string",
  "timestamp_ms": 0,
  "sha256": "string",
  "transcript_span": {"start_ms": 0, "end_ms": 0},
  "expected": {"instrument": null, "timeframe": null, "levels": [], "chart_elements": []},
  "human_annotation_status": "pending"
}
```

Una evaluación visual **no puede declarar "confirmado"** si falta: anotación humana independiente, evidencia del frame, referencia temporal a la transcripción, incertidumbre explícita, o coincidencia verificable con instrumento, temporalidad y nivel.

## 7. Riesgos restantes y decisión

Riesgos:
1. 7 `analysis_file`/`transcript_path` nulos y 32 rutas relativas: cualquier reanudación puede fallar o apuntar mal.
2. `subONxt5iag` con 4 `ERROR` declarado `vision=true`.
3. Sin motor de visión autorizado.

**Decisión: `BLOQUEADO`** para ejecutar el benchmark sintético (requiere crear entorno externo, instalar dependencias o transferir una imagen: todo pendiente de autorización). El estado está auditado y el preflight operativo.

Pendiente de autorización expresa: entorno externo + prueba de acelerador real + eliminación posterior. Ningún dato del proyecto sale del Mac sin autorización separada.
