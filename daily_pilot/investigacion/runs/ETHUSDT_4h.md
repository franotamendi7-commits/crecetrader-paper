# BANCO DE CANDIDATOS ETHUSDT — filtro null sintetico (ampliado)

PAPER_ONLY. Par: ETHUSDT | TF: 4h | Velas: 500 (2026-09-02 -> 2026-11-24)

Costos: comision 0.10% + slippage 0.05% por pasada. Stop 2.0% / Target 4.0% (2:1) base. Horizonte 30 barras. Muestra minima 30 trades.

Null sintetico: 1000 sims, block bootstrap, percentil 95. Seed 42.

Categorias: Base (20) + Gestion de posicion (6) + Regimen EMA200 (6) + Multi-timeframe 4h/1d (6).

| regla | cat | n trades | acierto% | esperanza R | p-valor | veredicto |
|---|---|---:|---:|---:|---:|---|
| MA cross 20/50 (golden) long | Base | 6 | 16.7 | -0.51 | 0.543 | MUESTRA CHICA (no declarar) |
| MA cross 50/200 (golden) long | Base | 1 | 0.0 | -1.15 | 0.8767 | MUESTRA CHICA (no declarar) |
| Precio cruza EMA200 al alza long | Base | 1 | 0.0 | -1.15 | 0.8945 | MUESTRA CHICA (no declarar) |
| EMA50 pendiente positiva long | Base | 13 | 46.2 | 0.11 | 0.188 | MUESTRA CHICA (no declarar) |
| Momentum 5 velas >3% long | Base | 13 | 23.1 | -0.458 | 0.587 | MUESTRA CHICA (no declarar) |
| Momentum 20 velas >5% long | Base | 6 | 0.0 | -1.071 | 0.8246 | MUESTRA CHICA (no declarar) |
| Rotura maximo 20 velas long | Base | 10 | 20.0 | -0.55 | 0.621 | MUESTRA CHICA (no declarar) |
| Rotura minimo 20 velas short | Base | 20 | 35.0 | -0.1 | 0.68 | MUESTRA CHICA (no declarar) |
| RSI(14) rebote desde <30 long | Base | 13 | 7.7 | -0.847 | 0.934 | MUESTRA CHICA (no declarar) |
| RSI(14) rechazo desde >70 short | Base | 6 | 83.3 | 1.114 | 0.2109 | MUESTRA CHICA (no declarar) |
| Mean reversion z<-2 long | Base | 20 | 30.0 | -0.282 | 0.579 | MUESTRA CHICA (no declarar) |
| Mean reversion z>+2 short | Base | 10 | 40.0 | -0.026 | 0.715 | MUESTRA CHICA (no declarar) |
| Baja vol (ATR/px<2.5%) + uptrend long | Base | 38 | 26.3 | -0.443 | 0.585 | RUIDO |
| Alta vol (ATR/px>4%) + downtrend short | Base | 0 | 0.0 | NA | NA | MUESTRA CHICA (no declarar) |
| Solo lunes long | Base | 12 | 33.3 | -0.15 | 0.273 | MUESTRA CHICA (no declarar) |
| Solo viernes short | Base | 12 | 33.3 | -0.29 | 0.882 | MUESTRA CHICA (no declarar) |
| Donchian breakout 10 long | Base | 19 | 26.3 | -0.361 | 0.5 | MUESTRA CHICA (no declarar) |
| Donchian breakdown 10 short | Base | 27 | 33.3 | -0.15 | 0.785 | MUESTRA CHICA (no declarar) |
| Regresion lineal slope>0 R2>0.5 long | Base | 10 | 0.0 | -1.15 | 0.979 | MUESTRA CHICA (no declarar) |
| Regresion lineal slope<0 R2>0.5 short | Base | 12 | 50.0 | 0.35 | 0.35 | MUESTRA CHICA (no declarar) |
| Donchian breakout 10 long — stop movil a BE tras +1R | Gestion de posicion | 19 | 10.5 | -0.571 | 0.641 | MUESTRA CHICA (no declarar) |
| Donchian breakdown 10 short — stop movil a BE tras +1R | Gestion de posicion | 27 | 11.1 | -0.372 | 0.745 | MUESTRA CHICA (no declarar) |
| Donchian breakout 10 long — cierre mitad en +1R, dejar correr | Gestion de posicion | 19 | 36.8 | -0.203 | 0.31 | MUESTRA CHICA (no declarar) |
| Donchian breakdown 10 short — cierre mitad en +1R, dejar correr | Gestion de posicion | 27 | 48.1 | -0.225 | 0.821 | MUESTRA CHICA (no declarar) |
| Donchian breakout 10 long — 3 objetivos escalonados 1R/2R/3R | Gestion de posicion | 19 | 36.8 | -0.361 | 0.55 | MUESTRA CHICA (no declarar) |
| Donchian breakdown 10 short — 3 objetivos escalonados 1R/2R/3R | Gestion de posicion | 27 | 48.1 | -0.067 | 0.672 | MUESTRA CHICA (no declarar) |
| Momentum 5 velas >3% long (regimen EMA200) | Regimen | 1 | 0.0 | -1.15 | 0.8537 | MUESTRA CHICA (no declarar) |
| Momentum 20 velas >5% long (regimen EMA200) | Regimen | 1 | 0.0 | -1.15 | 0.8588 | MUESTRA CHICA (no declarar) |
| Rotura maximo 20 velas long (regimen EMA200) | Regimen | 1 | 0.0 | -1.15 | 0.9088 | MUESTRA CHICA (no declarar) |
| Donchian breakout 10 long (regimen EMA200) | Regimen | 1 | 0.0 | -1.15 | 0.9041 | MUESTRA CHICA (no declarar) |
| Rotura minimo 20 velas short (regimen EMA200) | Regimen | 16 | 37.5 | -0.025 | 0.551 | MUESTRA CHICA (no declarar) |
| Donchian breakdown 10 short (regimen EMA200) | Regimen | 20 | 40.0 | 0.05 | 0.504 | MUESTRA CHICA (no declarar) |
| Momentum 5 velas >3% long (MTF: entrada 4h solo si 1d a favor) | Multi-timeframe | 9 | 22.2 | -0.483 | 0.56 | MUESTRA CHICA (no declarar) |
| Momentum 20 velas >5% long (MTF: entrada 4h solo si 1d a favor) | Multi-timeframe | 4 | 0.0 | -1.15 | 0.9243 | MUESTRA CHICA (no declarar) |
| Rotura maximo 20 velas long (MTF: entrada 4h solo si 1d a favor) | Multi-timeframe | 9 | 22.2 | -0.483 | 0.5115 | MUESTRA CHICA (no declarar) |
| Donchian breakout 10 long (MTF: entrada 4h solo si 1d a favor) | Multi-timeframe | 17 | 29.4 | -0.268 | 0.38 | MUESTRA CHICA (no declarar) |
| Rotura minimo 20 velas short (MTF: entrada 4h solo si 1d a favor) | Multi-timeframe | 10 | 40.0 | 0.05 | 0.4289 | MUESTRA CHICA (no declarar) |
| Donchian breakdown 10 short (MTF: entrada 4h solo si 1d a favor) | Multi-timeframe | 12 | 41.7 | 0.1 | 0.438 | MUESTRA CHICA (no declarar) |

