# BANCO DE CANDIDATOS BTCUSDT — filtro null sintetico (ampliado)

PAPER_ONLY. Par: BTCUSDT | TF: 1d | Velas: 500 (2025-07-13 -> 2026-11-24)

Costos: comision 0.10% + slippage 0.05% por pasada. Stop 2.0% / Target 4.0% (2:1) base. Horizonte 30 barras. Muestra minima 30 trades.

Null sintetico: 1000 sims, block bootstrap, percentil 95. Seed 42.

Categorias: Base (20) + Gestion de posicion (6) + Regimen EMA200 (6).

| regla | cat | n trades | acierto% | esperanza R | p-valor | veredicto |
|---|---|---:|---:|---:|---:|---|
| MA cross 20/50 (golden) long | Base | 5 | 40.0 | 0.05 | 0.327 | MUESTRA CHICA (no declarar) |
| MA cross 50/200 (golden) long | Base | 1 | 0.0 | -1.15 | 1.0 | MUESTRA CHICA (no declarar) |
| Precio cruza EMA200 al alza long | Base | 2 | 50.0 | 0.35 | 0.2994 | MUESTRA CHICA (no declarar) |
| EMA50 pendiente positiva long | Base | 9 | 33.3 | -0.15 | 0.493 | MUESTRA CHICA (no declarar) |
| Momentum 5 velas >3% long | Base | 37 | 27.0 | -0.339 | 0.684 | RUIDO |
| Momentum 20 velas >5% long | Base | 19 | 26.3 | -0.361 | 0.697 | MUESTRA CHICA (no declarar) |
| Rotura maximo 20 velas long | Base | 21 | 23.8 | -0.436 | 0.749 | MUESTRA CHICA (no declarar) |
| Rotura minimo 20 velas short | Base | 28 | 46.4 | 0.243 | 0.215 | MUESTRA CHICA (no declarar) |
| RSI(14) rebote desde <30 long | Base | 6 | 33.3 | -0.15 | 0.3243 | MUESTRA CHICA (no declarar) |
| RSI(14) rechazo desde >70 short | Base | 6 | 33.3 | -0.15 | 0.7282 | MUESTRA CHICA (no declarar) |
| Mean reversion z<-2 long | Base | 14 | 14.3 | -0.721 | 0.929 | MUESTRA CHICA (no declarar) |
| Mean reversion z>+2 short | Base | 11 | 45.5 | 0.214 | 0.458 | MUESTRA CHICA (no declarar) |
| Baja vol (ATR/px<2.5%) + uptrend long | Base | 18 | 33.3 | -0.15 | 0.475 | MUESTRA CHICA (no declarar) |
| Alta vol (ATR/px>4%) + downtrend short | Base | 12 | 16.7 | -0.65 | 0.4529 | MUESTRA CHICA (no declarar) |
| Solo lunes long | Base | 72 | 26.4 | -0.358 | 0.875 | RUIDO |
| Solo viernes short | Base | 71 | 31.0 | -0.22 | 0.947 | RUIDO |
| Donchian breakout 10 long | Base | 33 | 21.2 | -0.514 | 0.882 | RUIDO |
| Donchian breakdown 10 short | Base | 41 | 39.0 | 0.021 | 0.552 | RUIDO |
| Regresion lineal slope>0 R2>0.5 long | Base | 9 | 11.1 | -0.817 | 0.929 | MUESTRA CHICA (no declarar) |
| Regresion lineal slope<0 R2>0.5 short | Base | 10 | 20.0 | -0.55 | 0.939 | MUESTRA CHICA (no declarar) |
| Donchian breakout 10 long — stop movil a BE tras +1R | Gestion de posicion | 33 | 3.0 | -0.635 | 0.882 | RUIDO |
| Donchian breakdown 10 short — stop movil a BE tras +1R | Gestion de posicion | 41 | 0.0 | -0.516 | 0.734 | RUIDO |
| Donchian breakout 10 long — cierre mitad en +1R, dejar correr | Gestion de posicion | 33 | 45.5 | -0.257 | 0.575 | RUIDO |
| Donchian breakdown 10 short — cierre mitad en +1R, dejar correr | Gestion de posicion | 41 | 51.2 | 0.25 | 0.499 | RUIDO |
| Donchian breakout 10 long — 3 objetivos escalonados 1R/2R/3R | Gestion de posicion | 33 | 45.5 | -0.322 | 0.789 | RUIDO |
| Donchian breakdown 10 short — 3 objetivos escalonados 1R/2R/3R | Gestion de posicion | 41 | 51.2 | 0.013 | 0.55 | RUIDO |
| Momentum 5 velas >3% long (regimen EMA200) | Regimen | 7 | 14.3 | -0.721 | 0.6972 | MUESTRA CHICA (no declarar) |
| Momentum 20 velas >5% long (regimen EMA200) | Regimen | 2 | 0.0 | -1.15 | 0.7803 | MUESTRA CHICA (no declarar) |
| Rotura maximo 20 velas long (regimen EMA200) | Regimen | 3 | 33.3 | -0.15 | 0.4227 | MUESTRA CHICA (no declarar) |
| Donchian breakout 10 long (regimen EMA200) | Regimen | 4 | 50.0 | 0.35 | 0.124 | MUESTRA CHICA (no declarar) |
| Rotura minimo 20 velas short (regimen EMA200) | Regimen | 16 | 68.8 | 0.913 | 0.005 | MUESTRA CHICA (no declarar) |
| Donchian breakdown 10 short (regimen EMA200) | Regimen | 22 | 63.6 | 0.759 | 0.007 | MUESTRA CHICA (no declarar) |

