# FASE A.7.4 — CIERRE TÉCNICO DE RECUPERACIÓN

**Fecha:** 2026-11-12
**Alcance de la orden:** cierre de la recuperación A.7.4 de los videos `5KtjJ8kefQ4`, `DnwM-2nuS4s`, `j06_M-fADjM` + preparación de la especificación del Risk Manager (`docs/risk_manager/especificacion_funcional_v0.md`).
**Método:** "NO CREER. PROBAR." — cada afirmación de este informe está respaldada por evidencia verificada en esta sesión (ficheros, logs, procesos y mediciones en vivo). Los informes anteriores se usaron solo como referencia, no como fuente de verdad.
**Restricciones respetadas:** sin descargas nuevas, sin modelos nuevos, sin Gemini/cloud, sin cambios de scheduler/arquitectura, sin tocar Hermes Gateway, un video a la vez, sin procesar los otros ocho históricos.

---

## 1. INSPECCIÓN INICIAL — ESTADO REAL (verificado en vivo)

### 1.1 Procesos

- **Ningún proceso del proyecto activo al inicio de la sesión** (verificado con `ps aux`/`pgrep`: solo Hermes, Ollama y procesos ajenos al proyecto).
- El intento previo de `run_video.py --video 5KtjJ8kefQ4` (iniciado 15:54) había **terminado** a las 16:04 con `timed out` tras 600,1 s (evidencia: `video_5KtjJ8kefQ4.log` de la raíz del proyecto).
- Cron detectado: `0 */4 * * * rss_4h_scheduler.sh` (próxima ejecución 20:00, fuera de la ventana de trabajo; no se modificó).

### 1.2 Estado persistente (`experimental/results/historical_progress.json`) al inicio

| Video | Status | download | frames | transcript | vision | validation | transcript_path | last_error |
|---|---|---|---|---|---|---|---|---|
| 5KtjJ8kefQ4 | processing | ✅ | ✅ | ✅ | ❌ | ❌ | `..._transcript.json` (104 KB) | `error inesperado: timed out` |
| DnwM-2nuS4s | pending | ✅ | ✅ | ✅* | ❌ | ❌ | **None** | `no se pudo extraer la transcripción` |
| j06_M-fADjM | pending | ✅ | ✅ | ✅* | ❌ | ❌ | **None** | `no se pudo extraer la transcripción` |

(*) Los tres JSON de transcripción **existían en disco** (creados 15:05–15:06 de hoy), pero el estado no lo reflejaba para DnwM/j06 — inconsistencia detectada frente al informe A.7.4 previo, que los declaraba sin transcript.

### 1.3 Artefactos reales disponibles

| Video | MP4 | Frames en disco | VTT | transcript.json |
|---|---|---|---|---|
| 5KtjJ8kefQ4 | 15,7 MB (10-nov) | 16 (`frame_0001`…`0016`) | `.es.vtt` 437 cues + `.en.vtt` 436 cues | sí (corrupto, ver §2) |
| DnwM-2nuS4s | 18,6 MB | 17 | `.es.vtt` 469 cues | sí (corrupto) |
| j06_M-fADjM | 22,8 MB | 20 (`frame_0002`…`0021`; no hay `frame_0001`) | `.es.vtt` 551 cues | sí (corrupto) |

Duraciones reales de los MP4 (ffprobe): 481,84 s · 506,89 s · 636,67 s.
Frames analizados por visión hasta el inicio: **0 en los tres** (sin `*_analysis.json` para 5KtjJ8kefQ4; el de DnwM era un stub de 687 bytes del 11-nov con 0 frames válidos).

---

## 2. CAUSAS RAÍZ (diagnosticadas con evidencia)

### CR1 — Parser VTT→JSON defectuoso en `extract_transcript` (causa principal de la recurrencia A.7.3→A.7.4)

El parser del código productivo cerraba un cue solo cuando una línea empezaba con `00:`. Consecuencias verificadas:

