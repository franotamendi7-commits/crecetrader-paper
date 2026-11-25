# STOP CORREGIDO — resultados válidos

Fecha: 2026-11-25. Corrección pedida por Francisco.

## Qué estaba mal y qué se corrigió

**ANTES (mal):** `stop = min(lows[i-5:i+1])` → mínimo móvil de las últimas
6 velas. El stop se movía con la vela. No representaba la estructura.

**AHORA (bien):** `stop = stop_swing_entry(...)` → **último swing LOW antes de
la entrada**, es decir el bajo posterior al cambio de tendencia. Es un precio
fijo calculado una sola vez. Coincide con las fotos: entrada 59.778 /
stop 58.400, entrada 59.911 / stop 58.400 — mismo stop, distinta entrada.

**Sizing (antes no existía, ahora sí):**
```
unidades = riesgo_usd / (entrada - stop)
notional = unidades * entrada
margen   = notional / 20
```
El stop **nunca se mueve** para cambiar el tamaño. Siempre varía la cantidad.
Riesgo permitido: 1% a 5% del capital, según convicción.

Ejemplo real con $300 (entrada 82.640,73 / stop swing 79.800, dist 2.840,73):

| riesgo | USD | unidades | notional | margen 20x |
|---|---:|---:|---:|---:|
| 1% | $3 | 0,001056 | $87,27 | $4,36 |
| 2% | $6 | 0,002112 | $174,55 | $8,73 |
| 5% | $15 | 0,005280 | $436,37 | $21,82 |

## Resultados con stop corregido (BTC/ETH 4h, 9,3 años)

Grid de 96 combinaciones (ema 8/13/21/34, target 2R/3R, swing_n 2/3/5,
régimen None/EMA50↑). Null sintético 60 simulaciones. Walk-forward 70/30.

| variante | /mes | n | E(R) | win% | DD | PF | null p | WF |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **BTC ema34 tR2 sw5 EMA50↑** | 9,5 | 1061 | **+0,277** | 41,1 | −63 | **1,51** | **0,000 PASA** | −75% |
| BTC ema34 tR2 sw5 | 12,4 | 1377 | +0,264 | 40,7 | −52 | 1,48 | 0,000 PASA | −93% |
| ETH ema13 tR2 sw5 | **24,0** | 2672 | +0,254 | 39,5 | −108 | 1,47 | **0,017 PASA** | −103% |
| ETH ema13 tR3 sw5 | **24,0** | 2672 | **+0,312** | 30,2 | −122 | **1,53** | 0,000 PASA | −118% |

Cartera BTC+ETH (ema13 tR2 sw5): **51,2 señales/mes**, E=+0,189R,
DD=−163R, PF=1,33.

## Comparación con los números anteriores (stop mal puesto)

| | stop mal (móvil) | stop bien (swing fijo) |
|---|---:|---:|
| BTC ema34 tR2 E | +0,220 | **+0,277** |
| BTC ema34 tR2 PF | 1,38 | **1,51** |
| ETH ema13 tR2 E | +0,135 | **+0,254** |
| ETH ema13 tR2 PF | 1,22 | **1,47** |

Corregir el stop **mejoró la esperanza y el factor beneficio** en todos los
casos. El drawdown en R subió porque el stop estructural es más lejano y
por eso las pérdidas son más grandes en términos de R (pero el sizing en
dólares sigue siendo exactamente el riesgo elegido: 1%-5%).

## Lo que sigue sin resolverse

El walk-forward sigue degradando (−75% a −118%). Sigue siendo el mismo
problema: el pullback solo gana en tendencia, y el 30% final de la serie
tiene años laterales/bajistas.

La mezcla con la estrategia lenta (filtro de régimen externo) sigue siendo
el siguiente paso lógico. **Ese trabajo NO está hecho todavía.**

PAPER_ONLY. No se ejecutaron órdenes.
