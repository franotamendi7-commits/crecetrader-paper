# Auditoría de estado post-reinicios — YouTubeTradingAgent

**Fecha:** 2026-11-17, 18:30–18:55 (-03)
**Alcance:** cierre real de A.7.4 en los tres videos (`5KtjJ8kefQ4`, `DnwM-2nuS4s`, `j06_M-fADjM`), estado del Risk Manager V0, investigación de los reinicios del Mac del 2026-11-12 e integridad del estado persistente.
**Método:** "NO CREER. PROBAR." — evidencia primaria (ficheros, mtimes, logs, `ffprobe`, JSON, panic reports, `wtmp`/`pmset`, procesos vivos). Los informes anteriores se usaron como referencia, nunca como fuente de verdad.
**Restricciones respetadas:** auditoría de solo lectura. No se procesó ningún video, no se ejecutó visión, no se reinició ningún servicio, no se tocaron scheduler, checkpoints, flags, modelos ni configuración, y no se movió, borró ni sobrescribió ningún archivo. **El único archivo creado por esta auditoría es este informe.**

**Leyenda:** `[VERIFICADO]` evidencia primaria comprobada · `[INFERIDO]` deducción razonable sin log dedicado · `[NO VERIFICADO]` sin evidencia suficiente · `[NO DETERMINADO]` causa no establecida.

> **Veredicto en una línea:** A.7.4 está completo **como artefactos y checkpoint**, pero **no como calidad validada**; el Risk Manager V0 está completo **como especificación**, pero **no implementado**; los dos reinicios del 12-nov tienen firma de pánico `AMCC`/`iBoot async abort` y **causa no determinada**, sin evidencia de sobrecalentamiento ni de agotamiento de RAM en esos momentos; el scheduler y la validación automática tienen fallos de integridad que impiden leer `completed` sin matices.

---

## A. Resumen ejecutivo

### A.1 Lo que sí está probado

1. **Los tres videos tienen todos los artefactos operativos.** MP4, frames, transcripción JSON y análisis visual existen y son legibles. El checkpoint los marca `completed` con `download/frames/transcript/vision/validation = true` y `last_error = null` (`experimental/results/historical_progress.json`, mtime 2026-11-16 19:26).
2. **Las transcripciones actuales son válidas.** `437/437`, `469/469` y `550/551` cues; 0 segmentos contaminados con `-->`/`<c>`/`<00:`; 0 textos vacíos; timestamps monotónicos, sin solapes y sin formatos inválidos. La duración del JSON excede la de `ffprobe` en solo +1,818 s, +1,605 s y +1,630 s.
3. **La visión existe frame a frame, pero su calidad no está validada.** 5K: 16/16; DnwM: 17/17; j06: 20/20 (este último en `data_hist`, no en el lote A.7.4). Hay placeholders en 1/16, 6/17 y 1/20, y varias salidas muestran series sintéticas o precios que no corresponden a BTC.
4. **Los dos reinicios del 12-nov son pánicos de bajo nivel, no cierres limpios.** Dos `panic-base+socd` con la misma firma `iBoot Panic: : AMCC error ...`, `panicString = SOCD report detected: (iBoot async abort)`, `ResetCounter` con `Boot faults: wdog,reset_in_1`.
5. **El Risk Manager V0 es una especificación completa, no código.** `docs/risk_manager/especificacion_funcional_v0.md` tiene 387 líneas, secciones 0–9, 13 parámetros pendientes (P1–P13) y 11 criterios de aceptación. No se modificó después del 12-nov 18:07.
6. **Existe un prototipo separado de Risk Manager, pero no es el V0.** `daily_pilot/risk_manager/` contiene 186 líneas `PAPER_ONLY`, 14 casos de prueba declarados y una evaluación de 5 señales reales. Cubre un subconjunto; no implementa cuentas/categorías, correlación, apalancamiento, límites diarios/semanales, escenarios, ledger ni fail-closed del V0.
7. **No hubo reinicios desde el 12-nov 17:49.** `kern.boottime = Thu Nov 12 17:49:21 2026`; al 17-nov 18:37 el uptime era 5 días 48 min. Ollama está idle, sin `llama-server` cargado, y no hay procesos de A.7.4.

### A.2 Lo que no está probado

- Que la visión de los tres videos sea **semánticamente correcta**. La validación que pasó el checkpoint es estructural (existencia, JSON parseable, `frames_processed > 0`), no la validación visual/temporal D1–D6 que se aplicó a `LFHkc5dUoLw`.
- Que A.7.4 haya cerrado **documentalmente**: el informe de cierre `reports/fase_a7_4_cierre_tecnico.md` dejó las secciones §6, §7 y §8 como placeholders.
- Que el Risk Manager V0 esté implementado: la spec dice explícitamente "ESPECIFICACIÓN — no implementada".
- Que los reinicios hayan sido por **sobrecalentamiento** o **RAM agotada**: no hay eventos de **presión** térmica ni Jetsam en la ventana 17:00–17:50; los eventos de 14:11 y 15:42 son anteriores y no explican los pánicos.
- La causa exacta del arranque de 17:26: hay `reboot` en `wtmp`, pero **no** hay panic report asociado.

### A.3 Conclusión ejecutiva

**A.7.4:** completo en artefactos, incompleto en validación y reporte. El lote original (18:02–18:21 del 12-nov) hizo 16/16 y 17/17 frames de 5K/DnwM, pero falló la validación con `'str' object has no attribute 'exists'`; j06 quedó en 3/20 y fue matado externamente. Los 20/20 de j06 se completaron el 14-nov en un run posterior, sin log de modelo. El checkpoint se reescribió el 16-nov y marca `completed`, pero no hay log de validación por video que sostenga ese flag.

