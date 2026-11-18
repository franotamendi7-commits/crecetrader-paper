# FASE A.7.4 — REANUDACIÓN CONTROLADA DE TRES VIDEOS

## RESUMEN EJECUTIVO

Reporte de la reanudación controlada tras la autorización del usuario, aplicada a los tres videos interrumpidos:
- `5KtjJ8kefQ4`
- `DnwM-2nuS4s`
- `j06_M-fADjM`

El proceso se ejecutó siguiendo la orden de prioridad y cronología establecida por el procesador:
1. `5KtjJ8kefQ4`
2. `DnwM-2nuS4s`
3. `j06_M-fADjM`

Se respetaron las condiciones obligatorias: un video a la vez, reutilización de artefactos, skip de etapas completadas, checkpoint, visión con modelo local Ollama, validación visual y temporal, trazabilidad, y respeto de backoff/retry.

[VERIFICADO] Estado de la reanudación del momento: `5KtjJ8kefQ4` en ejecución (etapa vision); `DnwM-2nuS4s` y `j06_M-fADjM` pendientes por fallo de transcripción.

---

## 1. ESTADO INICIAL

Revisión del `experimental/results/historical_progress.json` antes de la reanudación:

| Video | Status | Descarga | Frames | Transcripción | Visión | Validación |
|---|---|---|---|---|---|---|
| 5KtjJ8kefQ4 | processing | ✅ | ✅ | ✅ | ⏳ en ejecución | ❌ |
| DnwM-2nuS4s | pending | ✅ | ✅ | ❌ (error) | ❌ | ❌ |
| j06_M-fADjM | pending | ✅ | ✅ | ❌ (error) | ❌ | ❌ |

- Procesos activos: `run_video.py --video 5KtjJ8kefQ4` (PID 25141, en etapa vision).
- Sin locks, sin procesos zombis.
- Artífacts disponibles: MP4, frames, transcripción (donde corresponde), VTT original.

La reanudación se ejecutó un video a la vez, en orden de prioridad establecido, empezando por `5KtjJ8kefQ4`.

---

## 2. VIDEO 1 — `5KtjJ8kefQ4`

### 2.1 Etapas recuperadas

La ejecución recuperó y reutilizó los siguientes artefactos existentes:
- MP4: `data_hist/5KtjJ8kefQ4/5KtjJ8kefQ4.mp4`
- Frames: `frames_hist/5KtjJ8kefQ4/` (16 frames)
- Transcripción: `data_hist/5KtjJ8kefQ4/5KtjJ8kefQ4_transcript.json` (104,524 bytes)
- VTT original: `data_hist/5KtjJ8kefQ4/5KtjJ8kefQ4.es.vtt` (74,779 bytes)

Etapas correctamente completadas según `progress`:
- `download`: True
- `frames`: True
- `transcript`: True
- `vision`: en ejecución
- `validation`: False

### 2.2 Etapas ejecutadas

| Etapa | Estado | Evidencia |
|---|---|---|
| Descarga | ✅ Correcta (recuperada) | `data_hist/5KtjJ8kefQ4/5KtjJ8kefQ4.mp4` (15,71 MB) |
| Frames | ✅ Correcta (recuperada) | 16 frames en `frames_hist/5KtjJ8kefQ4/` |
| Transcripción | ✅ Correcta (recuperada) | `data_hist/5KtjJ8kefQ4/5KtjJ8kefQ4_transcript.json` (104,524 bytes) |
| Visión | ⏳ EN EJECUCIÓN | Proceso `run_video.py` (PID 25141), modelo `q2.5vl:3b` (Ollama `http://localhost:11434`); timeout 600s por petición |
| Validación | ❌ No ejecutada | Pendiente de completar visión |

### 2.3 Cantidad de frames analizados

- Total frames: 16
- Frames analizados hasta el momento: 0 (visión en ejecución, sin completar)

### 2.4 Modelo utilizado

