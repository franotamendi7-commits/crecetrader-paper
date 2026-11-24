# BANCO DE CANDIDATOS BTC — por timeframe (1w, 1d, 4h)

PAPER_ONLY. Par: BTCUSDT. Mismo banco de 20 candidatos, mismas reglas, mismo null sintetico (1000 sims, block bootstrap, p95). Solo cambia el timeframe (--tf). Comision 0.10% + slippage 0.05% por pasada (costos_R). Stop 2.0% / Target 4.0% (2:1), horizonte 30 barras, muestra minima 30 trades.

TFs corridos: 1w, 1d, 4h. Velas por TF (limite 500 de Binance):
- 1w: 2017-08-14 -> 2026-11-23 (485 velas)
- 1d: 2025-07-13 -> 2026-11-24 (500 velas)
- 4h: 2026-09-02 -> 2026-11-24 (500 velas)

Criterio: PASA solo si la esperanza real supera el percentil 95 del null y p<0.05. n<30 -> MUESTRA CHICA (no declarar). n=0 -> sin disparos (regla no aplicable a esa temporalidad).

## Tabla consolidada (tf | regla | n trades | acierto% | esperanza R | p-valor | veredicto)

| tf | regla | n trades | acierto% | esperanza R | p-valor | veredicto |
|---|---|---:|---:|---:|---:|---|
| 1w | MA cross 20/50 (golden) long | 3 | 33.3 | -0.15 | 0.788 | MUESTRA CHICA (no declarar) |
| 1w | MA cross 50/200 (golden) long | 2 | 0.0 | -1.15 | 1.0 | MUESTRA CHICA (no declarar) |
| 1w | Precio cruza EMA200 al alza long | 6 | 33.3 | -0.15 | 0.8916 | MUESTRA CHICA (no declarar) |
| 1w | EMA50 pendiente positiva long | 8 | 50.0 | 0.35 | 0.605 | MUESTRA CHICA (no declarar) |
| 1w | Momentum 5 velas >3% long | 43 | 32.6 | -0.173 | 1.0 | RUIDO |
| 1w | Momentum 20 velas >5% long | 18 | 27.8 | -0.317 | 0.999 | MUESTRA CHICA (no declarar) |
| 1w | Rotura maximo 20 velas long | 37 | 21.6 | -0.501 | 1.0 | RUIDO |
| 1w | Rotura minimo 20 velas short | 14 | 42.9 | 0.136 | 0.2 | MUESTRA CHICA (no declarar) |
| 1w | RSI(14) rebote desde <30 long | 3 | 0.0 | -1.15 | 0.9913 | MUESTRA CHICA (no declarar) |
| 1w | RSI(14) rechazo desde >70 short | 11 | 9.1 | -0.877 | 0.992 | MUESTRA CHICA (no declarar) |
| 1w | Mean reversion z<-2 long | 8 | 0.0 | -1.15 | 1.0 | MUESTRA CHICA (no declarar) |
| 1w | Mean reversion z>+2 short | 15 | 0.0 | -1.15 | 0.998 | MUESTRA CHICA (no declarar) |
| 1w | Baja vol (ATR/px<2.5%) + uptrend long | 0 | 0.0 | NA | 1.0 | MUESTRA CHICA (no declarar) |
| 1w | Alta vol (ATR/px>4%) + downtrend short | 21 | 33.3 | -0.15 | 0.701 | MUESTRA CHICA (no declarar) |
| 1w | Solo lunes long | 0 | 0.0 | NA | NA | MUESTRA CHICA (no declarar) |
| 1w | Solo viernes short | 0 | 0.0 | NA | NA | MUESTRA CHICA (no declarar) |
| 1w | Donchian breakout 10 long | 59 | 18.6 | -0.591 | 1.0 | RUIDO |
| 1w | Donchian breakdown 10 short | 24 | 37.5 | -0.025 | 0.412 | MUESTRA CHICA (no declarar) |
| 1w | Regresion lineal slope>0 R2>0.5 long | 10 | 20.0 | -0.55 | 0.98 | MUESTRA CHICA (no declarar) |
| 1w | Regresion lineal slope<0 R2>0.5 short | 11 | 18.2 | -0.605 | 0.881 | MUESTRA CHICA (no declarar) |
| 1d | MA cross 20/50 (golden) long | 5 | 40.0 | 0.05 | 0.36 | MUESTRA CHICA (no declarar) |
| 1d | MA cross 50/200 (golden) long | 1 | 0.0 | -1.15 | 1.0 | MUESTRA CHICA (no declarar) |
| 1d | Precio cruza EMA200 al alza long | 2 | 50.0 | 0.35 | 0.188 | MUESTRA CHICA (no declarar) |
| 1d | EMA50 pendiente positiva long | 9 | 33.3 | -0.15 | 0.4629 | MUESTRA CHICA (no declarar) |
| 1d | Momentum 5 velas >3% long | 37 | 27.0 | -0.339 | 0.682 | RUIDO |
| 1d | Momentum 20 velas >5% long | 19 | 26.3 | -0.361 | 0.7 | MUESTRA CHICA (no declarar) |
| 1d | Rotura maximo 20 velas long | 21 | 23.8 | -0.436 | 0.745 | MUESTRA CHICA (no declarar) |
| 1d | Rotura minimo 20 velas short | 28 | 46.4 | 0.243 | 0.216 | MUESTRA CHICA (no declarar) |
| 1d | RSI(14) rebote desde <30 long | 6 | 33.3 | -0.15 | 0.3914 | MUESTRA CHICA (no declarar) |
| 1d | RSI(14) rechazo desde >70 short | 6 | 33.3 | -0.15 | 0.723 | MUESTRA CHICA (no declarar) |
| 1d | Mean reversion z<-2 long | 14 | 14.3 | -0.721 | 0.932 | MUESTRA CHICA (no declarar) |
| 1d | Mean reversion z>+2 short | 11 | 45.5 | 0.214 | 0.447 | MUESTRA CHICA (no declarar) |
| 1d | Baja vol (ATR/px<2.5%) + uptrend long | 18 | 33.3 | -0.15 | 0.462 | MUESTRA CHICA (no declarar) |
| 1d | Alta vol (ATR/px>4%) + downtrend short | 12 | 16.7 | -0.65 | 0.4529 | MUESTRA CHICA (no declarar) |
| 1d | Solo lunes long | 72 | 26.4 | -0.358 | 0.869 | RUIDO |
| 1d | Solo viernes short | 71 | 31.0 | -0.22 | 0.953 | RUIDO |
| 1d | Donchian breakout 10 long | 33 | 21.2 | -0.514 | 0.88 | RUIDO |
| 1d | Donchian breakdown 10 short | 41 | 39.0 | 0.021 | 0.553 | RUIDO |
| 1d | Regresion lineal slope>0 R2>0.5 long | 9 | 11.1 | -0.817 | 0.929 | MUESTRA CHICA (no declarar) |
| 1d | Regresion lineal slope<0 R2>0.5 short | 10 | 20.0 | -0.55 | 0.939 | MUESTRA CHICA (no declarar) |
| 4h | MA cross 20/50 (golden) long | 4 | 25.0 | -0.4 | 0.4344 | MUESTRA CHICA (no declarar) |
| 4h | MA cross 50/200 (golden) long | 1 | 0.0 | -1.15 | 0.968 | MUESTRA CHICA (no declarar) |
| 4h | Precio cruza EMA200 al alza long | 9 | 11.1 | -0.799 | 0.5829 | MUESTRA CHICA (no declarar) |
| 4h | EMA50 pendiente positiva long | 10 | 50.0 | 0.083 | 0.1884 | MUESTRA CHICA (no declarar) |
| 4h | Momentum 5 velas >3% long | 7 | 28.6 | -0.293 | 0.356 | MUESTRA CHICA (no declarar) |
| 4h | Momentum 20 velas >5% long | 3 | 33.3 | 0.053 | 0.1998 | MUESTRA CHICA (no declarar) |
| 4h | Rotura maximo 20 velas long | 12 | 16.7 | -0.65 | 0.644 | MUESTRA CHICA (no declarar) |
| 4h | Rotura minimo 20 velas short | 24 | 50.0 | 0.261 | 0.376 | MUESTRA CHICA (no declarar) |
| 4h | RSI(14) rebote desde <30 long | 8 | 37.5 | -0.381 | 0.501 | MUESTRA CHICA (no declarar) |
| 4h | RSI(14) rechazo desde >70 short | 3 | 66.7 | 0.494 | 0.4152 | MUESTRA CHICA (no declarar) |
| 4h | Mean reversion z<-2 long | 22 | 27.3 | -0.389 | 0.538 | MUESTRA CHICA (no declarar) |
| 4h | Mean reversion z>+2 short | 12 | 50.0 | 0.35 | 0.433 | MUESTRA CHICA (no declarar) |
| 4h | Baja vol (ATR/px<2.5%) + uptrend long | 33 | 21.2 | -0.525 | 0.604 | RUIDO |
| 4h | Alta vol (ATR/px>4%) + downtrend short | 0 | 0.0 | NA | NA | MUESTRA CHICA (no declarar) |
| 4h | Solo lunes long | 12 | 25.0 | -0.4 | 0.459 | MUESTRA CHICA (no declarar) |
| 4h | Solo viernes short | 12 | 66.7 | 0.426 | 0.291 | MUESTRA CHICA (no declarar) |
| 4h | Donchian breakout 10 long | 31 | 22.6 | -0.473 | 0.591 | RUIDO |
| 4h | Donchian breakdown 10 short | 32 | 50.0 | 0.135 | 0.509 | RUIDO |
| 4h | Regresion lineal slope>0 R2>0.5 long | 10 | 10.0 | -0.85 | 0.835 | MUESTRA CHICA (no declarar) |
| 4h | Regresion lineal slope<0 R2>0.5 short | 11 | 72.7 | 0.739 | 0.111 | MUESTRA CHICA (no declarar) |

