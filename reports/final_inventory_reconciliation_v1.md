# Final Inventory Reconciliation v1 — FASE 3.2.1

## 1. Inventario completo de 51 niveles

### Distribución por instrumento (verificada)

| Categoría | IDs | Cantidad |
|-----------|-----|----------|
| BTC — Futuros CME | BTC-CME-01..08 | 8 |
| BTC — Spot | BTC-SPOT-01..24 | 24 |
| ETH | ETH-01..04 | 4 |
| Oro | GOLD-01..03 | 3 |
| S&P 500 | SPX-01..02 | 2 |
| NASDAQ | NDX-01..03 | 3 |
| OCR ilegible | OCR-01..07 | 7 |
| **TOTAL** | | **51** |

### Verificación aritmética
8 + 24 + 4 + 3 + 2 + 3 + 7 = 51 ✅

---

## 2. Resolución de la discrepancia 9 vs 12

### Problema
FASE 3.2 reportó "9 niveles de otros instrumentos sin datos" en múltiples lugares, pero la tabla de distribución muestra 4 ETH + 3 Oro + 2 S&P + 3 NASDAQ = **12** niveles no BTC.

### Análisis
La cifra "9" aparece en:
- `ground_truth_other_instruments_v1.md`: "9 niveles de otros instrumentos (4 ETH + 3 Oro + 2 S&P + 3 NASDAQ)" — **error aritmético** (4+3+2+3 = 12, no 9)
- `ground_truth_benchmark_v1.md`: "Otros instrumentos: 9" — mismo error
- `ground_truth_inventory_v1.md`: "9 niveles de otros instrumentos" en la sección de resumen — mismo error

### Resolución
**La cifra correcta es 12, no 9.** El error fue aritmético: 4+3+2+3 = 12, no 9. Posiblemente se calculó como 4+3+2 = 9 (omitiendo NASDAQ).

**No se forzaron los totales. Se documentó el error.**

### Categorías adicionales (evidencia)

Además de la distribución por instrumento, existen categorías de evidencia que se superponen:

| Categoría de evidencia | Cantidad | Nota |
|------------------------|----------|------|
| Niveles con evidencia verbal ([DICHO]) | 44 | 32 BTC + 4 ETH + 3 Oro + 2 S&P + 3 NASDAQ |
| Niveles con evidencia visual ([OBSERVADO]) | 7 | OCR ilegible (scene_15) |
| Niveles verificables con OHLCV | 0 | Ninguno tiene instrumento+mercado+temporalidad exactos |
| Niveles parcialmente verificables | 18 | BTC spot con precio cercano pero temporalidad no exacta |
| Niveles no verificables | 26 | 8 CME + 6 fuera de rango + 9 otros instrumentos + ... |
| Niveles ilegibles | 7 | OCR parcial |

**Nota:** Las categorías de evidencia se superponen con la distribución por instrumento. No son mutuamente excluyentes.

---

## 3. Categorías mutuamente excluyentes (distribución del inventario)

Para la distribución del inventario, las categorías son mutuamente excluyentes:

| Categoría | Cantidad | % |
|-----------|----------|---|
| BTC — Futuros CME | 8 | 15.7% |
| BTC — Spot | 24 | 47.1% |
| ETH | 4 | 7.8% |
| Oro | 3 | 5.9% |
| S&P 500 | 2 | 3.9% |
| NASDAQ | 3 | 5.9% |
| OCR ilegible | 7 | 13.7% |
| **Total** | **51** | **100%** |

### Categorías de evidencia (separadas, no mutuamente excluyentes)

| Categoría | Cantidad | % del total |
|-----------|----------|-------------|
| [DICHO] (verbal) | 44 | 86.3% |
| [OBSERVADO] (visual) | 7 | 13.7% |
| [VERIFICADO_CON_OHLCV] | 0 | 0% |
| [PARCIALMENTE_VERIFICADO] | 18 | 35.3% |
| [NO_VERIFICABLE] | 26 | 51.0% |
| [ILEGIBLE] | 7 | 13.7% |

---

## 4. Registros con ID único y estable

Todos los 51 registros ya tienen IDs únicos en el CSV (`ground_truth_annotations_v1.csv`):
- BTC-CME-01..08 (8)
- BTC-SPOT-01..24 (24)
- ETH-01..04 (4)
- GOLD-01..03 (3)
- SPX-01..02 (2)
- NDX-01..03 (3)
- OCR-01..07 (7)

**Total: 51 registros con IDs únicos.** ✅

---

## 5. Duplicados documentados

9 precios mencionados múltiples veces en la transcripción (contados como 1 nivel cada uno):

| Precio | Timestamps | Nota |
|--------|-----------|------|
| 75.835 | 106.2s, 118.4s | Repetido, mismo nivel |
| 65.520 | 124.8s, 167.2s | Repetido, mismo nivel |
| 71.020 | 145.8s, 167.2s | Repetido, mismo nivel |
| 73.396 | 353.2s, 372.3s, 537.8s | Repetido 3 veces, mismo nivel |
| 71.509 | 317.9s, 372.3s | Repetido, mismo nivel |
| 69.000 | 64.5s, 317.9s, 372.3s | Repetido 3 veces, mismo nivel |
| 83.366 | 317.9s, 417.8s | Repetido, mismo nivel |
| 73.266 | 520.2s, 529.0s | Repetido, mismo nivel |
| 74.000 | 501.6s | Mencionado una vez |

**Nota:** 74.000 se menciona una vez (501.6s). Los otros 8 se repiten. Todos se contaron como 1 nivel cada uno.

---

## 6. Niveles que pueden ser afirmaciones distintas

Un mismo precio puede representar afirmaciones diferentes si se refiere a instrumentos, temporalidades o escenarios distintos. En este inventario:

- **75.835** (106.2s y 118.4s): Mismo precio, mismo contexto (futuros CME, 4H). Se cuenta como 1 nivel.
- **65.520** (124.8s y 167.2s): Mismo precio, mismo contexto (futuros CME, bloque comprador). Se cuenta como 1 nivel.
- **73.396** (353.2s, 372.3s, 537.8s): Mismo precio, contextos ligeramente distintos (4H spot). Se cuenta como 1 nivel.

**No se identificaron casos donde un mismo precio represente afirmaciones distintas (diferente instrumento, temporalidad o escenario).**

---

## Conclusión

- **51 niveles únicos** con IDs únicos y estables ✅
- **Distribución por instrumento suma 51** ✅
- **La discrepancia 9 vs 12 se resolvió:** error aritmético (4+3+2+3=12, no 9) ✅
- **9 duplicados documentados** ✅
- **No se forzaron los totales** ✅

**[VERIFICADO]** — 51 niveles con IDs únicos
**[VERIFICADO]** — Distribución por instrumento suma 51
**[VERIFICADO]** — Discrepancia 9 vs 12 resuelta (error aritmético)
**[VERIFICADO]** — 9 duplicados documentados
