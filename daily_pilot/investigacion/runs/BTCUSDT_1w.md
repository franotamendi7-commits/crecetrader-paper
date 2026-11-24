# BANCO DE CANDIDATOS BTCUSDT — filtro null sintetico (ampliado)

PAPER_ONLY. Par: BTCUSDT | TF: 1w | Velas: 485 (2017-08-14 -> 2026-11-23)

Costos: comision 0.10% + slippage 0.05% por pasada. Stop 2.0% / Target 4.0% (2:1) base. Horizonte 30 barras. Muestra minima 30 trades.

Null sintetico: 1000 sims, block bootstrap, percentil 95. Seed 42.

Categorias: Base (20) + Gestion de posicion (6) + Regimen EMA200 (6).

| regla | cat | n trades | acierto% | esperanza R | p-valor | veredicto |
|---|---|---:|---:|---:|---:|---|
| MA cross 20/50 (golden) long | Base | 3 | 33.3 | -0.15 | 0.851 | MUESTRA CHICA (no declarar) |
| MA cross 50/200 (golden) long | Base | 2 | 0.0 | -1.15 | 1.0 | MUESTRA CHICA (no declarar) |
| Precio cruza EMA200 al alza long | Base | 6 | 33.3 | -0.15 | 0.8532 | MUESTRA CHICA (no declarar) |
| EMA50 pendiente positiva long | Base | 8 | 50.0 | 0.35 | 0.715 | MUESTRA CHICA (no declarar) |
| Momentum 5 velas >3% long | Base | 43 | 32.6 | -0.173 | 1.0 | RUIDO |
| Momentum 20 velas >5% long | Base | 18 | 27.8 | -0.317 | 0.999 | MUESTRA CHICA (no declarar) |
| Rotura maximo 20 velas long | Base | 37 | 21.6 | -0.501 | 1.0 | RUIDO |
| Rotura minimo 20 velas short | Base | 14 | 42.9 | 0.136 | 0.216 | MUESTRA CHICA (no declarar) |
| RSI(14) rebote desde <30 long | Base | 3 | 0.0 | -1.15 | 0.9913 | MUESTRA CHICA (no declarar) |
| RSI(14) rechazo desde >70 short | Base | 11 | 9.1 | -0.877 | 0.993 | MUESTRA CHICA (no declarar) |
| Mean reversion z<-2 long | Base | 8 | 0.0 | -1.15 | 1.0 | MUESTRA CHICA (no declarar) |
| Mean reversion z>+2 short | Base | 15 | 0.0 | -1.15 | 0.998 | MUESTRA CHICA (no declarar) |
| Baja vol (ATR/px<2.5%) + uptrend long | Base | 0 | 0.0 | NA | 1.0 | MUESTRA CHICA (no declarar) |
| Alta vol (ATR/px>4%) + downtrend short | Base | 21 | 33.3 | -0.15 | 0.713 | MUESTRA CHICA (no declarar) |
| Solo lunes long | Base | 0 | 0.0 | NA | NA | MUESTRA CHICA (no declarar) |
| Solo viernes short | Base | 0 | 0.0 | NA | NA | MUESTRA CHICA (no declarar) |
| Donchian breakout 10 long | Base | 59 | 18.6 | -0.591 | 1.0 | RUIDO |
| Donchian breakdown 10 short | Base | 24 | 37.5 | -0.025 | 0.417 | MUESTRA CHICA (no declarar) |
| Regresion lineal slope>0 R2>0.5 long | Base | 10 | 20.0 | -0.55 | 0.981 | MUESTRA CHICA (no declarar) |
| Regresion lineal slope<0 R2>0.5 short | Base | 11 | 18.2 | -0.605 | 0.886 | MUESTRA CHICA (no declarar) |
| Donchian breakout 10 long — stop movil a BE tras +1R | Gestion de posicion | 59 | 0.0 | -0.303 | 0.084 | RUIDO |
| Donchian breakdown 10 short — stop movil a BE tras +1R | Gestion de posicion | 24 | 0.0 | -0.192 | 0.0 | MUESTRA CHICA (no declarar) |
| Donchian breakout 10 long — cierre mitad en +1R, dejar correr | Gestion de posicion | 59 | 18.6 | -0.724 | 1.0 | RUIDO |
| Donchian breakdown 10 short — cierre mitad en +1R, dejar correr | Gestion de posicion | 24 | 37.5 | 0.596 | 0.26 | MUESTRA CHICA (no declarar) |
| Donchian breakout 10 long — 3 objetivos escalonados 1R/2R/3R | Gestion de posicion | 59 | 18.6 | -0.642 | 1.0 | RUIDO |
| Donchian breakdown 10 short — 3 objetivos escalonados 1R/2R/3R | Gestion de posicion | 24 | 37.5 | -0.025 | 0.43 | MUESTRA CHICA (no declarar) |
| Momentum 5 velas >3% long (regimen EMA200) | Regimen | 23 | 34.8 | -0.107 | 0.9556 | MUESTRA CHICA (no declarar) |
| Momentum 20 velas >5% long (regimen EMA200) | Regimen | 10 | 40.0 | 0.05 | 0.831 | MUESTRA CHICA (no declarar) |
| Rotura maximo 20 velas long (regimen EMA200) | Regimen | 20 | 25.0 | -0.4 | 0.9829 | MUESTRA CHICA (no declarar) |
| Donchian breakout 10 long (regimen EMA200) | Regimen | 32 | 18.8 | -0.587 | 0.994 | RUIDO |
| Rotura minimo 20 velas short (regimen EMA200) | Regimen | 2 | 0.0 | -1.15 | 0.9891 | MUESTRA CHICA (no declarar) |
| Donchian breakdown 10 short (regimen EMA200) | Regimen | 5 | 20.0 | -0.55 | 0.7392 | MUESTRA CHICA (no declarar) |

