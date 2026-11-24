# BANCO DE CANDIDATOS ETHUSDT — filtro null sintetico (ampliado)

PAPER_ONLY. Par: ETHUSDT | TF: 1w | Velas: 485 (2017-08-14 -> 2026-11-23)

Costos: comision 0.10% + slippage 0.05% por pasada. Stop 2.0% / Target 4.0% (2:1) base. Horizonte 30 barras. Muestra minima 30 trades.

Null sintetico: 1000 sims, block bootstrap, percentil 95. Seed 42.

Categorias: Base (20) + Gestion de posicion (6) + Regimen EMA200 (6).

| regla | cat | n trades | acierto% | esperanza R | p-valor | veredicto |
|---|---|---:|---:|---:|---:|---|
| MA cross 20/50 (golden) long | Base | 5 | 0.0 | -1.15 | 0.999 | MUESTRA CHICA (no declarar) |
| MA cross 50/200 (golden) long | Base | 3 | 33.3 | -0.15 | 0.6062 | MUESTRA CHICA (no declarar) |
| Precio cruza EMA200 al alza long | Base | 10 | 10.0 | -0.85 | 0.9342 | MUESTRA CHICA (no declarar) |
| EMA50 pendiente positiva long | Base | 10 | 40.0 | 0.05 | 0.777 | MUESTRA CHICA (no declarar) |
| Momentum 5 velas >3% long | Base | 41 | 22.0 | -0.491 | 1.0 | RUIDO |
| Momentum 20 velas >5% long | Base | 19 | 15.8 | -0.676 | 1.0 | MUESTRA CHICA (no declarar) |
| Rotura maximo 20 velas long | Base | 44 | 20.5 | -0.536 | 1.0 | RUIDO |
| Rotura minimo 20 velas short | Base | 18 | 27.8 | -0.317 | 0.97 | MUESTRA CHICA (no declarar) |
| RSI(14) rebote desde <30 long | Base | 2 | 50.0 | 0.35 | 0.5467 | MUESTRA CHICA (no declarar) |
| RSI(14) rechazo desde >70 short | Base | 12 | 8.3 | -0.9 | 0.995 | MUESTRA CHICA (no declarar) |
| Mean reversion z<-2 long | Base | 9 | 22.2 | -0.483 | 0.9039 | MUESTRA CHICA (no declarar) |
| Mean reversion z>+2 short | Base | 16 | 6.2 | -0.962 | 0.997 | MUESTRA CHICA (no declarar) |
| Baja vol (ATR/px<2.5%) + uptrend long | Base | 0 | 0.0 | NA | NA | MUESTRA CHICA (no declarar) |
| Alta vol (ATR/px>4%) + downtrend short | Base | 20 | 35.0 | -0.1 | 0.859 | MUESTRA CHICA (no declarar) |
| Solo lunes long | Base | 0 | 0.0 | NA | NA | MUESTRA CHICA (no declarar) |
| Solo viernes short | Base | 0 | 0.0 | NA | NA | MUESTRA CHICA (no declarar) |
| Donchian breakout 10 long | Base | 59 | 18.6 | -0.591 | 1.0 | RUIDO |
| Donchian breakdown 10 short | Base | 28 | 28.6 | -0.293 | 0.989 | MUESTRA CHICA (no declarar) |
| Regresion lineal slope>0 R2>0.5 long | Base | 10 | 10.0 | -0.85 | 0.996 | MUESTRA CHICA (no declarar) |
| Regresion lineal slope<0 R2>0.5 short | Base | 10 | 10.0 | -0.85 | 0.979 | MUESTRA CHICA (no declarar) |
| Donchian breakout 10 long — stop movil a BE tras +1R | Gestion de posicion | 59 | 0.0 | -0.286 | 0.003 | PASA |
| Donchian breakdown 10 short — stop movil a BE tras +1R | Gestion de posicion | 28 | 0.0 | -0.257 | 0.002 | MUESTRA CHICA (no declarar) |
| Donchian breakout 10 long — cierre mitad en +1R, dejar correr | Gestion de posicion | 59 | 20.3 | 0.257 | 0.946 | RUIDO |
| Donchian breakdown 10 short — cierre mitad en +1R, dejar correr | Gestion de posicion | 28 | 28.6 | 0.347 | 0.664 | MUESTRA CHICA (no declarar) |
| Donchian breakout 10 long — 3 objetivos escalonados 1R/2R/3R | Gestion de posicion | 59 | 20.3 | -0.568 | 1.0 | RUIDO |
| Donchian breakdown 10 short — 3 objetivos escalonados 1R/2R/3R | Gestion de posicion | 28 | 28.6 | -0.293 | 0.989 | MUESTRA CHICA (no declarar) |
| Momentum 5 velas >3% long (regimen EMA200) | Regimen | 23 | 21.7 | -0.498 | 0.9665 | MUESTRA CHICA (no declarar) |
| Momentum 20 velas >5% long (regimen EMA200) | Regimen | 12 | 25.0 | -0.4 | 0.8963 | MUESTRA CHICA (no declarar) |
| Rotura maximo 20 velas long (regimen EMA200) | Regimen | 21 | 23.8 | -0.436 | 0.9672 | MUESTRA CHICA (no declarar) |
| Donchian breakout 10 long (regimen EMA200) | Regimen | 29 | 17.2 | -0.633 | 0.9755 | MUESTRA CHICA (no declarar) |
| Rotura minimo 20 velas short (regimen EMA200) | Regimen | 8 | 12.5 | -0.775 | 0.9491 | MUESTRA CHICA (no declarar) |
| Donchian breakdown 10 short (regimen EMA200) | Regimen | 10 | 30.0 | -0.25 | 0.8554 | MUESTRA CHICA (no declarar) |

