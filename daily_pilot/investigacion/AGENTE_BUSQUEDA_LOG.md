# AGENTE_BUSQUEDA_LOG — Exploración autónoma de nuevas estrategias
PAPER_ONLY. Sin órdenes. Sin modificaciones al repo salvo este archivo.

Protocolo aplicado a CADA idea:
- Velas leídas DIRECTO con `json` desde `daily_pilot/datos/velas/*.json` (nunca `velas()`).
- Walk-forward 70/30: optimización de parámetros SOLO en train (primer 70% de velas ordenadas por ts), evaluación en test (último 30%).
- Validación con `null_corregido` multi-seed (4 seeds: 7, 11, 23, 42; 50 permutaciones/seed sobre el test).
- VÁLIDA solo si: p<=0.05 en >=3/4 seeds Y E(test)>0 Y n(test)>=15.
- Métricas: n, señales/mes, esperanza R, win%, DD (R), PF.

---

## IDEA 1 — Scalping 1h EMA + ATR trailing stop
Idea: entrada en cruce alcista EMA rápida/lenta en 1h, stop ATR, trailing stop en R, target múltiplo de R. Ventana: últimas 20.000 velas 1h (ETH 1h descartado: solo 500 velas; no se descargan velas nuevas por restricción del repo).
### IDEA1 scalp_atr_trail | BTCUSDT 1h | params={'ef': 10, 'es': 50, 'k': 2.0, 'tp': 2.0, 'ts': 2.0, 'td': 1.5}
- TRAIN: n=183 señ/mes=9.55 E=-0.183R win=14.8% DD=-47.0R PF=0.547
- TEST : n=75 señ/mes=9.13 E=-0.293R win=8.0% DD=-22.0R PF=0.29
- NULL (test, 50 sims/seed): s7 p=0.800 Ereal=-0.293 p50=-0.211, s11 p=0.780 Ereal=-0.293 p50=-0.243, s23 p=0.680 Ereal=-0.293 p50=-0.237, s42 p=0.880 Ereal=-0.293 p50=-0.218
- p<=0.05 en 0/4 seeds | test E>0: False | VEREDICTO: DESCARTADA (0.7s)
- Grid=216 combinaciones, válidas en train=192. Top5 train: [({'ef': 10, 'es': 50, 'k': 2.0, 'tp': 2.0, 'ts': 2.0, 'td': 1.5}, -0.1831, 183), ({'ef': 10, 'es': 100, 'k': 1.5, 'tp': 2.0, 'ts': 2.0, 'td': 1.5}, -0.2341, 126), ({'ef': 20, 'es': 200, 'k': 2.0, 'tp': 2.0, 'ts': 2.0, 'td': 1.5}, -0.2381, 63), ({'ef': 10, 'es': 50, 'k': 2.0, 'tp': 2.0, 'ts': 1.0, 'td': 1.5}, -0.2486, 183), ({'ef': 10, 'es': 100, 'k': 2.0, 'tp': 2.0, 'ts': 1.0, 'td': 1.5}, -0.254, 126)]

## IDEA 1 — Scalping 1h EMA + ATR trailing stop
Idea: entrada en cruce alcista EMA rápida/lenta en 1h, stop ATR, trailing stop en R, target múltiplo de R. Ventana: últimas 20.000 velas 1h (ETH 1h descartado: solo 500 velas; no se descargan velas nuevas por restricción del repo).
### IDEA1 scalp_atr_trail | ETCUSDT 1h | params={'ef': 20, 'es': 50, 'k': 2.0, 'tp': 2.0, 'ts': 2.0, 'td': 1.5}
- TRAIN: n=144 señ/mes=7.51 E=-0.014R win=23.6% DD=-15.5R PF=0.962
- TEST : n=58 señ/mes=7.06 E=-0.267R win=8.6% DD=-16.0R PF=0.326
- NULL (test, 50 sims/seed): s7 p=1.000 Ereal=-0.267 p50=+0.011, s11 p=0.980 Ereal=-0.267 p50=-0.070, s23 p=0.960 Ereal=-0.267 p50=-0.042, s42 p=0.980 Ereal=-0.267 p50=-0.049
- p<=0.05 en 0/4 seeds | test E>0: False | VEREDICTO: DESCARTADA (0.7s)
- Grid=216 combinaciones, válidas en train=192. Top5 train: [({'ef': 20, 'es': 50, 'k': 2.0, 'tp': 2.0, 'ts': 2.0, 'td': 1.5}, -0.0139, 144), ({'ef': 20, 'es': 50, 'k': 1.5, 'tp': 2.0, 'ts': 2.0, 'td': 1.5}, -0.066, 144), ({'ef': 20, 'es': 100, 'k': 2.0, 'tp': 2.0, 'ts': 2.0, 'td': 1.5}, -0.0762, 105), ({'ef': 20, 'es': 50, 'k': 2.0, 'tp': 2.0, 'ts': 1.0, 'td': 1.5}, -0.0972, 144), ({'ef': 10, 'es': 100, 'k': 2.0, 'tp': 2.0, 'ts': 2.0, 'td': 1.5}, -0.1389, 144)]

## IDEA 1 — Scalping 1h EMA + ATR trailing stop
Idea: entrada en cruce alcista EMA rápida/lenta en 1h, stop ATR, trailing stop en R, target múltiplo de R. Ventana: últimas 20.000 velas 1h (ETH 1h descartado: solo 500 velas; no se descargan velas nuevas por restricción del repo).
### IDEA1 scalp_atr_trail | HBARUSDT 1h | params={'ef': 50, 'es': 200, 'k': 1.5, 'tp': 2.0, 'ts': 2.0, 'td': 1.5}
- TRAIN: n=42 señ/mes=2.19 E=+0.131R win=31.0% DD=-10.0R PF=1.393
- TEST : n=12 señ/mes=1.46 E=-0.042R win=25.0% DD=-2.5R PF=0.9
- NULL (test, 50 sims/seed): s7 p=0.200 Ereal=-0.042 p50=-0.231, s11 p=0.200 Ereal=-0.042 p50=-0.237, s23 p=0.180 Ereal=-0.042 p50=-0.278, s42 p=0.220 Ereal=-0.042 p50=-0.214
- p<=0.05 en 0/4 seeds | test E>0: False | VEREDICTO: DESCARTADA (0.7s)
- Grid=216 combinaciones, válidas en train=192. Top5 train: [({'ef': 50, 'es': 200, 'k': 1.5, 'tp': 2.0, 'ts': 2.0, 'td': 1.5}, 0.131, 42), ({'ef': 50, 'es': 200, 'k': 1.5, 'tp': 2.0, 'ts': 1.0, 'td': 1.5}, 0.0238, 42), ({'ef': 50, 'es': 100, 'k': 2.0, 'tp': 2.0, 'ts': 1.0, 'td': 1.5}, 0.0093, 54), ({'ef': 50, 'es': 100, 'k': 2.0, 'tp': 2.0, 'ts': 2.0, 'td': 1.5}, 0.0093, 54), ({'ef': 50, 'es': 100, 'k': 1.5, 'tp': 2.0, 'ts': 2.0, 'td': 1.5}, -0.0093, 54)]

## IDEA 1 — Scalping 1h EMA + ATR trailing stop
Idea: entrada en cruce alcista EMA rápida/lenta en 1h, stop ATR, trailing stop en R, target múltiplo de R. Ventana: últimas 20.000 velas 1h (ETH 1h descartado: solo 500 velas; no se descargan velas nuevas por restricción del repo).
### IDEA1 scalp_atr_trail | THETAUSDT 1h | params={'ef': 50, 'es': 200, 'k': 1.5, 'tp': 2.0, 'ts': 2.0, 'td': 1.5}
- TRAIN: n=39 señ/mes=2.04 E=-0.103R win=25.6% DD=-9.0R PF=0.789
- TEST : n=14 señ/mes=1.7 E=-0.643R win=0.0% DD=-9.0R PF=0.0
- NULL (test, 50 sims/seed): s7 p=1.000 Ereal=-0.643 p50=+0.000, s11 p=1.000 Ereal=-0.643 p50=-0.091, s23 p=0.980 Ereal=-0.643 p50=-0.100, s42 p=0.980 Ereal=-0.643 p50=-0.000
- p<=0.05 en 0/4 seeds | test E>0: False | VEREDICTO: DESCARTADA (0.9s)
- Grid=216 combinaciones, válidas en train=192. Top5 train: [({'ef': 50, 'es': 200, 'k': 1.5, 'tp': 2.0, 'ts': 2.0, 'td': 1.5}, -0.1026, 39), ({'ef': 50, 'es': 200, 'k': 2.0, 'tp': 2.0, 'ts': 2.0, 'td': 1.5}, -0.1154, 39), ({'ef': 20, 'es': 50, 'k': 1.5, 'tp': 2.0, 'ts': 2.0, 'td': 1.5}, -0.1455, 134), ({'ef': 50, 'es': 200, 'k': 2.0, 'tp': 2.0, 'ts': 1.0, 'td': 1.5}, -0.1538, 39), ({'ef': 10, 'es': 100, 'k': 1.0, 'tp': 2.0, 'ts': 2.0, 'td': 1.5}, -0.1654, 133)]

## IDEA 2 — Swing multi-day 1d con filtro de tendencia semanal
Idea: solo largos cuando 1w close>EMA(wf)>EMA(ws); entrada en 1d al cruce alcista de EMA(ef) con RSI(14) entre 45-70; stop ka*ATR, target tp*R, BE en 1R, max 90 velas. Parámetros optimizados en train 70%.
- BNBUSDT: DESCARTADA — sin combinaciones con n suficiente
- NOTA IDEA 2 (corrección): los archivos `*_1d.json` del repo están truncados (BTC/ETH/XRP/ADA/SOL: solo 3 velas; BNB: 500). Sin descargar nada (restricción), se re-muestrean velas 4h → 1d localmente en memoria. El filtro semanal usa `*_1w.json` (485 velas BTC, completo).
### IDEA2 swing_1d_weekly (1d re-muestreado de 4h) | BTCUSDT 1d+1w | params={'wf': 8, 'ws': 34, 'ef': 20, 'ka': 2.0, 'tp': 4.0}
- TRAIN: n=46 señ/mes=0.59 E=+0.685R win=63.0% DD=-6.0R PF=3.1
- TEST : n=19 señ/mes=0.57 E=-0.053R win=52.6% DD=-4.5R PF=0.875
- NULL (test, 50 sims/seed): s7 p=0.440 Ereal=-0.053 p50=-0.132, s11 p=0.420 Ereal=-0.053 p50=-0.107, s23 p=0.380 Ereal=-0.053 p50=-0.125, s42 p=0.340 Ereal=-0.053 p50=-0.167
- p<=0.05 en 0/4 seeds | test E>0: False | VEREDICTO: DESCARTADA (0.2s)
- Grid=72, válidas=72. Top5 train: [({'wf': 8, 'ws': 34, 'ef': 20, 'ka': 2.0, 'tp': 4.0}, 0.6848, 46), ({'wf': 8, 'ws': 34, 'ef': 20, 'ka': 1.5, 'tp': 4.0}, 0.663, 46), ({'wf': 13, 'ws': 34, 'ef': 20, 'ka': 2.0, 'tp': 4.0}, 0.6596, 47), ({'wf': 13, 'ws': 34, 'ef': 20, 'ka': 1.5, 'tp': 4.0}, 0.6383, 47), ({'wf': 8, 'ws': 34, 'ef': 20, 'ka': 2.0, 'tp': 3.0}, 0.587, 46)]
### IDEA2 swing_1d_weekly (1d re-muestreado de 4h) | ETHUSDT 1d+1w | params={'wf': 8, 'ws': 34, 'ef': 20, 'ka': 3.0, 'tp': 4.0}
- TRAIN: n=55 señ/mes=0.71 E=+0.691R win=58.2% DD=-12.5R PF=3.375
- TEST : n=9 señ/mes=0.27 E=-0.667R win=22.2% DD=-6.5R PF=0.143
- NULL (test, 50 sims/seed): s7 p=0.900 Ereal=-0.667 p50=+0.150, s11 p=0.900 Ereal=-0.667 p50=-0.182, s23 p=0.940 Ereal=-0.667 p50=+0.000, s42 p=0.920 Ereal=-0.667 p50=-0.083
- p<=0.05 en 0/4 seeds | test E>0: False | VEREDICTO: DESCARTADA (0.2s)
- Grid=72, válidas=72. Top5 train: [({'wf': 8, 'ws': 34, 'ef': 20, 'ka': 3.0, 'tp': 4.0}, 0.6909, 55), ({'wf': 13, 'ws': 34, 'ef': 20, 'ka': 3.0, 'tp': 4.0}, 0.5776, 58), ({'wf': 8, 'ws': 34, 'ef': 20, 'ka': 2.0, 'tp': 4.0}, 0.5455, 55), ({'wf': 8, 'ws': 34, 'ef': 20, 'ka': 3.0, 'tp': 3.0}, 0.5455, 55), ({'wf': 8, 'ws': 34, 'ef': 20, 'ka': 3.0, 'tp': 2.0}, 0.5273, 55)]
### IDEA2 swing_1d_weekly (1d re-muestreado de 4h) | BNBUSDT 1d+1w | params={'wf': 8, 'ws': 34, 'ef': 50, 'ka': 2.0, 'tp': 2.0}
- TRAIN: n=25 señ/mes=0.33 E=+0.620R win=68.0% DD=-4.0R PF=2.938
- TEST : n=13 señ/mes=0.4 E=-0.231R win=30.8% DD=-5.5R PF=0.667
- NULL (test, 50 sims/seed): s7 p=0.820 Ereal=-0.231 p50=+0.000, s11 p=0.840 Ereal=-0.231 p50=+0.056, s23 p=0.840 Ereal=-0.231 p50=+0.083, s42 p=0.740 Ereal=-0.231 p50=+0.000
- p<=0.05 en 0/4 seeds | test E>0: False | VEREDICTO: DESCARTADA (0.2s)
- Grid=72, válidas=72. Top5 train: [({'wf': 8, 'ws': 34, 'ef': 50, 'ka': 2.0, 'tp': 2.0}, 0.62, 25), ({'wf': 13, 'ws': 34, 'ef': 20, 'ka': 1.5, 'tp': 4.0}, 0.6047, 43), ({'wf': 8, 'ws': 34, 'ef': 20, 'ka': 1.5, 'tp': 4.0}, 0.5682, 44), ({'wf': 13, 'ws': 34, 'ef': 20, 'ka': 2.0, 'tp': 4.0}, 0.5581, 43), ({'wf': 13, 'ws': 34, 'ef': 50, 'ka': 2.0, 'tp': 2.0}, 0.5357, 28)]
### IDEA2 swing_1d_weekly (1d re-muestreado de 4h) | SOLUSDT 1d+1w | params={'wf': 8, 'ws': 34, 'ef': 50, 'ka': 3.0, 'tp': 4.0}
- TRAIN: n=15 señ/mes=0.28 E=+1.033R win=60.0% DD=-2.5R PF=4.1
- TEST : n=2 señ/mes=0.09 E=-1.000R win=0.0% DD=-2.0R PF=0.0
- NULL (test, 50 sims/seed): s7 p=1.000 Ereal=-1.000 p50=-0.250, s11 p=1.000 Ereal=-1.000 p50=+0.000, s23 p=1.000 Ereal=-1.000 p50=-0.400, s42 p=1.000 Ereal=-1.000 p50=-0.000
- p<=0.05 en 0/4 seeds | test E>0: False | VEREDICTO: DESCARTADA (0.1s)
- Grid=72, válidas=63. Top5 train: [({'wf': 8, 'ws': 34, 'ef': 50, 'ka': 3.0, 'tp': 4.0}, 1.0333, 15), ({'wf': 13, 'ws': 21, 'ef': 50, 'ka': 3.0, 'tp': 4.0}, 1.0, 17), ({'wf': 13, 'ws': 34, 'ef': 50, 'ka': 3.0, 'tp': 4.0}, 1.0, 17), ({'wf': 8, 'ws': 34, 'ef': 50, 'ka': 3.0, 'tp': 3.0}, 0.7667, 15), ({'wf': 13, 'ws': 21, 'ef': 50, 'ka': 3.0, 'tp': 3.0}, 0.7353, 17)]
### IDEA2 swing_1d_weekly (1d re-muestreado de 4h) | XRPUSDT 1d+1w | params={'wf': 8, 'ws': 34, 'ef': 50, 'ka': 3.0, 'tp': 4.0}
- TRAIN: n=22 señ/mes=0.31 E=+0.955R win=81.8% DD=-2.5R PF=6.25
- TEST : n=13 señ/mes=0.42 E=-0.231R win=30.8% DD=-5.0R PF=0.667
- NULL (test, 50 sims/seed): s7 p=0.460 Ereal=-0.231 p50=-0.250, s11 p=0.440 Ereal=-0.231 p50=-0.250, s23 p=0.360 Ereal=-0.231 p50=-0.357, s42 p=0.420 Ereal=-0.231 p50=-0.250
- p<=0.05 en 0/4 seeds | test E>0: False | VEREDICTO: DESCARTADA (0.2s)
- Grid=72, válidas=72. Top5 train: [({'wf': 8, 'ws': 34, 'ef': 50, 'ka': 3.0, 'tp': 4.0}, 0.9545, 22), ({'wf': 13, 'ws': 21, 'ef': 50, 'ka': 3.0, 'tp': 4.0}, 0.8542, 24), ({'wf': 13, 'ws': 34, 'ef': 50, 'ka': 3.0, 'tp': 4.0}, 0.8542, 24), ({'wf': 8, 'ws': 34, 'ef': 50, 'ka': 3.0, 'tp': 3.0}, 0.7727, 22), ({'wf': 8, 'ws': 21, 'ef': 50, 'ka': 3.0, 'tp': 4.0}, 0.725, 20)]
### IDEA2 swing_1d_weekly (1d re-muestreado de 4h) | ADAUSDT 1d+1w | params={'wf': 8, 'ws': 34, 'ef': 50, 'ka': 3.0, 'tp': 4.0}
- TRAIN: n=16 señ/mes=0.22 E=+1.062R win=62.5% DD=-1.0R PF=9.5
- TEST : n=5 señ/mes=0.16 E=-1.000R win=0.0% DD=-5.0R PF=0.0
- NULL (test, 50 sims/seed): s7 p=1.000 Ereal=-1.000 p50=-0.250, s11 p=1.000 Ereal=-1.000 p50=-0.250, s23 p=1.000 Ereal=-1.000 p50=-0.438, s42 p=1.000 Ereal=-1.000 p50=-0.500
- p<=0.05 en 0/4 seeds | test E>0: False | VEREDICTO: DESCARTADA (0.2s)
- Grid=72, válidas=72. Top5 train: [({'wf': 8, 'ws': 34, 'ef': 50, 'ka': 3.0, 'tp': 4.0}, 1.0625, 16), ({'wf': 8, 'ws': 34, 'ef': 50, 'ka': 2.0, 'tp': 4.0}, 1.0312, 16), ({'wf': 8, 'ws': 34, 'ef': 50, 'ka': 3.0, 'tp': 3.0}, 1.0312, 16), ({'wf': 13, 'ws': 34, 'ef': 20, 'ka': 3.0, 'tp': 3.0}, 0.9688, 32), ({'wf': 8, 'ws': 34, 'ef': 20, 'ka': 3.0, 'tp': 3.0}, 0.85, 30)]

