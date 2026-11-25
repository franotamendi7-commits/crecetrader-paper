# RONDA 2 de búsqueda — 1d y short

Fecha: 2026-11-25. Mientras Flint hace el dash parte 2.

## 1 · Timeframe 1d (descargado real de THETA, HBAR, ETC)

| par / config | /mes | E | DD | PF |
|---|---:|---:|---:|---:|
| THETA ema13/T200/sw5 | 1,6 | **+0,139** | **−20,9** | 1,39 |
| THETA ema13/T100/sw3 | 2,2 | +0,106 | **−18,2** | 1,29 |
| ETC ema21/T50/sw3 | 1,9 | +0,118 | **−19,6** | 1,29 |
| HBAR ema21/T50/sw3 | 1,8 | +0,041 | −19,7 | 1,09 |

Cartera 1d (config base): **21,7 señales/mes**, E=+0,064R, DD=−40,3R, PF=1,15.

**Conclusión:** el 1d es mucho más lento (2 señales/mes por par) pero su
DD es 3 veces menor. Es compatible con la cartera 4h como capa defensiva.
BTC 1d no se pudo usar: el archivo local tenía solo 3 velas (vacío).

## 2 · Short en tramos bajistas — DESCARTADO

Corregí un bug del simulador short y el resultado real es:

| par | /mes | E | DD | PF |
|---|---:|---:|---:|---:|
| BTC | 19,6 | −0,229 | −507,8 | 0,48 |
| THETA | 19,8 | −0,256 | −470,4 | 0,44 |
| HBAR | 22,9 | −0,227 | −487,5 | 0,48 |
| ETC | 24,4 | −0,231 | −652,7 | 0,50 |

Cartera short: 78,8 señales/mes, E=**−0,235R**, DD=−2033R, PF 0,48.
Pierde en 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025 y 2026.

**Conclusión:** vender en rebotes de EMA en tendencia bajista no funciona
en criptos con este stop. Se descarta. (El canal habla de bajistas, pero
los números no acompañan.)

## Estado

- Cartera 4h (BTC+THETA+HBAR+ETC): 59,4/mes, E=+0,128R, DD=−127,6R — sigue vigente.
- Capa 1d: opcional, 21,7/mes, DD=−40,3R — para evaluar.
- Short: fuera.
- ETH: fuera (p=0,217 con BE corregido).

PAPER_ONLY. No se ejecutaron órdenes.
