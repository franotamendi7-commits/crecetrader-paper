# BANCO DE CANDIDATOS ETHUSDT — filtro null sintetico (ampliado)

PAPER_ONLY. Par: ETHUSDT | TF: 1d | Velas: 500 (2025-07-13 -> 2026-11-24)

Costos: comision 0.10% + slippage 0.05% por pasada. Stop 2.0% / Target 4.0% (2:1) base. Horizonte 30 barras. Muestra minima 30 trades.

Null sintetico: 1000 sims, block bootstrap, percentil 95. Seed 42.

Categorias: Base (20) + Gestion de posicion (6) + Regimen EMA200 (6).

| regla | cat | n trades | acierto% | esperanza R | p-valor | veredicto |
|---|---|---:|---:|---:|---:|---|
| MA cross 20/50 (golden) long | Base | 4 | 25.0 | -0.4 | 0.716 | MUESTRA CHICA (no declarar) |
| MA cross 50/200 (golden) long | Base | 1 | 0.0 | -1.15 | 0.821 | MUESTRA CHICA (no declarar) |
| Precio cruza EMA200 al alza long | Base | 3 | 33.3 | -0.15 | 0.4686 | MUESTRA CHICA (no declarar) |
| EMA50 pendiente positiva long | Base | 9 | 33.3 | -0.15 | 0.55 | MUESTRA CHICA (no declarar) |
| Momentum 5 velas >3% long | Base | 41 | 29.3 | -0.272 | 0.717 | RUIDO |
| Momentum 20 velas >5% long | Base | 20 | 40.0 | 0.05 | 0.348 | MUESTRA CHICA (no declarar) |
| Rotura maximo 20 velas long | Base | 19 | 15.8 | -0.676 | 0.95 | MUESTRA CHICA (no declarar) |
| Rotura minimo 20 velas short | Base | 23 | 52.2 | 0.415 | 0.075 | MUESTRA CHICA (no declarar) |
| RSI(14) rebote desde <30 long | Base | 5 | 20.0 | -0.55 | 0.8156 | MUESTRA CHICA (no declarar) |
| RSI(14) rechazo desde >70 short | Base | 4 | 25.0 | -0.4 | 0.8863 | MUESTRA CHICA (no declarar) |
| Mean reversion z<-2 long | Base | 13 | 15.4 | -0.688 | 0.974 | MUESTRA CHICA (no declarar) |
| Mean reversion z>+2 short | Base | 12 | 16.7 | -0.65 | 0.984 | MUESTRA CHICA (no declarar) |
| Baja vol (ATR/px<2.5%) + uptrend long | Base | 1 | 100.0 | 1.85 | 0.0 | MUESTRA CHICA (no declarar) |
| Alta vol (ATR/px>4%) + downtrend short | Base | 21 | 33.3 | -0.15 | 0.6593 | MUESTRA CHICA (no declarar) |
| Solo lunes long | Base | 72 | 23.6 | -0.442 | 0.989 | RUIDO |
| Solo viernes short | Base | 71 | 23.9 | -0.432 | 1.0 | RUIDO |
| Donchian breakout 10 long | Base | 30 | 20.0 | -0.55 | 0.952 | RUIDO |
| Donchian breakdown 10 short | Base | 35 | 42.9 | 0.136 | 0.394 | RUIDO |
| Regresion lineal slope>0 R2>0.5 long | Base | 8 | 12.5 | -0.775 | 0.926 | MUESTRA CHICA (no declarar) |
| Regresion lineal slope<0 R2>0.5 short | Base | 9 | 11.1 | -0.817 | 0.986 | MUESTRA CHICA (no declarar) |
| Donchian breakout 10 long — stop movil a BE tras +1R | Gestion de posicion | 30 | 3.3 | -0.65 | 0.784 | RUIDO |
| Donchian breakdown 10 short — stop movil a BE tras +1R | Gestion de posicion | 35 | 0.0 | -0.379 | 0.088 | RUIDO |
| Donchian breakout 10 long — cierre mitad en +1R, dejar correr | Gestion de posicion | 30 | 36.7 | -0.405 | 0.78 | RUIDO |
| Donchian breakdown 10 short — cierre mitad en +1R, dejar correr | Gestion de posicion | 35 | 54.3 | 0.431 | 0.399 | RUIDO |
| Donchian breakout 10 long — 3 objetivos escalonados 1R/2R/3R | Gestion de posicion | 30 | 36.7 | -0.506 | 0.952 | RUIDO |
| Donchian breakdown 10 short — 3 objetivos escalonados 1R/2R/3R | Gestion de posicion | 35 | 54.3 | 0.088 | 0.477 | RUIDO |
| Momentum 5 velas >3% long (regimen EMA200) | Regimen | 5 | 40.0 | 0.05 | 0.3035 | MUESTRA CHICA (no declarar) |
| Momentum 20 velas >5% long (regimen EMA200) | Regimen | 2 | 100.0 | 1.85 | 0.0339 | MUESTRA CHICA (no declarar) |
| Rotura maximo 20 velas long (regimen EMA200) | Regimen | 3 | 33.3 | -0.15 | 0.5319 | MUESTRA CHICA (no declarar) |
| Donchian breakout 10 long (regimen EMA200) | Regimen | 4 | 25.0 | -0.4 | 0.7001 | MUESTRA CHICA (no declarar) |
| Rotura minimo 20 velas short (regimen EMA200) | Regimen | 15 | 60.0 | 0.65 | 0.0291 | MUESTRA CHICA (no declarar) |
| Donchian breakdown 10 short (regimen EMA200) | Regimen | 20 | 50.0 | 0.35 | 0.1665 | MUESTRA CHICA (no declarar) |