**Pasan el null: 0 / 32**

**NINGUNA regla supera el null sintetico.**

Muestra chica (<30): 21 reglas.

## Gestion de posicion — comparacion contra base

| variante | n | acierto% | esperanza R | p-valor | veredicto |
|---|---:|---:|---:|---:|---|
| Donchian breakout 10 long — stop movil a BE tras +1R | 33 | 3.0 | -0.635 | 0.882 | RUIDO |
| Donchian breakdown 10 short — stop movil a BE tras +1R | 41 | 0.0 | -0.516 | 0.734 | RUIDO |
| Donchian breakout 10 long — cierre mitad en +1R, dejar correr | 33 | 45.5 | -0.257 | 0.575 | RUIDO |
| Donchian breakdown 10 short — cierre mitad en +1R, dejar correr | 41 | 51.2 | 0.25 | 0.499 | RUIDO |
| Donchian breakout 10 long — 3 objetivos escalonados 1R/2R/3R | 33 | 45.5 | -0.322 | 0.789 | RUIDO |
| Donchian breakdown 10 short — 3 objetivos escalonados 1R/2R/3R | 41 | 51.2 | 0.013 | 0.55 | RUIDO |

## Regimen (EMA200) — comparacion

| regla | n | acierto% | esperanza R | p-valor | veredicto |
|---|---:|---:|---:|---:|---|
| Momentum 5 velas >3% long (regimen EMA200) | 7 | 14.3 | -0.721 | 0.6972 | MUESTRA CHICA (no declarar) |
| Momentum 20 velas >5% long (regimen EMA200) | 2 | 0.0 | -1.15 | 0.7803 | MUESTRA CHICA (no declarar) |
| Rotura maximo 20 velas long (regimen EMA200) | 3 | 33.3 | -0.15 | 0.4227 | MUESTRA CHICA (no declarar) |
| Donchian breakout 10 long (regimen EMA200) | 4 | 50.0 | 0.35 | 0.124 | MUESTRA CHICA (no declarar) |
| Rotura minimo 20 velas short (regimen EMA200) | 16 | 68.8 | 0.913 | 0.005 | MUESTRA CHICA (no declarar) |
| Donchian breakdown 10 short (regimen EMA200) | 22 | 63.6 | 0.759 | 0.007 | MUESTRA CHICA (no declarar) |

## Walk-forward (2/3 train, 1/3 test) — top 3 reglas base

| regla | n_train | n_test | E_IS | E_OOS | degradacion (OOS/IS) |
|---|---:|---:|---:|---:|---:|
| Rotura minimo 20 velas short | 333 | 137 | 0.271 | 0.183 | 0.676 |
| Baja vol (ATR/px<2.5%) + uptrend long | 333 | 137 | 0.35 | -0.65 | -1.857 |
| Donchian breakdown 10 short | 333 | 137 | -0.05 | 0.05 | -1.0 |

## Detalle por regla

### MA cross 20/50 (golden) long

- cat: Base
- n trades: 5
- acierto%: 40.0
- esperanza R: 0.05
- p-valor: 0.327
- null p95: 1.1 | null media: -0.13 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### MA cross 50/200 (golden) long