**Pasan el null: 0 / 38**

**NINGUNA regla supera el null sintetico.**

Muestra chica (<30): 37 reglas.

## Gestion de posicion — comparacion contra base

| variante | n | acierto% | esperanza R | p-valor | veredicto |
|---|---:|---:|---:|---:|---|
| Donchian breakout 10 long — stop movil a BE tras +1R | 19 | 10.5 | -0.571 | 0.641 | MUESTRA CHICA (no declarar) |
| Donchian breakdown 10 short — stop movil a BE tras +1R | 27 | 11.1 | -0.372 | 0.745 | MUESTRA CHICA (no declarar) |
| Donchian breakout 10 long — cierre mitad en +1R, dejar correr | 19 | 36.8 | -0.203 | 0.31 | MUESTRA CHICA (no declarar) |
| Donchian breakdown 10 short — cierre mitad en +1R, dejar correr | 27 | 48.1 | -0.225 | 0.821 | MUESTRA CHICA (no declarar) |
| Donchian breakout 10 long — 3 objetivos escalonados 1R/2R/3R | 19 | 36.8 | -0.361 | 0.55 | MUESTRA CHICA (no declarar) |
| Donchian breakdown 10 short — 3 objetivos escalonados 1R/2R/3R | 27 | 48.1 | -0.067 | 0.672 | MUESTRA CHICA (no declarar) |

