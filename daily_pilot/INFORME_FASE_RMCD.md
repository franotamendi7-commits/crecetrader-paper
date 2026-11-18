# INFORME — FASE R (Risk Manager) + M (Métricas) + C (Claims) + D (Dashboard)

Fecha: 2026-11-18 · Autorización: «arranca con todo!» · `PAPER_ONLY=true` en todo lo ejecutado.

## FASE R — Risk Manager

**R1 — Auditoría** de `daily_pilot/risk_manager/risk_manager.py` (186 líneas) + `test_risk_manager.py` + `INTERFACE.md`.
Hallazgos:
- **BUG real**: `invalidation: 0` se aceptaba como válido. El piloto real lo tenía (`S2-BTC-56750`).
- **Filtro demasiado estrecho**: solo evaluaba `SENAL_EXPLICITA` → **5 de 6** señales reales caían en `NO_EVALUABLE` (el RM no hacía nada útil).
- Contrato del clasificador (6 tipos) vs skill (9 tipos del modelo de planes): **inconsistencia documentada**, no resuelta.

**R2 — Correcciones** (`risk_manager.py`):
- Rechazo de `invalidation <= 0`, `entry <= 0` y objetivos `<= 0`/no numéricos.
- `tipos_evaluables` configurable: `ZONA_DE_INTERES`, `ESCENARIO_CONDICIONAL`, `SENAL_EXPLICITA`.
- **4 niveles** en la salida: `nivel_informativo` · `escenario` · `candidata` · `no_operable`.
- Resumen `por_nivel`.
- **19/19 tests** (5 nuevos).

**R3 — Conexión al Dashboard**: tarjeta «Risk Manager · PAPER ONLY» con decisión, exposición, por_nivel y detalle por señal (R múltiplos, razones).
**R4 — Pruebas**: `daily_pilot/tests/test_dashboard_risk.py` **8/8** + verificación en navegador.

Resultado real: `RECHAZAR` · exposición `$500` · por_nivel `{escenario: 4, candidata: 1, no_operable: 1}`.
- `S2-BTC-56750` → RECHAZAR (invalidación 0) — bug real detectado.
- `S5-XAU` → REVISION MANUAL (confianza 0.4).
- `S6` → REVISION MANUAL (exceso por instrumento BTCUSD).

## FASE M — Métricas

`daily_pilot/metrics/metrics.py` (PAPER_ONLY): registro de señales/resultados (JSONL), tasa de acierto, R medio, expectativa, drawdown.
- `registrar_desde_rm.py`: derivó **6 señales** reales (idempotente).
- Sin resultados reales → **NO DISPONIBLE, no se inventa**. Solo expectativa **teórica** 3,0117 con advertencia.
- `daily_pilot/tests/test_metrics.py` **10/10**.
- Tarjeta «Métricas del piloto · sin backtest» en el Dashboard.

## FASE C — Claims (E2)

- Tabla `claims` añadida al Knowledge Store (DDL idempotente + índices).
- `daily_pilot/scripts/extraer_claims.py`: **3.802 claims** en **21 vídeos**, procedencia **A** (dicho), idempotente por `claim_hash`.
- Tipos: `ESCENARIO_CONDICIONAL` 1.972 · `NIVEL_MENCIONADO` 1.428 · `ZONA_DE_INTERES` 157 · `NO_DETERMINABLE` 136 · `SENAL_EXPLICITA` 101 · `SIN_OPERACION` 8.
- **E1 se amplió**: 20 → 21 vídeos (`i0qXzL0eSYs` + sus 184 claims). **Backup**: `store.db.bak-preclaims-20261118T005330Z`. `cues` intactos (17.462).
- Tarjeta «Claims extraídos» en el Dashboard.

## FASE D — Dashboard

`daily_pilot/scripts/generar_dashboard.py` regenera `index.html` (47.804 bytes) con tarjetas nuevas:
`Estado` · `Escenarios comparados (37/50/13)` · `Risk Manager` · `Métricas` · `Claims` + las 5 secciones.
- `file://` limpio: **0 `fetch()`**, **0 refs http**.
- `PAPER_ONLY=true` visible.

## Verificación global

| Comprobación | Resultado |
|---|---|
| Tests | **55/55** (RM 19 · métricas 10 · dashboard 8 · core 18) |
| `store.db` | integrity `ok` · 21 vídeos · 17.462 cues · 3.802 claims |
| Skill `youtube-trading-agent` | `locked: true` · `pinned: true` · 6 hashes IGUAL |
| Scheduler/LaunchAgents | cron `0 */4` + `youtube-daily-check` + `youtube-2h-check` activos |
| Git | HEAD `7c7eb04` · **0 preexistentes modificados** |
| `file://` | 0 recursos externos |
| `PAPER_ONLY` | `true` en RM, métricas, dashboard |

## Pendiente / bloqueado

- **E3 Visión verificada**: sin motor autorizado (Kaggle sin GPU, Mac prohibido, servicios externos sin autorización).
- **Resultados reales** para métricas: requiere seguimiento temporal de las señales (se registran con fecha).
- **B4/B5**: requieren 2 anotadores humanos.
- **Procedencias B/C/D** de claims: el extractor solo emite A (no infiere).