**Risk Manager:** la spec V0 está bien formada y no se implementó; el prototipo de `daily_pilot` es un componente aislado útil, pero no satisface el V0. No se arrancó el Risk Manager ni el Analyst Manager durante esta auditoría.

**Reinicios:** dos pánicos idénticos el 12-nov a las 17:43:28 y 17:49:51, con `AMCC error`, `iBoot async abort` y `wdog,reset_in_1`. La causa es **NO DETERMINADA**. La firma apunta a un fallo de bajo nivel en el arranque (memoria/controlador/firmware), pero no se puede atribuir a un componente concreto sin diagnóstico de Apple. **No se sostiene** la hipótesis de sobrecalentamiento ni la de RAM agotada con la evidencia disponible.

---

## B. Matriz A.7.4

### B.1 Artefactos y transcripciones

| Dimensión | `5KtjJ8kefQ4` | `DnwM-2nuS4s` | `j06_M-fADjM` |
|---|---|---|---|
| Título | Bitcoin rebota tras las elecciones: ¿es el principio de la reversión? | Bitcoin cae desde los 80.308 tras abrir Nueva York: el plan se cumple | Bitcoin refugiado en 80.308: ¿quién le da la patada al balón? |
| Publicado | 2026-11-04T18:44:04Z | 2026-11-05T18:49:09Z | 2026-11-05T09:20:28Z |
| MP4 | 15.709.968 B · 481,837 s · h264 640×352 · 30 fps | 18.634.392 B · 506,892 s · h264 640×352 · 30 fps | 22.830.168 B · 636,668 s · h264 640×352 · 30 fps |
| Frames en disco | 16 (`frame_0001`–`frame_0016`) | 17 (`frame_0001`–`frame_0017`) | 20 (`frame_0002`–`frame_0021`; **no hay `frame_0001`**) |
| Cues JSON / VTT | 437 / 437 | 469 / 469 | 550 / 551 (1 cue vacío descartado) |
| Contaminación | 0 segmentos con `-->`, `<c>` o `<00:` | 0 | 0 |
| Textos vacíos | 0 | 0 | 0 |
| Timestamps | 0 malformados · monotónicos · 0 solapes | 0 · monotónicos · 0 | 0 · monotónicos · 0 |
| Duración JSON vs `ffprobe` | 483,655 vs 481,837 s (**+1,818 s**) | 508,497 vs 506,892 s (**+1,605 s**) | 638,298 vs 636,668 s (**+1,630 s**) |
| JSON actual | `data_hist/5KtjJ8kefQ4/5KtjJ8kefQ4_transcript.json` (mtime 17:20:19) | `data_hist/DnwM-2nuS4s/DnwM-2nuS4s_transcript.json` (17:20:19) | `data_hist/j06_M-fADjM/j06_M-fADjM_transcript.json` (17:20:19) |
| Checkpoint | `completed`; 5/5 pasos `true`; `last_error: null` | `completed`; 5/5 `true`; `null` | `completed`; 5/5 `true`; `null`; `analysis_file` apunta a `data_hist` |

**Observaciones de transcripción:**

- Los JSON actuales son los regenerados a las 17:20:19 del 12-nov. Los backups corruptos son anteriores: `experimental/results/backups_a74/*_transcript.json.corrupto.bak` (15:05–15:06).
- El `full_text` de los tres empieza con frases repetidas ("Saludos cordiales, pues vamos a Saludos cordiales, pues vamos a..."). Es el efecto de los auto-subtítulos "rolling" de YouTube, no contaminación de cues: los segmentos tienen texto limpio y timestamps válidos.
- `j06` tiene 551 líneas de cue en el VTT y 550 segmentos en el JSON: el parser descartó un cue sin texto. No es pérdida de contenido.
- El JSON no incluye `language` ni `source` a nivel raíz (sí `source` por segmento). No es un error funcional, pero es una inconsistencia de esquema.

### B.2 Visión y validación

| Dimensión | `5KtjJ8kefQ4` | `DnwM-2nuS4s` | `j06_M-fADjM` |
|---|---|---|---|
| Visión en el lote A.7.4 | 16/16 | 17/17 | 3/20 (`frame_0002`–`0004`) |
| Modelo del lote | `qwen2.5vl:3b` (comando verificado) | `qwen2.5vl:3b` | `qwen2.5vl:3b` (mismo comando) |
| Timestamps del lote | 21:02:36Z–21:14:01Z | 21:14:11Z–21:17:28Z | 21:17:44Z, 21:17:58Z, 21:20:24Z |
| Análisis final en disco | 16/16, mismo archivo | 17/17, mismo archivo | **20/20** en `data_hist/j06..._analysis.json` (14:21:11Z–14:32:19Z, 14-nov) |
| Modelo del run final de j06 | — | — | No registrado; se infiere `qwen2.5vl:3b` por coherencia, **[INFERIDO]** |
| Placeholders `PRICES: [list visible prices or null]` | 1/16 (`frame_0016`) | 6/17 (`0001`, `0002`, `0012`, `0015`, `0016`, `0017`) | 1/20 (`frame_0006`) |
| Señales de calidad | `frame_0013`: serie alternante `88.537/88.517`; `frame_0015`: `INSTRUMENT: ES` | `frame_0013`: precios `2.129,7–3.017,7` en un video de BTC; `frame_0014`: `ES`; 13/17 con `INDICATORS: MA` | 1 frame `ES`; 8/20 con `INDICATORS: MA` |
| Validación del lote | **FAIL** `'str' object has no attribute 'exists'` · 717,1 s · `result: False` | **FAIL** mismo error · 206,6 s · `result: False` | **No llegó**: matado externamente a las ~18:20, sin línea de cierre |
| Checkpoint actual | `validation: true` (estructural) | `validation: true` (estructural) | `validation: true` (estructural) |

**Evidencia del lote:**