## Resumen por TF

| tf | velas | candidatos | PASA | RUIDO | MUESTRA CHICA |
|---|---:|---:|---:|---:|---:|
| 1w | 485 | 20 | 0 | 3 | 17 |
| 1d | 500 | 20 | 0 | 5 | 15 |
| 4h | 500 | 20 | 0 | 3 | 17 |

## Lectura

- **1w**: 0/20 pasan. La mayoria muestra chica; solo Donchian breakout 10 long tiene n=59 pero es RUIDO (E=-0.591R). Reglas de dia de semana (lunes/viernes) no disparan en velas semanales (todas abren lunes) -> n=0.
- **1d**: 0/20 pasan (resultado previo). 5 reglas con n>=30, todas RUIDO.
- **4h**: 0/20 pasan. Solo 3 reglas con n>=30 (baja vol uptrend, Donchian break 10 long/breakdown) y son RUIDO. Span corto (83 dias) limita muestra; reglas de largo plazo (MA200, momentum 20) apenas disparan.

**Conclusion: ningun candidato supera el null sintetico en ningun TF. No hay edge detectable para BTC en este universo de reglas, bajo este protocolo (PAPER_ONLY).**

## Detalle por TF (completo)

### 1w — 2017-08-14 -> 2026-11-23 (485 velas)

