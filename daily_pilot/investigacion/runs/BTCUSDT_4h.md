# BANCO DE CANDIDATOS BTCUSDT — filtro null sintetico (ampliado)

PAPER_ONLY. Par: BTCUSDT | TF: 4h | Velas: 500 (2026-09-02 -> 2026-11-24)

Costos: comision 0.10% + slippage 0.05% por pasada. Stop 2.0% / Target 4.0% (2:1) base. Horizonte 30 barras. Muestra minima 30 trades.

Null sintetico: 1000 sims, block bootstrap, percentil 95. Seed 42.

Categorias: Base (20) + Gestion de posicion (6) + Regimen EMA200 (6) + Multi-timeframe 4h/1d (6).

| regla | cat | n trades | acierto% | esperanza R | p-valor | veredicto |
|---|---|---:|---:|---:|---:|---|
| MA cross 20/50 (golden) long | Base | 4 | 25.0 | -0.4 | 0.4615 | MUESTRA CHICA (no declarar) |
| MA cross 50/200 (golden) long | Base | 1 | 0.0 | -1.15 | 0.9694 | MUESTRA CHICA (no declarar) |
| Precio cruza EMA200 al alza long | Base | 9 | 11.1 | -0.799 | 0.5829 | MUESTRA CHICA (no declarar) |
| EMA50 pendiente positiva long | Base | 10 | 50.0 | 0.083 | 0.1884 | MUESTRA CHICA (no declarar) |
| Momentum 5 velas >3% long | Base | 7 | 28.6 | -0.293 | 0.357 | MUESTRA CHICA (no declarar) |
| Momentum 20 velas >5% long | Base | 3 | 33.3 | 0.041 | 0.212 | MUESTRA CHICA (no declarar) |
| Rotura maximo 20 velas long | Base | 12 | 16.7 | -0.65 | 0.647 | MUESTRA CHICA (no declarar) |
| Rotura minimo 20 velas short | Base | 24 | 50.0 | 0.261 | 0.376 | MUESTRA CHICA (no declarar) |
| RSI(14) rebote desde <30 long | Base | 8 | 37.5 | -0.381 | 0.502 | MUESTRA CHICA (no declarar) |
| RSI(14) rechazo desde >70 short | Base | 3 | 66.7 | 0.494 | 0.4152 | MUESTRA CHICA (no declarar) |
| Mean reversion z<-2 long | Base | 22 | 27.3 | -0.389 | 0.538 | MUESTRA CHICA (no declarar) |
| Mean reversion z>+2 short | Base | 12 | 50.0 | 0.35 | 0.423 | MUESTRA CHICA (no declarar) |
| Baja vol (ATR/px<2.5%) + uptrend long | Base | 33 | 21.2 | -0.525 | 0.604 | RUIDO |
| Alta vol (ATR/px>4%) + downtrend short | Base | 0 | 0.0 | NA | NA | MUESTRA CHICA (no declarar) |
| Solo lunes long | Base | 12 | 25.0 | -0.4 | 0.465 | MUESTRA CHICA (no declarar) |
| Solo viernes short | Base | 12 | 66.7 | 0.426 | 0.291 | MUESTRA CHICA (no declarar) |
| Donchian breakout 10 long | Base | 31 | 22.6 | -0.473 | 0.592 | RUIDO |
| Donchian breakdown 10 short | Base | 32 | 50.0 | 0.135 | 0.509 | RUIDO |
| Regresion lineal slope>0 R2>0.5 long | Base | 10 | 10.0 | -0.85 | 0.844 | MUESTRA CHICA (no declarar) |
| Regresion lineal slope<0 R2>0.5 short | Base | 11 | 72.7 | 0.739 | 0.111 | MUESTRA CHICA (no declarar) |
| Donchian breakout 10 long — stop movil a BE tras +1R | Gestion de posicion | 31 | 19.4 | -0.376 | 0.384 | RUIDO |
| Donchian breakdown 10 short — stop movil a BE tras +1R | Gestion de posicion | 32 | 18.8 | -0.259 | 0.742 | RUIDO |
| Donchian breakout 10 long — cierre mitad en +1R, dejar correr | Gestion de posicion | 31 | 38.7 | -0.141 | 0.236 | RUIDO |
| Donchian breakdown 10 short — cierre mitad en +1R, dejar correr | Gestion de posicion | 32 | 53.1 | -0.147 | 0.796 | RUIDO |
| Donchian breakout 10 long — 3 objetivos escalonados 1R/2R/3R | Gestion de posicion | 31 | 38.7 | -0.29 | 0.441 | RUIDO |
| Donchian breakdown 10 short — 3 objetivos escalonados 1R/2R/3R | Gestion de posicion | 32 | 53.1 | -0.063 | 0.717 | RUIDO |
| Momentum 5 velas >3% long (regimen EMA200) | Regimen | 0 | 0.0 | NA | 1.0 | MUESTRA CHICA (no declarar) |
| Momentum 20 velas >5% long (regimen EMA200) | Regimen | 0 | 0.0 | NA | 1.0 | MUESTRA CHICA (no declarar) |
| Rotura maximo 20 velas long (regimen EMA200) | Regimen | 3 | 0.0 | -1.15 | 0.9726 | MUESTRA CHICA (no declarar) |
| Donchian breakout 10 long (regimen EMA200) | Regimen | 5 | 0.0 | -1.15 | 0.916 | MUESTRA CHICA (no declarar) |
| Rotura minimo 20 velas short (regimen EMA200) | Regimen | 18 | 55.6 | 0.425 | 0.2352 | MUESTRA CHICA (no declarar) |
| Donchian breakdown 10 short (regimen EMA200) | Regimen | 20 | 55.0 | 0.374 | 0.2563 | MUESTRA CHICA (no declarar) |
| Momentum 5 velas >3% long (MTF: entrada 4h solo si 1d a favor) | Multi-timeframe | 4 | 25.0 | -0.4 | 0.4372 | MUESTRA CHICA (no declarar) |
| Momentum 20 velas >5% long (MTF: entrada 4h solo si 1d a favor) | Multi-timeframe | 2 | 50.0 | 0.35 | 0.1582 | MUESTRA CHICA (no declarar) |
| Rotura maximo 20 velas long (MTF: entrada 4h solo si 1d a favor) | Multi-timeframe | 11 | 18.2 | -0.605 | 0.578 | MUESTRA CHICA (no declarar) |
| Donchian breakout 10 long (MTF: entrada 4h solo si 1d a favor) | Multi-timeframe | 28 | 21.4 | -0.507 | 0.595 | MUESTRA CHICA (no declarar) |
| Rotura minimo 20 velas short (MTF: entrada 4h solo si 1d a favor) | Multi-timeframe | 13 | 69.2 | 0.927 | 0.0762 | MUESTRA CHICA (no declarar) |
| Donchian breakdown 10 short (MTF: entrada 4h solo si 1d a favor) | Multi-timeframe | 14 | 64.3 | 0.779 | 0.111 | MUESTRA CHICA (no declarar) |