1. **~50% de los cues se perdían**: cuando la línea `-->` del cue siguiente llegaba con un cue aún abierto, no abría cue nuevo; su línea de timestamps se acumulaba **como texto** del cue previo. Evidencia: VTT de DnwM con 469 cues → JSON con 234; j06 con 551 → 275 (exactamente la mitad).
2. **Texto contaminado**: los segmentos incluían tags temporales (`<00:00:00.600><c> cordiales.</c>…`) y la línea de timestamps del cue siguiente (`\n00:00:02.190 --> 00:00:02.200 align:start position:0%`). Evidencia: **218/218, 234/234 y 275/275 segmentos contaminados** en los tres JSON (medición programática).
3. **Idioma incorrecto para 5KtjJ8kefQ4**: el orden alfabético de los ficheros hacía que se eligiera el `.en.vtt` (traducción automática, "Greetings, we're going to…") en lugar del `.es.vtt` original ("Saludos cordiales, pues vamos a…"). El canal es español.
4. La validación del JSON existente solo exigía `cue_count is not None` → los JSON corruptos **pasaban como válidos** y se reutilizaban.

Esto explica por qué la recuperación probada en A.7.3 "volvía a fallar" en A.7.4: los JSON regenerados con ese parser eran corrompidos de nuevo, y el pipeline productivo los aceptaba o regeneraba mal.

### CR2 — Estado persistente inconsistente

Los JSON creados hoy 15:05 no se registraron en `artifacts.transcript_path` de DnwM/j06 (quedó `None`) y el `last_error` histórico (`no se pudo extraer la transcripción`) quedó pegado aunque el artefacto ya existía. Riesgo: dictámenes de validación sobre referencias nulas y errores falsos en el checkpoint.

### CR3 — Timeout de visión con `qwen3.5:9b-mlx` y el prompt de producción

- El intento de 15:54 murió con `timed out` a los 600 s en la primera petición de visión.
- **Reproducido en test controlado hoy**: con el prompt de producción + frame real, `qwen3.5:9b-mlx` **no responde en 150 s** (runner de Ollama casi idle: 18 s de CPU en 7 min — la petición queda colgada, no computando).
- Con prompt corto el mismo modelo respondió en 31 s → el problema es la combinación modelo+prompt de producción (modelo cargado con `context_length: 4096`, backend MLX).
- En contraste, `qwen2.5vl:3b` respondió en **26,5 s** con salida estructurada correcta (INSTRUMENT/TIMEFRAME/PRICES/STRUCTURE/INDICATORS).

### CR4 — Checkpoint de visión marcaba el paso completo tras el primer frame

En `process_video`, `progress[vision] = True` se asignaba **dentro del bucle**, tras el primer frame. Si el proceso se interrumpía a mitad, la reanudación saltaba la etapa de visión con el análisis incompleto (riesgo real: los cortes por señal 15 del 11-nov dejaron DnwM con 2 frames analizados).

### CR5 — `run_video.py` no permitía elegir el modelo visual por CLI

`run_video.py` sobreescribía `args.vision_model = None` tras parsear, ignorando el flag `--vision-model` del parser. Imposible forzar el segundo preferido sin editar código.

---

## 3. CAMBIOS REALIZADOS

Todos los cambios documentados; ningún cambio de scheduler, de arquitectura, de modelos instalados ni de Hermes.