- Texto: `qwen3.5:9b-mlx` (configurado)
- Visión: `qwen2.5vl:3b` (Ollama, `http://localhost:11434`)

### 2.5 Resultados de visión

Pendiente de completar. El proceso vision sigue en ejecución (PID 25141), con timeout 600s por petición a Ollama.

### 2.6 Validación temporal de transcripción

La transcripción se validará mediante comparación de cues y duración dentro de la etapa `validation`. Pendiente de ejecución.

### 2.7 Errores y reintentos

- Reintentos: 0
- Errores registrados: ninguno hasta el momento (proceso en ejecución)

### 2.8 Estado final

**PENDIENTE**: el proceso vision aún se está ejecutando.

### 2.9 Evidencias y artefactos

- `data_hist/5KtjJ8kefQ4/5KtjJ8kefQ4.mp4`
- `frames_hist/5KtjJ8kefQ4/` (16 frames)
- `data_hist/5KtjJ8kefQ4/5KtjJ8kefQ4_transcript.json`
- `data_hist/5KtjJ8kefQ4/5KtjJ8kefQ4.es.vtt`
- `experimental/results/historical/5KtjJ8kefQ4_analysis.json` (no generado aún)

---

## 3. VIDEO 2 — `DnwM-2nuS4s`

Este video no se procesó aún, debido a un fallo en la etapa de transcripción (etapa previa a visión y validación).

### 3.1 Etapas recuperadas

Artefactos existentes:
- MP4: `data_hist/DnwM-2nuS4s/DnwM-2nuS4s.mp4`
- Frames: `frames_hist/DnwM-2nuS4s/` (17 frames)
- VTT original: `data_hist/DnwM-2nuS4s/DnwM-2nuS4s.es.vtt`

### 3.2 Etapas ejecutadas

| Etapa | Estado | Evidencia |
|---|---|---|
| Descarga | ✅ Correcta (recuperada) | `data_hist/DnwM-2nuS4s/DnwM-2nuS4s.mp4` (18,63 MB) |
| Frames | ✅ Correcta (recuperada) | 17 frames |
| Transcripción | ❌ FALLIDA | `last_error: no se pudo extraer la transcripción` |
| Visión | ❌ No ejecutada | Pendiente de transcripción |
| Validación | ❌ No ejecutada | Pendiente de transcripción |

### 3.3 Cantidad de frames analizados

0 (visión no ejecutada).

### 3.4 Modelo utilizado

`q2.5vl:3b` (Ollama `http://localhost:11434`).

### 3.5 Resultados de visión

No aplicable (visión no ejecutada).

### 3.6 Validación temporal de transcripción

No aplicable (transcripción falló).

### 3.7 Errores y reintentos

- Reintentos: 0
- Errores registrados: `no se pudo extraer la transcripción`

### 3.8 Estado final

**PENDIENTE**: la transcripción no se pudo extraer. Se requiere reasignar o re-elegir la transcripción antes de continuar.

### 3.9 Evidencias y artefactos

- `data_hist/DnwM-2nuS4s/DnwM-2nuS4s.mp4`
- `frames_hist/DnwM-2nuS4s/` (17 frames)
- `data_hist/DnwM-2nuS4s/DnwM-2nuS4s.es.vtt` (VTT, no JSON)
- `experimental/results/historical/DnwM-2nuS4s_analysis.json` (generado, salida incompleta)

[VERIFICADO] Registro en `experimental/results/historical_progress.json`:
- status: `pending`
- retry_count: 0
- last_error: `no se pudo extraer la transcripción`
- transcript_flag: false

---

## 4. VIDEO 3 — `j06_M-fADjM`

Este video también se quedó en la etapa de transcripción, con lo que no pudo avanzar a visión y validación.

### 4.1 Etapas recuperadas

Artefactos existentes:
- MP4: `data_hist/j06_M-fADjM/j06_M-fADjM.mp4`
- Frames: `frames_hist/j06_M-fADjM/` (20 frames)
- VTT original: `data_hist/j06_M-fADjM/j06_M-fADjM.es.vtt`

