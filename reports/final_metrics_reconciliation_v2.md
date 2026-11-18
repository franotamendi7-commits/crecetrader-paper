# Final Metrics Reconciliation v2 — FASE 3.2.2

## A. Métricas de menciones

| Métrica | Valor | Fuente |
|---------|-------|--------|
| Total de menciones registradas (blind) | 56 | blind_annotation_v1.csv |
| Menciones correspondientes a precios | 55 | 56 - 1 (BLIND-056 = 1988, año) |
| Menciones repetidas (mismo nivel, distinto timestamp) | 14 | occurrence_level_mapping_v2.csv |
| Valores únicos normalizados | 44 + 7 OCR = 51 | ground_truth_annotations_v1.csv |
| Artefactos de transcripción | 2 | 898 (misheard), 2628400 (compuesto) |
| Elementos que no son precios | 1 | 1988 (año del método) |
| Menciones sin correspondencia | 1 | BLIND-056 (1988, no es precio) |

### Desglose de menciones
- 56 menciones totales
- 55 son precios
- 1 es no-precio (1988 = año)
- De las 55 precios: 44 niveles únicos con evidencia verbal + 7 OCR ilegibles (no en transcripción)
- 14 menciones son repeticiones de niveles ya contados
- 2 artefactos (898, 2628400) no son niveles independientes

---

## B. Métricas de niveles

| Métrica | Valor | Fuente |
|---------|-------|--------|
| Total de niveles únicos | 51 | ground_truth_annotations_v1.csv |
| Niveles con evidencia verbal ([DICHO]) | 44 | 32 BTC + 4 ETH + 3 Oro + 2 S&P + 3 NASDAQ |
| Niveles con evidencia visual ([OBSERVADO]) | 7 | OCR ilegible (scene_15) |
| Niveles verificados con OHLCV ([VERIFICADO_CON_OHLCV]) | 0 | Ninguno cumple instrumento+mercado+temporalidad exactos |
| Coincidencias aproximadas no concluyentes | 18 | BTC spot con precio cercano pero temporalidad no exacta |
| Niveles no verificables | 26 | 8 CME + 6 fuera de rango + 9 otros + 3 ... wait |

### Recuento de no verificables
- BTC CME: 8 (sin datos CME)
- BTC spot fuera de rango: 6 (69.000, 71.020, 78.900, 71.509, 69.997, 69.940)
- ETH: 4 (sin datos)
- Oro: 3 (sin datos)
- S&P 500: 2 (sin datos)
- NASDAQ: 3 (sin datos)
- **Total no verificables: 8 + 6 + 4 + 3 + 2 + 3 = 26** ✅

### Niveles ilegibles
- OCR: 7 (precios con dígitos cortados)

### Total: 0 (verificados) + 18 (aproximados) + 26 (no verificables) + 7 (ilegibles) = 51 ✅

---

## C. Métricas de cobertura OHLCV

### Por universo

| Universo | Total | Evaluables | Verificados | Aproximados | No verificables | No evaluables |
|----------|-------|------------|-------------|-------------|-----------------|---------------|
| BTC spot | 24 | 24 | 0 | 18 | 6 | 0 |
| BTC CME | 8 | 0 | 0 | 0 | 8 | 8 (sin datos) |
| ETH | 4 | 0 | 0 | 0 | 4 | 4 (sin datos) |
| Oro | 3 | 0 | 0 | 0 | 3 | 3 (sin datos) |
| S&P 500 | 2 | 0 | 0 | 0 | 2 | 2 (sin datos) |
| NASDAQ | 3 | 0 | 0 | 0 | 3 | 3 (sin datos) |
| OCR ilegible | 7 | 0 | 0 | 0 | 0 | 7 (ilegibles) |
| **Total** | **51** | **24** | **0** | **18** | **26** | **27** |

### Verificación: 24 + 8 + 4 + 3 + 2 + 3 + 7 = 51 ✅
### Verificación: 0 + 18 + 26 + 7 = 51 ✅

---

## D. Denominadores correctos

### 0/32 (BTC)
- Denominador: 32 (24 spot + 8 CME)
- Numerador: 0
- Significado: 0 de 32 niveles de BTC son verdaderamente verificados
- Evaluables: 24 (spot)
- No evaluables: 8 (CME, sin datos)

### 0/51 (Total)
- Denominador: 51 (todos)
- Numerador: 0
- Significado: 0 de 51 niveles totales son verdaderamente verificados
- Evaluables: 24 (BTC spot)
- No evaluables: 27 (8 CME + 9 otros + 7 OCR + 3 ... wait)

**Corrección:** No evaluables = 8 (CME) + 4 (ETH) + 3 (Oro) + 2 (S&P) + 3 (NASDAQ) + 7 (OCR) = 27
Evaluables = 24 (BTC spot)
Total = 24 + 27 = 51 ✅

---

## E. Precisión, recall y F1

**NO CALCULABLES** — No existe una referencia independiente válida.

La anotación ciega (56 menciones) fue realizada por el mismo sistema. No constituye una referencia independiente.

Las métricas de extracción (100% precisión, 100% recall) fueron calculadas contra una referencia construida por el mismo sistema. No son independientes.

**Única métrica con fuente externa:** Validación OHLCV = 0/24 (BTC spot) — porque usa datos de Kraken.

---

## F. Errores corregidos en FASE 3.2.2

1. **Granularidad:** Se diferenció menciones (56) de niveles únicos (51). No se comparan directamente.
2. **Denominadores:** Se definieron correctamente por universo. 0/32 y 0/51 son consistentes.
3. **Clasificación:** Se reemplazó "PARCIALMENTE_VERIFICADO" por "COINCIDENCIA_APROXIMADA_NO_CONCLUYENTE" para ser más preciso.
4. **Fuentes no buscadas:** Se documentó que ETH, Oro, S&P, NASDAQ no tienen fuentes buscadas (no "no disponibles").
5. **Artefactos:** Se identificaron 898 y 2628400 como artefactos, no como niveles.

## G. Errores pendientes

1. **OCR:** 7 niveles ilegibles. Requiere pre-procesamiento de imagen.
2. **Futuros CME:** 8 niveles sin datos. Requiere fuente gratuita de futuros CME.
3. **Otros instrumentos:** 12 niveles sin datos. Requiere búsqueda de fuentes OHLCV.
4. **Independencia:** No hay auditor externo. La anotación ciega es interna.
5. **Ground truth:** Solo 1 video. Métricas no estadísticamente significativas.

---

## Conclusión

- **Menciones:** 56 (55 precios + 1 no-precio)
- **Niveles únicos:** 51 (44 verbal + 7 visual ilegible)
- **Verificados OHLCV:** 0
- **Aproximados:** 18
- **No verificables:** 26
- **Ilegibles:** 7
- **Evaluables:** 24 (solo BTC spot)
- **No evaluables:** 27

**NO DEMOSTRADO INDEPENDIENTEMENTE** — Todas las métricas excepto validación OHLCV.
