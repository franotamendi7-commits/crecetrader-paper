# Auditoría — 5 herramientas nuevas del piloto CreceTrader

Ancla: `df2e6e3` (rama `crecetrader-limpio`). Fecha: 2026-11-23.

## Objetivo

Auditar **código nuevo** (no el pipeline de videos). Solo lectura. No regenerar
dashboard ni store. Reportar hallazgos con severidad P0/P1/P2 y evidencia.

## Archivos nuevos

| archivo | qué hace |
|---|---|
| `daily_pilot/scripts/agente_ticket.py` | análisis de un par/TF en formato del método |
| `daily_pilot/scripts/alertas_niveles.py` | niveles cercanos al precio |
| `daily_pilot/scripts/backtest_niveles.py` | toques y rebotes por nivel |
| `daily_pilot/scripts/canal_acierta.py` | predicciones del canal vs lo que pasó |
| `daily_pilot/scripts/paper_trading.py` | registro de operaciones simuladas |
| `daily_pilot/tests/test_herramientas.py` | 11 tests |

También cambió `daily_pilot/scripts/generar_dashboard_v5.py` (sacó el SVG de
velas, agregó los paneles ALERTAS y BACKTEST).

## Contexto obligatorio

- `daily_pilot/metodo/playbook_v0.1.md` (C01–C12)
- `daily_pilot/metodo/FIRMA_C01_C12.md`
- `daily_pilot/core/` — `tramos.py`, `zonas.py`, `jerarquia.py`, `velas.py`

## Qué revisar

### 1 · Fidelidad al método
- ¿El ticket respeta C01 (W>D>4H), C07 (régimen), C10 (confianza)?
- ¿Los retrocesos son 0,382 / 0,5 / 0,61 / 0,786 y las extensiones 1 / 1,25 /
  1,5 / 1,75 / 2 / 3?
- ¿La jerarquía W > D > 4H se aplica o solo se reporta?

### 2 · Corrección numérica del backtest
- La "tasa de rebote" define rebote como: la vela entra en el nivel y la
  siguiente cierra del lado opuesto. ¿Es una medida razonable? ¿Qué sesgo tiene?
- Con `detalle=90` velas, ¿el tamaño de muestra sirve? Marcar si algún número no
  es estadísticamente usable.

### 3 · Alertas
- `concordancia()` asume BTC cuando el nivel no tiene par. ¿Es aceptable?
- Umbral 1,5% fijo: ¿tiene sentido para distintos tamaños de precio?

### 4 · `canal_acierta.py`
- Usa `st_mtime` del archivo como fecha de publicación (no hay fecha real).
  ¿Qué tan grave es? ¿Qué alternativa proponés?
- Los videos se procesaron todos el mismo día → no hay histórico. Confirmar.

### 5 · Paper trading
- Resultado en USD = `res%/100 * 1000 * (riesgo_pct/2)`. ¿Es coherente con el
  riesgo del método (long 5%, corrección 1–2%)?
- ¿Falta registrar la comisión o el deslizamiento? Marcar como hallazgo.

### 6 · Riesgo y aislamiento
- ¿Alguna de las 5 puede escribir el store vivo o tocar archivos fuera de
  `daily_pilot/datos`?
- ¿PAPER_ONLY está respetado?

### 7 · Dash
- ¿Quedó «info justa» (sin las barras) o sobra/falta algo?
- Verificar que el dashboard sea autocontenido (sin llamadas externas).

## Entregable

Informe en markdown con:
1. Veredicto
2. Hallazgos P0 / P1 / P2 (archivo:línea + evidencia)
3. Números concretos que no sirven (muestras chicas, tasas sin significancia)
4. Qué corregir antes de seguir

No corrijas nada: solo informa.