## IDEA 3 — Squeeze breakout 4h (Bollinger bandwidth + volumen relativo)
Idea: bandwidth BB(20,2) en percentil bajo de los últimos 100 bares; ruptura de banda superior con volumen > vm*SMA(vol,20); stop k*ATR, target tp*R, BE 1R, max 60 bares. Distinta de 'ruptura de máximo con volumen' (aquí hay filtro de compresión previa). Grid 54 combinaciones.
### IDEA3 squeeze_breakout | BTCUSDT 4h | params={'pct': 20, 'vm': 2.0, 'k': 2.0, 'tp': 3.0}
- TRAIN: n=26 señ/mes=0.33 E=+0.211R win=53.8% DD=-4.0R PF=1.458
- TEST : n=17 señ/mes=0.51 E=-0.441R win=29.4% DD=-8.5R PF=0.25
- NULL (test, 50 sims/seed): s7 p=0.980 Ereal=-0.441 p50=-0.025, s11 p=1.000 Ereal=-0.441 p50=-0.000, s23 p=0.980 Ereal=-0.441 p50=+0.071, s42 p=0.980 Ereal=-0.441 p50=+0.025
- p<=0.05 en 0/4 seeds | test E>0: False | VEREDICTO: DESCARTADA (2.9s)
- Grid=54, válidas=48. Top5 train: [({'pct': 20, 'vm': 2.0, 'k': 2.0, 'tp': 3.0}, 0.2115, 26), ({'pct': 30, 'vm': 2.0, 'k': 1.0, 'tp': 3.0}, 0.2, 40), ({'pct': 20, 'vm': 1.5, 'k': 2.0, 'tp': 3.0}, 0.1579, 57), ({'pct': 30, 'vm': 2.0, 'k': 1.0, 'tp': 2.0}, 0.15, 40), ({'pct': 30, 'vm': 2.0, 'k': 2.0, 'tp': 2.0}, 0.125, 40)]
### IDEA3 squeeze_breakout | ETHUSDT 4h | params={'pct': 30, 'vm': 2.0, 'k': 2.0, 'tp': 2.0}
- TRAIN: n=59 señ/mes=0.76 E=+0.195R win=59.3% DD=-3.5R PF=1.479
- TEST : n=33 señ/mes=0.99 E=-0.121R win=42.4% DD=-10.0R PF=0.789
- NULL (test, 50 sims/seed): s7 p=0.760 Ereal=-0.121 p50=+0.017, s11 p=0.700 Ereal=-0.121 p50=+0.029, s23 p=0.720 Ereal=-0.121 p50=+0.056, s42 p=0.720 Ereal=-0.121 p50=+0.033
- p<=0.05 en 0/4 seeds | test E>0: False | VEREDICTO: DESCARTADA (2.8s)
- Grid=54, válidas=48. Top5 train: [({'pct': 30, 'vm': 2.0, 'k': 2.0, 'tp': 2.0}, 0.1949, 59), ({'pct': 30, 'vm': 2.0, 'k': 2.0, 'tp': 3.0}, 0.1864, 59), ({'pct': 30, 'vm': 2.0, 'k': 1.5, 'tp': 3.0}, 0.1695, 59), ({'pct': 20, 'vm': 2.0, 'k': 2.0, 'tp': 2.0}, 0.1429, 42), ({'pct': 20, 'vm': 2.0, 'k': 2.0, 'tp': 3.0}, 0.131, 42)]
### IDEA3 squeeze_breakout | SOLUSDT 4h | params={'pct': 10, 'vm': 1.5, 'k': 1.0, 'tp': 3.0}
- TRAIN: n=17 señ/mes=0.32 E=+0.412R win=76.5% DD=-1.0R PF=2.75
- TEST : n=15 señ/mes=0.66 E=+0.000R win=60.0% DD=-3.5R PF=1.0
- NULL (test, 50 sims/seed): s7 p=0.420 Ereal=+0.000 p50=-0.143, s11 p=0.580 Ereal=+0.000 p50=+0.071, s23 p=0.540 Ereal=+0.000 p50=+0.050, s42 p=0.380 Ereal=+0.000 p50=-0.182
- p<=0.05 en 0/4 seeds | test E>0: False | VEREDICTO: DESCARTADA (2.0s)
- Grid=54, válidas=48. Top5 train: [({'pct': 10, 'vm': 1.5, 'k': 1.0, 'tp': 3.0}, 0.4118, 17), ({'pct': 10, 'vm': 1.5, 'k': 1.0, 'tp': 2.0}, 0.3235, 17), ({'pct': 20, 'vm': 2.0, 'k': 1.0, 'tp': 3.0}, 0.2273, 22), ({'pct': 20, 'vm': 2.0, 'k': 1.5, 'tp': 2.0}, 0.2273, 22), ({'pct': 20, 'vm': 2.0, 'k': 1.0, 'tp': 2.0}, 0.1818, 22)]
### IDEA3 squeeze_breakout | XRPUSDT 4h | params={'pct': 10, 'vm': 1.2, 'k': 2.0, 'tp': 3.0}
- TRAIN: n=48 señ/mes=0.67 E=-0.031R win=47.9% DD=-8.0R PF=0.94
- TEST : n=23 señ/mes=0.75 E=-0.087R win=52.2% DD=-7.5R PF=0.818
- NULL (test, 50 sims/seed): s7 p=0.660 Ereal=-0.087 p50=-0.021, s11 p=0.500 Ereal=-0.087 p50=-0.056, s23 p=0.440 Ereal=-0.087 p50=-0.143, s42 p=0.540 Ereal=-0.087 p50=-0.029
- p<=0.05 en 0/4 seeds | test E>0: False | VEREDICTO: DESCARTADA (2.6s)
- Grid=54, válidas=54. Top5 train: [({'pct': 10, 'vm': 1.2, 'k': 2.0, 'tp': 3.0}, -0.0313, 48), ({'pct': 20, 'vm': 1.2, 'k': 1.5, 'tp': 3.0}, -0.0488, 82), ({'pct': 10, 'vm': 1.2, 'k': 2.0, 'tp': 2.0}, -0.0729, 48), ({'pct': 20, 'vm': 1.5, 'k': 1.0, 'tp': 2.0}, -0.0902, 61), ({'pct': 20, 'vm': 1.5, 'k': 1.0, 'tp': 3.0}, -0.0902, 61)]
### IDEA3 squeeze_breakout | LINKUSDT 4h | params={'pct': 10, 'vm': 1.2, 'k': 2.0, 'tp': 3.0}
- TRAIN: n=35 señ/mes=0.53 E=+0.286R win=60.0% DD=-3.0R PF=1.714
- TEST : n=23 señ/mes=0.81 E=+0.087R win=60.9% DD=-3.5R PF=1.25
- NULL (test, 50 sims/seed): s7 p=0.340 Ereal=+0.087 p50=+0.000, s11 p=0.380 Ereal=+0.087 p50=-0.000, s23 p=0.360 Ereal=+0.087 p50=+0.000, s42 p=0.460 Ereal=+0.087 p50=+0.043
- p<=0.05 en 0/4 seeds | test E>0: True | VEREDICTO: DESCARTADA (2.5s)
- Grid=54, válidas=48. Top5 train: [({'pct': 10, 'vm': 1.2, 'k': 2.0, 'tp': 3.0}, 0.2857, 35), ({'pct': 30, 'vm': 2.0, 'k': 2.0, 'tp': 3.0}, 0.2273, 33), ({'pct': 10, 'vm': 1.2, 'k': 2.0, 'tp': 2.0}, 0.2143, 35), ({'pct': 20, 'vm': 2.0, 'k': 2.0, 'tp': 3.0}, 0.1739, 23), ({'pct': 10, 'vm': 1.2, 'k': 1.5, 'tp': 3.0}, 0.1571, 35)]
### IDEA3 squeeze_breakout | AVAXUSDT 4h | params={'pct': 30, 'vm': 2.0, 'k': 1.5, 'tp': 2.0}
- TRAIN: n=31 señ/mes=0.6 E=+0.274R win=67.7% DD=-3.0R PF=1.85
- TEST : n=23 señ/mes=1.03 E=-0.087R win=52.2% DD=-6.0R PF=0.818
- NULL (test, 50 sims/seed): s7 p=0.480 Ereal=-0.087 p50=-0.115, s11 p=0.640 Ereal=-0.087 p50=+0.059, s23 p=0.700 Ereal=-0.087 p50=+0.000, s42 p=0.620 Ereal=-0.087 p50=-0.062
- p<=0.05 en 0/4 seeds | test E>0: False | VEREDICTO: DESCARTADA (1.9s)
- Grid=54, válidas=42. Top5 train: [({'pct': 30, 'vm': 2.0, 'k': 1.5, 'tp': 2.0}, 0.2742, 31), ({'pct': 30, 'vm': 2.0, 'k': 1.5, 'tp': 3.0}, 0.2581, 31), ({'pct': 30, 'vm': 2.0, 'k': 2.0, 'tp': 3.0}, 0.1129, 31), ({'pct': 30, 'vm': 2.0, 'k': 2.0, 'tp': 2.0}, 0.0968, 31), ({'pct': 30, 'vm': 1.5, 'k': 1.5, 'tp': 2.0}, 0.0667, 60)]