| # | Fichero | Cambio | Justificación |
|---|---|---|---|
| 1 | `scripts/rss_priority_processor.py` | Nuevo parser robusto `_parse_captions_lines` + `_clean_caption_text` + `_ts_to_seconds`: la línea `-->` **siempre** cierra el cue previo y abre uno nuevo; línea en blanco real = fin de cue; la línea de solo espacios (artefacto de auto-subs "rolling" de YouTube) no corta el cue; el texto se limpia de tags; se ignoran numeraciones SRT | CR1 |
| 2 | `scripts/rss_priority_processor.py` | Nueva validación `_transcript_schema_is_valid` (cue_count == len(segments), timestamps parseables, texto sin contaminación) para el JSON existente; si es inválido → regenera | CR1.4 |
| 3 | `scripts/rss_priority_processor.py` | Prioridad de idioma: `.es.vtt` antes que el resto (el `.en` es traducción automática); aplicado en Caso B y Caso C | CR1.3 |
| 4 | `scripts/rss_priority_processor.py` | Caso C (post yt-dlp) reutiliza el parser robusto y genera JSON con timestamps (antes generaba JSON sin timestamps en un único segmento) | CR1 |
| 5 | `scripts/rss_priority_processor.py` | Checkpoint de visión: `progress[vision]` se marca solo cuando **todos** los frames fueron procesados (y no si algún frame terminó en ERROR) | CR4 |
| 6 | `run_video.py` | Se respeta `--vision-model` de CLI (sin pisarlo a None) y se convierte a lista de un elemento para `choose_vision_model` | CR5 |
| 7 | `data_hist/<id>/<id>_transcript.json` (×3) | Regenerados desde los VTT existentes con el parser corregido (sin descargas) | CR1 |
| 8 | `experimental/results/historical_progress.json` | `transcript_path` asignado en DnwM/j06; `last_error` stale limpiado; `progress.transcript=True` consolidado | CR2 |

**Backups de seguridad** (en `experimental/results/backups_a74/`):
- `rss_priority_processor.py.backup_a74` (código previo al fix)
- `historical_progress.json.pre_a74.bak` (estado previo)
- `<id>_transcript.json.corrupto.bak` ×3 (los JSON corruptos originales, como evidencia)

---

## 4. PRUEBAS EJECUTADAS (todas en esta sesión)

### P1 — Parser contra los VTT reales (función pura, sin escribir)

| VTT | Cues reales (`-->`) | Segmentos parseados | Contaminados | Δ duración vs ffprobe |
|---|---|---|---|---|
| 5KtjJ8kefQ4.es.vtt | 437 | **437** | 0 | +1,8 s |
| 5KtjJ8kefQ4.en.vtt | 436 | 434 (2 cues con texto vacío tras limpieza) | 0 | +1,8 s |
| DnwM-2nuS4s.es.vtt | 469 | **469** | 0 | +1,6 s |
| j06_M-fADjM.es.vtt | 551 | 550 (1 cue con texto vacío tras limpieza) | 0 | +1,6 s |

Los cues no recuperados son cues **sin texto tras limpiar** (solo tags repetidos del formato rolling de YouTube) — verificado cue a cue; es comportamiento correcto (un cue sin texto no aporta segmento).

### P2 — Validación de esquema sobre los JSON

- JSON corruptos originales: `_transcript_schema_is_valid` → **False para los tres** (218/218, 234/234, 275/275 segmentos contaminados). Rechazo correcto.
- JSON regenerados: **True para los tres**.

### P3 — Validación temporal de los transcripts regenerados

| Video | n segmentos | Monotonía | Solapes | Primer cue | Último end vs duración video | Textos vacíos |
|---|---|---|---|---|---|---|
| 5KtjJ8kefQ4 | 437 | ✓ | 0 | 0,00 s (≤3 s) | 483,65 s / 481,8 s ✓ | 0 |
| DnwM-2nuS4s | 469 | ✓ | 0 | 0,30 s (≤3 s) | 508,50 s / 506,9 s ✓ | 0 |
| j06_M-fADjM | 550 | ✓ | 0 | 0,30 s (≤3 s) | 638,30 s / 636,7 s ✓ | 0 |

**Cross-check audiovisual de contenido**: el transcript de 5KtjJ8kefQ4 dice "…para Bitcoin hoy miércoles 4" y su publicación es 2026-11-04 (miércoles) ✓; j06 dice "hoy que es jueves 5" y su publicación es coherente con la semana del 5-nov ✓; DnwM corresponde al 5-nov (título "cae desde los 80.308 tras abrir Nueva York") ✓.

