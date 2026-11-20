# TradingView — indicador de niveles (C05)

`crecetrader_niveles.pine` — Pegar en el Pine Editor de TradingView (v5).

## Que dibuja
- **Retrocesos**: 0,382 / 0,5 / 0,61 / 0,786  (de el tramo del ciclo)
- **Extensiones**: 1 / 1,25 / 1,5 / 1,75 / 2 / 3  (arriba del maximo)
- **Abanico intradia**: cierre 21:00 (00:00 UTC) +/- fibo x 1.000 puntos
- **Nivel anual**: cierre del 1 de enero

## Reglas (validadas contra las capturas de Francisco, BNB 2026-11-20)
- Cada TF tiene su swing: **macro = semanal, micro = diario y 4h**
- Tramo = **maximo mas alto** -> **piso mas bajo posterior**
- El fibo se tira **al reves**: 0 = minimo, 1 = maximo
- Parametros: `n=3` (velas por extremo), `ventana=60` (swings)

## Verificacion
La logica del Pine esta **simulada en Python** y da **identico** que el motor
(`core/tramos.py::tramo_ciclo`) en los 3 TFs:

| TF | Pine simulado | motor | captura |
|---|---|---|---|
| 1W | 530,00 -> 1.375,11 | 530,00 -> 1.375,11 | 537,21 -> 1.371,90 |
| 1D | 530,00 -> 809,99 | 530,00 -> 809,99 | 536,58 -> 808,24 |
| 4H | 530,00 -> 809,99 | 530,00 -> 809,99 | 530,54 -> 809,57 |

**PENDIENTE**: pegarlo en TradingView y confirmar que compila y dibuja.
