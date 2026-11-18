# INFORME — Corrección del scheduler y preparación de Kaggle

Fecha: 2026-11-16 · Autorización parcial respetada (sin frames ni inferencia en Kaggle).

## A. Scheduler corregido y probado

**Dónde estaba la inferencia:** `scripts/rss_4h_scheduler.sh` → `rss_priority_processor.py::process_video` → paso 4 de visión (`analyze_frame_vision` → Ollama `/api/chat`), cada 4 h por `crontab`.

**Cambios** (con backup en `.backups_scheduler/`):
1. `rss_4h_scheduler.sh`: añadido `--no-vision`.
2. `rss_priority_processor.py`:
   - Nuevo estado `STATUS_TRANSCRIBED` (`"transcribed"`), añadido a `VALID_STATUSES`.
   - Con `--no-vision`, tras la transcripción el vídeo queda **`transcribed`** (visión pendiente) y **no** se marca `completed` ni pasa validación.
   - `run_cycle` excluye de la cola los `transcribed` cuando corre con `--no-vision`.

**Prueba ejecutada** (`--once --no-vision --max-videos-per-run 1`):
- Log: `[vision] omitido (--no-vision)` y `[ok] s_GjovZxQqY: transcrito (vision pendiente)`.
- Sin ninguna llamada a `/api/chat`: el único "qwen" del log es la línea informativa de modelos preferidos.
- `s_GjovZxQqY` → `status: transcribed`, `vision: false`.
- Sintaxis validada (`py_compile`, `bash -n`).

**Confirmaciones:**
- **Ningún proceso de visión activo** (`ps` limpio).
- RSS, detección, transcripción y registro **preservados**.
- **LaunchAgent de Harness intacto**: `com.hermes.youtube-daily-check.plist` sin cambios (md5 `c6e19b780bc8f78773e3fd4a424fa52b`, fecha 5 oct).
- Rollback: copias en `.backups_scheduler/` (`rss_priority_processor.py.bak_20261116_162208`, `rss_4h_scheduler.sh.bak_20261116_162208`).

## B. Kaggle — preparación técnica (sin procesamiento)

**Sonda de entorno ejecutada** (kernel privado, sin material del proyecto):
- Python 3.13.18 · PyTorch **2.11.0+cpu** · **CUDA: False → NO hay GPU** · 4 CPU · RAM 32,9 GB · disco 967 GB libres.
- transformers 5.20.2 · accelerate 1.15.0 · **qwen_vl_utils NO instalado** · PIL 13.0.0.

**Modelo verificado:** `Qwen/Qwen2.5-VL-3B-Instruct` (image-text-to-text, 2 shards). El 2B-Instruct no existe. El 7B es apache-2.0; el 3B no declara licencia en cardData → verificar antes de uso.

**Entregables:**
- `kaggle_notebook/qwen25vl/qwen25vl_vision.py` — notebook de inferencia (listo, **no ejecutado**).
- `kaggle_notebook/qwen25vl/probe_env.py` + `kernel-metadata.json`.
- `kaggle_notebook/qwen25vl/README.md` y `SONDA_ENTORNO.md`.
- `kaggle_notebook/test_image_sintetica.png` — imagen de prueba **no pertenece a los vídeos** y **no fue usada**.

**Costes y límites:**
- Coste 0 USD; cuota 30 h/semana de GPU, **no asignada** en la práctica.
- Rendimiento **estimado** (sin GPU): 60-180 s/frame en CPU → 157 frames ≈ 2,6-7,8 h. **Inviable en una sesión.**
- Fallo previo documentado (13-15/11, Qwen3-VL): errores de red y 401/403/404. No reutilizado.
- Privacidad: transferir frames exigiría dataset privado + autorización expresa. **No se transfirió nada.**

**Procedimiento propuesto (esperando autorización):** dataset privado → notebook con `pip install qwen-vl-utils` → lotes de 5-10 frames → descargar resultados → borrar dataset.

## Confirmaciones finales

- `PAPER_ONLY=true`. Ninguna operación de trading.
- Producción sin cambios de modelos, proveedores, prompts ni skills.
- Mac: **sin inferencia audiovisual por el scheduler**.
