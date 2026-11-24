# BANCO DE CANDIDATOS BTC — filtro null sintetico

PAPER_ONLY. Par: BTCUSDT | TF: 1d | Velas: 500 (2025-07-13 -> 2026-11-24)

Costos: comision 0.10% + slippage 0.05% por pasada (costos_R de validacion_protocolo.py). Stop 2.0% / Target 4.0% (2:1) para todos los candidatos. Horizonte de resolucion 30 barras. Muestra minima para declarar: 30 trades.

Null sintetico: 1000 sims, block bootstrap de retornos, percentil 95. Seed 42.

| regla | n trades | acierto% | esperanza R | p-valor | veredicto (PASA/RUIDO) |
|---|---:|---:|---:|---:|---|
| MA cross 20/50 (golden) long | 5 | 40.0 | 0.05 | 0.362 | MUESTRA CHICA (no declarar) |
| MA cross 50/200 (golden) long | 1 | 0.0 | -1.15 | 1.0 | MUESTRA CHICA (no declarar) |
| Precio cruza EMA200 al alza long | 2 | 50.0 | 0.35 | 0.1878 | MUESTRA CHICA (no declarar) |
| EMA50 pendiente positiva long | 9 | 33.3 | -0.15 | 0.4619 | MUESTRA CHICA (no declarar) |
| Momentum 5 velas >3% long | 37 | 27.0 | -0.339 | 0.682 | RUIDO |
| Momentum 20 velas >5% long | 19 | 26.3 | -0.361 | 0.7 | MUESTRA CHICA (no declarar) |
| Rotura maximo 20 velas long | 21 | 23.8 | -0.436 | 0.745 | MUESTRA CHICA (no declarar) |
| Rotura minimo 20 velas short | 28 | 46.4 | 0.243 | 0.216 | MUESTRA CHICA (no declarar) |
| RSI(14) rebote desde <30 long | 6 | 33.3 | -0.15 | 0.3894 | MUESTRA CHICA (no declarar) |
| RSI(14) rechazo desde >70 short | 6 | 33.3 | -0.15 | 0.7251 | MUESTRA CHICA (no declarar) |
| Mean reversion z<-2 long | 14 | 14.3 | -0.721 | 0.931 | MUESTRA CHICA (no declarar) |
| Mean reversion z>+2 short | 11 | 45.5 | 0.214 | 0.447 | MUESTRA CHICA (no declarar) |
| Baja vol (ATR/px<2.5%) + uptrend long | 18 | 33.3 | -0.15 | 0.461 | MUESTRA CHICA (no declarar) |
| Alta vol (ATR/px>4%) + downtrend short | 12 | 16.7 | -0.65 | 0.4529 | MUESTRA CHICA (no declarar) |
| Solo lunes long | 72 | 26.4 | -0.358 | 0.869 | RUIDO |
| Solo viernes short | 71 | 31.0 | -0.22 | 0.953 | RUIDO |
| Donchian breakout 10 long | 33 | 21.2 | -0.514 | 0.88 | RUIDO |
| Donchian breakdown 10 short | 41 | 39.0 | 0.021 | 0.554 | RUIDO |
| Regresion lineal slope>0 R2>0.5 long | 9 | 11.1 | -0.817 | 0.929 | MUESTRA CHICA (no declarar) |
| Regresion lineal slope<0 R2>0.5 short | 10 | 20.0 | -0.55 | 0.939 | MUESTRA CHICA (no declarar) |

**Pasan el null: 0 / 20**

**NINGUNA regla supera el null sintetico. Ese es un resultado valido: no hay edge detectable en este universo de candidatos para BTC 1d.**

Muestra chica (<30 trades): 15 reglas — no declarar edge.
- MA cross 20/50 (golden) long (n=5)
- MA cross 50/200 (golden) long (n=1)
- Precio cruza EMA200 al alza long (n=2)
- EMA50 pendiente positiva long (n=9)
- Momentum 20 velas >5% long (n=19)
- Rotura maximo 20 velas long (n=21)
- Rotura minimo 20 velas short (n=28)
- RSI(14) rebote desde <30 long (n=6)
- RSI(14) rechazo desde >70 short (n=6)
- Mean reversion z<-2 long (n=14)
- Mean reversion z>+2 short (n=11)
- Baja vol (ATR/px<2.5%) + uptrend long (n=18)
- Alta vol (ATR/px>4%) + downtrend short (n=12)
- Regresion lineal slope>0 R2>0.5 long (n=9)
- Regresion lineal slope<0 R2>0.5 short (n=10)

## Detalle por regla

### MA cross 20/50 (golden) long

- n trades: 5
- acierto%: 40.0
- esperanza R: 0.05
- p-valor (empirico vs null): 0.362
- null p95: 1.1 | null media: -0.13 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### MA cross 50/200 (golden) long