**Pasan el null: 0 / 32**

**NINGUNA regla supera el null sintetico.**

Muestra chica (<30): 21 reglas.

## Gestion de posicion — comparacion contra base

| variante | n | acierto% | esperanza R | p-valor | veredicto |
|---|---:|---:|---:|---:|---|
| Donchian breakout 10 long — stop movil a BE tras +1R | 30 | 3.3 | -0.65 | 0.784 | RUIDO |
| Donchian breakdown 10 short — stop movil a BE tras +1R | 35 | 0.0 | -0.379 | 0.088 | RUIDO |
| Donchian breakout 10 long — cierre mitad en +1R, dejar correr | 30 | 36.7 | -0.405 | 0.78 | RUIDO |
| Donchian breakdown 10 short — cierre mitad en +1R, dejar correr | 35 | 54.3 | 0.431 | 0.399 | RUIDO |
| Donchian breakout 10 long — 3 objetivos escalonados 1R/2R/3R | 30 | 36.7 | -0.506 | 0.952 | RUIDO |
| Donchian breakdown 10 short — 3 objetivos escalonados 1R/2R/3R | 35 | 54.3 | 0.088 | 0.477 | RUIDO |

## Regimen (EMA200) — comparacion

| regla | n | acierto% | esperanza R | p-valor | veredicto |
|---|---:|---:|---:|---:|---|
| Momentum 5 velas >3% long (regimen EMA200) | 5 | 40.0 | 0.05 | 0.3035 | MUESTRA CHICA (no declarar) |
| Momentum 20 velas >5% long (regimen EMA200) | 2 | 100.0 | 1.85 | 0.0339 | MUESTRA CHICA (no declarar) |
| Rotura maximo 20 velas long (regimen EMA200) | 3 | 33.3 | -0.15 | 0.5319 | MUESTRA CHICA (no declarar) |
| Donchian breakout 10 long (regimen EMA200) | 4 | 25.0 | -0.4 | 0.7001 | MUESTRA CHICA (no declarar) |
| Rotura minimo 20 velas short (regimen EMA200) | 15 | 60.0 | 0.65 | 0.0291 | MUESTRA CHICA (no declarar) |
| Donchian breakdown 10 short (regimen EMA200) | 20 | 50.0 | 0.35 | 0.1665 | MUESTRA CHICA (no declarar) |

## Walk-forward (2/3 train, 1/3 test) — top 3 reglas base

| regla | n_train | n_test | E_IS | E_OOS | degradacion (OOS/IS) |
|---|---:|---:|---:|---:|---:|
| Rotura minimo 20 velas short | 333 | 137 | 0.615 | -0.15 | -0.244 |
| Momentum 20 velas >5% long | 333 | 137 | -0.15 | 0.85 | -5.667 |
| Donchian breakdown 10 short | 333 | 137 | 0.35 | -0.25 | -0.714 |

## Detalle por regla

### MA cross 20/50 (golden) long