## IDEA 4 — RSI + EMA(200) 4h
Idea: largo cuando precio>EMA200 y RSI(n) cruza hacia arriba el nivel lvl; stop ka*ATR, target tp*R, BE 1R, max 80 bares. Grid 54 combinaciones.
### IDEA4 rsi_ema | BTCUSDT 4h | params={'rn': 14, 'lvl': 35, 'ka': 2.0, 'tp': 2.0}
- TRAIN: n=72 señ/mes=0.92 E=+0.201R win=54.2% DD=-9.0R PF=1.483
- TEST : n=29 señ/mes=0.87 E=+0.017R win=51.7% DD=-5.5R PF=1.036
- NULL (test, 50 sims/seed): s7 p=0.540 Ereal=+0.017 p50=+0.028, s11 p=0.600 Ereal=+0.017 p50=+0.043, s23 p=0.440 Ereal=+0.017 p50=-0.028, s42 p=0.560 Ereal=+0.017 p50=+0.076
- p<=0.05 en 0/4 seeds | test E>0: True | VEREDICTO: DESCARTADA (1.0s)
- Grid=54, válidas=45. Top5 train: [({'rn': 14, 'lvl': 35, 'ka': 2.0, 'tp': 2.0}, 0.2014, 72), ({'rn': 14, 'lvl': 35, 'ka': 2.0, 'tp': 3.0}, 0.1736, 72), ({'rn': 14, 'lvl': 35, 'ka': 2.0, 'tp': 1.5}, 0.1528, 72), ({'rn': 7, 'lvl': 30, 'ka': 2.0, 'tp': 2.0}, 0.0951, 142), ({'rn': 7, 'lvl': 35, 'ka': 2.0, 'tp': 2.0}, 0.0884, 249)]
### IDEA4 rsi_ema | ETHUSDT 4h | params={'rn': 7, 'lvl': 25, 'ka': 2.0, 'tp': 2.0}
- TRAIN: n=77 señ/mes=0.99 E=+0.279R win=61.0% DD=-3.5R PF=1.741
- TEST : n=24 señ/mes=0.72 E=-0.000R win=50.0% DD=-4.5R PF=1.0
- NULL (test, 50 sims/seed): s7 p=0.540 Ereal=-0.000 p50=+0.010, s11 p=0.520 Ereal=-0.000 p50=+0.000, s23 p=0.480 Ereal=-0.000 p50=-0.000, s42 p=0.480 Ereal=-0.000 p50=-0.012
- p<=0.05 en 0/4 seeds | test E>0: False | VEREDICTO: DESCARTADA (1.1s)
- Grid=54, válidas=45. Top5 train: [({'rn': 7, 'lvl': 25, 'ka': 2.0, 'tp': 2.0}, 0.2792, 77), ({'rn': 7, 'lvl': 25, 'ka': 2.0, 'tp': 3.0}, 0.2597, 77), ({'rn': 7, 'lvl': 25, 'ka': 2.0, 'tp': 1.5}, 0.2305, 77), ({'rn': 7, 'lvl': 30, 'ka': 2.0, 'tp': 2.0}, 0.2264, 148), ({'rn': 7, 'lvl': 30, 'ka': 2.0, 'tp': 3.0}, 0.2095, 148)]
### IDEA4 rsi_ema | SOLUSDT 4h | params={'rn': 7, 'lvl': 30, 'ka': 1.0, 'tp': 2.0}
- TRAIN: n=118 señ/mes=2.23 E=+0.076R win=55.9% DD=-7.5R PF=1.173
- TEST : n=36 señ/mes=1.59 E=+0.056R win=61.1% DD=-3.0R PF=1.143
- NULL (test, 50 sims/seed): s7 p=0.280 Ereal=+0.056 p50=-0.036, s11 p=0.240 Ereal=+0.056 p50=-0.073, s23 p=0.300 Ereal=+0.056 p50=-0.082, s42 p=0.280 Ereal=+0.056 p50=-0.033
- p<=0.05 en 0/4 seeds | test E>0: True | VEREDICTO: DESCARTADA (0.7s)
- Grid=54, válidas=36. Top5 train: [({'rn': 7, 'lvl': 30, 'ka': 1.0, 'tp': 2.0}, 0.0763, 118), ({'rn': 7, 'lvl': 30, 'ka': 1.0, 'tp': 3.0}, 0.0678, 118), ({'rn': 7, 'lvl': 30, 'ka': 1.0, 'tp': 1.5}, 0.0487, 118), ({'rn': 7, 'lvl': 30, 'ka': 1.5, 'tp': 2.0}, 0.0254, 118), ({'rn': 7, 'lvl': 30, 'ka': 1.5, 'tp': 3.0}, 0.0212, 118)]
### IDEA4 rsi_ema | XRPUSDT 4h | params={'rn': 14, 'lvl': 35, 'ka': 1.0, 'tp': 1.5}
- TRAIN: n=53 señ/mes=0.74 E=+0.061R win=58.5% DD=-4.0R PF=1.148
- TEST : n=19 señ/mes=0.62 E=-0.368R win=36.8% DD=-7.0R PF=0.417
- NULL (test, 50 sims/seed): s7 p=0.860 Ereal=-0.368 p50=-0.083, s11 p=1.000 Ereal=-0.368 p50=-0.014, s23 p=0.980 Ereal=-0.368 p50=-0.025, s42 p=0.980 Ereal=-0.368 p50=-0.007
- p<=0.05 en 0/4 seeds | test E>0: False | VEREDICTO: DESCARTADA (0.9s)
- Grid=54, válidas=36. Top5 train: [({'rn': 14, 'lvl': 35, 'ka': 1.0, 'tp': 1.5}, 0.0613, 53), ({'rn': 14, 'lvl': 35, 'ka': 1.0, 'tp': 2.0}, 0.0472, 53), ({'rn': 14, 'lvl': 35, 'ka': 1.0, 'tp': 3.0}, 0.0472, 53), ({'rn': 7, 'lvl': 35, 'ka': 1.5, 'tp': 3.0}, 0.0105, 191), ({'rn': 7, 'lvl': 35, 'ka': 1.5, 'tp': 2.0}, -0.0183, 191)]
### IDEA4 rsi_ema | LINKUSDT 4h | params={'rn': 14, 'lvl': 30, 'ka': 2.0, 'tp': 1.5}
- TRAIN: n=15 señ/mes=0.23 E=+0.550R win=73.3% DD=-3.0R PF=3.062
- TEST : n=4 señ/mes=0.14 E=-0.250R win=50.0% DD=-1.0R PF=0.5
- NULL (test, 50 sims/seed): s7 p=0.880 Ereal=-0.250 p50=+0.125, s11 p=0.780 Ereal=-0.250 p50=-0.000, s23 p=0.780 Ereal=-0.250 p50=+0.125, s42 p=0.680 Ereal=-0.250 p50=+0.125
- p<=0.05 en 0/4 seeds | test E>0: False | VEREDICTO: DESCARTADA (0.8s)
- Grid=54, válidas=45. Top5 train: [({'rn': 14, 'lvl': 30, 'ka': 2.0, 'tp': 1.5}, 0.55, 15), ({'rn': 14, 'lvl': 30, 'ka': 2.0, 'tp': 2.0}, 0.5, 15), ({'rn': 14, 'lvl': 30, 'ka': 2.0, 'tp': 3.0}, 0.2, 15), ({'rn': 7, 'lvl': 25, 'ka': 2.0, 'tp': 1.5}, 0.1336, 73), ({'rn': 7, 'lvl': 25, 'ka': 2.0, 'tp': 2.0}, 0.1164, 73)]
### IDEA4 rsi_ema | AVAXUSDT 4h | params={'rn': 7, 'lvl': 35, 'ka': 2.0, 'tp': 3.0}
- TRAIN: n=144 señ/mes=2.78 E=-0.031R win=43.8% DD=-17.0R PF=0.942
- TEST : n=54 señ/mes=2.43 E=+0.093R win=55.6% DD=-7.5R PF=1.227
- NULL (test, 50 sims/seed): s7 p=0.140 Ereal=+0.093 p50=-0.099, s11 p=0.040 Ereal=+0.093 p50=-0.067, s23 p=0.100 Ereal=+0.093 p50=-0.088, s42 p=0.060 Ereal=+0.093 p50=-0.125
- p<=0.05 en 1/4 seeds | test E>0: True | VEREDICTO: DESCARTADA (0.7s)
- Grid=54, válidas=36. Top5 train: [({'rn': 7, 'lvl': 35, 'ka': 2.0, 'tp': 3.0}, -0.0312, 144), ({'rn': 7, 'lvl': 35, 'ka': 2.0, 'tp': 2.0}, -0.066, 144), ({'rn': 7, 'lvl': 35, 'ka': 2.0, 'tp': 1.5}, -0.1007, 144), ({'rn': 7, 'lvl': 30, 'ka': 2.0, 'tp': 2.0}, -0.15, 90), ({'rn': 7, 'lvl': 35, 'ka': 1.5, 'tp': 3.0}, -0.1771, 144)]

## IDEA 5 — MACD + ATR 4h
Idea: largo cuando histograma MACD cruza de negativo a positivo con precio>EMA200; stop ka*ATR, target tp*R, BE 1R, max 100 bares. Grid 27 combinaciones.
### IDEA5 macd_atr | BTCUSDT 4h | params={'mf': 8, 'ms': 21, 'ka': 2.0, 'tp': 4.0}
- TRAIN: n=313 señ/mes=4.02 E=+0.214R win=56.2% DD=-23.5R PF=1.528
- TEST : n=127 señ/mes=3.81 E=-0.146R win=48.0% DD=-22.5R PF=0.706
- NULL (test, 50 sims/seed): s7 p=0.920 Ereal=-0.146 p50=-0.014, s11 p=0.840 Ereal=-0.146 p50=-0.032, s23 p=0.840 Ereal=-0.146 p50=-0.042, s42 p=0.880 Ereal=-0.146 p50=-0.052
- p<=0.05 en 0/4 seeds | test E>0: False | VEREDICTO: DESCARTADA (1.0s)
- Grid=27, válidas=27. Top5 train: [({'mf': 8, 'ms': 21, 'ka': 2.0, 'tp': 4.0}, 0.2141, 313), ({'mf': 12, 'ms': 26, 'ka': 3.0, 'tp': 4.0}, 0.2125, 273), ({'mf': 8, 'ms': 21, 'ka': 2.0, 'tp': 3.0}, 0.2045, 313), ({'mf': 8, 'ms': 21, 'ka': 3.0, 'tp': 4.0}, 0.2013, 313), ({'mf': 8, 'ms': 21, 'ka': 2.0, 'tp': 2.0}, 0.1949, 313)]
### IDEA5 macd_atr | ETHUSDT 4h | params={'mf': 8, 'ms': 21, 'ka': 3.0, 'tp': 2.0}
- TRAIN: n=313 señ/mes=4.02 E=+0.254R win=59.7% DD=-8.0R PF=1.685
- TEST : n=110 señ/mes=3.3 E=-0.104R win=42.7% DD=-12.0R PF=0.802
- NULL (test, 50 sims/seed): s7 p=0.880 Ereal=-0.105 p50=+0.004, s11 p=0.960 Ereal=-0.105 p50=+0.041, s23 p=0.820 Ereal=-0.105 p50=+0.040, s42 p=0.820 Ereal=-0.105 p50=+0.018
- p<=0.05 en 0/4 seeds | test E>0: False | VEREDICTO: DESCARTADA (1.0s)
- Grid=27, válidas=27. Top5 train: [({'mf': 8, 'ms': 21, 'ka': 3.0, 'tp': 2.0}, 0.254, 313), ({'mf': 8, 'ms': 21, 'ka': 3.0, 'tp': 3.0}, 0.254, 313), ({'mf': 5, 'ms': 13, 'ka': 3.0, 'tp': 3.0}, 0.2488, 420), ({'mf': 5, 'ms': 13, 'ka': 3.0, 'tp': 2.0}, 0.2393, 420), ({'mf': 12, 'ms': 26, 'ka': 3.0, 'tp': 3.0}, 0.2059, 272)]
### IDEA5 macd_atr | SOLUSDT 4h | params={'mf': 5, 'ms': 13, 'ka': 3.0, 'tp': 3.0}
- TRAIN: n=292 señ/mes=5.53 E=+0.151R win=47.6% DD=-26.0R PF=1.333
- TEST : n=106 señ/mes=4.68 E=-0.024R win=45.3% DD=-19.0R PF=0.952
- NULL (test, 50 sims/seed): s7 p=0.300 Ereal=-0.024 p50=-0.098, s11 p=0.120 Ereal=-0.024 p50=-0.123, s23 p=0.160 Ereal=-0.024 p50=-0.113, s42 p=0.240 Ereal=-0.024 p50=-0.095
- p<=0.05 en 0/4 seeds | test E>0: False | VEREDICTO: DESCARTADA (0.7s)
- Grid=27, válidas=27. Top5 train: [({'mf': 5, 'ms': 13, 'ka': 3.0, 'tp': 3.0}, 0.1507, 292), ({'mf': 5, 'ms': 13, 'ka': 1.5, 'tp': 4.0}, 0.1438, 292), ({'mf': 5, 'ms': 13, 'ka': 3.0, 'tp': 4.0}, 0.137, 292), ({'mf': 12, 'ms': 26, 'ka': 2.0, 'tp': 4.0}, 0.1332, 184), ({'mf': 5, 'ms': 13, 'ka': 3.0, 'tp': 2.0}, 0.1318, 292)]
### IDEA5 macd_atr | XRPUSDT 4h | params={'mf': 12, 'ms': 26, 'ka': 2.0, 'tp': 3.0}
- TRAIN: n=242 señ/mes=3.36 E=+0.021R win=49.6% DD=-21.0R PF=1.041
- TEST : n=92 señ/mes=2.99 E=-0.152R win=46.7% DD=-22.5R PF=0.714
- NULL (test, 50 sims/seed): s7 p=0.800 Ereal=-0.152 p50=-0.050, s11 p=0.660 Ereal=-0.152 p50=-0.100, s23 p=0.860 Ereal=-0.152 p50=-0.071, s42 p=0.760 Ereal=-0.152 p50=-0.071
- p<=0.05 en 0/4 seeds | test E>0: False | VEREDICTO: DESCARTADA (0.9s)
- Grid=27, válidas=27. Top5 train: [({'mf': 12, 'ms': 26, 'ka': 2.0, 'tp': 3.0}, 0.0207, 242), ({'mf': 12, 'ms': 26, 'ka': 2.0, 'tp': 4.0}, 0.0062, 242), ({'mf': 12, 'ms': 26, 'ka': 1.5, 'tp': 4.0}, 0.0, 242), ({'mf': 5, 'ms': 13, 'ka': 1.5, 'tp': 4.0}, -0.01, 350), ({'mf': 8, 'ms': 21, 'ka': 2.0, 'tp': 3.0}, -0.0107, 281)]
### IDEA5 macd_atr | LINKUSDT 4h | params={'mf': 8, 'ms': 21, 'ka': 3.0, 'tp': 2.0}
- TRAIN: n=308 señ/mes=4.67 E=+0.118R win=53.6% DD=-17.0R PF=1.287
- TEST : n=102 señ/mes=3.61 E=-0.029R win=49.0% DD=-22.5R PF=0.94
- NULL (test, 50 sims/seed): s7 p=0.840 Ereal=-0.029 p50=+0.070, s11 p=0.760 Ereal=-0.029 p50=+0.079, s23 p=0.820 Ereal=-0.029 p50=+0.052, s42 p=0.840 Ereal=-0.029 p50=+0.115
- p<=0.05 en 0/4 seeds | test E>0: False | VEREDICTO: DESCARTADA (0.9s)
- Grid=27, válidas=27. Top5 train: [({'mf': 8, 'ms': 21, 'ka': 3.0, 'tp': 2.0}, 0.1185, 308), ({'mf': 12, 'ms': 26, 'ka': 3.0, 'tp': 2.0}, 0.1164, 262), ({'mf': 5, 'ms': 13, 'ka': 3.0, 'tp': 2.0}, 0.1019, 417), ({'mf': 12, 'ms': 26, 'ka': 3.0, 'tp': 3.0}, 0.0897, 262), ({'mf': 8, 'ms': 21, 'ka': 3.0, 'tp': 3.0}, 0.0828, 308)]
### IDEA5 macd_atr | AVAXUSDT 4h | params={'mf': 12, 'ms': 26, 'ka': 3.0, 'tp': 3.0}
- TRAIN: n=155 señ/mes=2.99 E=+0.194R win=55.5% DD=-11.0R PF=1.469
- TEST : n=58 señ/mes=2.61 E=-0.224R win=43.1% DD=-13.0R PF=0.567
- NULL (test, 50 sims/seed): s7 p=0.660 Ereal=-0.224 p50=-0.154, s11 p=0.680 Ereal=-0.224 p50=-0.122, s23 p=0.700 Ereal=-0.224 p50=-0.149, s42 p=0.600 Ereal=-0.224 p50=-0.191
- p<=0.05 en 0/4 seeds | test E>0: False | VEREDICTO: DESCARTADA (0.6s)
- Grid=27, válidas=27. Top5 train: [({'mf': 12, 'ms': 26, 'ka': 3.0, 'tp': 3.0}, 0.1935, 155), ({'mf': 12, 'ms': 26, 'ka': 3.0, 'tp': 2.0}, 0.1903, 155), ({'mf': 12, 'ms': 26, 'ka': 3.0, 'tp': 4.0}, 0.1806, 155), ({'mf': 8, 'ms': 21, 'ka': 3.0, 'tp': 3.0}, 0.1397, 179), ({'mf': 5, 'ms': 13, 'ka': 3.0, 'tp': 3.0}, 0.1386, 249)]