**Pasan el null: 0 / 38**

**NINGUNA regla supera el null sintetico.**

Muestra chica (<30): 29 reglas.

## Gestion de posicion — comparacion contra base

| variante | n | acierto% | esperanza R | p-valor | veredicto |
|---|---:|---:|---:|---:|---|
| Donchian breakout 10 long — stop movil a BE tras +1R | 31 | 19.4 | -0.376 | 0.384 | RUIDO |
| Donchian breakdown 10 short — stop movil a BE tras +1R | 32 | 18.8 | -0.259 | 0.742 | RUIDO |
| Donchian breakout 10 long — cierre mitad en +1R, dejar correr | 31 | 38.7 | -0.141 | 0.236 | RUIDO |
| Donchian breakdown 10 short — cierre mitad en +1R, dejar correr | 32 | 53.1 | -0.147 | 0.796 | RUIDO |
| Donchian breakout 10 long — 3 objetivos escalonados 1R/2R/3R | 31 | 38.7 | -0.29 | 0.441 | RUIDO |
| Donchian breakdown 10 short — 3 objetivos escalonados 1R/2R/3R | 32 | 53.1 | -0.063 | 0.717 | RUIDO |

## Regimen (EMA200) — comparacion

| regla | n | acierto% | esperanza R | p-valor | veredicto |
|---|---:|---:|---:|---:|---|
| Momentum 5 velas >3% long (regimen EMA200) | 0 | 0.0 | NA | 1.0 | MUESTRA CHICA (no declarar) |
| Momentum 20 velas >5% long (regimen EMA200) | 0 | 0.0 | NA | 1.0 | MUESTRA CHICA (no declarar) |
| Rotura maximo 20 velas long (regimen EMA200) | 3 | 0.0 | -1.15 | 0.9726 | MUESTRA CHICA (no declarar) |
| Donchian breakout 10 long (regimen EMA200) | 5 | 0.0 | -1.15 | 0.916 | MUESTRA CHICA (no declarar) |
| Rotura minimo 20 velas short (regimen EMA200) | 18 | 55.6 | 0.425 | 0.2352 | MUESTRA CHICA (no declarar) |
| Donchian breakdown 10 short (regimen EMA200) | 20 | 55.0 | 0.374 | 0.2563 | MUESTRA CHICA (no declarar) |