- cat: Base
- n trades: 4
- acierto%: 25.0
- esperanza R: -0.4
- p-valor: 0.716
- null p95: 1.1 | null media: -0.0487 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### MA cross 50/200 (golden) long

- cat: Base
- n trades: 1
- acierto%: 0.0
- esperanza R: -1.15
- p-valor: 0.821
- null p95: 1.85 | null media: -0.1092 | sims validas: 799
- veredicto: MUESTRA CHICA (no declarar)

### Precio cruza EMA200 al alza long

- cat: Base
- n trades: 3
- acierto%: 33.3
- esperanza R: -0.15
- p-valor: 0.4686
- null p95: 1.85 | null media: -0.0802 | sims validas: 811
- veredicto: MUESTRA CHICA (no declarar)

### EMA50 pendiente positiva long

- cat: Base
- n trades: 9
- acierto%: 33.3
- esperanza R: -0.15
- p-valor: 0.55
- null p95: 0.7591 | null media: -0.0651 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Momentum 5 velas >3% long

- cat: Base
- n trades: 41
- acierto%: 29.3
- esperanza R: -0.272
- p-valor: 0.717
- null p95: 0.2711 | null media: -0.1298 | sims validas: 1000
- veredicto: RUIDO

### Momentum 20 velas >5% long

- cat: Base
- n trades: 20
- acierto%: 40.0
- esperanza R: 0.05
- p-valor: 0.348
- null p95: 0.4505 | null media: -0.0945 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Rotura maximo 20 velas long

- cat: Base
- n trades: 19
- acierto%: 15.8
- esperanza R: -0.676
- p-valor: 0.95
- null p95: 0.475 | null media: -0.0546 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Rotura minimo 20 velas short

- cat: Base
- n trades: 23
- acierto%: 52.2
- esperanza R: 0.415
- p-valor: 0.075
- null p95: 0.4621 | null media: 0.0444 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### RSI(14) rebote desde <30 long

- cat: Base
- n trades: 5
- acierto%: 20.0
- esperanza R: -0.55
- p-valor: 0.8156
- null p95: 0.85 | null media: -0.1257 | sims validas: 998
- veredicto: MUESTRA CHICA (no declarar)

### RSI(14) rechazo desde >70 short

- cat: Base
- n trades: 4
- acierto%: 25.0
- esperanza R: -0.4
- p-valor: 0.8863
- null p95: 1.85 | null media: 0.3514 | sims validas: 976
- veredicto: MUESTRA CHICA (no declarar)

### Mean reversion z<-2 long

- cat: Base
- n trades: 13
- acierto%: 15.4
- esperanza R: -0.688
- p-valor: 0.974
- null p95: 0.7455 | null media: 0.0907 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Mean reversion z>+2 short

- cat: Base
- n trades: 12
- acierto%: 16.7
- esperanza R: -0.65
- p-valor: 0.984
- null p95: 0.9929 | null media: 0.2476 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Baja vol (ATR/px<2.5%) + uptrend long

- cat: Base
- n trades: 1
- acierto%: 100.0
- esperanza R: 1.85
- p-valor: 0.0
- null p95: 0.4869 | null media: -0.0795 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Alta vol (ATR/px>4%) + downtrend short

- cat: Base
- n trades: 21
- acierto%: 33.3
- esperanza R: -0.15
- p-valor: 0.6593
- null p95: 0.95 | null media: 0.0227 | sims validas: 998
- veredicto: MUESTRA CHICA (no declarar)

### Solo lunes long

- cat: Base
- n trades: 72
- acierto%: 23.6
- esperanza R: -0.442
- p-valor: 0.989
- null p95: 0.2417 | null media: -0.0502 | sims validas: 1000
- veredicto: RUIDO

### Solo viernes short

- cat: Base
- n trades: 71
- acierto%: 23.9
- esperanza R: -0.432
- p-valor: 1.0
- null p95: 0.4979 | null media: 0.1634 | sims validas: 1000
- veredicto: RUIDO

### Donchian breakout 10 long

- cat: Base
- n trades: 30
- acierto%: 20.0
- esperanza R: -0.55
- p-valor: 0.952
- null p95: 0.3798 | null media: -0.0456 | sims validas: 1000
- veredicto: RUIDO

### Donchian breakdown 10 short

- cat: Base
- n trades: 35
- acierto%: 42.9
- esperanza R: 0.136
- p-valor: 0.394
- null p95: 0.4198 | null media: 0.073 | sims validas: 1000
- veredicto: RUIDO