## IDEA 6 — Momentum 1d EMA cross + filtro de volatilidad + trailing
Idea: cruce alcista EMA(ef)/EMA(es) en 1d (re-muestreada de 4h), solo si ATR14/close>=minatr; stop ka*ATR, target tp*R, trailing a partir de ts*R con distancia td*R, max 150 velas. Grid 32 combinaciones.
### IDEA6 momentum_1d_atr | BTCUSDT 1d | params={'ef': 20, 'es': 50, 'ka': 3.0, 'tp': 4.0, 'minatr': 0.01}
- TRAIN: n=16 señ/mes=0.21 E=-0.094R win=18.8% DD=-5.0R PF=0.833
- TEST : n=9 señ/mes=0.27 E=-0.056R win=11.1% DD=-2.0R PF=0.833
- NULL (test, 50 sims/seed): s7 p=0.180 Ereal=-0.056 p50=-0.333, s11 p=0.220 Ereal=-0.056 p50=-0.375, s23 p=0.320 Ereal=-0.056 p50=-0.188, s42 p=0.160 Ereal=-0.056 p50=-0.350
- p<=0.05 en 0/4 seeds | test E>0: False | VEREDICTO: DESCARTADA (0.2s)
- Grid=32, válidas=16. Top5 train: [({'ef': 20, 'es': 50, 'ka': 3.0, 'tp': 4.0, 'minatr': 0.01}, -0.0938, 16), ({'ef': 20, 'es': 50, 'ka': 3.0, 'tp': 4.0, 'minatr': 0.02}, -0.0938, 16), ({'ef': 10, 'es': 50, 'ka': 3.0, 'tp': 4.0, 'minatr': 0.01}, -0.1458, 24), ({'ef': 10, 'es': 50, 'ka': 3.0, 'tp': 6.0, 'minatr': 0.01}, -0.1667, 24), ({'ef': 10, 'es': 50, 'ka': 2.0, 'tp': 4.0, 'minatr': 0.01}, -0.2292, 24)]
### IDEA6 momentum_1d_atr | ETHUSDT 1d | params={'ef': 10, 'es': 50, 'ka': 2.0, 'tp': 4.0, 'minatr': 0.01}
- TRAIN: n=22 señ/mes=0.28 E=+0.295R win=22.7% DD=-4.0R PF=2.083
- TEST : n=12 señ/mes=0.36 E=-0.458R win=8.3% DD=-5.5R PF=0.312
- NULL (test, 50 sims/seed): s7 p=0.780 Ereal=-0.458 p50=-0.300, s11 p=0.860 Ereal=-0.458 p50=-0.227, s23 p=0.760 Ereal=-0.458 p50=-0.273, s42 p=0.740 Ereal=-0.458 p50=-0.346
- p<=0.05 en 0/4 seeds | test E>0: False | VEREDICTO: DESCARTADA (0.1s)
- Grid=32, válidas=16. Top5 train: [({'ef': 10, 'es': 50, 'ka': 2.0, 'tp': 4.0, 'minatr': 0.01}, 0.2955, 22), ({'ef': 10, 'es': 50, 'ka': 2.0, 'tp': 4.0, 'minatr': 0.02}, 0.2955, 22), ({'ef': 20, 'es': 50, 'ka': 2.0, 'tp': 4.0, 'minatr': 0.01}, 0.2778, 18), ({'ef': 20, 'es': 50, 'ka': 2.0, 'tp': 4.0, 'minatr': 0.02}, 0.2778, 18), ({'ef': 20, 'es': 50, 'ka': 2.0, 'tp': 6.0, 'minatr': 0.01}, 0.1111, 18)]
### IDEA6 momentum_1d_atr | BNBUSDT 1d | params={'ef': 10, 'es': 50, 'ka': 3.0, 'tp': 4.0, 'minatr': 0.01}
- TRAIN: n=24 señ/mes=0.32 E=+0.333R win=25.0% DD=-4.0R PF=2.143
- TEST : n=11 señ/mes=0.34 E=+0.227R win=27.3% DD=-4.0R PF=1.5
- NULL (test, 50 sims/seed): s7 p=0.080 Ereal=+0.227 p50=-0.227, s11 p=0.100 Ereal=+0.227 p50=-0.206, s23 p=0.120 Ereal=+0.227 p50=-0.206, s42 p=0.140 Ereal=+0.227 p50=-0.167
- p<=0.05 en 0/4 seeds | test E>0: True | VEREDICTO: DESCARTADA (0.1s)
- Grid=32, válidas=24. Top5 train: [({'ef': 10, 'es': 50, 'ka': 3.0, 'tp': 4.0, 'minatr': 0.01}, 0.3333, 24), ({'ef': 10, 'es': 50, 'ka': 3.0, 'tp': 4.0, 'minatr': 0.02}, 0.3333, 24), ({'ef': 10, 'es': 50, 'ka': 2.0, 'tp': 4.0, 'minatr': 0.01}, 0.2917, 24), ({'ef': 10, 'es': 50, 'ka': 2.0, 'tp': 4.0, 'minatr': 0.02}, 0.2917, 24), ({'ef': 10, 'es': 100, 'ka': 2.0, 'tp': 4.0, 'minatr': 0.01}, 0.1579, 19)]
### IDEA6 momentum_1d_atr | SOLUSDT 1d | params={'ef': 10, 'es': 50, 'ka': 3.0, 'tp': 4.0, 'minatr': 0.01}
- TRAIN: n=17 señ/mes=0.32 E=+0.324R win=29.4% DD=-5.0R PF=1.786
- TEST : n=7 señ/mes=0.31 E=+0.071R win=14.3% DD=-2.0R PF=1.25
- NULL (test, 50 sims/seed): s7 p=0.100 Ereal=+0.071 p50=-0.400, s11 p=0.100 Ereal=+0.071 p50=-0.364, s23 p=0.220 Ereal=+0.071 p50=-0.375, s42 p=0.140 Ereal=+0.071 p50=-0.375
- p<=0.05 en 0/4 seeds | test E>0: True | VEREDICTO: DESCARTADA (0.1s)
- Grid=32, válidas=8. Top5 train: [({'ef': 10, 'es': 50, 'ka': 3.0, 'tp': 4.0, 'minatr': 0.01}, 0.3235, 17), ({'ef': 10, 'es': 50, 'ka': 3.0, 'tp': 4.0, 'minatr': 0.02}, 0.3235, 17), ({'ef': 10, 'es': 50, 'ka': 3.0, 'tp': 6.0, 'minatr': 0.01}, -0.4118, 17), ({'ef': 10, 'es': 50, 'ka': 3.0, 'tp': 6.0, 'minatr': 0.02}, -0.4118, 17), ({'ef': 10, 'es': 50, 'ka': 2.0, 'tp': 4.0, 'minatr': 0.01}, -0.5882, 17)]
### IDEA6 momentum_1d_atr | XRPUSDT 1d | params={'ef': 10, 'es': 100, 'ka': 3.0, 'tp': 4.0, 'minatr': 0.01}
- TRAIN: n=22 señ/mes=0.31 E=-0.045R win=9.1% DD=-4.0R PF=0.833
- TEST : n=6 señ/mes=0.19 E=-0.083R win=16.7% DD=-2.0R PF=0.833
- NULL (test, 50 sims/seed): s7 p=0.080 Ereal=-0.083 p50=-0.500, s11 p=0.120 Ereal=-0.083 p50=-0.500, s23 p=0.160 Ereal=-0.083 p50=-0.450, s42 p=0.100 Ereal=-0.083 p50=-0.500
- p<=0.05 en 0/4 seeds | test E>0: False | VEREDICTO: DESCARTADA (0.1s)
- Grid=32, válidas=32. Top5 train: [({'ef': 10, 'es': 100, 'ka': 3.0, 'tp': 4.0, 'minatr': 0.01}, -0.0455, 22), ({'ef': 10, 'es': 100, 'ka': 3.0, 'tp': 4.0, 'minatr': 0.02}, -0.0455, 22), ({'ef': 20, 'es': 50, 'ka': 3.0, 'tp': 4.0, 'minatr': 0.01}, -0.2174, 23), ({'ef': 20, 'es': 50, 'ka': 3.0, 'tp': 4.0, 'minatr': 0.02}, -0.2174, 23), ({'ef': 10, 'es': 50, 'ka': 3.0, 'tp': 4.0, 'minatr': 0.01}, -0.25, 26)]
### IDEA6 momentum_1d_atr | ADAUSDT 1d | params={'ef': 10, 'es': 50, 'ka': 3.0, 'tp': 4.0, 'minatr': 0.01}
- TRAIN: n=20 señ/mes=0.28 E=+0.350R win=30.0% DD=-6.0R PF=1.875
- TEST : n=10 señ/mes=0.32 E=-0.600R win=0.0% DD=-6.0R PF=0.0
- NULL (test, 50 sims/seed): s7 p=0.720 Ereal=-0.600 p50=-0.500, s11 p=0.700 Ereal=-0.600 p50=-0.545, s23 p=0.600 Ereal=-0.600 p50=-0.500, s42 p=0.800 Ereal=-0.600 p50=-0.455
- p<=0.05 en 0/4 seeds | test E>0: False | VEREDICTO: DESCARTADA (0.1s)
- Grid=32, válidas=8. Top5 train: [({'ef': 10, 'es': 50, 'ka': 3.0, 'tp': 4.0, 'minatr': 0.01}, 0.35, 20), ({'ef': 10, 'es': 50, 'ka': 3.0, 'tp': 4.0, 'minatr': 0.02}, 0.35, 20), ({'ef': 10, 'es': 50, 'ka': 2.0, 'tp': 4.0, 'minatr': 0.01}, 0.15, 20), ({'ef': 10, 'es': 50, 'ka': 2.0, 'tp': 4.0, 'minatr': 0.02}, 0.15, 20), ({'ef': 10, 'es': 50, 'ka': 2.0, 'tp': 6.0, 'minatr': 0.01}, -0.175, 20)]