## Regimen (EMA200) — comparacion

| regla | n | acierto% | esperanza R | p-valor | veredicto |
|---|---:|---:|---:|---:|---|
| Momentum 5 velas >3% long (regimen EMA200) | 1 | 0.0 | -1.15 | 0.8537 | MUESTRA CHICA (no declarar) |
| Momentum 20 velas >5% long (regimen EMA200) | 1 | 0.0 | -1.15 | 0.8588 | MUESTRA CHICA (no declarar) |
| Rotura maximo 20 velas long (regimen EMA200) | 1 | 0.0 | -1.15 | 0.9088 | MUESTRA CHICA (no declarar) |
| Donchian breakout 10 long (regimen EMA200) | 1 | 0.0 | -1.15 | 0.9041 | MUESTRA CHICA (no declarar) |
| Rotura minimo 20 velas short (regimen EMA200) | 16 | 37.5 | -0.025 | 0.551 | MUESTRA CHICA (no declarar) |
| Donchian breakdown 10 short (regimen EMA200) | 20 | 40.0 | 0.05 | 0.504 | MUESTRA CHICA (no declarar) |

## Multi-timeframe 4h/1d

| regla | n | acierto% | esperanza R | p-valor | veredicto |
|---|---:|---:|---:|---:|---|
| Momentum 5 velas >3% long (MTF: entrada 4h solo si 1d a favor) | 9 | 22.2 | -0.483 | 0.56 | MUESTRA CHICA (no declarar) |
| Momentum 20 velas >5% long (MTF: entrada 4h solo si 1d a favor) | 4 | 0.0 | -1.15 | 0.9243 | MUESTRA CHICA (no declarar) |
| Rotura maximo 20 velas long (MTF: entrada 4h solo si 1d a favor) | 9 | 22.2 | -0.483 | 0.5115 | MUESTRA CHICA (no declarar) |
| Donchian breakout 10 long (MTF: entrada 4h solo si 1d a favor) | 17 | 29.4 | -0.268 | 0.38 | MUESTRA CHICA (no declarar) |
| Rotura minimo 20 velas short (MTF: entrada 4h solo si 1d a favor) | 10 | 40.0 | 0.05 | 0.4289 | MUESTRA CHICA (no declarar) |
| Donchian breakdown 10 short (MTF: entrada 4h solo si 1d a favor) | 12 | 41.7 | 0.1 | 0.438 | MUESTRA CHICA (no declarar) |

## Walk-forward (2/3 train, 1/3 test) — top 3 reglas base

| regla | n_train | n_test | E_IS | E_OOS | degradacion (OOS/IS) |
|---|---:|---:|---:|---:|---:|
| Donchian breakout 10 long | 333 | 137 | -0.35 | -0.15 | 0.429 |
| Mean reversion z<-2 long | 333 | 137 | 0.391 | -1.15 | -2.94 |
| Baja vol (ATR/px<2.5%) + uptrend long | 333 | 137 | -0.465 | 0.35 | -0.753 |

## Detalle por regla

### MA cross 20/50 (golden) long

- cat: Base
- n trades: 6
- acierto%: 16.7
- esperanza R: -0.51
- p-valor: 0.543
- null p95: 0.85 | null media: -0.3496 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### MA cross 50/200 (golden) long

- cat: Base
- n trades: 1
- acierto%: 0.0
- esperanza R: -1.15
- p-valor: 0.8767
- null p95: 1.85 | null media: -0.3184 | sims validas: 673
- veredicto: MUESTRA CHICA (no declarar)

### Precio cruza EMA200 al alza long

- cat: Base
- n trades: 1
- acierto%: 0.0
- esperanza R: -1.15
- p-valor: 0.8945
- null p95: 1.3857 | null media: -0.3664 | sims validas: 711
- veredicto: MUESTRA CHICA (no declarar)

### EMA50 pendiente positiva long

- cat: Base
- n trades: 13
- acierto%: 46.2
- esperanza R: 0.11
- p-valor: 0.188
- null p95: 0.65 | null media: -0.3303 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Momentum 5 velas >3% long

- cat: Base
- n trades: 13
- acierto%: 23.1
- esperanza R: -0.458
- p-valor: 0.587
- null p95: 0.35 | null media: -0.3578 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Momentum 20 velas >5% long

