# PLAN — Estrategia BTCUSDT 20x · intradía 4h · validación walk-forward + Monte Carlo

**Fecha:** 2026-11-24 · **PAPER_ONLY** · Par: BTCUSDT · TF: 4h · Apalancamiento: 20x · Exchange: Quantfury (spread 0, comisión 0)

---

## 0 · Modelo de gestión de riesgo (CORREGIDO)

El usuario opera con este modelo, que es el correcto:

```
Capital (margen): $100
Leverage: 20x → Notional máximo: $2.000
Riesgo por trade: 2% del capital = $2 (FIJO, no variable)
Position sizing: position = riesgo / distancia_stop
  → Si entrada=$61, stop=$60, distancia=$1 → position = $2/$1 = 2 unidades
  → Notional = 2 × $61 = $122 (dentro del límite de $2.000)
  → Margen usado = $122/20 = $6,10
Liquidación: solo si hay un gap más allá del stop (precio salta de $61 a <$59,4 sin tocar $60)
  → Con stop en $60, el trade se cierra a $2 de pérdida ANTES de llegar a liquidación
  → Liquidación a ~4,5% adverso, stop a ~1,6% adverso → el stop protege
Costos: Quantfury tiene spread 0 y comisión 0 → backtest SIN costos (más favorable)
```

**Conclusiones clave:**
1. **El riesgo por trade es $2 fijo**, controlado por position sizing, no por leverage.
2. **El 20x NO causa liquidación** si el stop está en su lugar. El stop cierra a $2 de pérdida antes de llegar al umbral de liquidación (~$5,49).
3. **El único riesgo de liquidación es un gap** (vela de 4h que salta de $61 a <$59,4 sin tocar $60). Con 4h candles, esto es posible pero infrecuente.
4. **Sin costos** (Quantfury: spread 0, comisión 0) → el backtest es más favorable que en Binance, pero los resultados no se traducen a otros exchanges.

---

## 1 · Investigación en GitHub — lo que encontré

| Repo | Stars | Edad | Qué hace | Veredicto |
|---|---|---|---|---|
| **LunarLoom4/quant-trading-engine** | 1 | Ago 2026 | 4 estrategias (Breakout Donchian+vol+ATR, Trend ADX+Supertrend, Momentum EMA+RSI, Mean Rev BB+ADX). WF + MC. Reporta 52,3% CAGR, Sharpe 1,42, DD -13%, WR 63% en 2024 OOS. | **Referencia de idea.** Pero 19 trades totales, stress test = 86,5% prob. ruina en crash -20%. No cumple filtro de madurez (≥2 años). No usar como dependencia. |
| **zhangxingthang/BTCUSDT-London-Volatility-Breakout** | 0 | Sep 2026 | Breakout de 1h durante sesión London (08-11h), risk 0,05%, stop 0,5%, close 16:00 London. 5 años. WR 39,35%, PF 1,11, Sharpe 0,62, DD -1,34%. | **Marginal.** PF 1,11 con costos cero (sin fees/slippage/funding). Con costos reales probablemente muere. |
| **loveolu/crypto-strategy-research** | 0 | Sep 2026 | Framework de validación pre-registrada: deflated Sharpe gate, WF, MC, costos medidos, SHA-256 data manifest. "La mayoría de hipótesis rechazadas en el gate." | **Metodología valiosa.** Adoptar el enfoque de pre-registro, no el código. |
| **ojeology/QUANTLAB** | 0 | Ago 2026 | 70+ iteraciones de investigación con WF, bootstrap CI, MC, validación de portfolio. | **Conceptual.** No cumplen filtro de madurez. |
| **nar1-frames/tradingai** | 0 | Ago 2026 | Backtest sin look-ahead, WF, MC, permutation test. "Resultados honestos: las estrategias pierden vs buy-and-hold." | **Honestidad metodológica.** El repo dice lo que otros ocultan. |
| **Milind0214/btc-ema-pullback-signal-dashboard** | 2 | — | Dashboard de señales EMA pullback BTCUSDT con backtest y paper trading. | **Indicador clásico.** No validado con null/MC. |

**Conclusión de la investigación:** No hay ninguna estrategia "demostrada" para BTCUSDT 4h con 20x que pase un filtro serio de validación. Los repos prometedores son de 0-1 estrella, de 2026, sin mantenimiento, sin tests, sin costos reales. **No hay Holy Grail.**

---

## 2 · Lo que SÍ tienes (tu proyecto)