## IDEA 7 — Donchian breakout con trailing ATR 4h (estilo Turtle)
Idea: ruptura del máximo de lb bares en 4h; stop ka*ATR, target tp*R, trailing desde ts*R con distancia td*R, max 120 bares. Grid 54 combinaciones.
### IDEA7 donchian_trail | BTCUSDT 4h | params={'lb': 40, 'ka': 2.5, 'tp': 3.0, 'ts': 2.0, 'td': 2.0}
- TRAIN: n=542 señ/mes=6.96 E=+0.070R win=23.2% DD=-50.0R PF=1.178
- TEST : n=212 señ/mes=6.36 E=-0.132R win=17.9% DD=-41.0R PF=0.731
- NULL (test, 50 sims/seed): s7 p=0.600 Ereal=-0.132 p50=-0.089, s11 p=0.500 Ereal=-0.132 p50=-0.127, s23 p=0.440 Ereal=-0.132 p50=-0.149, s42 p=0.440 Ereal=-0.132 p50=-0.148
- p<=0.05 en 0/4 seeds | test E>0: False | VEREDICTO: DESCARTADA (1.2s)
- Grid=54, válidas=54. Top5 train: [({'lb': 40, 'ka': 2.5, 'tp': 3.0, 'ts': 2.0, 'td': 2.0}, 0.0701, 542), ({'lb': 60, 'ka': 2.5, 'tp': 3.0, 'ts': 2.0, 'td': 2.0}, 0.0513, 468), ({'lb': 40, 'ka': 2.5, 'tp': 3.0, 'ts': 1.0, 'td': 2.0}, 0.048, 542), ({'lb': 60, 'ka': 2.5, 'tp': 3.0, 'ts': 1.0, 'td': 2.0}, 0.0256, 468), ({'lb': 20, 'ka': 2.5, 'tp': 3.0, 'ts': 2.0, 'td': 2.0}, 0.0251, 756)]
### IDEA7 donchian_trail | ETHUSDT 4h | params={'lb': 60, 'ka': 2.5, 'tp': 3.0, 'ts': 2.0, 'td': 2.0}
- TRAIN: n=470 señ/mes=6.03 E=+0.166R win=27.4% DD=-28.0R PF=1.433
- TEST : n=150 señ/mes=4.5 E=-0.153R win=17.3% DD=-36.0R PF=0.693
- NULL (test, 50 sims/seed): s7 p=0.520 Ereal=-0.153 p50=-0.141, s11 p=0.380 Ereal=-0.153 p50=-0.172, s23 p=0.520 Ereal=-0.153 p50=-0.141, s42 p=0.500 Ereal=-0.153 p50=-0.136
- p<=0.05 en 0/4 seeds | test E>0: False | VEREDICTO: DESCARTADA (1.4s)
- Grid=54, válidas=54. Top5 train: [({'lb': 60, 'ka': 2.5, 'tp': 3.0, 'ts': 2.0, 'td': 2.0}, 0.166, 470), ({'lb': 40, 'ka': 2.5, 'tp': 3.0, 'ts': 2.0, 'td': 2.0}, 0.1204, 565), ({'lb': 60, 'ka': 2.5, 'tp': 3.0, 'ts': 1.0, 'td': 2.0}, 0.1191, 470), ({'lb': 60, 'ka': 2.5, 'tp': 4.0, 'ts': 2.0, 'td': 2.0}, 0.0798, 470), ({'lb': 40, 'ka': 2.5, 'tp': 3.0, 'ts': 1.0, 'td': 2.0}, 0.0743, 565)]
### IDEA7 donchian_trail | SOLUSDT 4h | params={'lb': 20, 'ka': 2.5, 'tp': 3.0, 'ts': 2.0, 'td': 2.0}
- TRAIN: n=520 señ/mes=9.84 E=+0.017R win=24.2% DD=-60.0R PF=1.037
- TEST : n=204 señ/mes=9.01 E=-0.108R win=19.1% DD=-50.0R PF=0.78
- NULL (test, 50 sims/seed): s7 p=0.260 Ereal=-0.108 p50=-0.205, s11 p=0.220 Ereal=-0.108 p50=-0.215, s23 p=0.240 Ereal=-0.108 p50=-0.199, s42 p=0.260 Ereal=-0.108 p50=-0.236
- p<=0.05 en 0/4 seeds | test E>0: False | VEREDICTO: DESCARTADA (0.8s)
- Grid=54, válidas=54. Top5 train: [({'lb': 20, 'ka': 2.5, 'tp': 3.0, 'ts': 2.0, 'td': 2.0}, 0.0173, 520), ({'lb': 60, 'ka': 2.5, 'tp': 3.0, 'ts': 2.0, 'td': 2.0}, -0.003, 336), ({'lb': 20, 'ka': 2.5, 'tp': 3.0, 'ts': 1.0, 'td': 2.0}, -0.0173, 520), ({'lb': 40, 'ka': 2.5, 'tp': 3.0, 'ts': 2.0, 'td': 2.0}, -0.023, 392), ({'lb': 60, 'ka': 2.5, 'tp': 3.0, 'ts': 1.0, 'td': 2.0}, -0.0387, 336)]
### IDEA7 donchian_trail | XRPUSDT 4h | params={'lb': 40, 'ka': 2.5, 'tp': 3.0, 'ts': 2.0, 'td': 2.0}
- TRAIN: n=332 señ/mes=4.62 E=-0.187R win=13.9% DD=-64.0R PF=0.597
- TEST : n=165 señ/mes=5.36 E=-0.042R win=19.4% DD=-27.0R PF=0.901
- NULL (test, 50 sims/seed): s7 p=0.140 Ereal=-0.042 p50=-0.200, s11 p=0.120 Ereal=-0.042 p50=-0.245, s23 p=0.200 Ereal=-0.042 p50=-0.219, s42 p=0.120 Ereal=-0.042 p50=-0.260
- p<=0.05 en 0/4 seeds | test E>0: False | VEREDICTO: DESCARTADA (1.0s)
- Grid=54, válidas=54. Top5 train: [({'lb': 40, 'ka': 2.5, 'tp': 3.0, 'ts': 2.0, 'td': 2.0}, -0.1867, 332), ({'lb': 20, 'ka': 2.5, 'tp': 3.0, 'ts': 2.0, 'td': 2.0}, -0.2008, 503), ({'lb': 60, 'ka': 2.5, 'tp': 3.0, 'ts': 2.0, 'td': 2.0}, -0.2052, 268), ({'lb': 40, 'ka': 2.5, 'tp': 3.0, 'ts': 1.0, 'td': 2.0}, -0.2108, 332), ({'lb': 60, 'ka': 2.5, 'tp': 3.0, 'ts': 1.0, 'td': 2.0}, -0.2127, 268)]
### IDEA7 donchian_trail | LINKUSDT 4h | params={'lb': 20, 'ka': 2.5, 'tp': 3.0, 'ts': 2.0, 'td': 2.0}
- TRAIN: n=652 señ/mes=9.88 E=-0.058R win=21.0% DD=-93.0R PF=0.878
- TEST : n=280 señ/mes=9.9 E=-0.139R win=17.5% DD=-58.0R PF=0.715
- NULL (test, 50 sims/seed): s7 p=0.720 Ereal=-0.139 p50=-0.061, s11 p=0.520 Ereal=-0.139 p50=-0.137, s23 p=0.560 Ereal=-0.139 p50=-0.120, s42 p=0.660 Ereal=-0.139 p50=-0.070
- p<=0.05 en 0/4 seeds | test E>0: False | VEREDICTO: DESCARTADA (0.9s)
- Grid=54, válidas=54. Top5 train: [({'lb': 20, 'ka': 2.5, 'tp': 3.0, 'ts': 2.0, 'td': 2.0}, -0.0583, 652), ({'lb': 20, 'ka': 2.5, 'tp': 3.0, 'ts': 1.0, 'td': 2.0}, -0.0859, 652), ({'lb': 40, 'ka': 2.5, 'tp': 3.0, 'ts': 2.0, 'td': 2.0}, -0.1009, 446), ({'lb': 40, 'ka': 2.5, 'tp': 3.0, 'ts': 1.0, 'td': 2.0}, -0.1323, 446), ({'lb': 60, 'ka': 2.5, 'tp': 3.0, 'ts': 2.0, 'td': 2.0}, -0.1549, 355)]
### IDEA7 donchian_trail | AVAXUSDT 4h | params={'lb': 20, 'ka': 2.5, 'tp': 3.0, 'ts': 2.0, 'td': 2.0}
- TRAIN: n=511 señ/mes=9.85 E=-0.059R win=20.4% DD=-67.0R PF=0.874
- TEST : n=176 señ/mes=7.92 E=-0.301R win=14.8% DD=-53.0R PF=0.495
- NULL (test, 50 sims/seed): s7 p=0.540 Ereal=-0.301 p50=-0.250, s11 p=0.740 Ereal=-0.301 p50=-0.198, s23 p=0.640 Ereal=-0.301 p50=-0.244, s42 p=0.700 Ereal=-0.301 p50=-0.224
- p<=0.05 en 0/4 seeds | test E>0: False | VEREDICTO: DESCARTADA (0.6s)
- Grid=54, válidas=54. Top5 train: [({'lb': 20, 'ka': 2.5, 'tp': 3.0, 'ts': 2.0, 'td': 2.0}, -0.0587, 511), ({'lb': 40, 'ka': 2.5, 'tp': 3.0, 'ts': 2.0, 'td': 2.0}, -0.0988, 344), ({'lb': 20, 'ka': 2.5, 'tp': 3.0, 'ts': 1.0, 'td': 2.0}, -0.1018, 511), ({'lb': 60, 'ka': 2.5, 'tp': 3.0, 'ts': 2.0, 'td': 2.0}, -0.1221, 303), ({'lb': 20, 'ka': 2.0, 'tp': 3.0, 'ts': 2.0, 'td': 2.0}, -0.1311, 511)]

## IDEA 8 — Multi-timeframe: scalp 1h con filtro EMA200 de 4h
Idea: en 1h, solo largos si precio>EMA200 del 4h correspondiente; RSI(n) 1h cruza sobre lvl; stop ka*ATR(14) 1h, target tp*R, BE 1R, max 24 velas. Grid 36 combinaciones. Ventana últimas 20.000 velas 1h.
### IDEA8 mtf_scalp_1h_4h | BTCUSDT 1h+4h | params={'rn': 7, 'lvl': 35, 'ka': 2.0, 'tp': 2.0}
- TRAIN: n=324 señ/mes=16.91 E=-0.037R win=36.4% DD=-18.0R PF=0.906
- TEST : n=140 señ/mes=17.05 E=-0.164R win=31.4% DD=-28.0R PF=0.662
- NULL (test, 50 sims/seed): s7 p=0.580 Ereal=-0.164 p50=-0.139, s11 p=0.680 Ereal=-0.164 p50=-0.118, s23 p=0.620 Ereal=-0.164 p50=-0.132, s42 p=0.540 Ereal=-0.164 p50=-0.142
- p<=0.05 en 0/4 seeds | test E>0: False | VEREDICTO: DESCARTADA (1.5s)
- Grid=36, válidas=30. Top5 train: [({'rn': 7, 'lvl': 35, 'ka': 2.0, 'tp': 2.0}, -0.037, 324), ({'rn': 7, 'lvl': 35, 'ka': 1.5, 'tp': 2.0}, -0.0432, 324), ({'rn': 7, 'lvl': 30, 'ka': 2.0, 'tp': 2.0}, -0.0488, 205), ({'rn': 7, 'lvl': 30, 'ka': 1.5, 'tp': 2.0}, -0.0683, 205), ({'rn': 7, 'lvl': 25, 'ka': 1.5, 'tp': 2.0}, -0.1143, 105)]
### IDEA8 mtf_scalp_1h_4h | ETCUSDT 1h+4h | params={'rn': 14, 'lvl': 30, 'ka': 1.0, 'tp': 2.0}
- TRAIN: n=27 señ/mes=1.41 E=-0.204R win=48.1% DD=-6.0R PF=0.607
- TEST : n=12 señ/mes=1.46 E=+0.042R win=41.7% DD=-1.5R PF=1.167
- NULL (test, 50 sims/seed): s7 p=0.720 Ereal=+0.042 p50=+0.145, s11 p=0.780 Ereal=+0.042 p50=+0.132, s23 p=0.620 Ereal=+0.042 p50=+0.064, s42 p=0.640 Ereal=+0.042 p50=+0.092
- p<=0.05 en 0/4 seeds | test E>0: True | VEREDICTO: DESCARTADA (1.4s)
- Grid=36, válidas=30. Top5 train: [({'rn': 14, 'lvl': 30, 'ka': 1.0, 'tp': 2.0}, -0.2037, 27), ({'rn': 14, 'lvl': 35, 'ka': 2.0, 'tp': 2.0}, -0.2042, 71), ({'rn': 14, 'lvl': 30, 'ka': 1.0, 'tp': 3.0}, -0.2407, 27), ({'rn': 7, 'lvl': 35, 'ka': 1.5, 'tp': 2.0}, -0.2526, 192), ({'rn': 7, 'lvl': 25, 'ka': 2.0, 'tp': 2.0}, -0.2628, 78)]
### IDEA8 mtf_scalp_1h_4h | HBARUSDT 1h+4h | params={'rn': 14, 'lvl': 35, 'ka': 1.5, 'tp': 2.0}
- TRAIN: n=75 señ/mes=3.91 E=-0.027R win=45.3% DD=-13.5R PF=0.941
- TEST : n=31 señ/mes=3.78 E=-0.161R win=38.7% DD=-9.0R PF=0.667
- NULL (test, 50 sims/seed): s7 p=0.580 Ereal=-0.161 p50=-0.129, s11 p=0.600 Ereal=-0.161 p50=-0.064, s23 p=0.640 Ereal=-0.161 p50=-0.063, s42 p=0.680 Ereal=-0.161 p50=-0.102
- p<=0.05 en 0/4 seeds | test E>0: False | VEREDICTO: DESCARTADA (1.4s)
- Grid=36, válidas=30. Top5 train: [({'rn': 14, 'lvl': 35, 'ka': 1.5, 'tp': 2.0}, -0.0267, 75), ({'rn': 14, 'lvl': 35, 'ka': 1.0, 'tp': 2.0}, -0.0667, 75), ({'rn': 14, 'lvl': 30, 'ka': 1.5, 'tp': 2.0}, -0.087, 23), ({'rn': 14, 'lvl': 35, 'ka': 1.0, 'tp': 3.0}, -0.0933, 75), ({'rn': 7, 'lvl': 25, 'ka': 1.5, 'tp': 2.0}, -0.1558, 77)]
### IDEA8 mtf_scalp_1h_4h | THETAUSDT 1h+4h | params={'rn': 14, 'lvl': 35, 'ka': 1.5, 'tp': 2.0}
- TRAIN: n=53 señ/mes=2.77 E=+0.028R win=50.9% DD=-11.0R PF=1.063
- TEST : n=39 señ/mes=4.75 E=-0.269R win=38.5% DD=-13.0R PF=0.543
- NULL (test, 50 sims/seed): s7 p=1.000 Ereal=-0.269 p50=+0.084, s11 p=1.000 Ereal=-0.269 p50=+0.115, s23 p=1.000 Ereal=-0.269 p50=+0.087, s42 p=1.000 Ereal=-0.269 p50=+0.116
- p<=0.05 en 0/4 seeds | test E>0: False | VEREDICTO: DESCARTADA (1.4s)
- Grid=36, válidas=30. Top5 train: [({'rn': 14, 'lvl': 35, 'ka': 1.5, 'tp': 2.0}, 0.0283, 53), ({'rn': 7, 'lvl': 35, 'ka': 1.5, 'tp': 2.0}, 0.0029, 175), ({'rn': 7, 'lvl': 25, 'ka': 1.5, 'tp': 2.0}, -0.1207, 58), ({'rn': 7, 'lvl': 30, 'ka': 1.5, 'tp': 2.0}, -0.1217, 115), ({'rn': 14, 'lvl': 35, 'ka': 1.0, 'tp': 3.0}, -0.1509, 53)]