- n trades: 1
- acierto%: 0.0
- esperanza R: -1.15
- p-valor (empirico vs null): 1.0
- null p95: 1.85 | null media: -0.1085 | sims validas: 715
- veredicto: MUESTRA CHICA (no declarar)

### Precio cruza EMA200 al alza long

- n trades: 2
- acierto%: 50.0
- esperanza R: 0.35
- p-valor (empirico vs null): 0.1878
- null p95: 1.85 | null media: -0.1432 | sims validas: 719
- veredicto: MUESTRA CHICA (no declarar)

### EMA50 pendiente positiva long

- n trades: 9
- acierto%: 33.3
- esperanza R: -0.15
- p-valor (empirico vs null): 0.4619
- null p95: 0.725 | null media: -0.1385 | sims validas: 998
- veredicto: MUESTRA CHICA (no declarar)

### Momentum 5 velas >3% long

- n trades: 37
- acierto%: 27.0
- esperanza R: -0.339
- p-valor (empirico vs null): 0.682
- null p95: 0.2048 | null media: -0.2227 | sims validas: 1000
- veredicto: RUIDO

### Momentum 20 velas >5% long

- n trades: 19
- acierto%: 26.3
- esperanza R: -0.361
- p-valor (empirico vs null): 0.7
- null p95: 0.4654 | null media: -0.1594 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Rotura maximo 20 velas long

- n trades: 21
- acierto%: 23.8
- esperanza R: -0.436
- p-valor (empirico vs null): 0.745
- null p95: 0.41 | null media: -0.1976 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Rotura minimo 20 velas short

- n trades: 28
- acierto%: 46.4
- esperanza R: 0.243
- p-valor (empirico vs null): 0.216
- null p95: 0.4825 | null media: 0.0335 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### RSI(14) rebote desde <30 long

- n trades: 6
- acierto%: 33.3
- esperanza R: -0.15
- p-valor (empirico vs null): 0.3894
- null p95: 0.5643 | null media: -0.2574 | sims validas: 999
- veredicto: MUESTRA CHICA (no declarar)

### RSI(14) rechazo desde >70 short

- n trades: 6
- acierto%: 33.3
- esperanza R: -0.15
- p-valor (empirico vs null): 0.7251
- null p95: 1.85 | null media: 0.3694 | sims validas: 953
- veredicto: MUESTRA CHICA (no declarar)

### Mean reversion z<-2 long

- n trades: 14
- acierto%: 14.3
- esperanza R: -0.721
- p-valor (empirico vs null): 0.931
- null p95: 0.5008 | null media: -0.1637 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Mean reversion z>+2 short

- n trades: 11
- acierto%: 45.5
- esperanza R: 0.214
- p-valor (empirico vs null): 0.447
- null p95: 0.9929 | null media: 0.202 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Baja vol (ATR/px<2.5%) + uptrend long

- n trades: 18
- acierto%: 33.3
- esperanza R: -0.15
- p-valor (empirico vs null): 0.461
- null p95: 0.35 | null media: -0.1653 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Alta vol (ATR/px>4%) + downtrend short

- n trades: 12
- acierto%: 16.7
- esperanza R: -0.65
- p-valor (empirico vs null): 0.4529
- null p95: 1.85 | null media: -0.281 | sims validas: 658
- veredicto: MUESTRA CHICA (no declarar)

### Solo lunes long

- n trades: 72
- acierto%: 26.4
- esperanza R: -0.358
- p-valor (empirico vs null): 0.869
- null p95: 0.1513 | null media: -0.1499 | sims validas: 1000
- veredicto: RUIDO

### Solo viernes short

- n trades: 71
- acierto%: 31.0
- esperanza R: -0.22
- p-valor (empirico vs null): 0.953
- null p95: 0.4556 | null media: 0.1042 | sims validas: 1000
- veredicto: RUIDO

### Donchian breakout 10 long

- n trades: 33
- acierto%: 21.2
- esperanza R: -0.514
- p-valor (empirico vs null): 0.88
- null p95: 0.3047 | null media: -0.1739 | sims validas: 1000
- veredicto: RUIDO

### Donchian breakdown 10 short

- n trades: 41
- acierto%: 39.0
- esperanza R: 0.021
- p-valor (empirico vs null): 0.554
- null p95: 0.4058 | null media: 0.0407 | sims validas: 1000
- veredicto: RUIDO

### Regresion lineal slope>0 R2>0.5 long

- n trades: 9
- acierto%: 11.1
- esperanza R: -0.817
- p-valor (empirico vs null): 0.929
- null p95: 0.725 | null media: -0.1532 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Regresion lineal slope<0 R2>0.5 short

- n trades: 10
- acierto%: 20.0
- esperanza R: -0.55
- p-valor (empirico vs null): 0.939
- null p95: 0.95 | null media: 0.1589 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)