- Comando verificado en el registro de shell de OpenCode: `for v in 5K... DnwM... j06...; do .venv/bin/python run_video.py --video $v --vision-model qwen2.5vl:3b > experimental/logs/run_${v}_a74.log 2>&1; done`. PID 3373, inicio 18:02:04. [VERIFICADO]
- 5K: `experimental/logs/run_5KtjJ8kefQ4_a74.log`, línea 55: `Terminado en 717.1s - result: False`; línea 59: `last_error: error inesperado: 'str' object has no attribute 'exists'`; línea 60: `vision: True, validation: False`.
- DnwM: `experimental/logs/run_DnwM-2nuS4s_a74.log`, línea 57: `Terminado en 206.6s - result: False`; línea 61: mismo error; línea 62: `vision: True, validation: False`.
- j06: `experimental/logs/run_j06_M-fADjM_a74.log`, 24 líneas, solo frames 0002–0004, sin línea de cierre. `experimental/logs/batch_a74_done.flag` = `DONE_18:21:30`.
- El timeout inicial de 5K (15:54–16:04) fue con `qwen3.5:9b-mlx`: `video_5KtjJ8kefQ4.log`, `[vision] modelo local: qwen3`, `Terminado en 600.1s`, `timed out`. El lote de 18:02 cambió a `qwen2.5vl:3b`; la preferencia por defecto del código sigue siendo `qwen3.5:9b-mlx`. [VERIFICADO]

### B.3 Qué completó OpenCode en A.7.4

1. **Corrección del parser VTT→JSON (CR1).** Los tres JSON se regeneraron a las 17:20:19 y pasaron la validación de esquema: 437/469/550 cues, sin contaminación, timestamps válidos. Los backups corruptos quedaron preservados en `experimental/results/backups_a74/`.
2. **Reanudación secuencial con `qwen2.5vl:3b`.** El lote de 18:02:04 procesó 5K (16/16) y DnwM (17/17) y dejó los análisis con `frames_processed` correcto. j06 alcanzó 3/20 y fue interrumpido a las ~18:20; el flag de fin de lote se escribió a las 18:21:30.
3. **Fallo de validación por tipo de dato.** `validate_video` recibió rutas como `str` y llamó `.exists()`; el lote terminó con `result: False` en 5K y DnwM. El error es de software, no de datos.
4. **Cierre documental incompleto.** `reports/fase_a7_4_cierre_tecnico.md` se escribió a las 18:03:10, mientras el lote corría, y dejó §6 ("Frames analizados"), §7 ("Resultados y errores por video") y §8 ("Estado final real") como placeholders. No se actualizó después.
5. **Trabajo posterior, fuera del lote A.7.4.** `run_video.py` se corrigió el 14-nov 11:17 (coerción de artefactos `str` → `Path`); j06 se completó a 20/20 entre 11:21 y 11:32 del 14-nov. El 16-nov quedó la versión final de `rss_priority_processor.py` (mtime 19:25), que incluye persistencia atómica, estado `transcribed` y resolución de rutas; a las 19:26 se reescribió el checkpoint.
6. **Conclusión:** el **resultado** de A.7.4 existe y es utilizable, pero el **cierre** de A.7.4 no está probado: el lote original falló en validación, j06 no terminó en el lote y el informe de cierre quedó incompleto. La finalización real es una mezcla de 12-nov (5K/DnwM/parser), 14-nov (j06) y 16-nov (checkpoint).

### B.4 Calidad visual: lo que el checkpoint no dice

La validación que hoy marca `validation: true` es **estructural**: comprueba que el MP4 exista, que haya frames, que el transcript exista y que el JSON de análisis tenga `frames_processed` distinto de cero (`scripts/rss_priority_processor.py:911-958`). **No** comprueba:

- que `PRICES` no sea el placeholder;
- que la serie de precios no sea sintética o repetitiva;
- que el instrumento y la temporalidad correspondan al video;
- que cada frame tenga un mapeo temporal (`frame ↔ timestamp`);
- que los niveles citados en la transcripción aparezcan en la imagen.

El proyecto ya tiene un estándar más exigente: `reports/fase_a7_4_validacion_LFHkc5dUoLw.md` documenta D1–D6 (precios fabricados, MA falso positivo, Fibonacci no reportado, sin mapeo frame-timestamp, cobertura incompleta, frame no inspeccionado). Ese estándar **no se aplicó** a 5K/DnwM/j06.

Ejemplos concretos [VERIFICADO]:

- `5KtjJ8kefQ4`, `frame_0013`: `PRICES: [88.537, 88.517, 88.537, 88.517, ...]` repetido decenas de veces.
- `DnwM-2nuS4s`, `frame_0013`: `PRICES: [2,129.7, 2,227.7, 2,249.3, ..., 3,017.7]`, una progresión artificial en un video de BTC.
- `5K`, `frame_0015` y `DnwM`, `frame_0014`: `INSTRUMENT: ES` (futuros del S&P), no BTCUSD.

**Veredicto de calidad:** los tres videos están **operacionalmente completos** y **semánticamente no validados**. No se puede afirmar que la visión sea correcta solo porque haya 16/17/20 resultados no vacíos.

### B.5 Veredicto por video

| Video | Operacional | Calidad visual | Cierre documental | Veredicto |
|---|---|---|---|---|
| `5KtjJ8kefQ4` | Sí: MP4, 16 frames, transcript 437, visión 16/16 | No validada; 1 placeholder y serie sintética | §6–§8 del cierre A.7.4 incompletos | **Completo con reservas** |
| `DnwM-2nuS4s` | Sí: MP4, 17 frames, transcript 469, visión 17/17 | No validada; 6 placeholders y precios no-BTC | §6–§8 incompletos | **Completo con reservas** |
| `j06_M-fADjM` | Sí: MP4, 20 frames, transcript 550, visión 20/20 | No validada; 1 placeholder y 1 `ES` | Lote A.7.4 solo 3/20; 20/20 vino del 14-nov | **Completo con reservas; trazabilidad partida** |