- cat: Base
- n trades: 6
- acierto%: 0.0
- esperanza R: -1.071
- p-valor: 0.8246
- null p95: 0.5643 | null media: -0.4372 | sims validas: 998
- veredicto: MUESTRA CHICA (no declarar)

### Rotura maximo 20 velas long

- cat: Base
- n trades: 10
- acierto%: 20.0
- esperanza R: -0.55
- p-valor: 0.621
- null p95: 0.3293 | null media: -0.4028 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Rotura minimo 20 velas short

- cat: Base
- n trades: 20
- acierto%: 35.0
- esperanza R: -0.1
- p-valor: 0.68
- null p95: 0.6244 | null media: 0.0546 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### RSI(14) rebote desde <30 long

- cat: Base
- n trades: 13
- acierto%: 7.7
- esperanza R: -0.847
- p-valor: 0.934
- null p95: 0.5558 | null media: -0.2723 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### RSI(14) rechazo desde >70 short

- cat: Base
- n trades: 6
- acierto%: 83.3
- esperanza R: 1.114
- p-valor: 0.2109
- null p95: 1.85 | null media: 0.4142 | sims validas: 939
- veredicto: MUESTRA CHICA (no declarar)

### Mean reversion z<-2 long

- cat: Base
- n trades: 20
- acierto%: 30.0
- esperanza R: -0.282
- p-valor: 0.579
- null p95: 0.4712 | null media: -0.1869 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Mean reversion z>+2 short

- cat: Base
- n trades: 10
- acierto%: 40.0
- esperanza R: -0.026
- p-valor: 0.715
- null p95: 1.2246 | null media: 0.2965 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Baja vol (ATR/px<2.5%) + uptrend long

- cat: Base
- n trades: 38
- acierto%: 26.3
- esperanza R: -0.443
- p-valor: 0.585
- null p95: 0.2944 | null media: -0.3327 | sims validas: 1000
- veredicto: RUIDO

### Alta vol (ATR/px>4%) + downtrend short

- cat: Base
- n trades: 0
- acierto%: 0.0
- esperanza R: None
- p-valor: None
- null p95: None | null media: None | sims validas: 0
- veredicto: MUESTRA CHICA (no declarar)

### Solo lunes long

- cat: Base
- n trades: 12
- acierto%: 33.3
- esperanza R: -0.15
- p-valor: 0.273
- null p95: 0.3243 | null media: -0.3721 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Solo viernes short

- cat: Base
- n trades: 12
- acierto%: 33.3
- esperanza R: -0.29
- p-valor: 0.882
- null p95: 0.85 | null media: 0.2053 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Donchian breakout 10 long

- cat: Base
- n trades: 19
- acierto%: 26.3
- esperanza R: -0.361
- p-valor: 0.5
- null p95: 0.2213 | null media: -0.3593 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Donchian breakdown 10 short

- cat: Base
- n trades: 27
- acierto%: 33.3
- esperanza R: -0.15
- p-valor: 0.785
- null p95: 0.591 | null media: 0.0873 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Regresion lineal slope>0 R2>0.5 long

- cat: Base
- n trades: 10
- acierto%: 0.0
- esperanza R: -1.15
- p-valor: 0.979
- null p95: 0.5167 | null media: -0.3665 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Regresion lineal slope<0 R2>0.5 short

- cat: Base
- n trades: 12
- acierto%: 50.0
- esperanza R: 0.35
- p-valor: 0.35
- null p95: 0.9227 | null media: 0.1807 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Donchian breakout 10 long — stop movil a BE tras +1R

- cat: Gestion de posicion
- n trades: 19
- acierto%: 10.5
- esperanza R: -0.571
- p-valor: 0.641
- null p95: -0.0387 | null media: -0.4644 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Donchian breakdown 10 short — stop movil a BE tras +1R

- cat: Gestion de posicion
- n trades: 27
- acierto%: 11.1
- esperanza R: -0.372
- p-valor: 0.745
- null p95: 0.1444 | null media: -0.2221 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Donchian breakout 10 long — cierre mitad en +1R, dejar correr

- cat: Gestion de posicion
- n trades: 19
- acierto%: 36.8
- esperanza R: -0.203
- p-valor: 0.31
- null p95: 0.2236 | null media: -0.3425 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Donchian breakdown 10 short — cierre mitad en +1R, dejar correr

