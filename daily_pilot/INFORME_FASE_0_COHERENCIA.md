# INFORME — FASE 0 de COHERENCIA

Fecha: 2026-11-18 · Autorización: «hace todo en el orden que prefieras» · `PAPER_ONLY=true`

Origen: segunda auditoría DeepSeek (verificada por Hermes: **5/5 aciertos**).

## 1. Backfill de metadata
`cH2KY5vnsVQ` y `i0qXzL0eSYs` tenían `title/published = NULL` en DB y vacíos en `registro.json`.
- Se completó desde el **RSS** (fuente primaria).
- `cH2KY5vnsVQ` = «Bitcoin frenado antes de las actas de la FED: lo que vigilo hoy» · 2026-11-18T09:43:08Z.

## 2. Contrato del detalle (nuevo)
`daily_pilot/docs/contrato_detalle.md` + implementación en `generar_dashboard.py`.
- El detalle (mercado/escenarios) puede leerse **por separado** del estado.
- `dashboard_data.json` queda como **fallback con banner rojo visible**:
  `DETALLE DE OTRO VIDEO · s_GjovZxQqY · 2026-11-16`.
- `ultimo_analizado` = campo canónico único = `ultimo_analisis_completo`.

## 3. R:R y capital (2 bugs reales)
- **Bug de contrato**: `Manager.evaluar` recibía el wrapper `{'escenario': {...}}` pero `clasificar_escenario` esperaba el dict interno → **todos los escenarios caían en `INDETERMINADO`**. Corregido.
- **R:R**: ahora se calcula si hay entrada + stop (del Analyst o **propuesto**).
- Resultado: `rb` **3/8** (los que tienen entrada; `ZONA_DE_INTERES`/`NIVEL_REFERENCIADO` correctamente sin R:R).
- `risk_manager`: `exposicion_total` renombrado a **`perdida_potencial_total`** (alias conservado).

## 4. Integridad — orden canónico
El hash se rompió de nuevo por el mismo ciclo P0-3 (escribir `meta` después de medir).
- Nuevo `knowledge/sellado_integridad.py`: `sha(store)` → manifiesto → `.control.json`. **El store no se escribe.**
- `verify_integrity.py` ahora comprueba `.control.json` (canónico) y trata `meta` como legado.
- Resultado: **OK** — 42 vídeos · 34.061 cues · 6.831 claims.

## 5. Niveles sin instrumento — reportados, no asignados a ciegas
Un intento de fallback por título infló 60 → 1.947 versiones (asignaba 28.026 a BTC). **Revertido**.
Ahora la tarjeta muestra: **4.012 niveles SIN instrumento (no se asignan a ciegas)**, desglosados por video (`cH2KY5vnsVQ: 78`).
Cumple el criterio de DeepSeek: *«cH2K en vigentes o motivo explícito»*.

## 6. Verificación
| Comprobación | Resultado |
|---|---|
| `run_all.py` | **5/5 suites OK · FUENTES INTACTAS** |
| `verify_integrity.py` | **OK** |
| Dashboard | 63.034 B · `file://` limpio · badge `VIDEO NUEVO ANALIZADO` |
| `detalle.banner` | visible |
| R:R | 3/8 con stop propuesto |

## 7. Pendiente
1. **116 `metadata_conflicts`** en la migración → elegir regla de prioridad de fechas.
2. **Fase 1 — playbook del método** (machine-readable) + validador.
3. `dashboard_data.json` sigue siendo del 16/11: decidir si se regenera desde el último análisis.
4. 4.012 niveles sin instrumento: el siguiente salto de calidad es **datasheet de precio** (Fase 2), no más heurística de texto.