- cat: Base
- n trades: 1
- acierto%: 0.0
- esperanza R: -1.15
- p-valor: 1.0
- null p95: 1.85 | null media: -0.1169 | sims validas: 715
- veredicto: MUESTRA CHICA (no declarar)

### Precio cruza EMA200 al alza long

- cat: Base
- n trades: 2
- acierto%: 50.0
- esperanza R: 0.35
- p-valor: 0.2994
- null p95: 1.85 | null media: -0.1416 | sims validas: 718
- veredicto: MUESTRA CHICA (no declarar)

### EMA50 pendiente positiva long

- cat: Base
- n trades: 9
- acierto%: 33.3
- esperanza R: -0.15
- p-valor: 0.493
- null p95: 0.725 | null media: -0.1384 | sims validas: 998
- veredicto: MUESTRA CHICA (no declarar)

### Momentum 5 velas >3% long

- cat: Base
- n trades: 37
- acierto%: 27.0
- esperanza R: -0.339
- p-valor: 0.684
- null p95: 0.2048 | null media: -0.2226 | sims validas: 1000
- veredicto: RUIDO

### Momentum 20 velas >5% long

- cat: Base
- n trades: 19
- acierto%: 26.3
- esperanza R: -0.361
- p-valor: 0.697
- null p95: 0.4654 | null media: -0.1592 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Rotura maximo 20 velas long

- cat: Base
- n trades: 21
- acierto%: 23.8
- esperanza R: -0.436
- p-valor: 0.749
- null p95: 0.41 | null media: -0.1977 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Rotura minimo 20 velas short

- cat: Base
- n trades: 28
- acierto%: 46.4
- esperanza R: 0.243
- p-valor: 0.215
- null p95: 0.4825 | null media: 0.0337 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### RSI(14) rebote desde <30 long

- cat: Base
- n trades: 6
- acierto%: 33.3
- esperanza R: -0.15
- p-valor: 0.3243
- null p95: 0.5643 | null media: -0.2573 | sims validas: 999
- veredicto: MUESTRA CHICA (no declarar)

### RSI(14) rechazo desde >70 short

- cat: Base
- n trades: 6
- acierto%: 33.3
- esperanza R: -0.15
- p-valor: 0.7282
- null p95: 1.85 | null media: 0.3694 | sims validas: 953
- veredicto: MUESTRA CHICA (no declarar)

### Mean reversion z<-2 long

- cat: Base
- n trades: 14
- acierto%: 14.3
- esperanza R: -0.721
- p-valor: 0.929
- null p95: 0.5008 | null media: -0.1638 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Mean reversion z>+2 short

- cat: Base
- n trades: 11
- acierto%: 45.5
- esperanza R: 0.214
- p-valor: 0.458
- null p95: 0.9929 | null media: 0.202 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Baja vol (ATR/px<2.5%) + uptrend long

- cat: Base
- n trades: 18
- acierto%: 33.3
- esperanza R: -0.15
- p-valor: 0.475
- null p95: 0.35 | null media: -0.1653 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Alta vol (ATR/px>4%) + downtrend short

- cat: Base
- n trades: 12
- acierto%: 16.7
- esperanza R: -0.65
- p-valor: 0.4529
- null p95: 1.85 | null media: -0.2805 | sims validas: 658
- veredicto: MUESTRA CHICA (no declarar)

### Solo lunes long

- cat: Base
- n trades: 72
- acierto%: 26.4
- esperanza R: -0.358
- p-valor: 0.875
- null p95: 0.1513 | null media: -0.1499 | sims validas: 1000
- veredicto: RUIDO

### Solo viernes short

- cat: Base
- n trades: 71
- acierto%: 31.0
- esperanza R: -0.22
- p-valor: 0.947
- null p95: 0.4556 | null media: 0.1042 | sims validas: 1000
- veredicto: RUIDO

### Donchian breakout 10 long

- cat: Base
- n trades: 33
- acierto%: 21.2
- esperanza R: -0.514
- p-valor: 0.882
- null p95: 0.3047 | null media: -0.1739 | sims validas: 1000
- veredicto: RUIDO

### Donchian breakdown 10 short

- cat: Base
- n trades: 41
- acierto%: 39.0
- esperanza R: 0.021
- p-valor: 0.552
- null p95: 0.4058 | null media: 0.0408 | sims validas: 1000
- veredicto: RUIDO