---

## C. Risk Manager V0

### C.1 La especificación V0

- **Archivo:** `docs/risk_manager/especificacion_funcional_v0.md`.
- **Tamaño:** 387 líneas; secciones 0–9; mtime 2026-11-12 18:07:53; sin modificaciones posteriores. [VERIFICADO]
- **Estado declarado:** "ESPECIFICACIÓN — no implementada. Este documento no autoriza ninguna implementación ni modificación de código."
- **Rol:** evaluador único de riesgo y capital; **nunca ejecuta órdenes**; operativa manual.
- **Marcas:** `[CONFIRMADO]`, `[PENDIENTE]`, `[DISEÑO]`.
- **Pendientes P1–P13:** capital total y por cuenta; divisa USD/USDT; riesgo máximo por operación; límite diario; límite semanal; exposición máxima por activo/grupo; apalancamiento máximo; operaciones concurrentes; profundidad de escenarios; reserva intocable; frescura del snapshot; zona horaria/semana; tratamiento de spot largo plazo.
- **Criterios de aceptación (11):** pureza/determinismo, no-ejecución, separación de cuentas, spot vs apalancado, fail-closed, stop obligatorio, auditoría con hashes, aprobación humana, escenarios, tests, documentación.
- **Gobernanza §9:** primero el usuario define P1–P13 y firma `RiskPolicy` v1; después se implementa el evaluador puro y los tests; después el snapshot de capital; solo al final se integra con el YouTube Analyst.

**Veredicto V0:** especificación completa y coherente; **no implementada**. No hay evidencia de que el V0 se haya codificado.

### C.2 El prototipo de `daily_pilot`

- **Archivos:** `daily_pilot/risk_manager/risk_manager.py` (186 líneas, mtime 2026-11-16 14:57), `test_risk_manager.py` (109 líneas, 14:42), `INTERFACE.md` (14:44), `senales_piloto_s_GjovZxQqY.json` (14:58).
- **Modo:** `PAPER_ONLY = True`; no hay APIs de trading ni envío de órdenes; no se conecta a Binance/Quantfury.
- **Config por defecto:** capital 10.000; riesgo 1 %; exposición 5 %; máximo 2 señales por instrumento; confianza mínima 0,5; evidencia obligatoria.
- **Salida:** `ACEPTAR | RECHAZAR | REVISION MANUAL`, razones, exposición total, riesgo por señal (`risk_per_unit`, `position_size`, `perdida_potencial`, `r_multiples`).
- **Pruebas:** 14 casos sintéticos; el informe y la interfaz declaran **14/14 OK**. No se re-ejecutaron en esta auditoría porque la orden prohíbe arrancar el Risk Manager; la verificación es estática (conteo de 14 casos y lectura del código).
- **Señales reales:** 5 señales del video `s_GjovZxQqY`; resultado declarado 3 ACEPTAR, 2 REVISIÓN MANUAL; exposición 500 (5 %). [VERIFICADO en el informe de cierre, no re-ejecutado]

### C.3 Cobertura frente al V0

| Requisito V0 | Spec | Prototipo `daily_pilot` | Cobertura |
|---|---|---|---|
| Evaluador puro/determinista con `calc_trace` | Sí | Parcial: estado en memoria, sin traza reproducible | **Parcial** |
| No ejecución de órdenes | Sí | Sí: `PAPER_ONLY`, sin APIs de trading | **Sí** |
| Cuentas y categorías de capital (Binance Spot / Quantfury) | Sí | No: una sola cuenta implícita | **No** |
| Riesgo máximo por operación | Sí (valor P3) | Sí: 1 % por defecto, no por cuenta | **Parcial** |
| Exposición agregada por activo y correlación | Sí | Solo suma de pérdida potencial; sin correlación | **Parcial** |
| Apalancamiento y margen | Sí | No | **No** |
| Stop/invalidación obligatoria | Sí | Invalida si falta `invalidation`; no hay campo `stop` explícito | **Parcial** |
| Límites diarios y semanales | Sí | No | **No** |
| Escenarios de riesgo (gap, liquidación, reserva) | Sí | No | **No** |
| Aprobación humana obligatoria | Sí | `REVISION MANUAL` + `PAPER_ONLY`; no hay workflow de aprobación | **Parcial** |
| `RiskPolicy`/`CapitalSnapshot`/ledger con hashes/fail-closed | Sí | No: `Config` con defaults, historial en memoria | **No** |
| Tests de las reglas §4.1–§4.7 | Sí | 14 casos sintéticos de un subconjunto | **Parcial** |

### C.4 Veredicto Risk Manager

- **V0 (spec):** completo, coherente y con los parámetros financieros explícitamente pendientes. **No implementado.**
- **Prototipo:** componente aislado, útil para el piloto diario, `PAPER_ONLY`, con 14 casos declarados. **No es el V0** y no cubre cuentas, correlación, apalancamiento, límites temporales, escenarios, ledger ni fail-closed.
- **Riesgo de gobernanza:** llamar "Risk Manager V0 completado" al prototipo sería inexacto. La spec y el prototipo son dos artefactos distintos, con fechas y alcances distintos.
- **Estado de servicios:** no se arrancó el Risk Manager ni el Analyst Manager; no hay procesos de trading; no se enviaron órdenes.

---

## D. Cronología

### D.1 Tabla de eventos