**Pasan el null: 0 / 32**

**NINGUNA regla supera el null sintetico.**

Muestra chica (<30): 25 reglas.

## Gestion de posicion — comparacion contra base

| variante | n | acierto% | esperanza R | p-valor | veredicto |
|---|---:|---:|---:|---:|---|
| Donchian breakout 10 long — stop movil a BE tras +1R | 59 | 0.0 | -0.303 | 0.084 | RUIDO |
| Donchian breakdown 10 short — stop movil a BE tras +1R | 24 | 0.0 | -0.192 | 0.0 | MUESTRA CHICA (no declarar) |
| Donchian breakout 10 long — cierre mitad en +1R, dejar correr | 59 | 18.6 | -0.724 | 1.0 | RUIDO |
| Donchian breakdown 10 short — cierre mitad en +1R, dejar correr | 24 | 37.5 | 0.596 | 0.26 | MUESTRA CHICA (no declarar) |
| Donchian breakout 10 long — 3 objetivos escalonados 1R/2R/3R | 59 | 18.6 | -0.642 | 1.0 | RUIDO |
| Donchian breakdown 10 short — 3 objetivos escalonados 1R/2R/3R | 24 | 37.5 | -0.025 | 0.43 | MUESTRA CHICA (no declarar) |

## Regimen (EMA200) — comparacion

| regla | n | acierto% | esperanza R | p-valor | veredicto |
|---|---:|---:|---:|---:|---|
| Momentum 5 velas >3% long (regimen EMA200) | 23 | 34.8 | -0.107 | 0.9556 | MUESTRA CHICA (no declarar) |
| Momentum 20 velas >5% long (regimen EMA200) | 10 | 40.0 | 0.05 | 0.831 | MUESTRA CHICA (no declarar) |
| Rotura maximo 20 velas long (regimen EMA200) | 20 | 25.0 | -0.4 | 0.9829 | MUESTRA CHICA (no declarar) |
| Donchian breakout 10 long (regimen EMA200) | 32 | 18.8 | -0.587 | 0.994 | RUIDO |
| Rotura minimo 20 velas short (regimen EMA200) | 2 | 0.0 | -1.15 | 0.9891 | MUESTRA CHICA (no declarar) |
| Donchian breakdown 10 short (regimen EMA200) | 5 | 20.0 | -0.55 | 0.7392 | MUESTRA CHICA (no declarar) |

## Walk-forward (2/3 train, 1/3 test) — top 3 reglas base

| regla | n_train | n_test | E_IS | E_OOS | degradacion (OOS/IS) |
|---|---:|---:|---:|---:|---:|
| Donchian breakdown 10 short | 323 | 132 | -0.15 | 0.35 | -2.333 |
| Alta vol (ATR/px>4%) + downtrend short | 323 | 132 | -0.227 | 0.65 | -2.864 |
| Mean reversion z>+2 short | 323 | 132 | -1.15 | -1.15 | 1.0 |