- **MA cross 20/50 (golden) long**: n=3, acierto=33.3%, E=-0.15R, p=0.788, null_p95=1.85, veredicto=MUESTRA CHICA (no declarar)
- **MA cross 50/200 (golden) long**: n=2, acierto=0.0%, E=-1.15R, p=1.0, null_p95=1.85, veredicto=MUESTRA CHICA (no declarar)
- **Precio cruza EMA200 al alza long**: n=6, acierto=33.3%, E=-0.15R, p=0.8916, null_p95=1.85, veredicto=MUESTRA CHICA (no declarar)
- **EMA50 pendiente positiva long**: n=8, acierto=50.0%, E=0.35R, p=0.605, null_p95=1.35, veredicto=MUESTRA CHICA (no declarar)
- **Momentum 5 velas >3% long**: n=43, acierto=32.6%, E=-0.173R, p=1.0, null_p95=0.9167, veredicto=RUIDO
- **Momentum 20 velas >5% long**: n=18, acierto=27.8%, E=-0.317R, p=0.999, null_p95=1.1, veredicto=MUESTRA CHICA (no declarar)
- **Rotura maximo 20 velas long**: n=37, acierto=21.6%, E=-0.501R, p=1.0, null_p95=0.8604, veredicto=RUIDO
- **Rotura minimo 20 velas short**: n=14, acierto=42.9%, E=0.136R, p=0.2, null_p95=0.3741, veredicto=MUESTRA CHICA (no declarar)
- **RSI(14) rebote desde <30 long**: n=3, acierto=0.0%, E=-1.15R, p=0.9913, null_p95=1.85, veredicto=MUESTRA CHICA (no declarar)
- **RSI(14) rechazo desde >70 short**: n=11, acierto=9.1%, E=-0.877R, p=0.992, null_p95=0.725, veredicto=MUESTRA CHICA (no declarar)
- **Mean reversion z<-2 long**: n=8, acierto=0.0%, E=-1.15R, p=1.0, null_p95=1.35, veredicto=MUESTRA CHICA (no declarar)
- **Mean reversion z>+2 short**: n=15, acierto=0.0%, E=-1.15R, p=0.998, null_p95=0.1625, veredicto=MUESTRA CHICA (no declarar)
- **Baja vol (ATR/px<2.5%) + uptrend long**: n=0, acierto=0.0%, E=NAR, p=1.0, null_p95=1.85, veredicto=MUESTRA CHICA (no declarar)
- **Alta vol (ATR/px>4%) + downtrend short**: n=21, acierto=33.3%, E=-0.15R, p=0.701, null_p95=0.4954, veredicto=MUESTRA CHICA (no declarar)
- **Solo lunes long**: n=0, acierto=0.0%, E=NAR, p=NA, null_p95=None, veredicto=MUESTRA CHICA (no declarar)
- **Solo viernes short**: n=0, acierto=0.0%, E=NAR, p=NA, null_p95=None, veredicto=MUESTRA CHICA (no declarar)
- **Donchian breakout 10 long**: n=59, acierto=18.6%, E=-0.591R, p=1.0, null_p95=0.8295, veredicto=RUIDO
- **Donchian breakdown 10 short**: n=24, acierto=37.5%, E=-0.025R, p=0.412, null_p95=0.3106, veredicto=MUESTRA CHICA (no declarar)
- **Regresion lineal slope>0 R2>0.5 long**: n=10, acierto=20.0%, E=-0.55R, p=0.98, null_p95=1.1833, veredicto=MUESTRA CHICA (no declarar)
- **Regresion lineal slope<0 R2>0.5 short**: n=11, acierto=18.2%, E=-0.605R, p=0.881, null_p95=0.95, veredicto=MUESTRA CHICA (no declarar)