| Fecha/hora (-03) | Evento | Evidencia |
|---|---|---|
| 10-nov 17:33 | Detección de los tres videos | `detected_at` en el checkpoint (20:33:20Z) |
| 10–11-nov | Descarga, frames y primeras transcripciones | `data_hist/`, `frames_hist/`, logs del processor |
| 12-nov 13:55–14:46 | **27 crashes de `python3.11` de Harness** (SIGABRT, coalition `com.harness.jarvis-s2s`) | `~/Library/Logs/DiagnosticReports/Retired/python3.11-2026-11-12-*.ips` |
| 12-nov 14:11:41 | **Jetsam**: `python3.11` (Harness) 8,9 GB; `knowledgeconstructiond` matado por `per-process-limit`; free 9,7 GB | `JetsamEvent-2026-11-12-141141.ips` |
| 12-nov 15:05–15:06 | Backups de transcripts corruptos | `experimental/results/backups_a74/*.corrupto.bak` |
| 12-nov 15:42–15:43 | Presión térmica reportada por `mediaanalysisd` | `log show`, 5 mensajes "Device is under thermal pressure" |
| 12-nov 15:54–16:04 | 5K con `qwen3.5:9b-mlx`: timeout 600,1 s | `video_5KtjJ8kefQ4.log` |
| 12-nov 17:20:19 | JSON de transcript regenerados (437/469/550) | mtime de los tres `*_transcript.json` |
| 12-nov 17:26 | **Arranque** (sin panic report asociado) | `last reboot` / `wtmp` |
| 12-nov 17:43:28 | **Pánico #1**; reboot 17:43; consola 17:43–17:48 (crash a los 5 min) | `panic-base+socd-2026-11-12-174328.panic`; `wtmp` |
| 12-nov 17:49:51 | **Pánico #2**; reboot 17:49; sesión actual desde entonces | `panic-base+socd-2026-11-12-174951.panic`; `wtmp` |
| 12-nov 18:02:04 | Inicio del lote A.7.4 con `qwen2.5vl:3b` | PID 3373, registro de shell de OpenCode |
| 12-nov 18:03:10 | Informe de cierre A.7.4 con §6–§8 placeholders | `reports/fase_a7_4_cierre_tecnico.md` |
| 12-nov 18:14:01 | 5K termina: 16/16 visión, validación FAIL (`'str'...`) | `run_5KtjJ8kefQ4_a74.log` |
| 12-nov 18:17:28 | DnwM termina: 17/17 visión, validación FAIL | `run_DnwM-2nuS4s_a74.log` |
| 12-nov 18:20:24 | j06 matado tras 3/20 frames | `run_j06_M-fADjM_a74.log`; análisis de 3 frames |
| 12-nov 18:21:30 | Flag de fin de lote | `batch_a74_done.flag` |
| 12-nov 18:21:57 | Auditoría de recursos (sin análisis de pánicos; afirma "No hubo reinicio") | `reports/auditoria_recursos_mac.md` |
| 14-nov 11:17:41 | Fix de `run_video.py` (coerción `str` → `Path`) | mtime y líneas 58–62 |
| 14-nov 11:21–11:32 | j06 completado a 20/20 en `data_hist` | `j06..._analysis.json`, timestamps |
| 15-nov 13:47 | Detección de nuevos videos (`bCc`, `Vm7`, `rX2w`) | `rss_priority_processor.log` |
| 15-nov 17:00 | Validación LFH `LFHkc5dUoLw` con veredicto `validation=false` (D1–D6) | `reports/fase_a7_4_validacion_LFHkc5dUoLw.md` |
| 16-nov 14:42–14:58 | Prototipo Risk Manager + 14 tests declarados | `daily_pilot/risk_manager/` |
| 16-nov 16:22 | Backups y cambios del scheduler (`--no-vision`, `transcribed`) | `.backups_scheduler/`; `rss_4h_scheduler.sh` |
| 16-nov 19:25–19:26 | Cambio del processor y reescritura del checkpoint (22:26Z según R1–R4; atribución no trazada en el log del cron) | mtimes; `historical_progress.json`; `informe-r1-r4-2026-11-16.md` |
| 17-nov 12:00 y 16:00 | Ciclos del scheduler: **self-skip** y log de éxito falso | `~/.hermes/cron/output/rss_4h_scheduler.log` |
| 17-nov 18:30–18:55 | Esta auditoría; uptime 5 días 48 min | `kern.boottime`, `uptime` |

### D.2 Lectura de la secuencia

- **Los dos reinicios del Mac son los pánicos de 17:43 y 17:49**, no los "2 reinicios del servidor de ejecución" que menciona el cierre A.7.4 (§5.4). Esos otros reinicios son del servidor de OpenCode y mataron shells; no son reinicios de macOS.
- **El arranque de 17:26 es un tercer arranque**, sin panic report. No se puede afirmar que sea normal ni que sea un pánico sin reporte: simplemente **no está establecido**.
- **El lote A.7.4 corrió después de los pánicos** (18:02), así que los pánicos no interrumpieron el lote. Las causas del fallo del lote son software (validación `str.exists`) y una interrupción externa de j06.
- **Los 27 crashes de `python3.11` son de Harness, no del Mac.** Ocurrieron entre 13:55 y 14:46, en torno al Jetsam de 14:11 y antes de los pánicos de 17:43/17:49. No son la causa de los reinicios.

---

## E. Diagnóstico de los reinicios

### E.1 Evidencia primaria