### Estrategia "A favor del tramo" — la única con edge medible

```
1. Tramo del ciclo (C05): máximo más alto → piso posterior, por TF
2. Niveles: retrocesos 0,382 / 0,5 / 0,61 / 0,786 + extensiones 1..3
3. Lado: A FAVOR del tramo (bajista → SHORT, alcista → LONG)
4. Entrada (F1): la vela que toca el nivel debe CERRAR a favor
5. Stop: 2% del nivel (o nivel estructural)
6. Target: el siguiente nivel del método en esa dirección
```

**Resultados (con problemas metodológicos):**
- +0,499R en 337 ops (solo Quantfury, 21 pares)
- 13/21 pares positivos (62%)
- BTC: +1,718R en 10 ops, acierto 30%
- Peor DD: -32R (TON), BTC -10R → -4,5R con gestor de racha

**Problemas que la auditoría detectó (D1-D10):**
- D1: Look-ahead en F1 (se filtra con close, se entra al nivel)
- D2: DD no cronológico (agrupado por nivel, no por fecha)
- D3: Gestor de racha sobre secuencia falsa
- D4: Sin costos (fees, slippage, funding, gaps) — pero en Quantfury los costos son 0, así que esto es menos crítico
- D5: No resueltas = -1R (mezcla stop con abierta)
- D6: Un solo tramo para 150 velas (apuesta direccional, no estrategia)
- D7: Ops correlacionadas contadas como independientes
- D8: Datos no reproducibles (cache 5 min, sobrescribe)
- D9: min_muestra=5 (pares con n=2-3 entran al conteo)
- D10: Universo declarado ≠ universo corrido (BNB/ALGO/EGLD/FTM que no están en Quantfury)

---

## 3 · Plan concreto para validar BTCUSDT 4h 20x

### Fase 0 — Reparar el motor (1-2 días) [OBLIGATORIO antes de todo]

Sin esto, todo lo demás mide ruido. Los defectos D1-D10 invalidan los números actuales.

| # | Tarea | Archivo | Criterio de salida |
|---|---|---|---|
| 1 | Paginar Binance para BTCUSDT 4h (≥2 años, no limite=500). Guardar snapshot parquet + sha256 | `core/velas.py` | BTC 4h: ≥4.000 velas (≥2 años) |
| 2 | Eliminar look-ahead F1: entrar al cierre de la vela de confirmación | `backtest_afavor.py:165-173` | Reportar con y sin F1 |
| 3 | Ordenar trades por timestamp de entrada antes de DD y gestión de racha | `backtest_afavor.py:208-216` | DD monótono en el tiempo |
| 4 | Time-stop explícito a H velas + MtM al cierre (no -1R por defecto) | `backtest_afavor.py:182-194` | Reportar % de ambiguas |
| 5 | Costos: 0 en Quantfury (spread 0, comisión 0). Reportar también con costos de Binance (0,10%/lado) para robustez | `backtest_afavor.py:108-115` | Expectancy neta en ambos escenarios |
| 6 | Unificar universo = 33 de Quantfury, SUIUSDT no 'SUI' | `validar_33.py:20-25` | Universo declarado = corrido |
| 7 | Test de regresión: mismo snapshot → mismo resultado bit a bit | `tests/` | Reproducible |

### Fase 1 — Línea base honesta en BTC 4h (1 día)

Correr "A favor del tramo" en BTCUSDT 4h con historia completa (≥2 años), sin filtros, sin costos (Quantfury).

```
python3 daily_pilot/scripts/backtest_afavor.py BTCUSDT --tf 4h --detalle 500 --filtros "" --stop pct --stop-pct 2.0
```

**Expectativa: el +1,718R se va a derrumbar.** Ese es el resultado, no un fracaso.
Reportar por año y por régimen (bull/bear/rango).

### Fase 2 — Null sintético (2 días) [EL TEST QUE DECIDE TODO]

1.000 random walks con vol y autocorrelación de BTC 4h. Correr la misma regla.
Si la esperanza real cae dentro del 90% central del null → **no hay edge**. Lo que se midió es la geometría "target = siguiente nivel" + tendencia del período.

```
python3 daily_pilot/scripts/banco_candidatos.py BTCUSDT --tf 4h
```

### Fase 3 — Walk-forward rolling formal (2 días)

- Ventana de calibración: 3 años (o 40% de historia, lo que sea mayor)
- Paso: 6 meses
- Test: 6 meses inmediatamente después, sin solape
- Purga: H+1 velas entre train y test (H = holding máximo en velas)
- Embargo: 1% del sample
- ≥ 4-6 folds
- Reportar por fold, no solo agregado

