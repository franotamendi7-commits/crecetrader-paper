# DIVISAS — 12 pares de Quantfury testeados con el mismo sistema

2026-11-26 · PAPER_ONLY · Fuente: Yahoo Finance (yfinance, `/usr/bin/python3`).

## Por qué Yahoo y no Binance

Binance no cotiza divisas. TradingView no tiene API histórica gratuita (ya descartado).
Yahoo/yfinance es gratis, sin key, pero da **solo 730 días de velas 1h** (~17.000)
y 23 años de diario. Nuestro estándar es 6-9 años → **muestra 3× más corta**.
Por eso se agregó el filtro `n >= 20` señales y la doble verificación con semillas distintas.

## Lista oficial (12, tomada de la app)

AUD/USD · EUR/USD · GBP/USD · NZD/USD · USD/BRL · USD/CAD · USD/CHF ·
USD/CNY · USD/HKD · USD/JPY · USD/MXN · USD/NOK

Descargadas: 12 × (1h + 4h resampleado). Ej.: EURUSD 17.258 velas 1h / 4.452 4h.

## Resultado: 48 pruebas (12 pares × 4 estrategias)

```
4 VALIDAN · 29 DESCARTAN · 15 MUESTRA CORTA (n<20)
```

### Doble verificación (semillas originales + semillas +31337)

| Par | Estrategia | 1º | 2º | null medio | Veredicto |
|---|---|---|---|---:|---|
| **USDBRL** | BOS | p=0,048 | p=0,048 | **−4,05 / −3,63** | **AGREGADO** |
| USDMXN | scale-in | p=0,048 | p=0,048 | +399 / +429 | RESERVA (ventaja marginal) |
| USDNOK | scale-in | p=0,048 | p=0,048 | +514 / +504 | RESERVA (ventaja marginal) |
| AUDUSD | scale-in | p=0,048 | **p=0,095** | +698 | DESCARTADO |

USDBRL/BOS: 148 operaciones · 54,7% acierto · +35,25R · DD −19,0R · WF train 31,0 → test 4,25.
Es el único con **null negativo**: la estrategia gana donde el azar pierde. Los scale-in
pasan pero el null gana casi lo mismo que el real → no se incorporan.

## Integración

- `USDBRL` agregado a BOS (4º par), tracker, cartera y dash (14 pares).
- `actualizar_divisas.py` + launchd cada 15 min usa `/usr/bin/python3` (yfinance).
- Las otras 11 divisas quedan en `datos/velas/` para estudiarlas, sin estrategia.

## Honestidad

Muestra corta (2 años) y forex 24/5 (distinto de cripto 24/7): el resultado es un
**panorama**, no comparable al backtest de 6-9 años. Por eso solo se incorporó el
caso con ventaja clara sobre el null.