## Detalle por regla

### MA cross 20/50 (golden) long

- cat: Base
- n trades: 3
- acierto%: 33.3
- esperanza R: -0.15
- p-valor: 0.851
- null p95: 1.85 | null media: 0.4659 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### MA cross 50/200 (golden) long

- cat: Base
- n trades: 2
- acierto%: 0.0
- esperanza R: -1.15
- p-valor: 1.0
- null p95: 1.85 | null media: 0.3302 | sims validas: 995
- veredicto: MUESTRA CHICA (no declarar)

### Precio cruza EMA200 al alza long

- cat: Base
- n trades: 6
- acierto%: 33.3
- esperanza R: -0.15
- p-valor: 0.8532
- null p95: 1.85 | null media: 0.689 | sims validas: 913
- veredicto: MUESTRA CHICA (no declarar)

### EMA50 pendiente positiva long

- cat: Base
- n trades: 8
- acierto%: 50.0
- esperanza R: 0.35
- p-valor: 0.715
- null p95: 1.35 | null media: 0.5516 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Momentum 5 velas >3% long

- cat: Base
- n trades: 43
- acierto%: 32.6
- esperanza R: -0.173
- p-valor: 1.0
- null p95: 0.9167 | null media: 0.5565 | sims validas: 1000
- veredicto: RUIDO

### Momentum 20 velas >5% long

- cat: Base
- n trades: 18
- acierto%: 27.8
- esperanza R: -0.317
- p-valor: 0.999
- null p95: 1.1 | null media: 0.5457 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Rotura maximo 20 velas long

- cat: Base
- n trades: 37
- acierto%: 21.6
- esperanza R: -0.501
- p-valor: 1.0
- null p95: 0.8604 | null media: 0.5479 | sims validas: 1000
- veredicto: RUIDO

### Rotura minimo 20 velas short

- cat: Base
- n trades: 14
- acierto%: 42.9
- esperanza R: 0.136
- p-valor: 0.216
- null p95: 0.3741 | null media: -0.1189 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### RSI(14) rebote desde <30 long

- cat: Base
- n trades: 3
- acierto%: 0.0
- esperanza R: -1.15
- p-valor: 0.9913
- null p95: 1.85 | null media: 0.4863 | sims validas: 918
- veredicto: MUESTRA CHICA (no declarar)

### RSI(14) rechazo desde >70 short

- cat: Base
- n trades: 11
- acierto%: 9.1
- esperanza R: -0.877
- p-valor: 0.993
- null p95: 0.725 | null media: 0.0199 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Mean reversion z<-2 long

- cat: Base
- n trades: 8
- acierto%: 0.0
- esperanza R: -1.15
- p-valor: 1.0
- null p95: 1.35 | null media: 0.4793 | sims validas: 999
- veredicto: MUESTRA CHICA (no declarar)

### Mean reversion z>+2 short

- cat: Base
- n trades: 15
- acierto%: 0.0
- esperanza R: -1.15
- p-valor: 0.998
- null p95: 0.1625 | null media: -0.3264 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Baja vol (ATR/px<2.5%) + uptrend long

- cat: Base
- n trades: 0
- acierto%: 0.0
- esperanza R: None
- p-valor: 1.0
- null p95: 1.85 | null media: 0.4214 | sims validas: 126
- veredicto: MUESTRA CHICA (no declarar)

### Alta vol (ATR/px>4%) + downtrend short

- cat: Base
- n trades: 21
- acierto%: 33.3
- esperanza R: -0.15
- p-valor: 0.713
- null p95: 0.4954 | null media: 0.0097 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Solo lunes long

- cat: Base
- n trades: 0
- acierto%: 0.0
- esperanza R: None
- p-valor: None
- null p95: None | null media: None | sims validas: 0
- veredicto: MUESTRA CHICA (no declarar)

### Solo viernes short

- cat: Base
- n trades: 0
- acierto%: 0.0
- esperanza R: None
- p-valor: None
- null p95: None | null media: None | sims validas: 0
- veredicto: MUESTRA CHICA (no declarar)

### Donchian breakout 10 long

- cat: Base
- n trades: 59
- acierto%: 18.6
- esperanza R: -0.591
- p-valor: 1.0
- null p95: 0.8295 | null media: 0.5539 | sims validas: 1000
- veredicto: RUIDO