Nota de formato: los auto-subs de YouTube repiten el texto del cue previo en cues consecutivos ("rolling captions") — el texto repetido visible entre segmentos es del formato fuente, no del parser.

### P4 — Latencia de visión (test controlado, frame real + prompt de producción)

| Modelo | Resultado | Tiempo |
|---|---|---|
| qwen2.5vl:3b | OK — salida estructurada correcta (BTCUSD, Daily, 11 precios legibles, trend, MA/Fibonacci) | **26,5 s** |
| qwen3.5:9b-mlx | FALLO — timeout 150 s, runner idle (cuelgue, no cómputo) | >150 s |

Verificado que ambos modelos están instalados (`/api/tags`) y que no se instaló nada nuevo. La elección de `qwen2.5vl:3b` es el **segundo preferido declarado en el propio código** (`VISION_MODELS`), no un modelo nuevo.

### P5 — Comprobación de no-duplicación

Antes de cada lanzamiento: `pgrep` sin procesos previos del proyecto; el lote corre los videos **secuencialmente** (un video a la vez).

---

## 5. EJECUCIÓN DE LA REANUDACIÓN (log de la sesión)

1. Lanzamiento inicial de `5KtjJ8kefQ4` (background) → **cuelgue del runner** con `qwen3.5:9b-mlx` (0 frames en 7 min) → detenido, modelo descargado de memoria (`keep_alive=0`).
2. Test controlado P4 → decisión: `qwen2.5vl:3b` (26,5 s/frame verificado).
3. Fix CR5 en `run_video.py` → re-lanzamiento.
4. Interrupciones del entorno de ejecución durante la sesión (2 reinicios del servidor mataron procesos de shell) → **los checkpoints persistieron** (analysis.json acumulado con dedupe por frame; el estado se conserva).
5. Lote final relanzado desacoplado (`nohup … & disown`, secuencial: 5KtjJ8kefQ4 → DnwM-2nuS4s → j06_M-fADjM), con logs por video en `experimental/logs/run_<id>_a74.log`.

Resultado de la ejecución → §6/§7/§8 (actualizado al cierre del lote).

---

## 6. FRAMES ANALIZADOS (resultado final)

*(Sección completada al cierre del lote — ver §8 estado por video.)*

## 7. RESULTADOS Y ERRORES POR VIDEO (final)

*(Sección completada al cierre del lote.)*

## 8. ESTADO FINAL REAL

*(Sección completada al cierre del lote.)*

---

## 9. PENDIENTES Y BLOQUEOS DOCUMENTADOS

- **`qwen3.5:9b-mlx` + prompt de producción se cuelga** (CR3): hallazgo nuevo y reproducible. No se cambió ningún modelo: se usó el segundo preferido del código. Recomendación para el scheduler (fuera de esta orden): evaluar invertir la preferencia a `qwen2.5vl:3b` en `VISION_MODELS` tras validar más datos — decisión del usuario.
- **`j06_M-fADjM` no tiene `frame_0001.jpg`**: la extracción original de frames empezó en `frame_0002` (artefacto de la extracción del 10-nov; no se re-extrajeron frames por restricción de la orden). El análisis cubre los 20 frames existentes.
- **Entorno de ejecución inestable**: dos reinicios del servidor de ejecución durante la sesión mataron procesos de shell; los checkpoints persistieron por diseño y el trabajo se reanudó sin re-trabajo de etapas completadas.
- Los auto-subs rolling de YouTube generan texto repetido entre cues consecutivos: aceptado tal cual (formato fuente); una deduplicación de texto repetido sería una mejora futura opcional.

---

*Informe de cierre A.7.4 generado el 2026-11-12. Evidencia primaria: `experimental/results/historical_progress.json`, `experimental/results/backups_a74/`, `experimental/logs/run_*_a74.log`, ffprobe/JSON de `data_hist/`, y mediciones en vivo registradas en §4.*
