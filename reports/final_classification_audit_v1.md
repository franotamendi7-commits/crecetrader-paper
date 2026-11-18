# Final Classification Audit v1 — FASE 3.2.1

## Clasificación revisada de los 51 niveles

---

## Reglas de clasificación

1. `[DICHO]`: afirmación expresada verbalmente por el trader.
2. `[OBSERVADO]`: elemento realmente visible en el video.
3. `[VERIFICADO_CON_OHLCV]`: respaldado por datos externos del mismo instrumento, mercado y temporalidad.
4. `[PARCIALMENTE_VERIFICADO]`: precio cercano pero temporalidad no exacta.
5. `[INFERIDO]`: interpretación generada por el sistema.
6. `[NO_VERIFICABLE]`: evidencia insuficiente.
7. `[ILEGIBLE]`: precio no legible.
8. `[INCONSISTENTE]`: contradicción entre fuentes.

Una afirmación puede tener varias etiquetas.

---

## Clasificación por nivel

### BTC — Futuros CME (8)

| ID | Precio | Clasificación | Justificación |
|----|--------|---------------|---------------|
| BTC-CME-01 | 75.835 | [DICHO]+[NO_VERIFICABLE] | Mencionado como futuro CME, sin datos CME |
| BTC-CME-02 | 72.838 | [DICHO]+[NO_VERIFICABLE] | Mencionado como futuro CME, sin datos CME |
| BTC-CME-03 | 69.840 | [DICHO]+[NO_VERIFICABLE] | Mencionado como futuro CME, sin datos CME |
| BTC-CME-04 | 65.520 | [DICHO]+[NO_VERIFICABLE] | Mencionado como futuro CME, sin datos CME |
| BTC-CME-05 | 83.366 | [DICHO]+[NO_VERIFICABLE] | Mencionado como futuro CME, sin datos CME |
| BTC-CME-06 | 76.852 | [DICHO]+[NO_VERIFICABLE] | Mencionado como futuro CME, sin datos CME |
| BTC-CME-07 | 78.580 | [DICHO]+[NO_VERIFICABLE] | Mencionado como futuro CME, sin datos CME |
| BTC-CME-08 | 78.746 | [DICHO]+[NO_VERIFICABLE] | Mencionado como futuro CME, sin datos CME |

### BTC — Spot (24)

| ID | Precio | Clasificación | Justificación |
|----|--------|---------------|---------------|
| BTC-SPOT-01 | 72.554 | [DICHO]+[PARCIALMENTE_VERIFICADO] | Spot, precio cercano (diff 1.2%), temporalidad no exacta |
| BTC-SPOT-02 | 69.000 | [DICHO]+[NO_VERIFICABLE] | Spot, fuera de rango (diff 6.3%) |
| BTC-SPOT-03 | 75.508 | [DICHO]+[PARCIALMENTE_VERIFICADO] | Spot, precio cercano (diff 1.0%), temporalidad no exacta |
| BTC-SPOT-04 | 71.020 | [DICHO]+[NO_VERIFICABLE] | Spot, fuera de rango (diff 3.3%) |
| BTC-SPOT-05 | 78.900 | [DICHO]+[NO_VERIFICABLE] | Spot, fuera de rango (diff 2.4%) |
| BTC-SPOT-06 | 79.989 | [DICHO]+[PARCIALMENTE_VERIFICADO] | Spot, precio cercano (diff 1.0%), temporalidad no exacta |
| BTC-SPOT-07 | 80.308 | [DICHO]+[PARCIALMENTE_VERIFICADO] | Spot, precio cercano (diff 0.6%), temporalidad no exacta |
| BTC-SPOT-08 | 73.396 | [DICHO]+[PARCIALMENTE_VERIFICADO] | Spot, precio cercano (diff 0.3%), temporalidad no exacta |
| BTC-SPOT-09 | 71.509 | [DICHO]+[NO_VERIFICABLE] | Spot, fuera de rango (diff 2.9%) |
| BTC-SPOT-10 | 69.997 | [DICHO]+[NO_VERIFICABLE] | Spot, fuera de rango (diff 5.0%) |
| BTC-SPOT-11 | 69.940 | [DICHO]+[NO_VERIFICABLE] | Spot, fuera de rango (diff 5.0%) |
| BTC-SPOT-12 | 74.761 | [DICHO]+[PARCIALMENTE_VERIFICADO] | Spot, precio cercano (diff 0.9%), temporalidad no exacta |
| BTC-SPOT-13 | 75.047 | [DICHO]+[PARCIALMENTE_VERIFICADO] | Spot, precio cercano (diff 0.6%), temporalidad no exacta |
| BTC-SPOT-14 | 75.223 | [DICHO]+[PARCIALMENTE_VERIFICADO] | Spot, precio cercano (diff 0.3%), temporalidad no exacta |
| BTC-SPOT-15 | 75.509 | [DICHO]+[PARCIALMENTE_VERIFICADO] | Spot, precio cercano (diff 0.05%), temporalidad no exacta |
| BTC-SPOT-16 | 75.883 | [DICHO]+[PARCIALMENTE_VERIFICADO] | Spot, precio cercano (diff 0.5%), temporalidad no exacta |
| BTC-SPOT-17 | 76.256 | [DICHO]+[PARCIALMENTE_VERIFICADO] | Spot, precio cercano (diff 1.0%), temporalidad no exacta |
| BTC-SPOT-18 | 74.000 | [DICHO]+[PARCIALMENTE_VERIFICADO] | Spot, precio cercano (diff 0.5%), temporalidad no exacta |
| BTC-SPOT-19 | 74.476 | [DICHO]+[PARCIALMENTE_VERIFICADO] | Spot, precio cercano (diff 1.2%), temporalidad no exacta |
| BTC-SPOT-20 | 74.299 | [DICHO]+[PARCIALMENTE_VERIFICADO] | Spot, precio cercano (diff 0.9%), temporalidad no exacta |
| BTC-SPOT-21 | 74.014 | [DICHO]+[PARCIALMENTE_VERIFICADO] | Spot, precio cercano (diff 0.6%), temporalidad no exacta |
| BTC-SPOT-22 | 73.640 | [DICHO]+[PARCIALMENTE_VERIFICADO] | Spot, precio cercano (diff 0.05%), temporalidad no exacta |
| BTC-SPOT-23 | 73.266 | [DICHO]+[PARCIALMENTE_VERIFICADO] | Spot, precio cercano (diff 0.5%), temporalidad no exacta |
| BTC-SPOT-24 | 73.296 | [DICHO]+[PARCIALMENTE_VERIFICADO] | Spot, precio cercano (diff 0.4%), temporalidad no exacta |