### Regresion lineal slope>0 R2>0.5 long

- cat: Base
- n trades: 8
- acierto%: 12.5
- esperanza R: -0.775
- p-valor: 0.926
- null p95: 0.855 | null media: -0.0422 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Regresion lineal slope<0 R2>0.5 short

- cat: Base
- n trades: 9
- acierto%: 11.1
- esperanza R: -0.817
- p-valor: 0.986
- null p95: 0.95 | null media: 0.1688 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Donchian breakout 10 long — stop movil a BE tras +1R

- cat: Gestion de posicion
- n trades: 30
- acierto%: 3.3
- esperanza R: -0.65
- p-valor: 0.784
- null p95: -0.2552 | null media: -0.5208 | sims validas: 1000
- veredicto: RUIDO

### Donchian breakdown 10 short — stop movil a BE tras +1R

- cat: Gestion de posicion
- n trades: 35
- acierto%: 0.0
- esperanza R: -0.379
- p-valor: 0.088
- null p95: -0.3454 | null media: -0.5394 | sims validas: 1000
- veredicto: RUIDO

### Donchian breakout 10 long — cierre mitad en +1R, dejar correr

- cat: Gestion de posicion
- n trades: 30
- acierto%: 36.7
- esperanza R: -0.405
- p-valor: 0.78
- null p95: 1.293 | null media: 0.064 | sims validas: 1000
- veredicto: RUIDO

### Donchian breakdown 10 short — cierre mitad en +1R, dejar correr

- cat: Gestion de posicion
- n trades: 35
- acierto%: 54.3
- esperanza R: 0.431
- p-valor: 0.399
- null p95: 1.4657 | null media: 0.378 | sims validas: 1000
- veredicto: RUIDO

### Donchian breakout 10 long — 3 objetivos escalonados 1R/2R/3R

- cat: Gestion de posicion
- n trades: 30
- acierto%: 36.7
- esperanza R: -0.506
- p-valor: 0.952
- null p95: 0.3394 | null media: -0.0502 | sims validas: 1000
- veredicto: RUIDO

### Donchian breakdown 10 short — 3 objetivos escalonados 1R/2R/3R

- cat: Gestion de posicion
- n trades: 35
- acierto%: 54.3
- esperanza R: 0.088
- p-valor: 0.477
- null p95: 0.3944 | null media: 0.0717 | sims validas: 1000
- veredicto: RUIDO

### Momentum 5 velas >3% long (regimen EMA200)

- cat: Regimen
- n trades: 5
- acierto%: 40.0
- esperanza R: 0.05
- p-valor: 0.3035
- null p95: 0.7046 | null media: -0.2472 | sims validas: 771
- veredicto: MUESTRA CHICA (no declarar)

### Momentum 20 velas >5% long (regimen EMA200)

- cat: Regimen
- n trades: 2
- acierto%: 100.0
- esperanza R: 1.85
- p-valor: 0.0339
- null p95: 1.31 | null media: -0.1609 | sims validas: 709
- veredicto: MUESTRA CHICA (no declarar)

### Rotura maximo 20 velas long (regimen EMA200)

- cat: Regimen
- n trades: 3
- acierto%: 33.3
- esperanza R: -0.15
- p-valor: 0.5319
- null p95: 0.725 | null media: -0.1932 | sims validas: 814
- veredicto: MUESTRA CHICA (no declarar)

### Donchian breakout 10 long (regimen EMA200)

- cat: Regimen
- n trades: 4
- acierto%: 25.0
- esperanza R: -0.4
- p-valor: 0.7001
- null p95: 0.65 | null media: -0.1796 | sims validas: 817
- veredicto: MUESTRA CHICA (no declarar)

### Rotura minimo 20 velas short (regimen EMA200)

- cat: Regimen
- n trades: 15
- acierto%: 60.0
- esperanza R: 0.65
- p-valor: 0.0291
- null p95: 0.5643 | null media: 0.0134 | sims validas: 997
- veredicto: MUESTRA CHICA (no declarar)

### Donchian breakdown 10 short (regimen EMA200)

- cat: Regimen
- n trades: 20
- acierto%: 50.0
- esperanza R: 0.35
- p-valor: 0.1665
- null p95: 0.5457 | null media: 0.0439 | sims validas: 997
- veredicto: MUESTRA CHICA (no declarar)