### Regresion lineal slope>0 R2>0.5 long

- cat: Base
- n trades: 9
- acierto%: 11.1
- esperanza R: -0.817
- p-valor: 0.929
- null p95: 0.725 | null media: -0.1527 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Regresion lineal slope<0 R2>0.5 short

- cat: Base
- n trades: 10
- acierto%: 20.0
- esperanza R: -0.55
- p-valor: 0.939
- null p95: 0.95 | null media: 0.1592 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Donchian breakout 10 long — stop movil a BE tras +1R

- cat: Gestion de posicion
- n trades: 33
- acierto%: 3.0
- esperanza R: -0.635
- p-valor: 0.882
- null p95: -0.0339 | null media: -0.3836 | sims validas: 1000
- veredicto: RUIDO

### Donchian breakdown 10 short — stop movil a BE tras +1R

- cat: Gestion de posicion
- n trades: 41
- acierto%: 0.0
- esperanza R: -0.516
- p-valor: 0.734
- null p95: -0.1865 | null media: -0.4238 | sims validas: 1000
- veredicto: RUIDO

### Donchian breakout 10 long — cierre mitad en +1R, dejar correr

- cat: Gestion de posicion
- n trades: 33
- acierto%: 45.5
- esperanza R: -0.257
- p-valor: 0.575
- null p95: 0.6706 | null media: -0.1032 | sims validas: 1000
- veredicto: RUIDO

### Donchian breakdown 10 short — cierre mitad en +1R, dejar correr

- cat: Gestion de posicion
- n trades: 41
- acierto%: 51.2
- esperanza R: 0.25
- p-valor: 0.499
- null p95: 1.1697 | null media: 0.3168 | sims validas: 1000
- veredicto: RUIDO

### Donchian breakout 10 long — 3 objetivos escalonados 1R/2R/3R

- cat: Gestion de posicion
- n trades: 33
- acierto%: 45.5
- esperanza R: -0.322
- p-valor: 0.789
- null p95: 0.2875 | null media: -0.1252 | sims validas: 1000
- veredicto: RUIDO

### Donchian breakdown 10 short — 3 objetivos escalonados 1R/2R/3R

- cat: Gestion de posicion
- n trades: 41
- acierto%: 51.2
- esperanza R: 0.013
- p-valor: 0.55
- null p95: 0.3819 | null media: 0.0378 | sims validas: 1000
- veredicto: RUIDO

### Momentum 5 velas >3% long (regimen EMA200)

- cat: Regimen
- n trades: 7
- acierto%: 14.3
- esperanza R: -0.721
- p-valor: 0.6972
- null p95: 0.7667 | null media: -0.3304 | sims validas: 687
- veredicto: MUESTRA CHICA (no declarar)

### Momentum 20 velas >5% long (regimen EMA200)

- cat: Regimen
- n trades: 2
- acierto%: 0.0
- esperanza R: -1.15
- p-valor: 0.7803
- null p95: 1.25 | null media: -0.1838 | sims validas: 610
- veredicto: MUESTRA CHICA (no declarar)

### Rotura maximo 20 velas long (regimen EMA200)

- cat: Regimen
- n trades: 3
- acierto%: 33.3
- esperanza R: -0.15
- p-valor: 0.4227
- null p95: 0.6288 | null media: -0.3606 | sims validas: 724
- veredicto: MUESTRA CHICA (no declarar)

### Donchian breakout 10 long (regimen EMA200)

- cat: Regimen
- n trades: 4
- acierto%: 50.0
- esperanza R: 0.35
- p-valor: 0.124
- null p95: 0.5643 | null media: -0.361 | sims validas: 734
- veredicto: MUESTRA CHICA (no declarar)

### Rotura minimo 20 velas short (regimen EMA200)

- cat: Regimen
- n trades: 16
- acierto%: 68.8
- esperanza R: 0.913
- p-valor: 0.005
- null p95: 0.5778 | null media: 0.0044 | sims validas: 999
- veredicto: MUESTRA CHICA (no declarar)

### Donchian breakdown 10 short (regimen EMA200)

- cat: Regimen
- n trades: 22
- acierto%: 63.6
- esperanza R: 0.759
- p-valor: 0.007
- null p95: 0.5167 | null media: 0.0146 | sims validas: 999
- veredicto: MUESTRA CHICA (no declarar)