### 1d — 2025-07-13 -> 2026-11-24 (500 velas)

- **MA cross 20/50 (golden) long**: n=5, acierto=40.0%, E=0.05R, p=0.36, null_p95=1.1, veredicto=MUESTRA CHICA (no declarar)
- **MA cross 50/200 (golden) long**: n=1, acierto=0.0%, E=-1.15R, p=1.0, null_p95=1.85, veredicto=MUESTRA CHICA (no declarar)
- **Precio cruza EMA200 al alza long**: n=2, acierto=50.0%, E=0.35R, p=0.188, null_p95=1.85, veredicto=MUESTRA CHICA (no declarar)
- **EMA50 pendiente positiva long**: n=9, acierto=33.3%, E=-0.15R, p=0.4629, null_p95=0.725, veredicto=MUESTRA CHICA (no declarar)
- **Momentum 5 velas >3% long**: n=37, acierto=27.0%, E=-0.339R, p=0.682, null_p95=0.2048, veredicto=RUIDO
- **Momentum 20 velas >5% long**: n=19, acierto=26.3%, E=-0.361R, p=0.7, null_p95=0.4654, veredicto=MUESTRA CHICA (no declarar)
- **Rotura maximo 20 velas long**: n=21, acierto=23.8%, E=-0.436R, p=0.745, null_p95=0.41, veredicto=MUESTRA CHICA (no declarar)
- **Rotura minimo 20 velas short**: n=28, acierto=46.4%, E=0.243R, p=0.216, null_p95=0.4825, veredicto=MUESTRA CHICA (no declarar)
- **RSI(14) rebote desde <30 long**: n=6, acierto=33.3%, E=-0.15R, p=0.3914, null_p95=0.5643, veredicto=MUESTRA CHICA (no declarar)
- **RSI(14) rechazo desde >70 short**: n=6, acierto=33.3%, E=-0.15R, p=0.723, null_p95=1.85, veredicto=MUESTRA CHICA (no declarar)
- **Mean reversion z<-2 long**: n=14, acierto=14.3%, E=-0.721R, p=0.932, null_p95=0.5008, veredicto=MUESTRA CHICA (no declarar)
- **Mean reversion z>+2 short**: n=11, acierto=45.5%, E=0.214R, p=0.447, null_p95=0.9929, veredicto=MUESTRA CHICA (no declarar)
- **Baja vol (ATR/px<2.5%) + uptrend long**: n=18, acierto=33.3%, E=-0.15R, p=0.462, null_p95=0.35, veredicto=MUESTRA CHICA (no declarar)
- **Alta vol (ATR/px>4%) + downtrend short**: n=12, acierto=16.7%, E=-0.65R, p=0.4529, null_p95=1.85, veredicto=MUESTRA CHICA (no declarar)
- **Solo lunes long**: n=72, acierto=26.4%, E=-0.358R, p=0.869, null_p95=0.1513, veredicto=RUIDO
- **Solo viernes short**: n=71, acierto=31.0%, E=-0.22R, p=0.953, null_p95=0.4556, veredicto=RUIDO
- **Donchian breakout 10 long**: n=33, acierto=21.2%, E=-0.514R, p=0.88, null_p95=0.3047, veredicto=RUIDO
- **Donchian breakdown 10 short**: n=41, acierto=39.0%, E=0.021R, p=0.553, null_p95=0.4058, veredicto=RUIDO
- **Regresion lineal slope>0 R2>0.5 long**: n=9, acierto=11.1%, E=-0.817R, p=0.929, null_p95=0.725, veredicto=MUESTRA CHICA (no declarar)
- **Regresion lineal slope<0 R2>0.5 short**: n=10, acierto=20.0%, E=-0.55R, p=0.939, null_p95=0.95, veredicto=MUESTRA CHICA (no declarar)