**Umbrales:**
- WFE = expectancy_OOS / expectancy_IS ≥ 0,5
- ≥ 60% de folds OOS positivos
- ≥ 3 de 4 folds positivos

### Fase 4 — Monte Carlo sobre equity (1 día)

- Block-bootstrap de retornos por trade (preserva autocorrelación)
- 2.000-5.000 rutas
- Reportar: distribución de max DD, P(ruina), VaR/CVaR de equity
- Umbrales: mediana max DD < 20%, p95 max DD < 30%, P(ruina) < 5%
- **Importante:** simular también el riesgo de gap (vela de 4h que salta el stop)

### Fase 5 — Robustez (1 día)

- Costos de Binance (0,10%/lado) como stress test (aunque operes en Quantfury)
- Entrada 1 barra tarde (simula fill real)
- Grilla ±25% en cada parámetro (stop 1,5-2,5%, detalle 375-625)
- La expectancy debe seguir > 0,15R con costos de Binance y entrada +1 barra

### Fase 6 — Forward test real (3-6 meses)

PAPER_ONLY con config congelada, sin tocar parámetros. Si en 6 meses el forward se desvía > 1 sd del backtest, se para.

---

## 4 · Estrategia candidata para 4h BTCUSDT 20x

### Candidata principal: "A favor del tramo" adaptada a 4h

**Por qué esta y no otra:**
- Es la única con edge medible en tu proyecto (+0,499R, 13/21 pares)
- La lógica (niveles de retroceso Fibonacci) es independiente del timeframe
- Tiene una razón estructural: el retroceso dentro de una tendencia es una corrección, no un cambio
- Ya pasó el null sintético en 1d (aunque con problemas metodológicos)

**Adaptaciones para 4h:**
- Tramo: usar 4h para detectar el tramo (más rápido que 1d)
- Niveles: mismos retrocesos (0,382/0,5/0,61/0,786)
- Stop: 2% del nivel (igual, pero en 4h el ATR es menor, así que 2% es más holgado)
- Target: siguiente nivel (igual)
- Filtro F1: entrada al cierre de confirmación (sin look-ahead)
- F3: primer toque (evita re-entradas)
- **Holding máximo: 2-3 días (12-18 velas de 4h).** Si no toca target ni stop en ese tiempo, cerrar al mercado (time-stop)

**Position sizing (tu modelo):**
```
riesgo = $2 (2% de $100)
distancia_stop = |entrada - stop| en dólares
position_size = riesgo / distancia_stop
notional = position_size × entrada
margen_usado = notional / 20
```

**Ejemplo:**
- Entrada: $61.000, Stop: $60.000, distancia = $1.000
- position_size = $2 / $1.000 = 0,002 BTC
- notional = 0,002 × $61.000 = $122
- margen = $122 / 20 = $6,10
- Si el stop se toca: pérdida = 0,002 × $1.000 = $2 ✓

**Riesgo de gap:**
- Con 4h candles, si el precio salta de $61.000 a $59.000 sin tocar $60.000, el stop no se ejecuta a $60.000
- Pérdida real = 0,002 × $2.000 = $4 (en vez de $2)
- Con 20x, si el gap es de 5% ($3.050), la pérdida = 0,002 × $3.050 = $6,10 = 100% del margen → liquidación
- **Mitigación:** usar stop market (no limit) y aceptar slippage en gaps. Reportar % de gaps en el backtest.

### Candidata alternativa: London Volatility Breakout (intradía)

Si el usuario insiste en intradía (horas, no días), la estrategia de London Volatility Breakout es la más cercana:
- Breakout de 1h durante sesión London (08-11h)
- Risk 0,05%, stop 0,5%, close 16:00 London
- Pero PF 1,11 con costos cero → con costos reales probablemente muere
- Y con 20x, un stop de 0,5% = $10 de pérdida (5% del margen) por trade → 20 trades seguidos = liquidación

---

## 5 · Métricas y umbrales de decisión (de la auditoría)