**Pasan el null: 1 / 32**

- Donchian breakout 10 long — stop movil a BE tras +1R (n=59, E=-0.286R, p=0.003)

Muestra chica (<30): 26 reglas.

## Gestion de posicion — comparacion contra base

| variante | n | acierto% | esperanza R | p-valor | veredicto |
|---|---:|---:|---:|---:|---|
| Donchian breakout 10 long — stop movil a BE tras +1R | 59 | 0.0 | -0.286 | 0.003 | PASA |
| Donchian breakdown 10 short — stop movil a BE tras +1R | 28 | 0.0 | -0.257 | 0.002 | MUESTRA CHICA (no declarar) |
| Donchian breakout 10 long — cierre mitad en +1R, dejar correr | 59 | 20.3 | 0.257 | 0.946 | RUIDO |
| Donchian breakdown 10 short — cierre mitad en +1R, dejar correr | 28 | 28.6 | 0.347 | 0.664 | MUESTRA CHICA (no declarar) |
| Donchian breakout 10 long — 3 objetivos escalonados 1R/2R/3R | 59 | 20.3 | -0.568 | 1.0 | RUIDO |
| Donchian breakdown 10 short — 3 objetivos escalonados 1R/2R/3R | 28 | 28.6 | -0.293 | 0.989 | MUESTRA CHICA (no declarar) |

## Regimen (EMA200) — comparacion

| regla | n | acierto% | esperanza R | p-valor | veredicto |
|---|---:|---:|---:|---:|---|
| Momentum 5 velas >3% long (regimen EMA200) | 23 | 21.7 | -0.498 | 0.9665 | MUESTRA CHICA (no declarar) |
| Momentum 20 velas >5% long (regimen EMA200) | 12 | 25.0 | -0.4 | 0.8963 | MUESTRA CHICA (no declarar) |
| Rotura maximo 20 velas long (regimen EMA200) | 21 | 23.8 | -0.436 | 0.9672 | MUESTRA CHICA (no declarar) |
| Donchian breakout 10 long (regimen EMA200) | 29 | 17.2 | -0.633 | 0.9755 | MUESTRA CHICA (no declarar) |
| Rotura minimo 20 velas short (regimen EMA200) | 8 | 12.5 | -0.775 | 0.9491 | MUESTRA CHICA (no declarar) |
| Donchian breakdown 10 short (regimen EMA200) | 10 | 30.0 | -0.25 | 0.8554 | MUESTRA CHICA (no declarar) |

## Walk-forward (2/3 train, 1/3 test) — top 3 reglas base

