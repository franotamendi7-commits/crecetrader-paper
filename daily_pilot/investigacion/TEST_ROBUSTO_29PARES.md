# TEST ROBUSTO — scale-in Fibo en TODOS los pares disponibles

Fecha: 2026-11-25 · PAPER_ONLY · 20 seeds por par (piso p=1/21=0.048)
Regla: Fase1 → Fase2 retroceso 38,2% → entradas Fibo 61,8%/100%, filtro R≥4%, riesgo 2%.
Válida si p<0.05 Y test>0. Null = permutación de signos conservando magnitudes.
WF = split temporal 60/40 sobre operaciones (parámetros FIJOS, no re-optimizados).

| Par | n | win | real $ | DD $ | null media | p | train→test | desde | veredicto |
|---|---:|---:|---:|---:|---:|---:|---|---|---|
| BTC | 103 | 96.1% | +2521.49 | -10.55 | 1218.50 | 0.048 | 1594→928 | 2017-11 | VALIDAR |
| ETH | 43 | 100.0% | +1341.92 | 0.00 | 927.69 | 0.095 | 802→540 | 2018-11 | DESCARTAR |
| XRP | 32 | 96.9% | +1328.80 | -17.18 | 713.91 | 0.048 | 727→601 | 2019-05 | VALIDAR |
| LTC | 30 | 96.7% | +1138.84 | -17.20 | 751.88 | 0.095 | 760→379 | 2018-09 | DESCARTAR |
| HBAR | 21 | 100.0% | +1111.35 | 0.00 | 558.36 | 0.048 | 613→499 | 2020-04 | VALIDAR |
| LINK | 24 | 100.0% | +1104.14 | 0.00 | 438.53 | 0.048 | 629→475 | 2019-02 | VALIDAR |
| ETC | 18 | 100.0% | +960.02 | 0.00 | 717.47 | 0.143 | 536→424 | 2019-03 | DESCARTAR |
| ADA | 17 | 100.0% | +927.94 | 0.00 | 511.39 | 0.143 | 501→427 | 2019-09 | DESCARTAR |
| AVAX | 15 | 100.0% | +888.11 | 0.00 | 347.84 | 0.048 | 566→322 | 2021-10 | VALIDAR |
| NEO | 15 | 100.0% | +835.31 | 0.00 | 670.57 | 0.191 | 505→330 | 2018-11 | DESCARTAR |
| FIL | 14 | 100.0% | +812.45 | 0.00 | 377.32 | 0.048 | 432→381 | 2020-11 | VALIDAR |
| BCH | 17 | 94.1% | +718.83 | -20.33 | 593.50 | 0.238 | 387→332 | 2020-04 | DESCARTAR |
| DOGE | 20 | 85.0% | +659.67 | -42.77 | 676.50 | 0.476 | 283→376 | 2020-01 | DESCARTAR |
| INJ | 9 | 100.0% | +600.14 | 0.00 | 224.13 | 0.095 | 331→269 | 2020-11 | DESCARTAR |
| SOL | 13 | 92.3% | +589.10 | -11.21 | 375.33 | 0.095 | 390→199 | 2020-12 | DESCARTAR |
| THETA | 10 | 100.0% | +536.68 | 0.00 | 531.26 | 0.571 | 352→185 | 2019-10 | DESCARTAR |
| ATOM | 10 | 100.0% | +536.60 | 0.00 | 457.24 | 0.381 | 327→209 | 2020-12 | DESCARTAR |
| NEAR | 9 | 100.0% | +513.41 | 0.00 | 273.36 | 0.048 | 314→199 | 2021-11 | VALIDAR |
| MANA | 10 | 100.0% | +493.11 | 0.00 | 405.08 | 0.333 | 257→236 | 2022-08 | DESCARTAR |
| AAVE | 9 | 100.0% | +488.96 | 0.00 | 329.36 | 0.191 | 285→204 | 2021-03 | DESCARTAR |
| SNX | 9 | 100.0% | +453.62 | 0.00 | 328.60 | 0.238 | 243→211 | 2023-07 | DESCARTAR |
| SAND | 9 | 88.9% | +426.10 | -44.43 | 341.87 | 0.333 | 198→228 | 2022-03 | DESCARTAR |
| APT | 11 | 81.8% | +419.70 | -45.54 | 236.94 | 0.143 | 277→143 | 2023-07 | DESCARTAR |
| RUNE | 12 | 91.7% | +406.69 | -38.15 | 395.52 | 0.571 | 206→201 | 2023-01 | DESCARTAR |
| STX | 8 | 87.5% | +350.04 | -53.06 | 504.58 | 0.809 | 111→239 | 2020-01 | DESCARTAR |
| DOT | 14 | 92.9% | +301.46 | -44.17 | 501.40 | 0.905 | 198→104 | 2020-12 | DESCARTAR |
| ONDO | 4 | 100.0% | +226.00 | 0.00 | 68.79 | 0.095 | 100→126 | 2025-05 | DESCARTAR |
| POL | 3 | 100.0% | +152.62 | 0.00 | 207.40 | 0.571 | 20→133 | 2025-02 | DESCARTAR |
| OP | 4 | 75.0% | +142.20 | -30.13 | 218.45 | 0.762 | -16→158 | 2023-09 | DESCARTAR |

**RESULTADO: 7 validan / 22 descartan de 29 pares.**

VALIDADOS con 20 seeds: BTC, XRP, HBAR, LINK, AVAX, FIL, NEAR

DESCARTADOS: ETH, LTC, ETC, ADA, NEO, BCH, DOGE, INJ, SOL, THETA, ATOM, MANA, AAVE, SNX, SAND, APT, RUNE, STX, DOT, ONDO, POL, OP

## Cambios respecto al test de 6 seeds
Con 6 seeds el piso era 1/7=0.143 y varios pares daban p=0.00 (0 de 6 nulls superaban al real).
Con 20 seeds algunos caen: BTC, ETH, SOL, ADA, ETC, THETA pierden la validación.
Esto es **honestidad estadística**: con más simulaciones el p es más confiable y menos optimista.

## Decisión
La cartera scale-in queda con los que pasan el test estricto de 20 seeds.
Los descartados siguen en el universo para otras estrategias (pullback/reversión), no para scale-in.