### 4h — 2026-09-02 -> 2026-11-24 (500 velas)

- **MA cross 20/50 (golden) long**: n=4, acierto=25.0%, E=-0.4R, p=0.4344, null_p95=0.7006, veredicto=MUESTRA CHICA (no declarar)
- **MA cross 50/200 (golden) long**: n=1, acierto=0.0%, E=-1.15R, p=0.968, null_p95=1.85, veredicto=MUESTRA CHICA (no declarar)
- **Precio cruza EMA200 al alza long**: n=9, acierto=11.1%, E=-0.799R, p=0.5829, null_p95=1.3408, veredicto=MUESTRA CHICA (no declarar)
- **EMA50 pendiente positiva long**: n=10, acierto=50.0%, E=0.083R, p=0.1884, null_p95=0.595, veredicto=MUESTRA CHICA (no declarar)
- **Momentum 5 velas >3% long**: n=7, acierto=28.6%, E=-0.293R, p=0.356, null_p95=0.4383, veredicto=MUESTRA CHICA (no declarar)
- **Momentum 20 velas >5% long**: n=3, acierto=33.3%, E=0.053R, p=0.1998, null_p95=0.7551, veredicto=MUESTRA CHICA (no declarar)
- **Rotura maximo 20 velas long**: n=12, acierto=16.7%, E=-0.65R, p=0.644, null_p95=0.2987, veredicto=MUESTRA CHICA (no declarar)
- **Rotura minimo 20 velas short**: n=24, acierto=50.0%, E=0.261R, p=0.376, null_p95=0.7082, veredicto=MUESTRA CHICA (no declarar)
- **RSI(14) rebote desde <30 long**: n=8, acierto=37.5%, E=-0.381R, p=0.501, null_p95=0.5463, veredicto=MUESTRA CHICA (no declarar)
- **RSI(14) rechazo desde >70 short**: n=3, acierto=66.7%, E=0.494R, p=0.4152, null_p95=1.85, veredicto=MUESTRA CHICA (no declarar)
- **Mean reversion z<-2 long**: n=22, acierto=27.3%, E=-0.389R, p=0.538, null_p95=0.2809, veredicto=MUESTRA CHICA (no declarar)
- **Mean reversion z>+2 short**: n=12, acierto=50.0%, E=0.35R, p=0.433, null_p95=1.1841, veredicto=MUESTRA CHICA (no declarar)
- **Baja vol (ATR/px<2.5%) + uptrend long**: n=33, acierto=21.2%, E=-0.525R, p=0.604, null_p95=0.1895, veredicto=RUIDO
- **Alta vol (ATR/px>4%) + downtrend short**: n=0, acierto=0.0%, E=NAR, p=NA, null_p95=None, veredicto=MUESTRA CHICA (no declarar)
- **Solo lunes long**: n=12, acierto=25.0%, E=-0.4R, p=0.459, null_p95=0.1565, veredicto=MUESTRA CHICA (no declarar)
- **Solo viernes short**: n=12, acierto=66.7%, E=0.426R, p=0.291, null_p95=0.8832, veredicto=MUESTRA CHICA (no declarar)
- **Donchian breakout 10 long**: n=31, acierto=22.6%, E=-0.473R, p=0.591, null_p95=0.1834, veredicto=RUIDO
- **Donchian breakdown 10 short**: n=32, acierto=50.0%, E=0.135R, p=0.509, null_p95=0.6327, veredicto=RUIDO
- **Regresion lineal slope>0 R2>0.5 long**: n=10, acierto=10.0%, E=-0.85R, p=0.835, null_p95=0.3502, veredicto=MUESTRA CHICA (no declarar)
- **Regresion lineal slope<0 R2>0.5 short**: n=11, acierto=72.7%, E=0.739R, p=0.111, null_p95=0.9232, veredicto=MUESTRA CHICA (no declarar)