| Evidencia | 17:43 | 17:49 | Lectura |
|---|---|---|---|
| Panic report | `panic-base+socd-2026-11-12-174328.panic` | `panic-base+socd-2026-11-12-174951.panic` | Dos pánicos, no un cierre limpio |
| `panicString` | `SOCD report detected: (iBoot async abort)` | Idéntico | Firma de aborto asíncrono de iBoot |
| Firma decodificada | `iBoot Panic: : AMCC error: AMCC 1/1 error: INTSTS0/1/2 0x8000/0/0 AFERRLOG... ADDR 0x10106db3fc0 ... Board: j713ap:0x4 Chip: 8132:0x11 Build: RELEASE:iBoot-13822.41.1 UUID: B858961D-8C26-3EA3-A47D-19CC650B2990` | Idéntica, mismo UUID | Misma firma en ambos |
| `ResetCounter` | 17:43:29: reset count 1, boot failure count 1, `Boot faults: wdog,reset_in_1` | 17:49:52: idéntico | Watchdog + reset en el arranque |
| `pmset` | `powerd process is started` 17:43:28 | `powerd process is started` 17:49:52 | Dos arranques, sin shutdown cause registrado |
| `wtmp` | `reboot 17:43`; consola 17:43–17:48 (crash a los 5 min) | `reboot 17:49`; consola 17:49 "still logged in" | Dos reinicios; el segundo dejó la sesión actual |
| Ollama | `server-1.log` inicia 17:43:41 | `server.log` inicia 17:50:03 | Corrobora ambos arranques |
| Térmico | Sin eventos de presión 17:00–17:50; solo `mediaanalysisd` 15:42–15:43; `itunescloudd` reporta `thermal pressure level=0` a las 17:49:57 | Ídem | No hay apagado térmico ni presión térmica cerca de los pánicos |
| Memoria | Sin Jetsam 17:00–17:50; Jetsam de 14:11 (Harness) | Ídem | No hay agotamiento de RAM en la ventana de los pánicos |

### E.2 Secuencia reconstruida

1. **17:26** — arranque. No hay panic report. La causa no está establecida; no se encontró un `shutdown cause` en `pmset`.
2. **17:43:28** — pánico #1 con firma `AMCC`. El sistema reinicia; hay una sesión de consola de ~5 minutos que termina en crash.
3. **17:49:51** — pánico #2 con la misma firma y el mismo UUID de iBoot. El sistema reinicia y queda en la sesión actual; `kern.boottime` marca 17:49:21 y `pmset` registra `powerd` a las 17:49:52 (desfase de reloj de ~30 s, coherente con el aviso "Wall Clock adjustment detected").
4. **Después** — no hay más pánicos ni reinicios. Al 17-nov 18:37, 5 días 48 min de uptime.

### E.3 Qué se puede y qué no se puede afirmar

**Se puede afirmar:**

- Hubo **dos pánicos** con firma idéntica `AMCC error` / `iBoot async abort`, ambos con `wdog,reset_in_1`.
- Fueron reinicios **no limpios**, no apagados programados.
- **No** hay evidencia de presión térmica ni de Jetsam en la ventana 17:00–17:50.
- La firma es de bajo nivel (iBoot/firmware/controlador), no un panic de un proceso de usuario.

**No se puede afirmar:**

- Que la causa sea **sobrecalentamiento**. Los únicos eventos de presión térmica verificados son de `mediaanalysisd` a las 15:42–15:43, más de dos horas antes, y no hay shutdown térmico.
- Que la causa sea **RAM agotada**. El Jetsam de 14:11 fue un evento de límite de proceso (`knowledgeconstructiond`) con 9,7 GB libres y 5,7 GB de compresor; no es un agotamiento global y ocurrió 3,5 horas antes.
- Que sea un componente hardware concreto (memoria, SSD, etc.) o un bug de firmware concreto. La firma `AMCC` es compatible con un fallo de bajo nivel en el arranque, pero **requiere diagnóstico de Apple**.
- Que el arranque de 17:26 haya sido normal o provocado. No hay evidencia suficiente.

### E.4 Veredicto de reinicios

**Causa: NO DETERMINADA.** La hipótesis mejor sostenida por la evidencia es un fallo de bajo nivel en el arranque (memoria/controlador/firmware), no un problema térmico ni de RAM. La hipótesis de sobrecalentamiento o de agotamiento de RAM **no está probada** y no debe presentarse como conclusión.

**Recomendaciones (no ejecutadas):**

1. Ejecutar Apple Diagnostics o llevar el equipo a servicio técnico con los dos panic reports y los `ResetCounter`.
2. Revisar actualizaciones de macOS/firmware disponibles para `Mac16,12` (macOS 15.5, build 24F74) antes de decidir nada.
3. Monitorear recurrencia; si vuelve a ocurrir, capturar `sysdiagnose` inmediatamente y preservar `/Library/Logs/DiagnosticReports/`.
4. No atribuir los pánicos a la carga de Ollama/Harness sin evidencia temporal; los pánicos ocurrieron antes del lote A.7.4 y no hay eventos térmicos/Memoria en esa ventana.

---

## F. Integridad

### F.1 Checkpoint vs artefactos

| Video | Checkpoint | Artefacto real | Evidencia de validación | Integridad |
|---|---|---|---|---|
| 5K | `completed`, 5/5 `true` | 16/16 frames; 437 cues; 16/16 visión | **No hay log de validación posterior**; el lote falló a las 18:14 | **Flag optimista** |
| DnwM | `completed`, 5/5 `true` | 17/17 frames; 469 cues; 17/17 visión | **No hay log de validación posterior**; el lote falló a las 18:17 | **Flag optimista** |
| j06 | `completed`, 5/5 `true` | 20/20 frames; 550 cues; 20/20 visión en `data_hist` | 20/20 del 14-nov; sin log de modelo; el lote solo hizo 3/20 | **Completo, trazabilidad partida** |

**Conclusión F.1:** el checkpoint describe el **estado actual de los archivos**, no el **resultado del lote A.7.4**. El `validation: true` de 5K/DnwM no tiene un log dedicado que lo sostenga; el código actual solo valida estructura. j06 sí tiene 20/20, pero el análisis está en `data_hist` y el checkpoint apunta allí; el análisis de 3 frames del lote sigue en `experimental/results/historical/j06_M-fADjM_analysis.json` como artefacto obsoleto.

### F.2 Informes vs evidencia