## IDEA 9 — Flash-crash: cierre bajo BB inferior + volumen en 1d
Idea: cierre por debajo de BB(20,k) con volumen>vm*SMA(vol,20) en 1d (re-muestreada de 4h); entrada al cierre, stop=low de la vela, target=rebote '../../../del centro de la banda. max 40 velas. Grid 27 combinaciones.
### IDEA9 bb_crash_1d | BTCUSDT 1d | params={'bbk': 2.5, 'vm': 1.5, 'reb': 0.3}
- TRAIN: n=30 señ/mes=0.39 E=-0.147R win=13.3% DD=-9.36R PF=0.661
- TEST : n=15 señ/mes=0.45 E=-0.010R win=20.0% DD=-2.0R PF=0.962
- NULL (test, 50 sims/seed): s7 p=0.580 Ereal=-0.010 p50=+0.199, s11 p=0.560 Ereal=-0.010 p50=+0.040, s23 p=0.480 Ereal=-0.010 p50=-0.060, s42 p=0.620 Ereal=-0.010 p50=+0.304
- p<=0.05 en 0/4 seeds | test E>0: False | VEREDICTO: DESCARTADA (0.4s)
- Grid=27, válidas=12. Top5 train: [({'bbk': 2.5, 'vm': 1.5, 'reb': 0.3}, -0.147, 30), ({'bbk': 2.0, 'vm': 1.5, 'reb': 0.3}, -0.1575, 56), ({'bbk': 2.5, 'vm': 1.5, 'reb': 0.7}, -0.1649, 30), ({'bbk': 2.0, 'vm': 1.5, 'reb': 0.7}, -0.2296, 56), ({'bbk': 2.5, 'vm': 1.5, 'reb': 0.5}, -0.2321, 30)]
### IDEA9 bb_crash_1d | ETHUSDT 1d | params={'bbk': 2.5, 'vm': 2.0, 'reb': 0.3}
- TRAIN: n=15 señ/mes=0.19 E=-0.050R win=6.7% DD=-4.0R PF=0.849
- TEST : n=11 señ/mes=0.33 E=+0.342R win=36.4% DD=-3.0R PF=2.255
- NULL (test, 50 sims/seed): s7 p=0.360 Ereal=+0.342 p50=+0.028, s11 p=0.280 Ereal=+0.342 p50=-0.008, s23 p=0.260 Ereal=+0.342 p50=+0.034, s42 p=0.300 Ereal=+0.342 p50=+0.009
- p<=0.05 en 0/4 seeds | test E>0: True | VEREDICTO: DESCARTADA (0.4s)
- Grid=27, válidas=12. Top5 train: [({'bbk': 2.5, 'vm': 2.0, 'reb': 0.3}, -0.0503, 15), ({'bbk': 2.0, 'vm': 2.0, 'reb': 0.3}, -0.0998, 26), ({'bbk': 2.0, 'vm': 1.5, 'reb': 0.3}, -0.1149, 55), ({'bbk': 2.5, 'vm': 1.5, 'reb': 0.3}, -0.1469, 27), ({'bbk': 2.0, 'vm': 1.5, 'reb': 0.7}, -0.2031, 55)]
### IDEA9 bb_crash_1d | BNBUSDT 1d | params={'bbk': 2.0, 'vm': 1.5, 'reb': 0.3}
- TRAIN: n=38 señ/mes=0.5 E=+0.001R win=23.7% DD=-7.95R PF=1.004
- TEST : n=21 señ/mes=0.64 E=+0.322R win=52.4% DD=-3.0R PF=2.127
- NULL (test, 50 sims/seed): s7 p=0.240 Ereal=+0.322 p50=+0.114, s11 p=0.200 Ereal=+0.322 p50=+0.064, s23 p=0.200 Ereal=+0.322 p50=+0.143, s42 p=0.300 Ereal=+0.322 p50=+0.165
- p<=0.05 en 0/4 seeds | test E>0: True | VEREDICTO: DESCARTADA (0.4s)
- Grid=27, válidas=9. Top5 train: [({'bbk': 2.0, 'vm': 1.5, 'reb': 0.3}, 0.0014, 38), ({'bbk': 2.0, 'vm': 1.5, 'reb': 0.7}, -0.1432, 38), ({'bbk': 2.0, 'vm': 2.0, 'reb': 0.3}, -0.1445, 26), ({'bbk': 2.0, 'vm': 1.5, 'reb': 0.5}, -0.1925, 38), ({'bbk': 2.5, 'vm': 1.5, 'reb': 0.3}, -0.3684, 19)]
### IDEA9 bb_crash_1d | SOLUSDT 1d | params={'bbk': 2.0, 'vm': 2.0, 'reb': 0.5}
- TRAIN: n=20 señ/mes=0.38 E=+0.223R win=35.0% DD=-4.0R PF=1.892
- TEST : n=12 señ/mes=0.53 E=-0.222R win=8.3% DD=-3.0R PF=0.335
- NULL (test, 50 sims/seed): s7 p=0.620 Ereal=-0.222 p50=-0.085, s11 p=0.640 Ereal=-0.222 p50=-0.056, s23 p=0.740 Ereal=-0.222 p50=-0.030, s42 p=0.600 Ereal=-0.222 p50=-0.087
- p<=0.05 en 0/4 seeds | test E>0: False | VEREDICTO: DESCARTADA (0.3s)
- Grid=27, válidas=6. Top5 train: [({'bbk': 2.0, 'vm': 2.0, 'reb': 0.5}, 0.2229, 20), ({'bbk': 2.0, 'vm': 2.0, 'reb': 0.3}, 0.2223, 20), ({'bbk': 2.0, 'vm': 2.0, 'reb': 0.7}, 0.1458, 20), ({'bbk': 2.0, 'vm': 1.5, 'reb': 0.3}, -0.0012, 38), ({'bbk': 2.0, 'vm': 1.5, 'reb': 0.5}, -0.061, 38)]
### IDEA9 bb_crash_1d | XRPUSDT 1d | params={'bbk': 2.5, 'vm': 2.0, 'reb': 0.3}
- TRAIN: n=17 señ/mes=0.24 E=+0.602R win=47.1% DD=-1.0R PF=4.409
- TEST : n=7 señ/mes=0.23 E=-0.016R win=42.9% DD=-1.77R PF=0.945
- NULL (test, 50 sims/seed): s7 p=0.400 Ereal=-0.016 p50=-0.046, s11 p=0.360 Ereal=-0.016 p50=-0.113, s23 p=0.400 Ereal=-0.016 p50=-0.154, s42 p=0.460 Ereal=-0.016 p50=-0.027
- p<=0.05 en 0/4 seeds | test E>0: False | VEREDICTO: DESCARTADA (0.3s)
- Grid=27, válidas=12. Top5 train: [({'bbk': 2.5, 'vm': 2.0, 'reb': 0.3}, 0.6017, 17), ({'bbk': 2.5, 'vm': 1.5, 'reb': 0.3}, 0.5121, 24), ({'bbk': 2.5, 'vm': 2.0, 'reb': 0.5}, 0.4404, 17), ({'bbk': 2.0, 'vm': 2.0, 'reb': 0.3}, 0.3679, 23), ({'bbk': 2.5, 'vm': 1.5, 'reb': 0.5}, 0.2994, 24)]
### IDEA9 bb_crash_1d | ADAUSDT 1d | params={'bbk': 2.5, 'vm': 2.0, 'reb': 0.3}
- TRAIN: n=17 señ/mes=0.24 E=+0.024R win=23.5% DD=-2.0R PF=1.068
- TEST : n=10 señ/mes=0.32 E=+0.576R win=50.0% DD=-1.0R PF=6.762
- NULL (test, 50 sims/seed): s7 p=0.320 Ereal=+0.576 p50=+0.095, s11 p=0.340 Ereal=+0.576 p50=+0.210, s23 p=0.360 Ereal=+0.576 p50=+0.257, s42 p=0.300 Ereal=+0.576 p50=+0.230
- p<=0.05 en 0/4 seeds | test E>0: True | VEREDICTO: DESCARTADA (0.3s)
- Grid=27, válidas=12. Top5 train: [({'bbk': 2.5, 'vm': 2.0, 'reb': 0.3}, 0.0241, 17), ({'bbk': 2.5, 'vm': 1.5, 'reb': 0.3}, -0.0691, 23), ({'bbk': 2.0, 'vm': 2.0, 'reb': 0.3}, -0.0868, 26), ({'bbk': 2.0, 'vm': 1.5, 'reb': 0.3}, -0.089, 41), ({'bbk': 2.0, 'vm': 1.5, 'reb': 0.7}, -0.1413, 41)]

## IDEA 10 — Inside-bar breakout 4h
Idea: vela contenida en el rango de la anterior (ratio<=r); entrada al cierre de la siguiente vela si rompe el máximo; stop ka*max(ATR, rango de la inside), target tp*R, BE 1R, max 60 bares. Grid 18 combinaciones.
### IDEA10 inside_bar | BTCUSDT 4h | params={'ratio': 0.6, 'tp': 3.0, 'ka': 1.5}
- TRAIN: n=461 señ/mes=5.92 E=+0.006R win=49.0% DD=-32.5R PF=1.014
- TEST : n=217 señ/mes=6.51 E=-0.076R win=48.8% DD=-25.0R PF=0.837
- NULL (test, 50 sims/seed): s7 p=0.760 Ereal=-0.076 p50=+0.000, s11 p=0.800 Ereal=-0.076 p50=-0.007, s23 p=0.760 Ereal=-0.076 p50=-0.021, s42 p=0.840 Ereal=-0.076 p50=-0.021
- p<=0.05 en 0/4 seeds | test E>0: False | VEREDICTO: DESCARTADA (0.8s)
- Grid=18, válidas=18. Top5 train: [({'ratio': 0.6, 'tp': 3.0, 'ka': 1.5}, 0.0065, 461), ({'ratio': 0.5, 'tp': 3.0, 'ka': 1.5}, -0.0, 293), ({'ratio': 0.6, 'tp': 2.0, 'ka': 1.5}, 0.0, 461), ({'ratio': 0.5, 'tp': 2.0, 'ka': 1.5}, -0.0051, 293), ({'ratio': 0.7, 'tp': 2.0, 'ka': 1.5}, -0.0141, 604)]
### IDEA10 inside_bar | ETHUSDT 4h | params={'ratio': 0.6, 'tp': 3.0, 'ka': 1.5}
- TRAIN: n=485 señ/mes=6.23 E=-0.032R win=45.6% DD=-25.5R PF=0.935
- TEST : n=204 señ/mes=6.12 E=-0.086R win=45.1% DD=-28.5R PF=0.821
- NULL (test, 50 sims/seed): s7 p=0.760 Ereal=-0.086 p50=-0.032, s11 p=0.680 Ereal=-0.086 p50=-0.040, s23 p=0.840 Ereal=-0.086 p50=-0.011, s42 p=0.700 Ereal=-0.086 p50=-0.042
- p<=0.05 en 0/4 seeds | test E>0: False | VEREDICTO: DESCARTADA (0.8s)
- Grid=18, válidas=18. Top5 train: [({'ratio': 0.6, 'tp': 3.0, 'ka': 1.5}, -0.032, 485), ({'ratio': 0.7, 'tp': 2.0, 'ka': 1.5}, -0.0342, 628), ({'ratio': 0.7, 'tp': 3.0, 'ka': 1.5}, -0.0366, 628), ({'ratio': 0.7, 'tp': 1.5, 'ka': 1.5}, -0.0398, 628), ({'ratio': 0.6, 'tp': 2.0, 'ka': 1.5}, -0.0412, 485)]
### IDEA10 inside_bar | SOLUSDT 4h | params={'ratio': 0.5, 'tp': 1.5, 'ka': 1.5}
- TRAIN: n=173 señ/mes=3.27 E=-0.085R win=45.7% DD=-24.25R PF=0.838
- TEST : n=82 señ/mes=3.62 E=-0.021R win=50.0% DD=-6.75R PF=0.957
- NULL (test, 50 sims/seed): s7 p=0.520 Ereal=-0.021 p50=-0.010, s11 p=0.660 Ereal=-0.021 p50=+0.032, s23 p=0.460 Ereal=-0.021 p50=-0.025, s42 p=0.500 Ereal=-0.021 p50=-0.018
- p<=0.05 en 0/4 seeds | test E>0: False | VEREDICTO: DESCARTADA (0.5s)
- Grid=18, válidas=18. Top5 train: [({'ratio': 0.5, 'tp': 1.5, 'ka': 1.5}, -0.0853, 173), ({'ratio': 0.5, 'tp': 2.0, 'ka': 1.5}, -0.0983, 173), ({'ratio': 0.5, 'tp': 3.0, 'ka': 1.5}, -0.1301, 173), ({'ratio': 0.7, 'tp': 1.5, 'ka': 1.5}, -0.137, 385), ({'ratio': 0.7, 'tp': 2.0, 'ka': 1.5}, -0.139, 385)]
### IDEA10 inside_bar | XRPUSDT 4h | params={'ratio': 0.5, 'tp': 2.0, 'ka': 1.5}
- TRAIN: n=260 señ/mes=3.61 E=-0.027R win=46.2% DD=-19.0R PF=0.946
- TEST : n=110 señ/mes=3.57 E=-0.023R win=50.0% DD=-18.0R PF=0.952
- NULL (test, 50 sims/seed): s7 p=0.480 Ereal=-0.023 p50=-0.023, s11 p=0.440 Ereal=-0.023 p50=-0.039, s23 p=0.460 Ereal=-0.023 p50=-0.041, s42 p=0.440 Ereal=-0.023 p50=-0.038
- p<=0.05 en 0/4 seeds | test E>0: False | VEREDICTO: DESCARTADA (0.7s)
- Grid=18, válidas=18. Top5 train: [({'ratio': 0.5, 'tp': 2.0, 'ka': 1.5}, -0.0269, 260), ({'ratio': 0.5, 'tp': 1.5, 'ka': 1.5}, -0.0413, 260), ({'ratio': 0.5, 'tp': 3.0, 'ka': 1.5}, -0.0692, 260), ({'ratio': 0.5, 'tp': 3.0, 'ka': 1.0}, -0.075, 260), ({'ratio': 0.6, 'tp': 2.0, 'ka': 1.5}, -0.0852, 411)]
### IDEA10 inside_bar | LINKUSDT 4h | params={'ratio': 0.7, 'tp': 1.5, 'ka': 1.5}
- TRAIN: n=465 señ/mes=7.05 E=-0.040R win=48.4% DD=-33.0R PF=0.92
- TEST : n=169 señ/mes=5.98 E=-0.101R win=45.0% DD=-28.5R PF=0.807
- NULL (test, 50 sims/seed): s7 p=0.980 Ereal=-0.101 p50=+0.038, s11 p=0.940 Ereal=-0.101 p50=+0.028, s23 p=0.900 Ereal=-0.101 p50=+0.044, s42 p=0.980 Ereal=-0.101 p50=+0.048
- p<=0.05 en 0/4 seeds | test E>0: False | VEREDICTO: DESCARTADA (0.6s)
- Grid=18, válidas=18. Top5 train: [({'ratio': 0.7, 'tp': 1.5, 'ka': 1.5}, -0.0403, 465), ({'ratio': 0.7, 'tp': 2.0, 'ka': 1.5}, -0.0462, 465), ({'ratio': 0.5, 'tp': 1.5, 'ka': 1.5}, -0.0721, 229), ({'ratio': 0.6, 'tp': 1.5, 'ka': 1.5}, -0.0747, 358), ({'ratio': 0.5, 'tp': 2.0, 'ka': 1.5}, -0.0764, 229)]
### IDEA10 inside_bar | AVAXUSDT 4h | params={'ratio': 0.5, 'tp': 2.0, 'ka': 1.5}
- TRAIN: n=158 señ/mes=3.05 E=-0.019R win=48.1% DD=-21.0R PF=0.961
- TEST : n=72 señ/mes=3.24 E=-0.201R win=40.3% DD=-16.0R PF=0.628
- NULL (test, 50 sims/seed): s7 p=0.900 Ereal=-0.201 p50=-0.051, s11 p=0.940 Ereal=-0.201 p50=-0.031, s23 p=0.860 Ereal=-0.201 p50=-0.031, s42 p=0.900 Ereal=-0.201 p50=-0.048
- p<=0.05 en 0/4 seeds | test E>0: False | VEREDICTO: DESCARTADA (0.5s)
- Grid=18, válidas=18. Top5 train: [({'ratio': 0.5, 'tp': 2.0, 'ka': 1.5}, -0.019, 158), ({'ratio': 0.5, 'tp': 1.5, 'ka': 1.5}, -0.0316, 158), ({'ratio': 0.5, 'tp': 3.0, 'ka': 1.5}, -0.0443, 158), ({'ratio': 0.6, 'tp': 1.5, 'ka': 1.5}, -0.0597, 247), ({'ratio': 0.6, 'tp': 2.0, 'ka': 1.5}, -0.0628, 247)]

