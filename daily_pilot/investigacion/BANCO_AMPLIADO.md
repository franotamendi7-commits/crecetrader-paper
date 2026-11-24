# BANCO AMPLIADO — CreceTrader (PAPER_ONLY)

**Paradigma:** piloto PAPER_ONLY. No toca metodo/ ni la FIRMA. No escribe el store vivo.
**Filtro comun:** null sintetico (block bootstrap de retornos, 1000 sims, percentil 95, seed 42). Muestra minima para declarar edge: 30 trades. Comision 0.10% + slippage 0.05% por pasada (costos_R). Stop base 2% / target 4% (2:1), horizonte 30 barras.

## Resumen ejecutivo

Se evaluaron 6 combinaciones (BTC y ETH x 1w/1d/4h). Por combinacion: 20 reglas base + 6 de gestion de posicion + 6 de regimen (EMA200) + 6 multi-timeframe (solo 4h). Total ~192-204 candidatos.

**Pasan el filtro (n>=30, real>p95, p<0.05): 1 candidato, pero con esperanza NEGATIVA**
- ETH 1w — "Donchian breakout 10 long — stop movil a BE tras +1R": n=59, acierto 0.0%, E=-0.286R, p=0.003. Pasa el null solo porque el null (trailing a BE) es aun peor; no es utilizable (acierto 0%, pierde dinero). Se considera falso positivo.

**Ninguna regla con esperanza positiva pasa el filtro.** Igual que en el banco original (0/20 en BTC 1d): no hay edge detectable en reglas de precio simples.

**Destellos (muestra chica, p<0.05, E>0) — vigilar, no declarar:**
- BTC 1d — Rotura minimo 20 velas short (regimen EMA200): n=16, acierto 68.8%, E=+0.913R, p=0.005
- BTC 1d — Donchian breakdown 10 short (regimen EMA200): n=22, acierto 63.6%, E=+0.759R, p=0.007
- ETH 1d — Rotura minimo 20 velas short (regimen EMA200): n=15, acierto 68.8%, E=+0.65R, p=0.029

El filtro de regimen EMA200 en cortos concentra los unicos casos con p bajo y E positivo, pero todos con n<30. Sugiere que "operar cortos solo bajo EMA200" merece mas datos, no una declaracion de edge.

**Gestion de posicion:** en general no mejora la version base. El trailing a break-even colapsa el acierto (muchos stops en BE/loss) y solo "pasa" con E negativo. Cierre de mitad y 3 objetivos escalonados no superan el null.

**Multi-timeframe (4h solo si 1d a favor):** no mejora; ninguno pasa.

**Walk-forward:** degradacion fuerte en las pocas reglas con IS positivo (ej. Baja vol long: IS +0.35 -> OOS -0.65). Consistente con ruido/overfit, no con edge estable.

## Veredicto claro

**No existe sistema detectable en este universo ampliado (BTC+ETH, 1w/1d/4h, reglas de precio + gestion + regimen + MTF).** El banco original (0/20) se mantiene tras ampliar categorias y pares. Los unicos destellos son regimen EMA200 en cortos con muestra chica (<30), que no superan el umbral de declaracion. PAPER_ONLY: no promover a real. Recomendacion: ampliar historia (mas velas/periodos) o cambiar de universo (otros pares/activos) antes de descartar; si se quiere seguir, priorizar el filtro de regimen en cortos con acumulacion de muestra.

---



# BTCUSDT — 1d


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


# BTCUSDT — 4h


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


# BTCUSDT — 1w


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


# ETHUSDT — 1d


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


# ETHUSDT — 4h


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


# ETHUSDT — 1w


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