- **`reports/fase_a7_4_cierre_tecnico.md` (18:03:10):** §6, §7 y §8 son placeholders explícitos ("Sección completada al cierre del lote..."). El informe no contiene la tabla final de frames, resultados ni estado real. [VERIFICADO]
- **`reports/fase_a7_4_reanudacion_tres_videos.md` (15:58):** es una foto del estado de las 15:58, no un informe final. Declara DnwM/j06 con transcripción fallida (el checkpoint de ese momento decía `no se pudo extraer la transcripción`, aunque los JSON corruptos existían) y atribuye a 5K el modelo `qwen2.5vl:3b`, mientras el log de las 16:04 registra `qwen3[.5]`. No debe usarse como fuente de verdad del resultado final. [VERIFICADO]
- **`reports/auditoria_recursos_mac.md` (18:21:57):** analiza RAM/CPU/térmica, pero **no analiza los panic reports** de 17:43/17:49 y afirma en §6 "No hubo reinicio". Esa afirmación es inexacta para la jornada (hubo dos pánicos y tres arranques). Además, los eventos térmicos de 14:27/15:26/15:34 que cita no se reproducen en la consulta actual de `log show` (solo se verifican los de `mediaanalysisd` 15:42–15:43). [VERIFICADO]
- **`docs/audits/informe-r1-r4-2026-11-16.md`:** atribuye la reescritura del checkpoint a un ciclo del scheduler a las 22:26Z, pero el `rss_4h_scheduler.log` no muestra un ciclo a esa hora (los ciclos registrados son 19:00Z y 23:00Z). La atribución exacta no quedó trazada. [VERIFICADO]
- **`reports/fase_a7_4_validacion_LFHkc5dUoLw.md`:** es el estándar de validación más exigente del proyecto (D1–D6). No se aplicó a los tres videos de esta auditoría. [VERIFICADO]

### F.3 Calidad de visión

- Placeholders: 1/16 (5K), 6/17 (DnwM), 1/20 (j06). [VERIFICADO]
- Series sintéticas: 5K `frame_0013` alterna `88.537/88.517`; DnwM `frame_0013` recorre `2.129,7–3.017,7` en un video de BTC. [VERIFICADO]
- `INSTRUMENT: ES` en 1 frame de 5K, 1 de DnwM y 1 de j06. [VERIFICADO]
- `INDICATORS: MA` en 7/16, 13/17 y 8/20; el estándar LFH ya documentó que MA puede ser falso positivo. [VERIFICADO]
- El validador estructural no detecta ninguno de estos defectos. [VERIFICADO en `scripts/rss_priority_processor.py:911-958`]

### F.4 Scheduler y backlog

- **Bug de lock:** `scripts/rss_4h_scheduler.sh` crea el lock con `echo $$ > "$LOCK_FILE"` y luego pasa el mismo `--lock-file` al processor. El processor intenta `os.open(..., O_CREAT|O_EXCL)` y falla porque el archivo ya existe; registra `[lock] OMITIDO` y sale con éxito. El scheduler borra el lock y escribe "✅ RSS 4h check completado exitosamente". [VERIFICADO]
- **Frecuencia:** 30 entradas `OMITIDO` en `~/.hermes/cron/output/rss_4h_scheduler.log`; el ciclo del 17-nov 19:00Z (16:00 local) volvió a auto-omitirse. El lock no existe ahora. [VERIFICADO]
- **Consecuencia:** el backlog no avanza solo. Estado global del checkpoint: **20 videos — 15 completed, 1 processing, 3 detected, 1 transcribed**. [VERIFICADO]
  - `LFHkc5dUoLw`: `processing`, `validation: false`, con D1–D6 en `last_error`; no es un video "completado".
  - `bCc--rvyHpY`, `Vm7nUxLCMZQ`, `rX2wj_FXvT4`: `detected`, sin descarga/frames/transcripción.
  - `s_GjovZxQqY`: `transcribed`, visión pendiente.
- **Además:** el scheduler actual corre con `--no-vision`, así que incluso si el lock se arreglara, no ejecutaría visión. La decisión de dónde correr visión (Mac vs Kaggle/Colab) sigue abierta.

### F.5 Estado actual del sistema

- Uptime: 5 días 48 min; boot 2026-11-12 17:49:21. [VERIFICADO]
- Sin procesos `run_video.py`, `rss_priority_processor.py` ni `llama-server`; Ollama serve idle (`/api/ps` vacío). [VERIFICADO]
- Swap: 6.531,31 MB usados de 7.168 MB; no hay presión de visión activa. [VERIFICADO]
- Hermes, Gateway y OpenCode siguen corriendo; no se reiniciaron. [VERIFICADO]
- Esta auditoría no modificó nada salvo este informe. [VERIFICADO]

### F.6 "NO CREER. PROBAR." — tabla de afirmaciones

| Afirmación | Prueba aplicada | Veredicto |
|---|---|---|
| "A.7.4 está completado" | Artefactos sí; validación del lote falló; cierre §6–§8 incompleto | **PARCIAL** |
| "La visión de los tres videos está validada" | Solo validación estructural; placeholders y series sintéticas | **NO** |
| "Las transcripciones están recuperadas" | 437/469/550 cues; 0 contaminación; monotónicas | **SÍ** |
| "j06 tiene 20/20 frames analizados" | 20/20 en `data_hist` (14-nov); el lote solo hizo 3/20 | **SÍ, con trazabilidad partida** |
| "El Risk Manager V0 está hecho" | Spec sí; implementación V0 no; prototipo es un subconjunto | **NO** (spec sí) |
| "Los reinicios fueron por sobrecalentamiento" | Sin eventos térmicos 17:00–17:50; solo `mediaanalysisd` 15:42 | **NO** |
| "Los reinicios fueron por RAM agotada" | Jetsam de 14:11, no en 17:43/17:49; free 9,7 GB | **NO** |
| "El scheduler procesa videos cada 4 h" | 30 self-skips; log de éxito falso | **NO** |
| "No hubo reinicios desde el 12-nov" | Uptime 5 días 48 min | **SÍ** |

