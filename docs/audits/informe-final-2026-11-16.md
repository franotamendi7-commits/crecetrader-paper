# INFORME FINAL — ÚLTIMA AUDITORÍA TÉCNICA Y RECUPERACIÓN DEL DASHBOARD

Fecha: 16/11/2026 · Solo lectura + tests aislados · Sin Ollama, sin red, sin inferencia
`PAPER_ONLY=true` · Producción sin modificar

---

## 1. Estado general

- **Dashboard: recuperado y operativo** (`daily_pilot/dashboard/index.html`, 84.634 bytes). Abierto en el navegador. Datos incrustados **idénticos** a `daily_pilot/datos/dashboard_data.json`; 0 recursos externos.
- **Persistencia**: `save_state` es atómico; `_save_analysis` **no** y **crashea** si `analysis_file` es `None`.
- **Historial**: 20 vídeos, 382 frames, 306 resultados, 4 errores.
- **Modelos**: ninguno residente (`ollama ps` vacío).
- **Pruebas**: 8 + 9 + 23 = **40 passed** (vision_state, integración real, tests de producción).

## 2. Causas raíz demostradas (con evidencia)

| # | Causa | Evidencia |
|---|---|---|
| R1 | `_save_analysis(None, …)` → `AttributeError: 'NoneType' object has no attribute 'parent'` y no se escribe el checkpoint | ejecutado hoy; fallo real previo `proc_d0904ecc6af1` |
| R2 | `save_state` usa **un `.tmp` fijo**: dos procesos concurrentes pisan el mismo temporal | test de concurrencia: `FileNotFoundError` repetidos |
| R3 | `_save_analysis` escribe con `write_text` directo (sin tmp+replace) | inspección de código (líneas 925-975) |
| R4 | **32 rutas relativas** dependientes del *cwd* | `tools/vision_preflight.py --check-only` |
| R5 | Checkpoint de visión por frame (CR4, corregido antes) | `reports/fase_a7_4_cierre_tecnico.md:67`; 4 ERROR en `subONxt5iag` |

## 3. Problemas corregidos y pruebas realizadas

Corregidos en esta etapa (sin tocar producción): `tools/vision_preflight.py`, `tests/test_vision_state.py`, `tests/test_vision_state_integration.py`.

Pruebas ejecutadas (todas pasadas):
- `tests/test_vision_state.py` → **8 passed**
- `tests/test_vision_state_integration.py` → **9 passed** (integración con `_save_analysis`, `save_state`, `load_state` reales; interrupción, reanudación, rutas desde otro directorio, concurrencia, regresión de esquema real)
- `scripts/test_rss_priority_processor.py` + `test_resource_lifecycle_manager.py` → **23 passed**

## 4. Problemas pendientes e impacto

| Impacto | Problema | Efecto |
|---|---|---|
| **CRÍTICO** | R1 (crash con `analysis_file=None`) | impide procesar vídeos nuevos |
| **ALTO** | R2 (carrera en `.tmp`) | pérdida/corrupción si dos procesos escriben a la vez |
| **ALTO** | R4 (32 rutas relativas) | fallos si el cwd cambia (LaunchAgents/Hermes) |
| **ALTO** | R3 (no atómico) | JSON corrupto ante interrupción |
| MEDIO | `subONxt5iag`: `vision=true` con 4 ERROR | estado que no refleja la realidad |
| MEDIO | `mv2VdVtXvDw`: `transcript_path` apunta al `.vtt` (el `.json` sí existe) | referencia obsoleta |
| MEDIO | `0prmrS6nnRk`, `o6n6UDNVtCk`, `rTtXDLq2kOQ`: `completed` con `vision=false` | inconsistencia declarativa |

## 5. Persistencia y reanudación

- **Atómica**: `save_state` sí; `_save_analysis` no.
- **Checkpoint por frame**: persistido en `*_analysis.json` (`_save_analysis`), con anti-duplicado por nombre de frame (verificado).
- **Identificación de frames**: por nombre de archivo; **no por timestamp** (el timestamp no se persiste en el análisis).
- **ERROR/PENDING/COMPLETED**: `vision` solo se marca si **todos** los frames tienen resultado; los ERROR se arrastran sin marcar el paso (CR4 corregido).
- **Rutas**: no hay política de resolución; dependen del *cwd*.