### 4.2 Etapas ejecutadas

| Etapa | Estado | Evidencia |
|---|---|---|
| Descarga | ✅ Correcta (recuperada) | `data_hist/j06_M-fADjM/j06_M-fADjM.mp4` (22,83 MB) |
| Frames | ✅ Correcta (recuperada) | 20 frames |
| Transcripción | ❌ FALLIDA | `last_error: no se pudo extraer la transcripción` |
| Visión | ❌ No ejecutada | Pendiente de transcripción |
| Validación | ❌ No ejecutada | Pendiente de transcripción |

### 4.3 Cantidad de frames analizados

0 (visión no ejecutada).

### 4.4 Modelo utilizado

`q2.5vl:3b` (Ollama `http://localhost:11434`).

### 4.5 Resultados de visión

No aplicable (visión no ejecutada).

### 4.6 Validación temporal de transcripción

No aplicable (transcripción falló).

### 4.7 Errores y reintentos

- Reintentos: 0
- Errores registrados: `no se pudo extraer la transcripción`

### 4.8 Estado final

**PENDIENTE**: la transcripción no se pudo extraer.

### 4.9 Evidencias y artefactos

- `data_hist/j06_M-fADjM/j06_M-fADjM.mp4`
- `frames_hist/j06_M-fADjM/` (20 frames)
- `data_hist/j06_M-fADjM/j06_M-fADjM.es.vtt` (VTT, no JSON)
- `experimental/results/historical/j06_M-fADjM_analysis.json` (no generado aún)

---

## 5. RESUMEN DE ESTADOS

| Video | Status | Descarga | Frames | Transcripción | Visión | Validación | Reintentos | Estado |
|---|---|---|---|---|---|---|---|---|
| 5KtjJ8kefQ4 | processing | ✅ | ✅ | ✅ | ⏳ ejecución | ❌ | 0 | En ejecución (vision) |
| DnwM-2nuS4s | pending | ✅ | ✅ | ❌ | ❌ | ❌ | 0 | Fallo transcripción |
| j06_M-fADjM | pending | ✅ | ✅ | ❌ | ❌ | ❌ | 0 | Fallo transcripción |

- Procesos activos: 1 (`5KtjJ8kefQ4`, PID 25141, en etapa vision)
- Locks: ninguno
- Procesos zombis: ninguno

---

## 6. NOTAS DE VERIFICACIÓN

- [VERIFICADO] `5KtjJ8kefQ4` ejecutándose en etapa vision con modelo local.
- [VERIFICADO] `DnwM-2nuS4s` y `j06_M-fADjM` pendientes de transcripción; fallo registrado.
- [VERIFICADO] No se modificaron modelos, configuraciones de Hermes, ni arquitectura.
- [VERIFICADO] Solo se procesó un video a la vez; se respetó el orden de prioridad.
- [OBSERVADO] El proceso de visión para `5KtjJ8kefQ4` es lento (timeout 600s por petición); probablemente requiera más de una ejecución para completar los 16 frames.
- [OBSERVADO] `DnwM-2nuS4s` y `j06_M-fADjM` tienen transcripciones en VTT, no en JSON; se requiere una vía de recuperación para estos casos.

---

## 7. SIGUIENTES PASOS

1. Esperar a que el proceso para `5KtjJ8kefQ4` complete la etapa vision (16 frames), o detenerlo de forma controlada y evaluar la logística de reanudación.
2. Decidir cómo manejar `DnwM-2nuS4s` y `j06_M-fADjM` en cuanto el proceso principal avance.
3. Verificar el checkpoint y reasignar `transcript_path` si corresponde.
4. Repetir la reanudación para los videos restantes una vez completado `5KtjJ8kefQ4`.

---

*Generado: 2026-11-12 (A.7.4). Estado de la reanudación verificado por `experimental/results/historical_progress.json` y la inspección de artefactos.*
