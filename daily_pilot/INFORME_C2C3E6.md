# INFORME — C2 (relaciones) · C3/E5 (escenarios versionados) · E6 (temporalidad) · seguimiento

Fecha: 2026-11-18 · Autorización: «hace todo eso!» · `PAPER_ONLY=true` en todo.

## E6 — Temporalidad (base)
- `daily_pilot/scripts/anadir_temporalidad.py`: columna `temporalidad` en `claims` (ALTER TABLE idempotente).
- 3.802 claims clasificados: **semanal 120 · diario 45 · 4h 51 · intradía 24 · neutro 3.562**.
- Método: declaración explícita en el texto. Backup `store.db.bak-pree6-*`.

## C2 — Relación entre vídeos
`daily_pilot/relaciones/relaciones.py` → `relaciones/relaciones.json`.
- **4 niveles repetidos** plausibles:
  - BTCUSD ~69.997 en 3 vídeos · BTCUSD ~69.000 en 3 vídeos
  - XAUUSD ~3.906 en 2 vídeos · BTCUSD ~78.746 en 2 vídeos
- **0 contradicciones** (ningún nivel compartido con sentidos opuestos).
- **25 niveles descartados** por filtro de plausibilidad (años, percentiles, rangos imposibles).
- **Bug corregido**: el agrupamiento original usaba una constante (`int(v/(v*tol))` = 200 para todo) → ahora banda logarítmica `round(log(v)/log(1+tol))`.
- Línea de tiempo: 16 vídeos con niveles fechados.

## C3 / E5 — Escenarios versionados
`daily_pilot/escenarios/construir_escenarios.py` → `historial.json` + `vigentes.json`.
- **34 versiones** en 3 instrumentos (XAUUSD, BTCUSD, ETHUSD).
- **17 escenarios vigentes** (última versión por banda de nivel), cada uno con fecha, vídeo, sentido y procedencia A.
- Historial **no destructivo**: no se borra ninguna versión.

## Seguimiento (E7 parte 2)
- `daily_pilot/seguimiento/seguimiento.py` + `estados.jsonl`.
- 7 estados canónicos (`EN_OBSERVACION` … `EXPIRADO`).
- **No automático**: hoy `SIN REGISTROS`. Los resultados reales requieren confirmación.

## Dashboard
Tarjetas nuevas (56.798 bytes): `Niveles repetidos` · `Escenarios vigentes` · `Temporalidad` · `Seguimiento` + las anteriores.
`file://`: **0 `fetch()`**, **0 refs http**.

## Verificación
| Comprobación | Resultado |
|---|---|
| Tests | **69/69** (RM 19 · métricas 10 · dashboard 8 · core 18 · C2C3E6 14) |
| `store.db` | integrity `ok` · 21 vídeos · 17.462 cues · 3.802 claims |
| Backups E1 | `preB1`, `preclaims`, `pree6` |
| Skill protegida | `locked`+`pinned` · hash IGUAL |
| Git | HEAD `7c7eb04` · 0 preexistentes modificados |
| `PAPER_ONLY` | `true` |

## Limitaciones declaradas
- Procedencia **solo A** (B requiere visión, bloqueada; C y D no se infieren).
- Temporalidad `neutro` = no declarada (93,7% de los claims).
- Los niveles repetidos son **coincidencias de texto**, no confirmaciones de gráfico.
- Métricas siguen en `NO DISPONIBLE` hasta haber resultados reales.
