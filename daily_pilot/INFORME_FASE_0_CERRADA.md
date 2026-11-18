# INFORME — FASE 0 CERRADA (coherencia + fixes de la auditoría DeepSeek)

Fecha: 2026-11-18 · `PAPER_ONLY=true` · Snapshot: **12:26:08Z**

## Veredicto de la auditoría DeepSeek
**7/7 hallazgos ciertos** (H-01…H-07), más un borrador de playbook cuyos ejemplos **verifiqué contra `store.db`** (todos existen).

## Aplicado

| # | Fix | Evidencia |
|---|---|---|
| **H-01/H-05** | El **detalle del dashboard sale del último análisis** (`analisis/<id>_analisis.json`). `dashboard_data.json` deja de alimentar el detalle. | `detalle.tipo = analisis` · `video_id = cH2KY5vnsVQ` · el dashboard ya **no** dice «OTRO VIDEO» |
| **H-02** | `_capital` capea por `exposicion_maxima` (**notional**, definida explícitamente) | notional $20.000 → **$500** en los 3 escenarios |
| **H-03** | Runner separado + `--check` | `run_all.py` (readonly) / `--integracion`; `generar_dashboard.py --no-rss --check` deriva sin escribir |
| **H-04** | `macro`/`escenarios` heredados → `NO DETERMINADO` con motivo | antes contradecían el estado |
| **H-06** | mtimes del snapshot en UTC real | — |
| **H-07** | Runner dice «no tocado (hash igual al pre)» | — |
| — | `116 metadata_conflicts` | ya estaban resueltos (0 pendientes) |

## Verificación
| Comprobación | Resultado |
|---|---|
| `run_all.py` (readonly) | **3 OK · 0 FALLO · FUENTES INTACTAS** |
| `run_all.py --integracion` | **5 OK · 0 FALLO · FUENTES INTACTAS** |
| `verify_integrity.py` | **OK** · 42/34.061/6.831 |
| Dashboard | 48.654 B · `file://` limpio · `VIDEO NUEVO ANALIZADO` |
| `dashboard_data.json` | **intacto** (`d92faf24…`) — no se tocó |

## Entregables
- `daily_pilot/metodo/playbook_v0.1.md` — C01–C12 con ejemplos reales y estados (`propuesto` / `a_validar` / `NO_DETERMINABLE`).
- `daily_pilot/docs/contrato_detalle.md`.
- `daily_pilot/investigacion/SNAPSHOT_AUDITORIA.md` — snapshot 12:26:08Z.
- `daily_pilot/scripts/importar_nocturno.py`, `reclasificar_claims.py`, `reconciliar_linaje.py`.
- `daily_pilot/knowledge/{verify_integrity.py, sellado_integridad.py}`.

## Pendiente (solo decisión de Francisco)
1. **Validar el playbook C01–C12** (de acuerdo / no / matiz).
2. **Fase 2 — capa de precio**: los 4.012 niveles sin instrumento no se resuelven con más heurística de texto; requieren OHLCV.
3. **E3 visión** sigue bloqueada (sin motor autorizado).

## Estado del sistema
- E1: 42 vídeos · 34.061 cues · 6.831 claims · integrity ok.
- Linaje: DB = registro = data_hist = **42**.
- Git: `main @ 7c7eb04` · 0 preexistentes modificados.
- Skill `youtube-trading-agent`: locked + pinned.