### Donchian breakdown 10 short

- cat: Base
- n trades: 24
- acierto%: 37.5
- esperanza R: -0.025
- p-valor: 0.417
- null p95: 0.3106 | null media: -0.08 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Regresion lineal slope>0 R2>0.5 long

- cat: Base
- n trades: 10
- acierto%: 20.0
- esperanza R: -0.55
- p-valor: 0.981
- null p95: 1.1833 | null media: 0.4613 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Regresion lineal slope<0 R2>0.5 short

- cat: Base
- n trades: 11
- acierto%: 18.2
- esperanza R: -0.605
- p-valor: 0.886
- null p95: 0.95 | null media: 0.0419 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Donchian breakout 10 long — stop movil a BE tras +1R

- cat: Gestion de posicion
- n trades: 59
- acierto%: 0.0
- esperanza R: -0.303
- p-valor: 0.084
- null p95: -0.2769 | null media: -0.4225 | sims validas: 1000
- veredicto: RUIDO

### Donchian breakdown 10 short — stop movil a BE tras +1R

- cat: Gestion de posicion
- n trades: 24
- acierto%: 0.0
- esperanza R: -0.192
- p-valor: 0.0
- null p95: -0.5059 | null media: -0.6905 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Donchian breakout 10 long — cierre mitad en +1R, dejar correr

- cat: Gestion de posicion
- n trades: 59
- acierto%: 18.6
- esperanza R: -0.724
- p-valor: 1.0
- null p95: 13.8076 | null media: 5.8392 | sims validas: 1000
- veredicto: RUIDO

### Donchian breakdown 10 short — cierre mitad en +1R, dejar correr

- cat: Gestion de posicion
- n trades: 24
- acierto%: 37.5
- esperanza R: 0.596
- p-valor: 0.26
- null p95: 1.7283 | null media: 0.2324 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Donchian breakout 10 long — 3 objetivos escalonados 1R/2R/3R

- cat: Gestion de posicion
- n trades: 59
- acierto%: 18.6
- esperanza R: -0.642
- p-valor: 1.0
- null p95: 0.8219 | null media: 0.5449 | sims validas: 1000
- veredicto: RUIDO

### Donchian breakdown 10 short — 3 objetivos escalonados 1R/2R/3R

- cat: Gestion de posicion
- n trades: 24
- acierto%: 37.5
- esperanza R: -0.025
- p-valor: 0.43
- null p95: 0.3095 | null media: -0.0712 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Momentum 5 velas >3% long (regimen EMA200)

- cat: Regimen
- n trades: 23
- acierto%: 34.8
- esperanza R: -0.107
- p-valor: 0.9556
- null p95: 1.1326 | null media: 0.5618 | sims validas: 992
- veredicto: MUESTRA CHICA (no declarar)

### Momentum 20 velas >5% long (regimen EMA200)

- cat: Regimen
- n trades: 10
- acierto%: 40.0
- esperanza R: 0.05
- p-valor: 0.831
- null p95: 1.475 | null media: 0.5274 | sims validas: 982
- veredicto: MUESTRA CHICA (no declarar)

### Rotura maximo 20 velas long (regimen EMA200)

- cat: Regimen
- n trades: 20
- acierto%: 25.0
- esperanza R: -0.4
- p-valor: 0.9829
- null p95: 0.9235 | null media: 0.5076 | sims validas: 997
- veredicto: MUESTRA CHICA (no declarar)

### Donchian breakout 10 long (regimen EMA200)

- cat: Regimen
- n trades: 32
- acierto%: 18.8
- esperanza R: -0.587
- p-valor: 0.994
- null p95: 0.9059 | null media: 0.5142 | sims validas: 997
- veredicto: RUIDO

### Rotura minimo 20 velas short (regimen EMA200)

- cat: Regimen
- n trades: 2
- acierto%: 0.0
- esperanza R: -1.15
- p-valor: 0.9891
- null p95: 0.5329 | null media: -0.2699 | sims validas: 921
- veredicto: MUESTRA CHICA (no declarar)

### Donchian breakdown 10 short (regimen EMA200)

- cat: Regimen
- n trades: 5
- acierto%: 20.0
- esperanza R: -0.55
- p-valor: 0.7392
- null p95: 0.528 | null media: -0.2482 | sims validas: 924
- veredicto: MUESTRA CHICA (no declarar)