### Otros instrumentos (12)

| ID | Precio | Clasificación | Justificación |
|----|--------|---------------|---------------|
| ETH-01 | 2.077 | [DICHO]+[NO_VERIFICABLE] | ETH, sin datos OHLCV |
| ETH-02 | 1.890 | [DICHO]+[NO_VERIFICABLE] | ETH, sin datos OHLCV |
| ETH-03 | 2.156 | [DICHO]+[NO_VERIFICABLE] | ETH, sin datos OHLCV |
| ETH-04 | 2.478 | [DICHO]+[NO_VERIFICABLE] | ETH, sin datos OHLCV |
| GOLD-01 | 3.906 | [DICHO]+[NO_VERIFICABLE] | Oro, sin datos OHLCV |
| GOLD-02 | 3.623 | [DICHO]+[NO_VERIFICABLE] | Oro, sin datos OHLCV |
| GOLD-03 | 2.280 | [DICHO]+[NO_VERIFICABLE] | Oro, sin datos OHLCV |
| SPX-01 | 7.139 | [DICHO]+[NO_VERIFICABLE] | S&P 500, sin datos OHLCV |
| SPX-02 | 6.544 | [DICHO]+[NO_VERIFICABLE] | S&P 500, sin datos OHLCV |
| NDX-01 | 25.400 | [DICHO]+[NO_VERIFICABLE] | NASDAQ, sin datos OHLCV |
| NDX-02 | 25.479 | [DICHO]+[NO_VERIFICABLE] | NASDAQ, sin datos OHLCV |
| NDX-03 | 28.000 | [DICHO]+[NO_VERIFICABLE] | NASDAQ, sin datos OHLCV |

### OCR ilegible (7)

| ID | Precio OCR | Clasificación | Justificación |
|----|-----------|---------------|---------------|
| OCR-01..07 | ILEGIBLE | [OBSERVADO]+[ILEGIBLE]+[NO_VERIFICABLE] | Precios con dígitos cortados, no legibles |

---

## Resumen de clasificación

| Clasificación | Cantidad | % |
|---------------|----------|---|
| [DICHO] | 44 | 86.3% |
| [OBSERVADO] | 7 | 13.7% |
| [VERIFICADO_CON_OHLCV] | 0 | 0% |
| [PARCIALMENTE_VERIFICADO] | 18 | 35.3% |
| [NO_VERIFICABLE] | 26 | 51.0% |
| [ILEGIBLE] | 7 | 13.7% |
| [INCONSISTENTE] | 0 | 0% |

**Nota:** Los porcentajes suman más del 100% porque una afirmación puede tener múltiples etiquetas.

---

## Verificación

- [VERIFICADO_CON_OHLCV] requiere coincidencia de instrumento, mercado, temporalidad, fecha/hora y precio. Ningún nivel cumple esto. ✅
- [PARCIALMENTE_VERIFICADO] requiere precio cercano pero temporalidad no exacta. 18 niveles BTC spot cumplen esto. ✅
- [NO_VERIFICABLE] requiere evidencia insuficiente. 26 niveles cumplen esto. ✅
- [ILEGIBLE] requiere precio no legible. 7 niveles OCR cumplen esto. ✅

**[VERIFICADO]** — 51 niveles clasificados
**[VERIFICADO]** — 0 [VERIFICADO_CON_OHLCV]
**[VERIFICADO]** — 18 [PARCIALMENTE_VERIFICADO]
**[VERIFICADO]** — 26 [NO_VERIFICABLE]
**[VERIFICADO]** — 7 [ILEGIBLE]
