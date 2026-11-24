# PROTOCOLO DE VALIDACIÓN — CreceTrader (PAPER_ONLY)

**Ancla:** `76ba3cd` · **Fecha:** 2026-11-24 · **Modo:** PAPER_ONLY.
No toca `daily_pilot/metodo/` ni la FIRMA. No escribe el store vivo (`paper_trades.json`).

## Por qué este protocolo

La estrategia "a favor del tramo" mostraba +0,499R, pero tenía dos bugs:
1. F1 con look-ahead (filtraba con el cierre pero entraba al nivel).
2. Drawdown calculado agrupado por nivel, no por fecha.

Corregidos, la esperanza da **-0,204R** (8/21 pares positivos). **La ventaja era del bug.**

Este protocolo existe para que eso no vuelva a pasar: ningún número se considera
real hasta pasar los 5 filtros de abajo, en este orden, sin saltear.

---

## 1 · NULL SINTÉTICO

**Pregunta que responde:** ¿el edge es real o es la geometría del método
(target = siguiente nivel de Fibonacci) más la tendencia del período?

### 1.1 Cómo armar 1.000 random walks sobre los mismos datos

1. Tomar la serie real del par (velas 1d, historia completa, no 500).
2. Calcular los retornos diarios `r_t = close_t / close_{t-1} - 1`.
3. Calibrar la volatilidad y la autocorrelación **por block bootstrap de retornos**
   (Politis-Romano): resamplear bloques contiguos de retornos (longitud
   `bloque ≈ n^(1/3)`, típicamente 5–8 días) con reemplazo, hasta completar `n`
   retornos. Esto preserva la autocorrelación y los clusters de volatilidad que
   un random walk i.i.d. destruiría.
4. Reconstruir precios a partir del primer cierre real y los retornos sintéticos.
5. Generar velas OHLC sintéticas: `open = cierre anterior`, `high/low` con un
   rango intrabar mínimo (≈3 bp) para que los toques de nivel existan.
6. Correr **la misma regla** (mismo código, mismos parámetros) sobre cada serie.
7. Repetir **1.000 veces** (semilla fija para reproducibilidad).

No se cambia nada del método: solo se cambian los precios de entrada.

### 1.2 Umbral de decisión

- Calcular la esperanza R de cada una de las 1.000 series sintéticas → distribución nula.
- Tomar el **percentil 95** de esa distribución.
- **Regla:** la esperanza real debe superar el percentil 95 del null
  (p-valor empírico < 0,05, one-sided).
- Si la esperanza real cae dentro del 90% central del null → **es ruido**,
  por más que el número sea positivo. No hay edge que medir todavía.

**Reportar también:** media, sd, p05, p50, p95, p99 del null, y el p-valor empírico.

---

## 2 · WALK-FORWARD REAL

### 2.1 Tipo y ventanas

- **Tipo:** **rolling** (ventana fija), no anchored. Anchored arrastra regímenes
  viejos y hace que el OOS temprano pese distinto que el tardío.
- **Calibración (train):** **3 años** (o 40% de la historia, lo que sea mayor).
  Suficiente para ver un bull y un bear; más corto no contiene régimen.
- **Test (OOS):** **6 meses** inmediatamente después, sin solape.
- **Paso:** **6 meses** (o `ventana/6`). Paso = ventana genera 1 fold: inútil.
- **Objetivo:** ≥ 6 folds con 4+ años de historia (BTC tiene 9).

### 2.2 Purga (embargo) entre train y test

- **Purga:** `H + 1` velas entre el fin del train y el inicio del test, donde `H`
  es el holding máximo de la estrategia (en 1d, si un trade puede durar 30 días,
  purgar 31 velas). Evita que un trade abierto en train se resuelva en test.
- **Embargo:** **1% del sample** removido del final del train y del inicio del test
  (López de Prado, *AFML*, cap. 7). Evita fuga por autocorrelación.
- **Gap total:** `purga + embargo`. Train y test nunca se tocan.

### 2.3 Repeticiones necesarias

- Mínimo **6 folds** para poder decir "hay algo".
- Reportar **por fold**, no solo el agregado: 6 folds con 4 positivos y 2 negativos
  es información; un promedio lo esconde.
- **Umbral:** `WFE = expectancy_OOS / expectancy_IS ≥ 0,5` y **≥ 60% de folds OOS
  positivos** (y al menos 3 de 4). Con menos, el "edge" es del período de calibración.

### 2.4 Nested (si se optimiza algo)

WF externo para evaluar, WF interno para elegir parámetros. Evita que la selección
vea el test.

---

## 3 · SIGNIFICANCIA

### 3.1 Deflated Sharpe (o PBO simple), declarando N de intentos

- Contar y **escribir** todos los intentos: variantes de filtros (F1/F2/F3),
  stops (pct/estructural/atr), `detalle`, gestión (P1/P2/P3), 33 pares. Son
  **cientos de configuraciones**. El máximo Sharpe esperado por azar crece con
  `√(2·ln N)`.
- **Deflated Sharpe Ratio** (Bailey & López de Prado 2014): corrige el "mejor de N".
  Umbral: **DSR > 0** con N declarado. Si no se puede contar N, no se puede creer
  el Sharpe.
- Alternativa/complemento: **PBO** (Probability of Backtest Overfitting).
  Umbral: **PBO ≤ 0,20**. Por encima de 0,2, es ruido.

### 3.2 Costos incluidos antes de medir

Ninguna métrica se reporta sin costos. Antes de medir:

- Fee **0,10% por lado** (ida y vuelta 0,20%).
- Slippage **0,05%** (o 1 tick, lo que sea mayor).
- Gap de apertura: si la vela abre más allá del nivel, la entrada es al **open**,
  no al nivel.
- Convertir a R con `costos_R(entry, risk)` (incluida en el código).
- **Robustez:** la expectancy debe seguir ≥ 0,15R con costos ×2 y entrada 1 barra
  tarde. Si no sobrevive, no es edge.

### 3.3 Métricas y umbrales (resumen)

| Métrica | Umbral mínimo |
|---|---|
| N efectivo (clusters) | ≥ 30 por par · ≥ 100 pooled |
| Expectancy neta (R, con costos) | ≥ +0,15R y IC95 inferior > 0 |
| t clusterizado | ≥ 2,5 |
| Deflated Sharpe | DSR > 0 con N declarado |
| PBO | ≤ 0,20 |
| WFE | ≥ 0,50 |
| Folds OOS positivos | ≥ 60% y ≥ 3 de 4 |
| Max DD (realizado y MC p95) | ≤ 15R · P(DD>20R) ≤ 10% |
| P(ruina) a 0,5%/trade | ≤ 1% |
| Concentración | top-3 trades ≤ 50% del P&L |
| Robustez a parámetros | variación < 30% en grilla ±25% |

**Regla de decisión:** un par se habilita solo si pasa todas las filas de N,
expectancy, t y robustez. La estrategia global se habilita si pasa DSR, PBO y WFE.
No hay "casi pasa".

---

## 4 · ORDEN DE TRABAJO

### 4.1 Secuencia de pares

1. **BTC solo** (9 años de historia diaria; único par con potencia suficiente para
   distinguir señal de ruido). Si la regla no pasa ahí, no pasa en ningún lado.
2. **8 majors como holdout** (ETH, SOL, BNB, XRP, ADA, DOGE, LINK, AVAX;
   ≥ 4 años, alta liquidez). No se tocan hasta la Fase 4.
3. **Los 33** con contracción jerárquica (empirical Bayes) y FDR sobre los
   p-valores. Holdout final: 17 pares nunca vistos + últimos 12–18 meses.

Pares nuevos (ONDO, S, TON, ARB, OP, INJ, STX…) se reportan como **exploratorios**
hasta tener ≥ 3 años. No se les asigna riesgo.

### 4.2 Trades mínimos para que un número sirva

- **Mínimo por par: 30 trades** (por debajo, el IC es más ancho que el efecto).
- **Pooled: ≥ 100 trades**.
- Potencia (σ≈1R, α=0,05 dos colas, potencia 80%): `n ≈ 15,7/δ²`
  | edge a detectar | trades independientes |
  |---|---|
  | 0,50R | 63 |
  | 0,30R | 174 |
  | 0,20R | 393 |
  | 0,10R | 1.570 |
- Con 1d y ~15–20 trades por par por año, **un par solo no alcanza ni para
  detectar 0,3R en 10 años**. De ahí que la única salida honesta sea
  **pooling + shrinkage**, no 33 backtests separados.

### 4.3 Fases (criterio de salida por fase)

- Fase 0: reparar motor (snapshot inmutable, sin look-ahead, DD cronológico,
  costos, universo = 33 de Quantfury).
- Fase 1: línea base honesta en BTC con historia completa.
- Fase 2: null sintético (decide si vale la pena seguir).
- Fase 3: walk-forward rolling formal.
- Fase 4: escalar a 33 con jerarquía + holdout de 17 pares.
- Fase 5: robustez + decisión (DSR, PBO, costos ×2, grilla ±25%).
- Fase 6: forward test real 3–6 meses en PAPER, sin tocar parámetros.

---

## 5 · CÓDIGO

Archivo listo para meter en `daily_pilot/scripts/`:

**`daily_pilot/scripts/validacion_protocolo.py`**

Sin dependencias raras (solo stdlib). Implementa:

- `generar_sintetica(velas, seed, block)` — random walk por block bootstrap.
- `null_sintetico(velas, n_sim=1000, ...)` — 1.000 random walks, compara la
  esperanza real contra el percentil 95 del null, devuelve veredicto.
- `walk_forward(candles, train, test, purge, embargo, mode='rolling'|'anchored', ...)`
  — rolling o anchored, con purga `H+1` y embargo 1%, reporte por fold y WFE global.
- `deflated_sharpe(returns, n_trials)` — DSR simple con N declarado.
- `pbo_simple(perf)` — PBO simple.
- `costos_R(entry, risk, comision_pct, slippage_pct)` — costos en R.

Reusa `backtest_afavor` parcheando en memoria (sin escribir archivos), por lo que
el null y el walk-forward miden **exactamente** la misma regla que el backtest real.

### Uso

```bash
# Null sintetico (1.000 sims) + walk-forward rolling en BTC
python3 daily_pilot/scripts/validacion_protocolo.py BTCUSDT --tf 1d --detalle 150

# Solo null, mas simulaciones
python3 daily_pilot/scripts/validacion_protocolo.py BTCUSDT --tf 1d --null-sim 2000 --skip-wf

# Walk-forward anchored
python3 daily_pilot/scripts/validacion_protocolo.py BTCUSDT --tf 1d --wf-mode anchored
```

### Reglas de uso

- **PAPER_ONLY.** No instala nada, no toca `metodo/` ni la FIRMA, no escribe
  `paper_trades.json` ni ningún store vivo. Solo lee `daily_pilot/datos/velas/*.json`.
- Declarar siempre `--n-trials` con el N real de intentos/configs probados.
- Un par se habilita solo si pasa **todas** las filas de §3.3.
- No hay "casi pasa".