## Multi-timeframe 4h/1d

| regla | n | acierto% | esperanza R | p-valor | veredicto |
|---|---:|---:|---:|---:|---|
| Momentum 5 velas >3% long (MTF: entrada 4h solo si 1d a favor) | 4 | 25.0 | -0.4 | 0.4372 | MUESTRA CHICA (no declarar) |
| Momentum 20 velas >5% long (MTF: entrada 4h solo si 1d a favor) | 2 | 50.0 | 0.35 | 0.1582 | MUESTRA CHICA (no declarar) |
| Rotura maximo 20 velas long (MTF: entrada 4h solo si 1d a favor) | 11 | 18.2 | -0.605 | 0.578 | MUESTRA CHICA (no declarar) |
| Donchian breakout 10 long (MTF: entrada 4h solo si 1d a favor) | 28 | 21.4 | -0.507 | 0.595 | MUESTRA CHICA (no declarar) |
| Rotura minimo 20 velas short (MTF: entrada 4h solo si 1d a favor) | 13 | 69.2 | 0.927 | 0.0762 | MUESTRA CHICA (no declarar) |
| Donchian breakdown 10 short (MTF: entrada 4h solo si 1d a favor) | 14 | 64.3 | 0.779 | 0.111 | MUESTRA CHICA (no declarar) |

## Walk-forward (2/3 train, 1/3 test) — top 3 reglas base

| regla | n_train | n_test | E_IS | E_OOS | degradacion (OOS/IS) |
|---|---:|---:|---:|---:|---:|
| Rotura minimo 20 velas short | 333 | 137 | -0.568 | 0.927 | -1.633 |
| Donchian breakdown 10 short | 333 | 137 | -0.381 | 0.927 | -2.43 |
| Mean reversion z<-2 long | 333 | 137 | 0.148 | -1.15 | -7.789 |

## Detalle por regla

### MA cross 20/50 (golden) long

- cat: Base
- n trades: 4
- acierto%: 25.0
- esperanza R: -0.4
- p-valor: 0.4615
- null p95: 0.7006 | null media: -0.3939 | sims validas: 999
- veredicto: MUESTRA CHICA (no declarar)

### MA cross 50/200 (golden) long

- cat: Base
- n trades: 1
- acierto%: 0.0
- esperanza R: -1.15
- p-valor: 0.9694
- null p95: 1.85 | null media: -0.3726 | sims validas: 687
- veredicto: MUESTRA CHICA (no declarar)

### Precio cruza EMA200 al alza long

- cat: Base
- n trades: 9
- acierto%: 11.1
- esperanza R: -0.799
- p-valor: 0.5829
- null p95: 1.3408 | null media: -0.3737 | sims validas: 736
- veredicto: MUESTRA CHICA (no declarar)

### EMA50 pendiente positiva long

- cat: Base
- n trades: 10
- acierto%: 50.0
- esperanza R: 0.083
- p-valor: 0.1884
- null p95: 0.595 | null media: -0.383 | sims validas: 998
- veredicto: MUESTRA CHICA (no declarar)

### Momentum 5 velas >3% long

- cat: Base
- n trades: 7
- acierto%: 28.6
- esperanza R: -0.293
- p-valor: 0.357
- null p95: 0.4383 | null media: -0.4327 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Momentum 20 velas >5% long

- cat: Base
- n trades: 3
- acierto%: 33.3
- esperanza R: 0.041
- p-valor: 0.212
- null p95: 0.7551 | null media: -0.4497 | sims validas: 981
- veredicto: MUESTRA CHICA (no declarar)

### Rotura maximo 20 velas long

