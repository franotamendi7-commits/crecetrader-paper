# SNAPSHOT PARA AUDITORÍA — 2026-11-18T12:26:08Z

> Para el auditor externo. **Read-only.** Si un hash cambia mientras auditás, pará y avisá.
> mtimes en **UTC real**.

## Hashes y mtime

| Archivo | sha256 (16) | mtime UTC |
|---|---|---|
| `daily_pilot/knowledge/store.db` | `6826b7e148fe13da` | 2026-11-18T11:52:36Z |
| `daily_pilot/dashboard/index.html` | `1f8a1ae1558920dc` | 2026-11-18T12:25:30Z |
| `daily_pilot/estado/estado_hoy.json` | `70da7e72874a48fd` | 2026-11-18T12:19:57Z |
| `daily_pilot/registro/registro.json` | `9288bc5dd3af6f3b` | 2026-11-18T11:50:07Z |
| `daily_pilot/datos/dashboard_data.json` | `d92faf246999b876` | 2026-11-16T20:40:34Z |
| `daily_pilot/relaciones/relaciones.json` | `63bb3a5f081c4ab0` | 2026-11-18T12:25:30Z |
| `daily_pilot/escenarios/historial.json` | `52d9965f612c0dfa` | 2026-11-18T12:25:30Z |
| `daily_pilot/escenarios/vigentes.json` | `18827526935713ee` | 2026-11-18T12:25:30Z |

**Git**: `main` @ `7c7eb0455799` · untracked 76 · **preexistentes modificados: 0**
(`dashboard_data.json` **intacto**: `d92faf24…` — no se tocó.)

## Verificación (en verde)

| Comando | Resultado |
|---|---|
| `python3 -B daily_pilot/knowledge/verify_integrity.py` | `OK` · 42/34.061/6.831 |
| `python3 -B daily_pilot/tests/run_all.py` | `3 OK · 0 FALLO · FUENTES INTACTAS` |
| `python3 -B daily_pilot/tests/run_all.py --integracion` | `5 OK · 0 FALLO · FUENTES INTACTAS` |
| `python3 -B daily_pilot/scripts/generar_dashboard.py --no-rss --check` | deriva sin escribir (HTML intacto) |

## Resueltos en esta tanda

- **H-01 / H-05** — el **detalle ya sale del último análisis** (`tipo: analisis`, `cH2KY5vnsVQ`). El dashboard ya **no** dice «DETALLE DE OTRO VIDEO».
- **H-02** — sizing capeado por `exposicion_maxima` (**notional**): $20.000 → **$500**.
- **H-03** — runner separado (`--readonly` default / `--integracion`) + `generar_dashboard.py --check`.
- **H-04** — `macro`/`escenarios` heredados → `NO DETERMINADO` con motivo.
- **H-06** — mtimes en UTC real.
- **H-07** — «no tocado (hash igual al pre)».
- **116 `metadata_conflicts`** — ya estaban resueltos (0 pendientes).

## Nuevos artefactos

- `daily_pilot/metodo/playbook_v0.1.md` — borrador C01–C12 (DeepSeek), ejemplos verificados. **Pendiente de validación de Francisco.**
- `daily_pilot/docs/contrato_detalle.md` — contrato del detalle.

## Pendiente por decisión de Francisco

- **Playbook C01–C12**: marcar de acuerdo / no / matiz.
- **4.012 niveles sin instrumento** — el siguiente salto es la **capa de precio** (Fase 2).
- `dashboard_data.json` (16/11) ya **no alimenta el detalle**; queda como histórico/fallback.

## Lo que no se auditó

Repo padre completo, los 42 transcripts, visión/benchmark, licencias.
