# VEREDICTO — Auditoría DeepSeek (opencode/deepseek-v4.1-flash-free)

Fecha: 2026-11-18 · Verificado por Hermes contra el repo real · **Solo lectura**

## Veredicto de la verificación

**La auditoría es SÓLIDA.** Los 5 hallazgos P0 y los P1 clave son **reales y reproducibles**.
 Única diferencia: el lote nocturno tiene **21** vídeos fuera de DB/registro (el informe dice 20).

| # | Hallazgo | Estado | Evidencia de Hermes |
|---|---|---|---|
| P0-1 | Expectativa mal calculada (doble descuento) | **CONFIRMADO** | `metrics/metrics.py:91-93` = `tasa*r_medio-(1-tasa)*1.0`; `r_medio` ya incluye perdedores |
| P0-2 | Estado se invierte a medianoche local | **CONFIRMADO** | `daily_pilot.py:84` UTC vs `control_diario.py:95` `hoy()` local. El log real: 03:49Z → `SIN VIDEO NUEVO` |
| P0-3 | Cadena de integridad rota | **CONFIRMADO** | `hashes_store.pre == .post` (`1f6b9b61…`); `store.db` real `c55ace4f…`; `meta` `13cc57f4…`; manifest real `de692f5a…`; `pruebas.conteo_videos_20: True` con `videos_post: 21` |
| P0-4 | Linaje roto DB/registro/nocturno | **CONFIRMADO** | DB 21 vs registro 16; 5 vídeos en DB ausentes del registro; **21** del nocturno fuera de ambos; `i0qXzL0eSYs` con 3 fechas |
| P0-5 | Dashboard mezcla estado actual con datos viejos | **CONFIRMADO** | `dashboard_data.json` fuente `s_GjovZxQqY (2026-11-16)`; `situacion` dice "no fue analizado" cuando `analisis/i0qXzL0eSYs_analisis.json` existe; `ultimo_analizado` = `s_GjovZxQqY` |
| P1-1 | `published=NULL` → 1970 | **CONFIRMADO** | `construir_escenarios.py:23-24`; 4 entradas con fecha `1970-01-01` |
| P1-2 | 101 `SENAL_EXPLICITA` falsos | **CONFIRMADO** | 101 casos; ejemplos: «si vemos entrar aquí», «vería si el dinero institucional entra» |
| P1-3 | Contaminación de instrumento | **CONFIRMADO** | `vigentes.json` XAUUSD incluye 1890 / 2077 / 2132 |
| P1-4 | Manager usa `stop or 0` como riesgo | **CONFIRMADO** | `core/manager.py:170` → `riesgo = abs((entrada or 0) - (stop or 0)) or None` |

## Impacto inmediato (hoy)

El dashboard **miente ahora mismo**: con `i0qXzL0eSYs` analizado a las 21:43Z, el estado dice
`SIN VIDEO NUESTA` / `SIN VIDEO NUEVO` y la situación «NO DISPONIBLE · el video todavía no fue analizado»,
por el bug de timezone (P0-2) + `ultimo_analizado` desactualizado (P0-5).

## Plan propuesto — FASE 0 (sanear confianza, sin features)

**Objetivo**: que los datos, el tiempo y el dashboard vuelvan a ser confiables antes de construir nada.

1. **P0-1** `metrics.py`: `expectativa = mean(r_real)`; reportar `n` y `NO DISPONIBLE` si `n < 30`. Test golden `+2R/-1R = +0.5`.
2. **P0-2** Timezone: comparar en **UTC** (`detectado[:10] == now_utc[:10]`); hora local solo para mostrar. Test con reloj fijo 03:30Z.
3. **P0-3** Integridad: hashear **después** de todos los writes; una clave canónica; nuevo `knowledge/verify_integrity.py` (read-only) que **falle** si no coincide.
4. **P0-4** Linaje: reporte de reconciliación **read-only** + decisión explícita (¿importar el nocturno?) **antes** de tocar E1, con backup verificado.
5. **P0-5** Dashboard: separar `estado` de `último análisis completo`; no publicar datos de mercado sin fecha.
6. **P1-1/2/3/4**: `1970`→`SIN_FECHA`, negación/condición como precondición del clasificador, instrumento por claim, `stop` ausente → `None`.
7. **Tests herméticos**: `tests/run_all.py` en directorios temporales; `sha256` de `store.db`/`registro.json`/`dashboard_data.json` idéntico antes y después.

**No se toca**: skill `youtube-trading-agent`, cron/scheduler/LaunchAgents, `dashboard_data.json`, `registro.json`, `config.yaml`, E1 sin backup.

**Aceptación**: golden test de expectativa; test de timezone; `verify_integrity` OK; hashes de producción invariantes; 0 escrituras en E1.

**Estimación**: 2-3 días (Fase 0). Total de la ruta completa: 22-36 días sin visión.

## Decisiones que necesito de vos

1. ¿Ejecuto **Fase 0** ahora (con los fixes P0/P1 y tests herméticos)?
2. El lote nocturno (21 vídeos): ¿**importarlo a E1** (con backup) o dejarlo fuera como data histórica?
3. ¿Autorización de **código nuevo** (`verify_integrity.py`, `market_data/`) o solo fixes?