- cat: Base
- n trades: 12
- acierto%: 16.7
- esperanza R: -0.65
- p-valor: 0.647
- null p95: 0.2987 | null media: -0.4362 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Rotura minimo 20 velas short

- cat: Base
- n trades: 24
- acierto%: 50.0
- esperanza R: 0.261
- p-valor: 0.376
- null p95: 0.7082 | null media: 0.118 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### RSI(14) rebote desde <30 long

- cat: Base
- n trades: 8
- acierto%: 37.5
- esperanza R: -0.381
- p-valor: 0.502
- null p95: 0.5463 | null media: -0.2896 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### RSI(14) rechazo desde >70 short

- cat: Base
- n trades: 3
- acierto%: 66.7
- esperanza R: 0.494
- p-valor: 0.4152
- null p95: 1.85 | null media: 0.4473 | sims validas: 961
- veredicto: MUESTRA CHICA (no declarar)

### Mean reversion z<-2 long

- cat: Base
- n trades: 22
- acierto%: 27.3
- esperanza R: -0.389
- p-valor: 0.538
- null p95: 0.2809 | null media: -0.329 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Mean reversion z>+2 short

- cat: Base
- n trades: 12
- acierto%: 50.0
- esperanza R: 0.35
- p-valor: 0.423
- null p95: 1.1841 | null media: 0.2981 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Baja vol (ATR/px<2.5%) + uptrend long

- cat: Base
- n trades: 33
- acierto%: 21.2
- esperanza R: -0.525
- p-valor: 0.604
- null p95: 0.1895 | null media: -0.3928 | sims validas: 1000
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
- acierto%: 25.0
- esperanza R: -0.4
- p-valor: 0.465
- null p95: 0.1565 | null media: -0.4108 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Solo viernes short

- cat: Base
- n trades: 12
- acierto%: 66.7
- esperanza R: 0.426
- p-valor: 0.291
- null p95: 0.8938 | null media: 0.2253 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Donchian breakout 10 long

- cat: Base
- n trades: 31
- acierto%: 22.6
- esperanza R: -0.473
- p-valor: 0.592
- null p95: 0.1834 | null media: -0.3799 | sims validas: 1000
- veredicto: RUIDO

### Donchian breakdown 10 short

- cat: Base
- n trades: 32
- acierto%: 50.0
- esperanza R: 0.135
- p-valor: 0.509
- null p95: 0.6327 | null media: 0.1263 | sims validas: 1000
- veredicto: RUIDO

### Regresion lineal slope>0 R2>0.5 long

- cat: Base
- n trades: 10
- acierto%: 10.0
- esperanza R: -0.85
- p-valor: 0.844
- null p95: 0.3502 | null media: -0.41 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Regresion lineal slope<0 R2>0.5 short

- cat: Base
- n trades: 11
- acierto%: 72.7
- esperanza R: 0.739
- p-valor: 0.111
- null p95: 0.9232 | null media: 0.2157 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Donchian breakout 10 long — stop movil a BE tras +1R

- cat: Gestion de posicion
- n trades: 31
- acierto%: 19.4
- esperanza R: -0.376
- p-valor: 0.384
- null p95: -0.0056 | null media: -0.4615 | sims validas: 1000
- veredicto: RUIDO

### Donchian breakdown 10 short — stop movil a BE tras +1R

- cat: Gestion de posicion
- n trades: 32
- acierto%: 18.8
- esperanza R: -0.259
- p-valor: 0.742
- null p95: 0.3317 | null media: -0.0886 | sims validas: 1000
- veredicto: RUIDO

### Donchian breakout 10 long — cierre mitad en +1R, dejar correr

- cat: Gestion de posicion
- n trades: 31
- acierto%: 38.7
- esperanza R: -0.141
- p-valor: 0.236
- null p95: 0.1713 | null media: -0.3626 | sims validas: 1000
- veredicto: RUIDO

### Donchian breakdown 10 short — cierre mitad en +1R, dejar correr

- cat: Gestion de posicion
- n trades: 32
- acierto%: 53.1
- esperanza R: -0.147
- p-valor: 0.796
- null p95: 0.744 | null media: 0.1299 | sims validas: 1000
- veredicto: RUIDO

### Donchian breakout 10 long — 3 objetivos escalonados 1R/2R/3R