## RE-EVALUACIÓN UNIFORME — null sobre historial COMPLETO (convención del proyecto)
Motivo: el null calculado solo sobre el último 30% es muy conservador (con n~50 señales casi nada alcanza p<=0.05; incluso la estrategia validada `reversion ARB` da p=0.10-0.12 en test). Se recalcula el null con las 4 seeds sobre TODA la serie, manteniendo el walk-forward 70/30 para E(test). Criterio: p<=0.05 en >=3/4 seeds Y E(test)>0.
| Idea | Par | params | E(test) | n(test) | p por seed (7/11/23/42) | p<=.05 | Válida |
|---|---|---|---|---|---|---|---|
| I1 | BTCUSDT | `{'ef': 10, 'es': 50, 'k': 2.0, 'tp': 2.0, 'ts': 2.0, 'td': 1.5}` | -0.2933 | 75 | 0.50/0.64/0.58/0.54 | 0/4 | no |
| I1 | ETCUSDT | `{'ef': 20, 'es': 50, 'k': 2.0, 'tp': 2.0, 'ts': 2.0, 'td': 1.5}` | -0.2672 | 58 | 0.40/0.30/0.28/0.36 | 0/4 | no |
| I1 | HBARUSDT | `{'ef': 50, 'es': 200, 'k': 1.5, 'tp': 2.0, 'ts': 2.0, 'td': 1.5}` | -0.0417 | 12 | 0.02/0.00/0.08/0.00 | 3/4 | no |
| I1 | THETAUSDT | `{'ef': 50, 'es': 200, 'k': 1.5, 'tp': 2.0, 'ts': 2.0, 'td': 1.5}` | -0.6429 | 14 | 0.96/0.94/0.96/0.94 | 0/4 | no |
| I2 | BTCUSDT | `{'wf': 8, 'ws': 34, 'ef': 20, 'ka': 2.0, 'tp': 4.0}` | -0.0526 | 19 | 0.02/0.00/0.02/0.02 | 4/4 | no |
| I2 | ETHUSDT | `{'wf': 8, 'ws': 34, 'ef': 20, 'ka': 3.0, 'tp': 4.0}` | -0.6667 | 9 | 0.04/0.12/0.10/0.04 | 2/4 | no |
| I2 | BNBUSDT | `{'wf': 8, 'ws': 34, 'ef': 50, 'ka': 2.0, 'tp': 2.0}` | -0.2308 | 13 | 0.44/0.36/0.34/0.44 | 0/4 | no |
| I2 | SOLUSDT | `{'wf': 8, 'ws': 34, 'ef': 50, 'ka': 3.0, 'tp': 4.0}` | -1.0000 | 2 | 0.02/0.02/0.00/0.04 | 4/4 | no |
| I2 | XRPUSDT | `{'wf': 8, 'ws': 34, 'ef': 50, 'ka': 3.0, 'tp': 4.0}` | -0.2308 | 13 | 0.00/0.02/0.02/0.10 | 3/4 | no |
| I2 | ADAUSDT | `{'wf': 8, 'ws': 34, 'ef': 50, 'ka': 3.0, 'tp': 4.0}` | -1.0000 | 5 | 0.02/0.00/0.02/0.06 | 3/4 | no |
| I3 | BTCUSDT | `{'pct': 20, 'vm': 2.0, 'k': 2.0, 'tp': 3.0}` | -0.4412 | 17 | 0.62/0.62/0.54/0.60 | 0/4 | no |
| I3 | ETHUSDT | `{'pct': 30, 'vm': 2.0, 'k': 2.0, 'tp': 2.0}` | -0.1212 | 33 | 0.22/0.24/0.30/0.14 | 0/4 | no |
| I3 | SOLUSDT | `{'pct': 10, 'vm': 1.5, 'k': 1.0, 'tp': 3.0}` | +0.0000 | 15 | 0.16/0.08/0.14/0.18 | 0/4 | no |
| I3 | XRPUSDT | `{'pct': 10, 'vm': 1.2, 'k': 2.0, 'tp': 3.0}` | -0.0870 | 23 | 0.42/0.46/0.48/0.46 | 0/4 | no |
| I3 | LINKUSDT | `{'pct': 10, 'vm': 1.2, 'k': 2.0, 'tp': 3.0}` | +0.0870 | 23 | 0.10/0.06/0.08/0.02 | 1/4 | no |
| I3 | AVAXUSDT | `{'pct': 30, 'vm': 2.0, 'k': 1.5, 'tp': 2.0}` | -0.0870 | 23 | 0.12/0.12/0.16/0.12 | 0/4 | no |
| I4 | BTCUSDT | `{'rn': 14, 'lvl': 35, 'ka': 2.0, 'tp': 2.0}` | +0.0172 | 29 | 0.14/0.22/0.16/0.18 | 0/4 | no |
| I4 | ETHUSDT | `{'rn': 7, 'lvl': 25, 'ka': 2.0, 'tp': 2.0}` | -0.0000 | 24 | 0.06/0.02/0.04/0.04 | 3/4 | no |
| I4 | SOLUSDT | `{'rn': 7, 'lvl': 30, 'ka': 1.0, 'tp': 2.0}` | +0.0556 | 36 | 0.10/0.16/0.08/0.18 | 0/4 | no |
| I4 | XRPUSDT | `{'rn': 14, 'lvl': 35, 'ka': 1.0, 'tp': 1.5}` | -0.3684 | 19 | 0.44/0.36/0.44/0.44 | 0/4 | no |
| I4 | LINKUSDT | `{'rn': 14, 'lvl': 30, 'ka': 2.0, 'tp': 1.5}` | -0.2500 | 4 | 0.06/0.06/0.06/0.10 | 0/4 | no |
| I4 | AVAXUSDT | `{'rn': 7, 'lvl': 35, 'ka': 2.0, 'tp': 3.0}` | +0.0926 | 54 | 0.24/0.38/0.38/0.28 | 0/4 | no |
| I5 | BTCUSDT | `{'mf': 8, 'ms': 21, 'ka': 2.0, 'tp': 4.0}` | -0.1457 | 127 | 0.02/0.02/0.00/0.02 | 4/4 | no |
| I5 | ETHUSDT | `{'mf': 8, 'ms': 21, 'ka': 3.0, 'tp': 2.0}` | -0.1045 | 110 | 0.08/0.02/0.02/0.04 | 3/4 | no |
| I5 | SOLUSDT | `{'mf': 5, 'ms': 13, 'ka': 3.0, 'tp': 3.0}` | -0.0236 | 106 | 0.06/0.04/0.02/0.06 | 2/4 | no |
| I5 | XRPUSDT | `{'mf': 12, 'ms': 26, 'ka': 2.0, 'tp': 3.0}` | -0.1522 | 92 | 0.32/0.58/0.36/0.30 | 0/4 | no |
| I5 | LINKUSDT | `{'mf': 8, 'ms': 21, 'ka': 3.0, 'tp': 2.0}` | -0.0294 | 102 | 0.12/0.16/0.20/0.18 | 0/4 | no |
| I5 | AVAXUSDT | `{'mf': 12, 'ms': 26, 'ka': 3.0, 'tp': 3.0}` | -0.2241 | 58 | 0.06/0.02/0.06/0.10 | 1/4 | no |
| I6 | BTCUSDT | `{'ef': 20, 'es': 50, 'ka': 3.0, 'tp': 4.0, 'minatr': 0.01}` | -0.0556 | 9 | 0.20/0.18/0.18/0.24 | 0/4 | no |
| I6 | ETHUSDT | `{'ef': 10, 'es': 50, 'ka': 2.0, 'tp': 4.0, 'minatr': 0.01}` | -0.4583 | 12 | 0.00/0.00/0.00/0.02 | 4/4 | no |
| I6 | BNBUSDT | `{'ef': 10, 'es': 50, 'ka': 3.0, 'tp': 4.0, 'minatr': 0.01}` | +0.2273 | 11 | 0.04/0.02/0.08/0.02 | 3/4 | no |
| I6 | SOLUSDT | `{'ef': 10, 'es': 50, 'ka': 3.0, 'tp': 4.0, 'minatr': 0.01}` | +0.0714 | 7 | 0.02/0.06/0.02/0.06 | 2/4 | no |
| I6 | XRPUSDT | `{'ef': 10, 'es': 100, 'ka': 3.0, 'tp': 4.0, 'minatr': 0.01}` | -0.0833 | 6 | 0.06/0.10/0.14/0.20 | 0/4 | no |
| I6 | ADAUSDT | `{'ef': 10, 'es': 50, 'ka': 3.0, 'tp': 4.0, 'minatr': 0.01}` | -0.6000 | 10 | 0.06/0.04/0.02/0.08 | 2/4 | no |
| I7 | BTCUSDT | `{'lb': 40, 'ka': 2.5, 'tp': 3.0, 'ts': 2.0, 'td': 2.0}` | -0.1321 | 212 | 0.06/0.04/0.08/0.02 | 2/4 | no |
| I7 | ETHUSDT | `{'lb': 60, 'ka': 2.5, 'tp': 3.0, 'ts': 2.0, 'td': 2.0}` | -0.1533 | 150 | 0.00/0.00/0.00/0.00 | 4/4 | no |
| I7 | SOLUSDT | `{'lb': 20, 'ka': 2.5, 'tp': 3.0, 'ts': 2.0, 'td': 2.0}` | -0.1078 | 204 | 0.06/0.06/0.04/0.06 | 1/4 | no |
| I7 | XRPUSDT | `{'lb': 40, 'ka': 2.5, 'tp': 3.0, 'ts': 2.0, 'td': 2.0}` | -0.0424 | 165 | 0.12/0.14/0.20/0.14 | 0/4 | no |
| I7 | LINKUSDT | `{'lb': 20, 'ka': 2.5, 'tp': 3.0, 'ts': 2.0, 'td': 2.0}` | -0.1393 | 280 | 0.12/0.18/0.14/0.18 | 0/4 | no |
| I7 | AVAXUSDT | `{'lb': 20, 'ka': 2.5, 'tp': 3.0, 'ts': 2.0, 'td': 2.0}` | -0.3011 | 176 | 0.26/0.36/0.24/0.28 | 0/4 | no |
| I8 | BTCUSDT | `{'rn': 7, 'lvl': 35, 'ka': 2.0, 'tp': 2.0}` | -0.1643 | 140 | 0.32/0.38/0.26/0.24 | 0/4 | no |
| I8 | ETCUSDT | `{'rn': 14, 'lvl': 30, 'ka': 1.0, 'tp': 2.0}` | +0.0417 | 12 | 1.00/0.94/0.98/0.98 | 0/4 | no |
| I8 | HBARUSDT | `{'rn': 14, 'lvl': 35, 'ka': 1.5, 'tp': 2.0}` | -0.1613 | 31 | 0.58/0.56/0.46/0.52 | 0/4 | no |
| I8 | THETAUSDT | `{'rn': 14, 'lvl': 35, 'ka': 1.5, 'tp': 2.0}` | -0.2692 | 39 | 1.00/1.00/1.00/1.00 | 0/4 | no |
| I9 | BTCUSDT | `{'bbk': 2.5, 'vm': 1.5, 'reb': 0.3}` | -0.0103 | 15 | 0.78/0.70/0.84/0.82 | 0/4 | no |
| I9 | ETHUSDT | `{'bbk': 2.5, 'vm': 2.0, 'reb': 0.3}` | +0.3423 | 11 | 0.38/0.50/0.36/0.48 | 0/4 | no |
| I9 | BNBUSDT | `{'bbk': 2.0, 'vm': 1.5, 'reb': 0.3}` | +0.3221 | 21 | 0.58/0.42/0.48/0.46 | 0/4 | no |
| I9 | SOLUSDT | `{'bbk': 2.0, 'vm': 2.0, 'reb': 0.5}` | -0.2217 | 12 | 0.42/0.46/0.50/0.38 | 0/4 | no |
| I9 | XRPUSDT | `{'bbk': 2.5, 'vm': 2.0, 'reb': 0.3}` | -0.0156 | 7 | 0.06/0.08/0.02/0.06 | 1/4 | no |
| I9 | ADAUSDT | `{'bbk': 2.5, 'vm': 2.0, 'reb': 0.3}` | +0.5762 | 10 | 0.52/0.40/0.46/0.46 | 0/4 | no |
| I10 | BTCUSDT | `{'ratio': 0.6, 'tp': 3.0, 'ka': 1.5}` | -0.0760 | 217 | 0.56/0.62/0.54/0.52 | 0/4 | no |
| I10 | ETHUSDT | `{'ratio': 0.6, 'tp': 3.0, 'ka': 1.5}` | -0.0858 | 204 | 0.72/0.74/0.56/0.62 | 0/4 | no |
| I10 | SOLUSDT | `{'ratio': 0.5, 'tp': 1.5, 'ka': 1.5}` | -0.0213 | 82 | 0.84/0.90/0.82/0.86 | 0/4 | no |
| I10 | XRPUSDT | `{'ratio': 0.5, 'tp': 2.0, 'ka': 1.5}` | -0.0227 | 110 | 0.38/0.38/0.26/0.36 | 0/4 | no |
| I10 | LINKUSDT | `{'ratio': 0.7, 'tp': 1.5, 'ka': 1.5}` | -0.1006 | 169 | 0.96/0.86/0.90/0.96 | 0/4 | no |
| I10 | AVAXUSDT | `{'ratio': 0.5, 'tp': 2.0, 'ka': 1.5}` | -0.2014 | 72 | 0.64/0.72/0.70/0.80 | 0/4 | no |

- RESULTADO: 0/56 combinaciones idea×par cumplen simultáneamente E(test)>0 y p<=0.05 en >=3/4 seeds con n>=15.
- Candidatos parciales (NO válidos): IDEA6 BNBUSDT E=+0.2273, n=11, null 3/4 (pero n<15 y null-en-test 0/4); IDEA3 SOLUSDT E=0.0000, null 0/4; IDEA4 ETHUSDT E≈0, null 3/4. Ninguno sobrevive criterio completo.
- Sanity check: `reversion ARB` del proyecto (caída 12%, rebote 30%, null full-history) da p=[0.04,0.02,0.00,0.04] → 4/4 PASA; `reversion XRP` p=[0.10,0.02,0.08,0.06] → 1/4. El harness reproduce el comportamiento conocido, con XRP sensible a la seed. Este hecho se registra para no sobre-claimar resultados.