| regla | n_train | n_test | E_IS | E_OOS | degradacion (OOS/IS) |
|---|---:|---:|---:|---:|---:|
| Alta vol (ATR/px>4%) + downtrend short | 323 | 132 | 0.004 | -1.15 | -299.0 |
| Rotura minimo 20 velas short | 323 | 132 | 0.05 | -1.15 | -23.0 |
| Donchian breakdown 10 short | 323 | 132 | -0.35 | -0.4 | 1.143 |

## Detalle por regla

### MA cross 20/50 (golden) long

- cat: Base
- n trades: 5
- acierto%: 0.0
- esperanza R: -1.15
- p-valor: 0.999
- null p95: 1.3536 | null media: 0.3409 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### MA cross 50/200 (golden) long

- cat: Base
- n trades: 3
- acierto%: 33.3
- esperanza R: -0.15
- p-valor: 0.6062
- null p95: 1.85 | null media: 0.323 | sims validas: 975
- veredicto: MUESTRA CHICA (no declarar)

### Precio cruza EMA200 al alza long

- cat: Base
- n trades: 10
- acierto%: 10.0
- esperanza R: -0.85
- p-valor: 0.9342
- null p95: 1.85 | null media: 0.5071 | sims validas: 958
- veredicto: MUESTRA CHICA (no declarar)

### EMA50 pendiente positiva long

- cat: Base
- n trades: 10
- acierto%: 40.0
- esperanza R: 0.05
- p-valor: 0.777
- null p95: 1.1234 | null media: 0.3902 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Momentum 5 velas >3% long

- cat: Base
- n trades: 41
- acierto%: 22.0
- esperanza R: -0.491
- p-valor: 1.0
- null p95: 0.85 | null media: 0.5005 | sims validas: 1000
- veredicto: RUIDO

### Momentum 20 velas >5% long

- cat: Base
- n trades: 19
- acierto%: 15.8
- esperanza R: -0.676
- p-valor: 1.0
- null p95: 0.9947 | null media: 0.425 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Rotura maximo 20 velas long

- cat: Base
- n trades: 44
- acierto%: 20.5
- esperanza R: -0.536
- p-valor: 1.0
- null p95: 0.7047 | null media: 0.4 | sims validas: 1000
- veredicto: RUIDO

### Rotura minimo 20 velas short

- cat: Base
- n trades: 18
- acierto%: 27.8
- esperanza R: -0.317
- p-valor: 0.97
- null p95: 0.57 | null media: 0.1982 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### RSI(14) rebote desde <30 long

- cat: Base
- n trades: 2
- acierto%: 50.0
- esperanza R: 0.35
- p-valor: 0.5467
- null p95: 1.85 | null media: 0.6494 | sims validas: 931
- veredicto: MUESTRA CHICA (no declarar)

### RSI(14) rechazo desde >70 short

- cat: Base
- n trades: 12
- acierto%: 8.3
- esperanza R: -0.9
- p-valor: 0.995
- null p95: 0.85 | null media: 0.0873 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Mean reversion z<-2 long

- cat: Base
- n trades: 9
- acierto%: 22.2
- esperanza R: -0.483
- p-valor: 0.9039
- null p95: 1.1833 | null media: 0.2578 | sims validas: 999
- veredicto: MUESTRA CHICA (no declarar)

### Mean reversion z>+2 short

- cat: Base
- n trades: 16
- acierto%: 6.2
- esperanza R: -0.962
- p-valor: 0.997
- null p95: 0.4214 | null media: -0.0975 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Baja vol (ATR/px<2.5%) + uptrend long

- cat: Base
- n trades: 0
- acierto%: 0.0
- esperanza R: None
- p-valor: None
- null p95: None | null media: None | sims validas: 0
- veredicto: MUESTRA CHICA (no declarar)

### Alta vol (ATR/px>4%) + downtrend short

- cat: Base
- n trades: 20
- acierto%: 35.0
- esperanza R: -0.1
- p-valor: 0.859
- null p95: 0.6896 | null media: 0.2178 | sims validas: 1000
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
- null p95: 0.6962 | null media: 0.4252 | sims validas: 1000
- veredicto: RUIDO

### Donchian breakdown 10 short

- cat: Base
- n trades: 28
- acierto%: 28.6
- esperanza R: -0.293
- p-valor: 0.989
- null p95: 0.5265 | null media: 0.2224 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Regresion lineal slope>0 R2>0.5 long

