# OHLCV Denominator Reconciliation v1 — FASE 3.2.1

## Definición de universos

### Universo A — Total de afirmaciones
Todos los niveles identificados, independientemente de verificabilidad.

| Métrica | Valor |
|---------|-------|
| Total | 51 |
| Evaluable con fuentes existentes | 24 (BTC spot) |
| No evaluable | 27 (8 CME + 9 otros + 7 OCR + 3 fuera de rango... wait) |

**Corrección:** Los 51 se distribuyen así:
- 24 BTC spot (evaluables parcialmente con Kraken)
- 8 BTC futuros CME (no evaluables, sin datos CME)
- 4 ETH (no evaluables, sin datos ETH)
- 3 Oro (no evaluables, sin datos Oro)
- 2 S&P 500 (no evaluables, sin datos S&P)
- 3 NASDAQ (no evaluables, sin datos NASDAQ)
- 7 OCR ilegible (no evaluables, precios ilegibles)

Evaluable: 24 (BTC spot)
No evaluable: 27 (8+4+3+2+3+7 = 27)
Total: 24 + 27 = 51 ✅

### Universo B — BTC spot
| Métrica | Valor |
|---------|-------|
| Total | 24 |
| Evaluable con Kraken | 24 |
| Verificado (instrumento+mercado+temporalidad exactos) | 0 |
| Parcialmente verificado (precio cercano, temporalidad no exacta) | 18 |
| No verificado (fuera de rango) | 6 |
| **0/24 verificados** |

### Universo C — BTC futuros CME
| Métrica | Valor |
|---------|-------|
| Total | 8 |
| Evaluable con fuentes existentes | 0 (sin datos CME gratuitos) |
| Verificado | 0 |
| Parcialmente verificado | 0 |
| No verificado | 8 |
| **0/8 verificados** |

### Universo D — Otros instrumentos
| Métrica | Valor |
|---------|-------|
| Total | 12 (4 ETH + 3 Oro + 2 S&P + 3 NASDAQ) |
| Evaluable con fuentes existentes | 0 (sin datos) |
| Verificado | 0 |
| No verificado | 12 |
| **0/12 verificados** |

### Universo E — No identificables
| Métrica | Valor |
|---------|-------|
| Total | 7 (OCR ilegible) |
| Evaluable | 0 (precios ilegibles) |
| Verificado | 0 |
| No verificado | 7 |
| **0/7 verificados** |

---

## Resolución de 0/32 vs 0/51

### 0/32
- Universo: BTC (24 spot + 8 CME = 32)
- Significa: 0 de 32 niveles de BTC son verdaderamente verificados con OHLCV
- Denominador: 32 (todos los niveles de BTC)
- Numerador: 0 (ninguno tiene instrumento+mercado+temporalidad exactos)

### 0/51
- Universo: Total (51)
- Significa: 0 de 51 niveles totales son verdaderamente verificados con OHLCV
- Denominador: 51 (todos los niveles)
- Numerador: 0 (ninguno verificado)

### Relación
0/32 es un subconjunto de 0/51. Los 19 niveles no BTC (12 otros + 7 OCR) tampoco son verificables, por lo que 0/51 es consistente con 0/32.

**Ambos son correctos. 0/32 es más específico (solo BTC). 0/51 es más general (todo).**

---

## Tabla resumen de universos

| Universo | Total | Evaluable | Verificado | Parcial | No verificado | Ilegible |
|----------|-------|-----------|------------|---------|---------------|----------|
| A (Total) | 51 | 24 | 0 | 18 | 26 | 7 |
| B (BTC spot) | 24 | 24 | 0 | 18 | 6 | 0 |
| C (BTC CME) | 8 | 0 | 0 | 0 | 8 | 0 |
| D (Otros) | 12 | 0 | 0 | 0 | 12 | 0 |
| E (Ilegible) | 7 | 0 | 0 | 0 | 0 | 7 |

**Verificación:** 24 + 8 + 12 + 7 = 51 ✅

---

## Notas importantes

1. **No se cuenta un nivel como verificado simplemente porque su precio se encuentra dentro del rango general del activo.** Se requiere coincidencia de instrumento, mercado, temporalidad, fecha/hora y precio.

2. **No se utiliza BTC spot para verificar futuros CME.** Son mercados distintos.

3. **No se utiliza datos de otra temporalidad como sustituto sin justificarlo.** Los niveles intradía se comparan contra 4H (el mínimo disponible en Kraken), pero se documenta que la temporalidad no coincide exactamente.

4. **No se inventa disponibilidad de datos.** Futuros CME, ETH, Oro, S&P, NASDAQ no tienen datos disponibles gratuitamente.

**[VERIFICADO]** — 5 universos definidos
**[VERIFICADO]** — 0/32 y 0/51 son consistentes
**[VERIFICADO]** — 24 evaluable, 27 no evaluable
**[VERIFICADO]** — No se cuenta como verificado sin coincidencia exacta
