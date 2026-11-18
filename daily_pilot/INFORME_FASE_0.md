# INFORME — FASE 0 (sanear confianza)

Fecha: 2026-11-18 · Autorización: «dale! autorizado!» · `PAPER_ONLY=true` · Backup: `daily_pilot/.backups_fase0_20261118T111917Z/`

Origen: auditoría DeepSeek (`opencode/deepseek-v4.1-flash-free`), **verificada por Hermes** — los 5 P0 y los P1 clave eran reales.

## Fixes aplicados

| # | Fix | Archivo | Verificación |
|---|---|---|---|
| **P0-1** | Expectativa = media de `r_real` (antes: doble descuento) | `metrics/metrics.py:90-99` | golden `+2R/-1R = +0.5` ✅ |
| **P0-2** | Comparar fechas en **UTC** (antes: hora local -03 invertía el estado a medianoche) | `control_diario.py:31-33` · `generar_dashboard.py:46-49,131` | el estado ya no se invierte ✅ |
| **P0-3** | Hash **post-escritura** + `verify_integrity.py` read-only | `knowledge/verify_integrity.py` (nuevo) | `RESULTADO: OK — hashes y conteos consistentes` ✅ |
| **P0-4** | Reconciliación de linaje read-only | `scripts/reconciliar_linaje.py` (nuevo) | `investigacion/linaje.json` ✅ |
| **P0-5** | `estado` separado de `ultimo_analisis_completo` | `control_diario.py:57-86,154-160` · `generar_dashboard.py:103-141` | dashboard: `ANALISIS PENDIENTE` + último análisis `i0qXzL0eSYs` ✅ |
| **P1-1** | `SIN_FECHA` en vez de `1970`; excluido de vigentes | `escenarios/construir_escenarios.py:23-27,51-52` | 4 entradas SIN_FECHA fuera de vigentes ✅ |
| **P1-2** | Negaciones ampliadas («no voy a comprar», «ni se me ocurre comprar»…) | `signal_classifier.py:26-32` | `SENAL_EXPLICITA` 101 → **93**; `SIN_OPERACION` 8 → **16** ✅ |
| **P1-3** | Instrumento por **proximidad** al número, sin cruzar «punto y aparte» | `relaciones/relaciones.py:66-83,91-105` | **XAUUSD 1890 eliminado** de vigentes (era contaminación real: «los 1.890. A continuación vemos el oro») ✅ |
| **P1-4** | Sin stop → `tamano_propuesto=None` (antes: riesgo = entrada) | `core/manager.py:169-181` | ✅ |

## Archivos nuevos (Fase 0, autorizados)
- `daily_pilot/knowledge/verify_integrity.py` — read-only, **falla** si el hash no cierra.
- `daily_pilot/tests/run_all.py` — suite hermética con verificación de hashes de E1 antes/después.
- `daily_pilot/scripts/reconciliar_linaje.py` — read-only.
- `daily_pilot/scripts/reclasificar_claims.py` — aplica el clasificador nuevo a los claims existentes.

## Verificación
| Comprobación | Resultado |
|---|---|
| `run_all.py` | **5/5 suites OK · FUENTES INTACTAS** |
| Tests | 18 core · 10 métricas · 19 RM · 8 dashboard · 14 C2C3E6 = **69** |
| `verify_integrity.py` | **OK** — `store.db` `e23b2241…` = `hashes_store.post` = `.control.json` |
| `store.db` | integrity `ok` · 21 vídeos · 17.462 cues · 3.802 claims |
| Dashboard | 57.024 B · `file://` limpio (0 fetch / 0 http) |
| Skill protegida | `locked`+`pinned` · hash IGUAL |

## Hallazgos nuevos (no estaban en la auditoría)
1. **Video nuevo en el canal**: `cH2KY5vnsVQ` → estado `ANALISIS PENDIENTE` (transcrito, sin análisis). Sin procesar.
2. **El nocturno tiene 21 vídeos** (el informe decía 20) y **ninguno** tiene transcripción en `data_hist/` (solapamiento 0).
3. **XAUUSD 1890 era contaminación real**, no un caso hipotético: el número va antes de la mención al oro. 2077/2132 sí son legítimos («igual que en el oro»).

## Pendiente / decisiones
1. **¿Analizar `cH2KY5vnsVQ`?** (está transcrito; falta `analisis/cH2KY5vnsVQ_analisis.json`).
2. **Importar el nocturno a E1**: ahora sí se puede (con `verify_integrity` operativo), pero es un paso aparte: 21 vídeos + ~15.000 cues + VTT.
3. `i0qXzL0eSYs` tiene `published=NULL` en DB (el registro sí lo tiene).
4. 5 vídeos en DB no están en `registro.json`.
