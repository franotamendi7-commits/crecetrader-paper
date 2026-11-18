# INFORME CORRECTIVO — YouTube Analyst

Fecha: 2026-11-16 · Alcance: componentes aislados (`daily_pilot/`, `benchmark_vision_b1/`).

## 1. Correcciones realizadas

- **Clasificador obligatorio** (`daily_pilot/signal_classifier.py`) con 6 tipos: `NIVEL_MENCIONADO`, `ZONA_DE_INTERES`, `ESCENARIO_CONDICIONAL`, `SENAL_EXPLICITA`, `SIN_OPERACION`, `NO_DETERMINABLE`.
  - La **negación explícita prevalece** sobre todo otro criterio.
  - Solo `SENAL_EXPLICITA` es candidata operativa.
  - Sin condición explícita no hay escenario activable; sin entrada explícita no hay señal.
- **Risk Manager actualizado** (`risk_manager.py`): evalúa **únicamente** `SENAL_EXPLICITA`; el resto se marca `NO_EVALUABLE` con el motivo. Si falta `tipo`, lo infiere con el clasificador. Decisión global `REVISION MANUAL` si no hay candidatas.
- **Piloto diario** (`daily_pilot/scripts/`): detección RSS, anti-duplicados por registro, transcripción con timestamps, registro de estado y resumen. Script `run_daily.sh` listo.

## 2. Pruebas nuevas y resultados

| Suite | Resultado |
|---|---|
| `test_signal_classifier.py` | **10/10 OK** |
| `test_risk_manager.py` | **14/14 OK** |
| Clasificador + Risk Manager sobre las 5 señales del vídeo real | Las 5 quedan **NO_EVALUABLE**; solo una señal explícita hipotética es evaluada |

## 3. Ejemplos de clasificación (antes → después)

| Ejemplo del 16/11 | Antes | Después | Candidata operativa |
|---|---|---|---|
| 69.000–71.509 ("no era una señal de compra") | compra | **SIN_OPERACION** | no |
| 65.520 ("había que vigilar") | compra | **ZONA_DE_INTERES** | no |
| 56.750 ("en caso de caída") | compra | **ESCENARIO_CONDICIONAL** | no |
| 3.906–3.623 oro ("podría corregir") | venta | **ESCENARIO_CONDICIONAL** | no |

## 4. Estado real de la programación diaria

- **Existe y es real**: `crontab` → `0 */4 * * * …/rss_4h_scheduler.sh` (26 ejecuciones completadas registradas).
- **Riesgo crítico**: ese scheduler ejecuta `process_video`, que **incluye visión** → **inferencia audiovisual en el Mac cada 4 h** (prohibido). No lo desactivé (requiere autorización).
- **Piloto propio**: `run_daily.sh` está **listo pero NO instalado** (no hay cron del piloto). No afirmo automatización del piloto.
- LaunchAgent `com.hermes.youtube-daily-check` (9:00) pertenece al sistema **Harness** (no al piloto) y **genera señales automáticamente** — pendiente de revisión.

## 5. Último vídeo procesado

`s_GjovZxQqY` (2026-11-16, 21:02) — transcripción con timestamps completada. Informe: `daily_pilot/informes/s_GjovZxQqY_2026-11-16.md`. Sin análisis visual.

## 6. Estado de la arquitectura de visión

- **No hay infraestructura autorizada** para inferencia audiovisual.
- **Disponible y verificado (HTTP 200):** Kaggle (token en `~/.kaggle/`), Colab, HuggingFace. Kaggle sandbox **sin GPU** (CPU).
- **Propuesta concreta:** notebook Kaggle con `Qwen2.5-VL-2B/4B` en CPU por lotes de frames; coste 0; lento en CPU; cuota 30 h/sem. Requiere autorización para enviar frames y para usar la cuenta Kaggle.
- **Mientras tanto:** el análisis textual se identifica como **PARCIAL**.

## 7. Estado del Risk Manager

- Aislado, `PAPER_ONLY=true`, sin conexión con Binance/Quantfury.
- Interfaz documentada; distingue tipo de señal; no acepta señales experimentales automáticamente.
- Con las señales reales del vídeo: decisión global **ACEPTAR solo sobre la señal explícita hipotética**; las 5 reales no son operativas.

## 8. Bloqueos restantes

1. **B4**: faltan 2 anotadores humanos → modelo de visión no validado.
2. **Visión**: requiere máquina externa autorizada (propuesta en el punto 6).
3. **Scheduler RSS con visión**: el cron de 4 h ejecuta inferencia audiovisual en el Mac; requiere autorización para desactivarlo o añadir `--no-vision`.
4. **Harness daily-check**: genera señales automáticamente; fuera del alcance del piloto.
5. **Títulos desalineados** en `historical_progress.json` (no corregido: producción).

## Confirmación

Sin cambios en producción, prompts, modelos, skills ni configuración. `PAPER_ONLY=true`. No se ejecutó inferencia audiovisual en el Mac.