### F.7 Inconsistencias menores de esquema

- `j06` no tiene `frame_0001`; se analizaron los 20 frames existentes (`0002`–`0021`). No se re-extrajo para no cambiar el muestreo. [VERIFICADO]
- El checkpoint guarda `analysis_file` tanto dentro de `artifacts` como en el nivel superior; en DnwM/j06 hay rutas relativas y absolutas mezcladas. No rompe la lectura actual, pero es una fuente de ambigüedad. [VERIFICADO]
- Los JSON de análisis tienen `transcript_available: None`; no es un error, pero no documenta si el transcript se usó o no. [VERIFICADO]
- El análisis de 3 frames de j06 en `experimental/results/historical/` sigue existiendo; si alguna herramienta lo lee por convención, obtendrá un resultado obsoleto. [VERIFICADO]

---

## G. Próximos pasos priorizados

> **Ninguno de estos pasos fue ejecutado.** Se describen para autorización explícita.

| Prioridad | Acción | Por qué | ¿Requiere autorización? |
|---|---|---|---|
| **P0.1** | Validar semánticamente 5K/DnwM/j06 con el protocolo LFH (D1–D6), empezando por los frames con placeholder y series sintéticas; decidir si se aceptan o se reprocesan. | La validación estructural no distingue una visión correcta de una fabricada. | **Sí** (implica visión/procesamiento) |
| **P0.2** | Completar `reports/fase_a7_4_cierre_tecnico.md` §6–§8 y corregir las afirmaciones inexactas de los informes de reanudación y recursos. | El cierre documental de A.7.4 está incompleto y los informes previos contienen errores. | **Sí** (escritura) |
| **P0.3** | Diagnóstico de los pánicos `AMCC`: Apple Diagnostics/servicio, revisión de actualizaciones, preservación de logs, monitoreo de recurrencia. | Dos pánicos idénticos en 6 minutos; causa no determinada. | **Sí** (servicio/actualización) |
| **P1.4** | Corregir el lock del scheduler (handoff scheduler → processor) y el log de "completado exitosamente" cuando hubo self-skip. | El scheduler no procesa nada y reporta éxito. | **Sí** (código) |
| **P1.5** | Endurecer `validate_video`: detectar placeholders, series sintéticas, frame count vs disco, mapeo frame↔timestamp y coherencia instrumento/temporalidad. | `validation: true` hoy no significa calidad. | **Sí** (código) |
| **P1.6** | Normalizar artefactos y checkpoint: j06 3-frame vs 20-frame, rutas relativas/absolutas, campos duplicados, `frame_0001` ausente. | Evitar que una herramienta lea el artefacto obsoleto. | **Sí** (datos/checkpoint) |
| **P1.7** | Decidir la política de visión (Mac vs Kaggle/Colab) y el orden del backlog: `LFHkc5dUoLw` (processing), 3 `detected`, 1 `transcribed`. | El backlog no avanza y la arquitectura de visión está bloqueada. | **Sí** (decisión) |
| **P2.8** | Definir P1–P13 del Risk Manager V0 y, solo después, implementar el evaluador puro + tests. | La spec no se puede implementar sin los parámetros del usuario. | **Sí** (decisión/diseño) |
| **P2.9** | Documentar el alcance del prototipo `daily_pilot` y sus límites; no presentarlo como V0 ni conectarlo a trading. | Evitar una falsa sensación de Risk Manager completo. | **Sí** (documentación) |
| **P3.10** | Housekeeping: backups, rotación de logs, índice de informes. | Mantener la trazabilidad a futuro. | **Sí** (housekeeping) |

### Cierre

- **No se ejecutó ninguno de los pasos de G.**
- No se procesó ningún video, no se ejecutó visión, no se reinició ningún servicio, no se modificaron scheduler, checkpoints, flags, modelos ni configuración.
- El único archivo creado por esta auditoría es `reports/auditoria_estado_post_reinicios.md`.
- Si se autoriza algo, conviene indicarlo por número (por ejemplo, `P0.1`, `P1.4`) para mantener la trazabilidad.

### Limitaciones de esta auditoría

1. `log show` tiene retención limitada; los eventos térmicos de 14:27/15:26/15:34 que cita el informe de recursos **no** se pudieron reproducir en la consulta actual. Solo se usan como evidencia los eventos verificados (15:42–15:43).
2. El modelo del run de j06 del 14-nov no quedó registrado; se infiere `qwen2.5vl:3b` por coherencia con el lote y la configuración, pero no está verificado.
3. Los 14/14 tests del prototipo Risk Manager son una afirmación de `INTERFACE.md`/`INFORME_CIERRE_FASES.md`; no se re-ejecutaron porque la orden prohíbe arrancar el Risk Manager.
4. La causa del arranque de 17:26 no está establecida; no hay panic report asociado.
5. La atribución exacta de la reescritura del checkpoint del 16-nov 19:26 no quedó trazada en un log de validación por video.

---

*Auditoría generada el 2026-11-17. Evidencia primaria: `experimental/results/historical_progress.json`, `experimental/logs/run_*_a74.log`, `experimental/results/historical/*_analysis.json`, `data_hist/*/`, `frames_hist/*/`, `reports/*.md`, `docs/risk_manager/*`, `daily_pilot/risk_manager/*`, `/Library/Logs/DiagnosticReports/Retired/`, `~/.hermes/cron/output/rss_4h_scheduler.log`, `~/.ollama/logs/`, `pmset -g log`, `last reboot` y `wtmp`.*