- cat: Base
- n trades: 10
- acierto%: 10.0
- esperanza R: -0.85
- p-valor: 0.996
- null p95: 1.1 | null media: 0.3734 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Regresion lineal slope<0 R2>0.5 short

- cat: Base
- n trades: 10
- acierto%: 10.0
- esperanza R: -0.85
- p-valor: 0.979
- null p95: 0.9929 | null media: 0.1711 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Donchian breakout 10 long — stop movil a BE tras +1R

- cat: Gestion de posicion
- n trades: 59
- acierto%: 0.0
- esperanza R: -0.286
- p-valor: 0.003
- null p95: -0.3974 | null media: -0.5207 | sims validas: 1000
- veredicto: PASA

### Donchian breakdown 10 short — stop movil a BE tras +1R

- cat: Gestion de posicion
- n trades: 28
- acierto%: 0.0
- esperanza R: -0.257
- p-valor: 0.002
- null p95: -0.4092 | null media: -0.579 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Donchian breakout 10 long — cierre mitad en +1R, dejar correr

- cat: Gestion de posicion
- n trades: 59
- acierto%: 20.3
- esperanza R: 0.257
- p-valor: 0.946
- null p95: 15.7113 | null media: 5.354 | sims validas: 1000
- veredicto: RUIDO

### Donchian breakdown 10 short — cierre mitad en +1R, dejar correr

- cat: Gestion de posicion
- n trades: 28
- acierto%: 28.6
- esperanza R: 0.347
- p-valor: 0.664
- null p95: 2.7746 | null media: 0.8904 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Donchian breakout 10 long — 3 objetivos escalonados 1R/2R/3R

- cat: Gestion de posicion
- n trades: 59
- acierto%: 20.3
- esperanza R: -0.568
- p-valor: 1.0
- null p95: 0.7044 | null media: 0.4416 | sims validas: 1000
- veredicto: RUIDO

### Donchian breakdown 10 short — 3 objetivos escalonados 1R/2R/3R

- cat: Gestion de posicion
- n trades: 28
- acierto%: 28.6
- esperanza R: -0.293
- p-valor: 0.989
- null p95: 0.5215 | null media: 0.2265 | sims validas: 1000
- veredicto: MUESTRA CHICA (no declarar)

### Momentum 5 velas >3% long (regimen EMA200)

- cat: Regimen
- n trades: 23
- acierto%: 21.7
- esperanza R: -0.498
- p-valor: 0.9665
- null p95: 1.1441 | null media: 0.4687 | sims validas: 955
- veredicto: MUESTRA CHICA (no declarar)

### Momentum 20 velas >5% long (regimen EMA200)

- cat: Regimen
- n trades: 12
- acierto%: 25.0
- esperanza R: -0.4
- p-valor: 0.8963
- null p95: 1.85 | null media: 0.3874 | sims validas: 926
- veredicto: MUESTRA CHICA (no declarar)

### Rotura maximo 20 velas long (regimen EMA200)

- cat: Regimen
- n trades: 21
- acierto%: 23.8
- esperanza R: -0.436
- p-valor: 0.9672
- null p95: 0.8065 | null media: 0.335 | sims validas: 977
- veredicto: MUESTRA CHICA (no declarar)

### Donchian breakout 10 long (regimen EMA200)

- cat: Regimen
- n trades: 29
- acierto%: 17.2
- esperanza R: -0.633
- p-valor: 0.9755
- null p95: 0.796 | null media: 0.3465 | sims validas: 980
- veredicto: MUESTRA CHICA (no declarar)

### Rotura minimo 20 velas short (regimen EMA200)

- cat: Regimen
- n trades: 8
- acierto%: 12.5
- esperanza R: -0.775
- p-valor: 0.9491
- null p95: 0.725 | null media: 0.1213 | sims validas: 982
- veredicto: MUESTRA CHICA (no declarar)

### Donchian breakdown 10 short (regimen EMA200)

- cat: Regimen
- n trades: 10
- acierto%: 30.0
- esperanza R: -0.25
- p-valor: 0.8554
- null p95: 0.6908 | null media: 0.137 | sims validas: 982
- veredicto: MUESTRA CHICA (no declarar)