## 6. Estado de los 20 vídeos y sus frames

382 frames · 306 resultados completos · 0 pendientes · 4 errores. Tabla completa en `docs/audits/vision-preflight-2026-11-16.md`.

Resumen: 16 vídeos con análisis; 3 sin frames (`bCc--rvyHpY`, `Vm7nUxLCMZQ`, `rX2wj_FXvT4`); `s_GjovZxQqY` con 20 frames sin analizar; `subONxt5iag` con 4 ERROR.

## 7. Modelos locales

- Instalados: `qwen2.5vl:3b` (3,2 GB), `moondream:latest` (1,7 GB), `qwen3.5:9b-mlx` (8,9 GB).
- **Residentes** (`ollama ps`): **ninguno**.
- Configurado: `VISION_MODELS = ["qwen3.5:9b-mlx", "qwen2.5vl:3b"]`.

## 8. Estado del Dashboard

- **Implementado y operativo**: HTML autocontenido, 5 vistas (Mercado, Planes, Oportunidades, Seguimiento, Decisión), datos reales de `s_GjovZxQqY` (8 escenarios), decisiones locales por `localStorage`.
- **No está servido** (archivo estático); se abrió con el navegador.
- **Parcial respecto a la sección 5**: no hay Gráficos Weekly/Daily/4H por instrumento, Fibonacci, liquidez ni volumen de forma sistemática; solo lo que los escenarios aportan.
- Sin backend ni servicios asociados; sin Risk Manager ni Analyst Manager (correcto por ahora).

## 9. Funcionalidades existentes y faltantes

**Operativas (verificadas)**: RSS + detección, transcripción, registro, clasificador de planes (9 tipos), Manager (4 dimensiones), Risk Manager, Dashboard.

**Faltantes/parciales**: verificación visual (bloqueada), persistencia corregida (propuesta), dashboard multi-temporalidad completo, feed OHLCV, feedback humano en el Dashboard.

## 10. Riesgos técnicos restantes

1. Reanudar vídeos nuevos puede fallar (R1) o corromper (R2/R3).
2. Rutas relativas frágiles en entornos con distinto *cwd*.
3. Estado declarativo incoherente en 4 vídeos.
4. Sin validación visual: todo nivel sigue sin contrastar con el gráfico.

## 11. Recomendación de continuidad

**Continuar**, con una única autorización consolidada para corregir R1-R4. No abrir nuevas líneas de investigación.

## 12. Próxima fase propuesta

Aplicar las correcciones consolidadas y rehacer el dashboard multi-temporalidad con los datos ya disponibles.

---

## Propuesta consolidada de correcciones (REQUIERE UNA ÚNICA AUTORIZACIÓN)

| Archivo | Cambio | Riesgo | Rollback |
|---|---|---|---|
| `scripts/rss_priority_processor.py` | `_save_analysis`: si `analysis_file` es None, derivar `experimental/results/historical/{video_id}_analysis.json` | bajo | revertir función |
| `scripts/rss_priority_processor.py` | `save_state`: `.tmp` único (PID+uuid) | bajo | revertir función |
| `scripts/rss_priority_processor.py` | `_save_analysis`: escritura atómica (tmp+replace+fsync) | bajo | revertir función |
| `scripts/rss_priority_processor.py` | Normalizar artefactos a rutas absolutas al cargar | medio | revertir |

- **Regresión**: las 40 pruebas actuales + tests de producción.
- **Backup**: copia de `rss_priority_processor.py` antes de tocarlo.
- **No** se ejecutará nada hasta la autorización.

## Confirmaciones

- No se ejecutaron modelos de visión; no se instaló nada; no se envió información fuera del Mac.
- No se modificó producción, scheduler, LaunchAgents ni configuración.
- Dashboard abierto y visible; datos coherentes con la última consolidación.
- No se inició FASE 3.3, benchmark sintético ni procesamiento masivo.