## IDEA 11 — Keltner channel breakout 4h
Idea importada de repo público `xy3293/crypto-strategy-backtest` (keltner_breakout: BTC +69.31%, PF 1.312, Sharpe 0.7173 en su backtest). Entrada al romper EMA(ke)+mult*ATR(14) con confirmación de cruce; stop ka*ATR, target tp*R, BE 1R, max 80 bares. Grid 54 combinaciones.
### IDEA11 | BTCUSDT 4h | params={'ke': 20, 'mult': 2.5, 'ka': 2.0, 'tp': 3.0}
- TRAIN: n=362 señ/mes=4.65 E=+0.239R win=58.3% DD=-13.5R PF=1.609
- TEST : n=144 señ/mes=4.32 E=-0.073R win=50.0% DD=-19.0R PF=0.854
- NULL (test, 50 sims/seed): s7 p=0.800 Ereal=-0.073 p50=-0.011, s11 p=0.720 Ereal=-0.073 p50=-0.008, s23 p=0.580 Ereal=-0.073 p50=-0.039, s42 p=0.560 Ereal=-0.073 p50=-0.032
- p<=0.05 en 0/4 seeds | test E>0: False | VEREDICTO: DESCARTADA (1.1s)
- NULL full-history 4 seeds: p=[0.0, 0.0, 0.0, 0.0] → 4/4. Veredicto FINAL: DESCARTADA
- Grid=54, válidas=54. Top5 train: [({'ke': 20, 'mult': 2.5, 'ka': 2.0, 'tp': 3.0}, 0.239, 362), ({'ke': 10, 'mult': 2.0, 'ka': 2.0, 'tp': 3.0}, 0.2274, 409), ({'ke': 10, 'mult': 1.5, 'ka': 2.0, 'tp': 3.0}, 0.2178, 622), ({'ke': 50, 'mult': 2.0, 'ka': 2.0, 'tp': 3.0}, 0.1957, 437), ({'ke': 20, 'mult': 2.5, 'ka': 2.0, 'tp': 2.0}, 0.1948, 362)]
### IDEA11 | ETHUSDT 4h | params={'ke': 50, 'mult': 2.5, 'ka': 2.0, 'tp': 3.0}
- TRAIN: n=447 señ/mes=5.74 E=+0.245R win=57.3% DD=-24.5R PF=1.602
- TEST : n=144 señ/mes=4.32 E=-0.170R win=43.8% DD=-32.5R PF=0.694
- NULL (test, 50 sims/seed): s7 p=0.880 Ereal=-0.170 p50=-0.003, s11 p=0.880 Ereal=-0.170 p50=+0.013, s23 p=0.900 Ereal=-0.170 p50=-0.000, s42 p=0.860 Ereal=-0.170 p50=-0.032
- p<=0.05 en 0/4 seeds | test E>0: False | VEREDICTO: DESCARTADA (1.7s)
- NULL full-history 4 seeds: p=[0.02, 0.02, 0.0, 0.02] → 4/4. Veredicto FINAL: DESCARTADA
- Grid=54, válidas=54. Top5 train: [({'ke': 50, 'mult': 2.5, 'ka': 2.0, 'tp': 3.0}, 0.245, 447), ({'ke': 20, 'mult': 2.5, 'ka': 2.0, 'tp': 3.0}, 0.1856, 396), ({'ke': 50, 'mult': 2.5, 'ka': 2.0, 'tp': 2.0}, 0.1734, 447), ({'ke': 10, 'mult': 2.5, 'ka': 2.0, 'tp': 3.0}, 0.1609, 261), ({'ke': 20, 'mult': 2.5, 'ka': 2.0, 'tp': 2.0}, 0.1515, 396)]
### IDEA11 | SOLUSDT 4h | params={'ke': 50, 'mult': 2.5, 'ka': 2.0, 'tp': 3.0}
- TRAIN: n=314 señ/mes=5.94 E=+0.146R win=55.7% DD=-18.5R PF=1.338
- TEST : n=97 señ/mes=4.28 E=-0.103R win=43.3% DD=-17.5R PF=0.808
- NULL (test, 50 sims/seed): s7 p=0.500 Ereal=-0.103 p50=-0.097, s11 p=0.520 Ereal=-0.103 p50=-0.094, s23 p=0.580 Ereal=-0.103 p50=-0.035, s42 p=0.540 Ereal=-0.103 p50=-0.084
- p<=0.05 en 0/4 seeds | test E>0: False | VEREDICTO: DESCARTADA (1.0s)
- NULL full-history 4 seeds: p=[0.16, 0.06, 0.1, 0.14] → 0/4. Veredicto FINAL: DESCARTADA
- Grid=54, válidas=54. Top5 train: [({'ke': 50, 'mult': 2.5, 'ka': 2.0, 'tp': 3.0}, 0.1465, 314), ({'ke': 10, 'mult': 2.5, 'ka': 2.0, 'tp': 3.0}, 0.1416, 166), ({'ke': 50, 'mult': 2.0, 'ka': 2.0, 'tp': 3.0}, 0.1271, 350), ({'ke': 50, 'mult': 1.5, 'ka': 2.0, 'tp': 3.0}, 0.1267, 363), ({'ke': 20, 'mult': 2.5, 'ka': 2.0, 'tp': 3.0}, 0.112, 259)]
### IDEA11 | XRPUSDT 4h | params={'ke': 50, 'mult': 1.5, 'ka': 2.0, 'tp': 3.0}
- TRAIN: n=430 señ/mes=5.98 E=+0.057R win=52.3% DD=-25.0R PF=1.121
- TEST : n=174 señ/mes=5.65 E=-0.058R win=47.7% DD=-27.0R PF=0.888
- NULL (test, 50 sims/seed): s7 p=0.380 Ereal=-0.057 p50=-0.077, s11 p=0.360 Ereal=-0.057 p50=-0.111, s23 p=0.500 Ereal=-0.057 p50=-0.053, s42 p=0.360 Ereal=-0.057 p50=-0.118
- p<=0.05 en 0/4 seeds | test E>0: False | VEREDICTO: DESCARTADA (1.5s)
- NULL full-history 4 seeds: p=[0.08, 0.14, 0.04, 0.12] → 1/4. Veredicto FINAL: DESCARTADA
- Grid=54, válidas=54. Top5 train: [({'ke': 50, 'mult': 1.5, 'ka': 2.0, 'tp': 3.0}, 0.057, 430), ({'ke': 50, 'mult': 1.5, 'ka': 2.0, 'tp': 2.0}, 0.0384, 430), ({'ke': 10, 'mult': 2.0, 'ka': 2.0, 'tp': 3.0}, 0.0119, 293), ({'ke': 20, 'mult': 2.5, 'ka': 2.0, 'tp': 2.0}, 0.0103, 243), ({'ke': 10, 'mult': 2.0, 'ka': 2.0, 'tp': 2.0}, 0.0085, 293)]
### IDEA11 | LINKUSDT 4h | params={'ke': 50, 'mult': 2.0, 'ka': 2.0, 'tp': 3.0}
- TRAIN: n=446 señ/mes=6.76 E=+0.050R win=51.8% DD=-39.0R PF=1.106
- TEST : n=140 señ/mes=4.95 E=+0.011R win=49.3% DD=-24.5R PF=1.022
- NULL (test, 50 sims/seed): s7 p=0.420 Ereal=+0.011 p50=+0.003, s11 p=0.500 Ereal=+0.011 p50=+0.014, s23 p=0.480 Ereal=+0.011 p50=-0.003, s42 p=0.460 Ereal=+0.011 p50=+0.000
- p<=0.05 en 0/4 seeds | test E>0: True | VEREDICTO: DESCARTADA (0.9s)
- NULL full-history 4 seeds: p=[0.14, 0.26, 0.08, 0.12] → 0/4. Veredicto FINAL: DESCARTADA
- Grid=54, válidas=54. Top5 train: [({'ke': 50, 'mult': 2.0, 'ka': 2.0, 'tp': 3.0}, 0.0504, 446), ({'ke': 50, 'mult': 1.5, 'ka': 2.0, 'tp': 3.0}, 0.0238, 484), ({'ke': 50, 'mult': 1.5, 'ka': 2.0, 'tp': 2.0}, 0.0165, 484), ({'ke': 50, 'mult': 2.0, 'ka': 2.0, 'tp': 2.0}, 0.0157, 446), ({'ke': 50, 'mult': 2.5, 'ka': 2.0, 'tp': 3.0}, 0.0152, 361)]
### IDEA11 | AVAXUSDT 4h | params={'ke': 10, 'mult': 2.5, 'ka': 2.0, 'tp': 3.0}
- TRAIN: n=150 señ/mes=2.89 E=+0.177R win=56.7% DD=-9.5R PF=1.414
- TEST : n=75 señ/mes=3.37 E=+0.000R win=53.3% DD=-14.0R PF=1.0
- NULL (test, 50 sims/seed): s7 p=0.220 Ereal=+0.000 p50=-0.120, s11 p=0.300 Ereal=+0.000 p50=-0.070, s23 p=0.260 Ereal=+0.000 p50=-0.143, s42 p=0.300 Ereal=+0.000 p50=-0.077
- p<=0.05 en 0/4 seeds | test E>0: False | VEREDICTO: DESCARTADA (0.7s)
- NULL full-history 4 seeds: p=[0.14, 0.04, 0.08, 0.02] → 2/4. Veredicto FINAL: DESCARTADA
- Grid=54, válidas=54. Top5 train: [({'ke': 10, 'mult': 2.5, 'ka': 2.0, 'tp': 3.0}, 0.1767, 150), ({'ke': 50, 'mult': 1.5, 'ka': 2.0, 'tp': 3.0}, 0.1413, 329), ({'ke': 10, 'mult': 2.0, 'ka': 2.0, 'tp': 3.0}, 0.1361, 305), ({'ke': 50, 'mult': 1.5, 'ka': 1.5, 'tp': 2.0}, 0.114, 329), ({'ke': 50, 'mult': 1.5, 'ka': 2.0, 'tp': 2.0}, 0.114, 329)]

## IDEA 12 — Supertrend (ATR trailing) 4h
Idea importada del mismo repo (`supertrend_4h`: BTC +31.46%, PF 1.167, Sharpe 0.4741, DD -12.77%). Flipo de dirección Supertrend (banda EMA/ATR mult); stop=banda inferior, trailing td*R, target tp*R, max 120 bares. Grid 27 combinaciones.
### IDEA12 | BTCUSDT 4h | params={'mult': 2.0, 'tp': 2.0, 'tdist': 1.5}
- TRAIN: n=82 señ/mes=1.05 E=-0.006R win=23.2% DD=-9.5R PF=0.983
- TEST : n=37 señ/mes=1.11 E=-0.257R win=18.9% DD=-13.0R PF=0.525
- NULL (test, 50 sims/seed): s7 p=0.660 Ereal=-0.257 p50=-0.143, s11 p=0.740 Ereal=-0.257 p50=-0.148, s23 p=0.660 Ereal=-0.257 p50=-0.167, s42 p=0.620 Ereal=-0.257 p50=-0.194
- p<=0.05 en 0/4 seeds | test E>0: False | VEREDICTO: DESCARTADA (1.1s)
- NULL full-history 4 seeds: p=[0.28, 0.24, 0.22, 0.28] → 0/4. Veredicto FINAL: DESCARTADA
- Grid=27, válidas=18. Top5 train: [({'mult': 2.0, 'tp': 2.0, 'tdist': 1.5}, -0.0061, 82), ({'mult': 3.0, 'tp': 3.0, 'tdist': 1.5}, -0.0968, 31), ({'mult': 2.0, 'tp': 3.0, 'tdist': 1.5}, -0.1098, 82), ({'mult': 3.0, 'tp': 2.0, 'tdist': 1.5}, -0.1613, 31), ({'mult': 2.0, 'tp': 4.0, 'tdist': 1.5}, -0.1707, 82)]
### IDEA12 | ETHUSDT 4h | params={'mult': 2.0, 'tp': 2.0, 'tdist': 1.5}
- TRAIN: n=70 señ/mes=0.9 E=+0.293R win=38.6% DD=-5.0R PF=2.025
- TEST : n=34 señ/mes=1.02 E=-0.544R win=2.9% DD=-18.5R PF=0.075
- NULL (test, 50 sims/seed): s7 p=1.000 Ereal=-0.544 p50=-0.145, s11 p=1.000 Ereal=-0.544 p50=-0.154, s23 p=0.980 Ereal=-0.544 p50=-0.207, s42 p=1.000 Ereal=-0.544 p50=-0.188
- p<=0.05 en 0/4 seeds | test E>0: False | VEREDICTO: DESCARTADA (1.1s)
- NULL full-history 4 seeds: p=[0.0, 0.04, 0.0, 0.04] → 4/4. Veredicto FINAL: DESCARTADA
- Grid=27, válidas=18. Top5 train: [({'mult': 2.0, 'tp': 2.0, 'tdist': 1.5}, 0.2929, 70), ({'mult': 2.0, 'tp': 3.0, 'tdist': 1.5}, 0.1429, 70), ({'mult': 3.0, 'tp': 2.0, 'tdist': 1.5}, -0.0227, 22), ({'mult': 2.0, 'tp': 4.0, 'tdist': 1.5}, -0.1071, 70), ({'mult': 3.0, 'tp': 3.0, 'tdist': 1.5}, -0.2273, 22)]
### IDEA12 | SOLUSDT 4h | params={'mult': 2.0, 'tp': 2.0, 'tdist': 1.5}
- TRAIN: n=35 señ/mes=0.66 E=+0.129R win=31.4% DD=-3.0R PF=1.375
- TEST : n=19 señ/mes=0.84 E=-0.289R win=15.8% DD=-7.0R PF=0.45
- NULL (test, 50 sims/seed): s7 p=0.660 Ereal=-0.289 p50=-0.227, s11 p=0.620 Ereal=-0.289 p50=-0.222, s23 p=0.600 Ereal=-0.289 p50=-0.214, s42 p=0.620 Ereal=-0.289 p50=-0.231
- p<=0.05 en 0/4 seeds | test E>0: False | VEREDICTO: DESCARTADA (0.7s)
- NULL full-history 4 seeds: p=[0.2, 0.2, 0.2, 0.24] → 0/4. Veredicto FINAL: DESCARTADA
- Grid=27, válidas=9. Top5 train: [({'mult': 2.0, 'tp': 2.0, 'tdist': 1.5}, 0.1286, 35), ({'mult': 2.0, 'tp': 3.0, 'tdist': 1.5}, -0.0, 35), ({'mult': 2.0, 'tp': 4.0, 'tdist': 1.5}, -0.2, 35), ({'mult': 2.0, 'tp': 2.0, 'tdist': 1.0}, -0.3429, 35), ({'mult': 2.0, 'tp': 3.0, 'tdist': 1.0}, -0.5143, 35)]
### IDEA12 | XRPUSDT 4h | params={'mult': 3.0, 'tp': 2.0, 'tdist': 1.5}
- TRAIN: n=23 señ/mes=0.32 E=-0.022R win=21.7% DD=-2.5R PF=0.937
- TEST : n=6 señ/mes=0.19 E=-0.417R win=16.7% DD=-3.0R PF=0.375
- NULL (test, 50 sims/seed): s7 p=0.640 Ereal=-0.417 p50=-0.300, s11 p=0.620 Ereal=-0.417 p50=-0.250, s23 p=0.700 Ereal=-0.417 p50=-0.250, s42 p=0.720 Ereal=-0.417 p50=-0.200
- p<=0.05 en 0/4 seeds | test E>0: False | VEREDICTO: DESCARTADA (1.0s)
- NULL full-history 4 seeds: p=[0.26, 0.32, 0.16, 0.22] → 0/4. Veredicto FINAL: DESCARTADA
- Grid=27, válidas=18. Top5 train: [({'mult': 3.0, 'tp': 2.0, 'tdist': 1.5}, -0.0217, 23), ({'mult': 2.0, 'tp': 2.0, 'tdist': 1.5}, -0.0776, 58), ({'mult': 2.0, 'tp': 3.0, 'tdist': 1.5}, -0.1724, 58), ({'mult': 3.0, 'tp': 3.0, 'tdist': 1.5}, -0.1739, 23), ({'mult': 3.0, 'tp': 4.0, 'tdist': 1.5}, -0.2391, 23)]
