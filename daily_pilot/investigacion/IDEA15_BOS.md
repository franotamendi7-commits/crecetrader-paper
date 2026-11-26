# IDEA 15 — Break of Structure (BOS) 4h + confirmación 1h

2026-11-25 · PAPER_ONLY · 20 seeds, p<0.05, WF test>0.
Regla: máximos crecientes en 4h → ruptura del último máximo → cierre 1h arriba del nivel roto.
Stop en el último swing bajo, target 1.5R, BE en 1R. Espejo short sin señales válidas.

| Par | n | win | E (R) | DD (R) | null media | p | train→test | veredicto |
|---|---:|---:|---:|---:|---:|---:|---|---|
| ETH | 520 | 48.1% | +39.25 | -24.5 | -2.59 | 0.048 | +45.5→-6.2 | DESCARTAR |
| ADA | 383 | 50.4% | +28.50 | -14.5 | -0.96 | 0.048 | +35.5→-7.0 | DESCARTAR |
| SOL | 281 | 50.9% | +27.75 | -22.8 | -0.30 | 0.048 | +43.5→-15.8 | DESCARTAR |
| INJ | 226 | 53.1% | +26.75 | -14.5 | -0.86 | 0.048 | +23.5→+3.2 | VALIDAR |
| RUNE | 265 | 50.9% | +23.25 | -16.0 | +0.03 | 0.048 | +31.0→-7.8 | DESCARTAR |
| DOGE | 349 | 50.7% | +22.50 | -13.2 | -1.11 | 0.048 | +9.5→+13.0 | VALIDAR |
| THETA | 316 | 52.5% | +18.75 | -28.0 | -0.24 | 0.048 | +32.5→-13.8 | DESCARTAR |
| DOT | 289 | 48.1% | +9.25 | -21.0 | -0.16 | 0.048 | +6.2→+3.0 | VALIDAR |
| ETC | 378 | 47.9% | +8.25 | -25.5 | -0.91 | 0.048 | +27.0→-18.8 | DESCARTAR |
| SNX | 247 | 49.8% | +7.50 | -25.0 | +0.14 | 0.048 | +22.5→-15.0 | DESCARTAR |
| AAVE | 281 | 48.8% | -2.75 | -23.2 | -0.30 | 0.952 | +13.2→-16.0 | DESCARTAR |
| BCH | 354 | 45.8% | -8.75 | -35.8 | -0.86 | 1.000 | +15.8→-24.5 | DESCARTAR |
| NEO | 418 | 45.7% | -11.50 | -52.5 | -0.25 | 1.000 | +31.8→-43.2 | DESCARTAR |
| STX | 258 | 49.6% | -12.00 | -24.8 | -0.14 | 1.000 | +6.2→-18.2 | DESCARTAR |
| LTC | 462 | 42.4% | -14.75 | -34.0 | -0.46 | 1.000 | +11.8→-26.5 | DESCARTAR |
| ONDO | 79 | 38.0% | -16.75 | -21.5 | -0.86 | 1.000 | -13.0→-3.8 | DESCARTAR |
| APT | 183 | 43.7% | -22.50 | -30.2 | -1.04 | 1.000 | -20.0→-2.5 | DESCARTAR |
| OP | 173 | 42.8% | -23.50 | -29.2 | -0.11 | 1.000 | -10.2→-13.2 | DESCARTAR |
| ATOM | 345 | 42.9% | -24.25 | -37.8 | -0.60 | 1.000 | +5.2→-29.5 | DESCARTAR |
| MANA | 247 | 42.1% | -31.50 | -37.0 | -0.45 | 1.000 | -29.2→-2.2 | DESCARTAR |
| POL | 101 | 27.7% | -39.50 | -43.5 | -0.30 | 1.000 | -37.0→-2.5 | DESCARTAR |
| SAND | 242 | 41.7% | -41.50 | -41.5 | -0.71 | 1.000 | -23.0→-18.5 | DESCARTAR |

## Resultado

**3 validan: INJ, DOGE, DOT.** Los 3 con p=0.0476 (piso de 1/21).

Verificación extra: se repitió el null con **semillas distintas** (+31337).
Los 3 mantuvieron p=0.0476 con null medio negativo (−0.21R, −1.48R, −0.21R)
frente a un real de +26.75R, +22.50R y +9.25R. No es suerte de seed.

El resto (19 pares) se descarta: 10 con test negativo y 9 con p=1.00.
El espejo short no generó señales suficientes con este detector.

## Integración

Cuarta estrategia de la cartera: **BOS long** (INJ, DOGE, DOT).
Tracker propio `tracker_bos.py` + launchd cada 4h + alertas a Discord.
768 operaciones históricas · 50% win · +49.75R · DD −27.50R.
Dash: 13 pares. Suite 15/15.