- cat: Gestion de posicion
- n trades: 31
- acierto%: 38.7
- esperanza R: -0.29
- p-valor: 0.441
- null p95: 0.1729 | null media: -0.3386 | sims validas: 1000
- veredicto: RUIDO

### Donchian breakdown 10 short — 3 objetivos escalonados 1R/2R/3R

- cat: Gestion de posicion
- n trades: 32
- acierto%: 53.1
- esperanza R: -0.063
- p-valor: 0.717
- null p95: 0.5699 | null media: 0.0955 | sims validas: 1000
- veredicto: RUIDO

### Momentum 5 velas >3% long (regimen EMA200)

- cat: Regimen
- n trades: 0
- acierto%: 0.0
- esperanza R: None
- p-valor: 1.0
- null p95: 0.9896 | null media: -0.4718 | sims validas: 615
- veredicto: MUESTRA CHICA (no declarar)

### Momentum 20 velas >5% long (regimen EMA200)

- cat: Regimen
- n trades: 0
- acierto%: 0.0
- esperanza R: None
- p-valor: 1.0
- null p95: 1.3051 | null media: -0.4717 | sims validas: 581
- veredicto: MUESTRA CHICA (no declarar)

### Rotura maximo 20 velas long (regimen EMA200)

- cat: Regimen
- n trades: 3
- acierto%: 0.0
- esperanza R: -1.15
- p-valor: 0.9726
- null p95: 0.4907 | null media: -0.6079 | sims validas: 731
- veredicto: MUESTRA CHICA (no declarar)

### Donchian breakout 10 long (regimen EMA200)

- cat: Regimen
- n trades: 5
- acierto%: 0.0
- esperanza R: -1.15
- p-valor: 0.916
- null p95: 0.4753 | null media: -0.5951 | sims validas: 738
- veredicto: MUESTRA CHICA (no declarar)

### Rotura minimo 20 velas short (regimen EMA200)

- cat: Regimen
- n trades: 18
- acierto%: 55.6
- esperanza R: 0.425
- p-valor: 0.2352
- null p95: 0.8426 | null media: 0.0635 | sims validas: 999
- veredicto: MUESTRA CHICA (no declarar)

### Donchian breakdown 10 short (regimen EMA200)

- cat: Regimen
- n trades: 20
- acierto%: 55.0
- esperanza R: 0.374
- p-valor: 0.2563
- null p95: 0.7561 | null media: 0.0732 | sims validas: 999
- veredicto: MUESTRA CHICA (no declarar)

### Momentum 5 velas >3% long (MTF: entrada 4h solo si 1d a favor)

- cat: Multi-timeframe
- n trades: 4
- acierto%: 25.0
- esperanza R: -0.4
- p-valor: 0.4372
- null p95: 0.5452 | null media: -0.4537 | sims validas: 995
- veredicto: MUESTRA CHICA (no declarar)

### Momentum 20 velas >5% long (MTF: entrada 4h solo si 1d a favor)

- cat: Multi-timeframe
- n trades: 2
- acierto%: 50.0
- esperanza R: 0.35
- p-valor: 0.1582
- null p95: 0.85 | null media: -0.4736 | sims validas: 948
- veredicto: MUESTRA CHICA (no declarar)

### Rotura maximo 20 velas long (MTF: entrada 4h solo si 1d a favor)

- cat: Multi-timeframe
- n trades: 11
- acierto%: 18.2
- esperanza R: -0.605
- p-valor: 0.578
- null p95: 0.3745 | null media: -0.469 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Donchian breakout 10 long (MTF: entrada 4h solo si 1d a favor)

- cat: Multi-timeframe
- n trades: 28
- acierto%: 21.4
- esperanza R: -0.507
- p-valor: 0.595
- null p95: 0.2687 | null media: -0.4033 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Rotura minimo 20 velas short (MTF: entrada 4h solo si 1d a favor)

- cat: Multi-timeframe
- n trades: 13
- acierto%: 69.2
- esperanza R: 0.927
- p-valor: 0.0762
- null p95: 1.0215 | null media: -0.0508 | sims validas: 998
- veredicto: MUESTRA CHICA (no declarar)

### Donchian breakdown 10 short (MTF: entrada 4h solo si 1d a favor)

- cat: Multi-timeframe
- n trades: 14
- acierto%: 64.3
- esperanza R: 0.779
- p-valor: 0.111
- null p95: 0.9885 | null media: 0.0032 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)