| Métrica | Umbral mínimo | Por qué |
|---|---|---|
| N efectivo (clusters) | ≥ 30 por par · ≥ 100 pooled | Por debajo, el IC es más ancho que el efecto |
| Expectancy neta (R, con costos) | ≥ +0,15R y IC95% inferior > 0 | Piso para sobrevivir a un DD normal |
| t clusterizado | ≥ 2,5 | Harvey & Liu: t=2 es demasiado flojo |
| Deflated Sharpe (DSR) | > 0 con N de intentos declarado | Corrige el "mejor de N" |
| PBO | ≤ 0,20 | P(que la mejor config IS sea peor que la mediana OOS) |
| WFE | ≥ 0,50 | Si OOS rinde la mitad o menos, no hay estabilidad |
| Folds OOS positivos | ≥ 60% y ≥ 3 de 4 | Un fold bueno no es una estrategia |
| Max DD (realizado y MC p95) | ≤ 15R · P(DD>20R) ≤ 10% | Es el problema declarado |
| P(ruina) a 0,5%/trade | ≤ 1% | PAPER_ONLY, pero el sizing se diseña igual |
| Concentración | top-3 trades ≤ 50% del P&L | Si 3 trades hacen todo, es un lotto |
| Robustez a costos | expectancy ≥ 0,7× con costos de Binance y entrada +1 barra | El fill optimista y el look-ahead mueren acá |
| Robustez a parámetros | variación < 30% en grilla ±25% | Un pico aislado es sobreajuste; una meseta es señal |
| % de gaps | Reportar en el backtest | Con 4h candles, los gaps son el principal riesgo de liquidación |

**Regla de decisión:** un par se habilita solo si pasa TODAS las filas. La estrategia global se habilita si pasa DSR, PBO y WFE. **No hay "casi pasa".**

---

## 6 · Recomendación final

### Lo que NO conviene (y por qué)

| No hacer | Por qué |
|---|---|
| **Buscar "la estrategia que ya tiene un trader demostrada"** | No existe. Si existiera, no estaría publicada. Los repos de GitHub con resultados prometedores son de 0-1 estrella, sin costos reales, sin walk-forward honesto. |
| **Usar los candidatos simples (MA, RSI, Donchian, momentum)** | 0/20 pasan el null sintético en ningún TF. No hay edge. |
| **Bajar a 4h para "tener más muestras" sin corregir el motor** | Multiplica por 6 las barras pero también el ruido, el costo relativo y la autocorrelación. Da falsa sensación de n. |
| **Kelly completo ahora** | p incierto con colas gordas ⇒ sobreapuesta ⇒ ruina. |
| **"Gestor de racha" como solución al DD** | Reduce el tamaño después de perder: baja el DD Y la esperanza. No agrega edge. |
| **Ignorar el riesgo de gap** | Con 4h candles y 20x, un gap de 5% liquida. Es el riesgo #1, no el stop. |

### Lo que SÍ conviene

1. **Reparar el motor** (Fase 0) — sin esto, todo lo demás mide ruido.
2. **Correr "A favor del tramo" en BTC 4h con historia completa** (Fase 1) — para ver si el edge sobrevive.
3. **Null sintético** (Fase 2) — el test que decide si vale la pena seguir.
4. **Walk-forward + Monte Carlo** (Fases 3-4) — la validación que pides.
5. **Reportar % de gaps** en el backtest — es el riesgo #1 con 20x.
6. **Sizing conservador: $2 por trade (2% de $100)** — tu modelo ya lo hace bien.

### El número que importa

Con 20x leverage y un stop de $2, el trade se cierra a $2 de pérdida antes de llegar a liquidación. **El riesgo real no es el leverage, es el gap.** Con 4h candles, un gap de 5% liquida la posición. La mitigación es: stop market (no limit), aceptar slippage en gaps, y reportar el % de gaps en el backtest.

---

## 7 · Siguiente paso inmediato

```bash
# 1. Paginar Binance para BTCUSDT 4h (≥2 años) — modificar core/velas.py
#    (aunque operes en Quantfury, los datos de precio son los mismos)

# 2. Línea base
python3 daily_pilot/scripts/backtest_afavor.py BTCUSDT --tf 4h --detalle 500 --filtros "" --stop pct --stop-pct 2.0

# 3. Null sintético
python3 daily_pilot/scripts/banco_candidatos.py BTCUSDT --tf 4h

# 4. Verificar que el DD es cronológico, los costos son 0 (Quantfury), y el % de gaps se reporta
```

**Sin esto, no hay estrategia que valga la pena.** El mercado no regala dinero: el edge, si existe, está en los detalles (costos, fills, look-ahead, gaps) que la mayoría ignora. Tu modelo de risk management ($2 fijo por trade, position sizing por distancia de stop) es correcto y te protege de la liquidación en condiciones normales. El único riesgo real es el gap.