- cat: Gestion de posicion
- n trades: 27
- acierto%: 48.1
- esperanza R: -0.225
- p-valor: 0.821
- null p95: 0.8051 | null media: 0.1241 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Donchian breakout 10 long — 3 objetivos escalonados 1R/2R/3R

- cat: Gestion de posicion
- n trades: 19
- acierto%: 36.8
- esperanza R: -0.361
- p-valor: 0.55
- null p95: 0.2052 | null media: -0.3086 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Donchian breakdown 10 short — 3 objetivos escalonados 1R/2R/3R

- cat: Gestion de posicion
- n trades: 27
- acierto%: 48.1
- esperanza R: -0.067
- p-valor: 0.672
- null p95: 0.4979 | null media: 0.0542 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Momentum 5 velas >3% long (regimen EMA200)

- cat: Regimen
- n trades: 1
- acierto%: 0.0
- esperanza R: -1.15
- p-valor: 0.8537
- null p95: 0.8511 | null media: -0.4955 | sims validas: 629
- veredicto: MUESTRA CHICA (no declarar)

### Momentum 20 velas >5% long (regimen EMA200)

- cat: Regimen
- n trades: 1
- acierto%: 0.0
- esperanza R: -1.15
- p-valor: 0.8588
- null p95: 1.1 | null media: -0.4945 | sims validas: 595
- veredicto: MUESTRA CHICA (no declarar)

### Rotura maximo 20 velas long (regimen EMA200)

- cat: Regimen
- n trades: 1
- acierto%: 0.0
- esperanza R: -1.15
- p-valor: 0.9088
- null p95: 0.5643 | null media: -0.576 | sims validas: 702
- veredicto: MUESTRA CHICA (no declarar)

### Donchian breakout 10 long (regimen EMA200)

- cat: Regimen
- n trades: 1
- acierto%: 0.0
- esperanza R: -1.15
- p-valor: 0.9041
- null p95: 0.4987 | null media: -0.5701 | sims validas: 709
- veredicto: MUESTRA CHICA (no declarar)

### Rotura minimo 20 velas short (regimen EMA200)

- cat: Regimen
- n trades: 16
- acierto%: 37.5
- esperanza R: -0.025
- p-valor: 0.551
- null p95: 0.7003 | null media: 0.0096 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Donchian breakdown 10 short (regimen EMA200)

- cat: Regimen
- n trades: 20
- acierto%: 40.0
- esperanza R: 0.05
- p-valor: 0.504
- null p95: 0.6784 | null media: 0.0336 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Momentum 5 velas >3% long (MTF: entrada 4h solo si 1d a favor)

- cat: Multi-timeframe
- n trades: 9
- acierto%: 22.2
- esperanza R: -0.483
- p-valor: 0.56
- null p95: 0.4796 | null media: -0.3854 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Momentum 20 velas >5% long (MTF: entrada 4h solo si 1d a favor)

- cat: Multi-timeframe
- n trades: 4
- acierto%: 0.0
- esperanza R: -1.15
- p-valor: 0.9243
- null p95: 0.725 | null media: -0.4703 | sims validas: 991
- veredicto: MUESTRA CHICA (no declarar)

### Rotura maximo 20 velas long (MTF: entrada 4h solo si 1d a favor)

- cat: Multi-timeframe
- n trades: 9
- acierto%: 22.2
- esperanza R: -0.483
- p-valor: 0.5115
- null p95: 0.4656 | null media: -0.4437 | sims validas: 999
- veredicto: MUESTRA CHICA (no declarar)

### Donchian breakout 10 long (MTF: entrada 4h solo si 1d a favor)

- cat: Multi-timeframe
- n trades: 17
- acierto%: 29.4
- esperanza R: -0.268
- p-valor: 0.38
- null p95: 0.3325 | null media: -0.3889 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Rotura minimo 20 velas short (MTF: entrada 4h solo si 1d a favor)

- cat: Multi-timeframe
- n trades: 10
- acierto%: 40.0
- esperanza R: 0.05
- p-valor: 0.4289
- null p95: 0.8524 | null media: -0.0629 | sims validas: 998
- veredicto: MUESTRA CHICA (no declarar)

### Donchian breakdown 10 short (MTF: entrada 4h solo si 1d a favor)

- cat: Multi-timeframe
- n trades: 12
- acierto%: 41.7
- esperanza R: 0.1
- p-valor: 0.438
- null p95: 0.8011 | null media: -0.0063 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)
