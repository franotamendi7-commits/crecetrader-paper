# Final Metrics Reconciliation v3 — FASE 3.2.3

## Recalculo desde datos originales

### A. Menciones

| Métrica | Valor | Fuente |
|---------|-------|--------|
| Total de ocurrencias (blind) | 56 | blind_annotation_v1.csv (57 líneas - 1 header) |
| Menciones numéricas (precios) | 55 | 56 - 1 (BLIND-056 = 1988, año) |
| Menciones no-precio | 1 | BLIND-056 (1988 = año del método) |
| Valores únicos normalizados | 44 | occurrence_level_mapping_v3.csv |
| Repeticiones (ocurrencias adicionales) | 11 | 55 - 44 = 11 |
| Artefactos de transcripción | 2 | 898 (contexto BLIND-009), 2628400 (contexto BLIND-055) |
| Niveles verbales únicos | 44 | 32 BTC + 4 ETH + 3 Oro + 2 S&P + 3 NASDAQ |
| Elementos visuales ilegibles | 7 | OCR-01 a OCR-07 (scene_15) |

### B. Niveles

| Métrica | Valor |
|---------|-------|
| Total de niveles únicos | 51 |
| VERIFICADO_CON_OHLCV | 0 |
| COINCIDENCIA_APROXIMADA_NO_CONCLUYENTE | 18 (BTC spot) |
| SIN_COINCIDENCIA_EN_RANGO | 6 (BTC spot) |
| NO_EVALUABLE | 20 (8 CME + 12 otros) |
| ILEGIBLE | 7 (OCR) |
| **Total** | **0 + 18 + 6 + 20 + 7 = 51** ✅ |

### C. OHLCV por universo

| Universo | Total | Evaluables | Verificados | Aproximados | Sin coincidencia | No evaluables | Ilegibles |
|----------|-------|------------|-------------|-------------|------------------|---------------|-----------|
| BTC spot | 24 | 24 | 0 | 18 | 6 | 0 | 0 |
| BTC CME | 8 | 0 | 0 | 0 | 0 | 8 | 0 |
| ETH | 4 | 0 | 0 | 0 | 0 | 4 | 0 |
| Oro | 3 | 0 | 0 | 0 | 0 | 3 | 0 |
| S&P 500 | 2 | 0 | 0 | 0 | 0 | 2 | 0 |
| NASDAQ | 3 | 0 | 0 | 0 | 0 | 3 | 0 |
| OCR ilegible | 7 | 0 | 0 | 0 | 0 | 0 | 7 |
| **Total** | **51** | **24** | **0** | **18** | **6** | **20** | **7** |

### D. Verificación

- 0 + 18 + 6 + 20 + 7 = 51 ✅
- 24 evaluables + 27 no evaluables = 51 ✅ (27 = 8 CME + 4 ETH + 3 Oro + 2 S&P + 3 NASDAQ + 7 OCR)

### E. Métricas no demostrables

Las siguientes métricas NO pueden sostenerse con la evidencia actual:
- Precisión de extracción: NO_CALCULABLE (referencia no independiente)
- Recall de extracción: NO_CALCULABLE (referencia no independiente)
- Exactitud de instrumentos: NO_CALCULABLE (muestra pequeña)
- Exactitud de temporalidades: NO_CALCULABLE (muestra pequeña)
- Clasificación 100%: NO_CALCULABLE (mismo sistema)
- F1: NO_CALCULABLE (sin referencia independiente)

### F. Métrica con fuente externa

- Validación OHLCV (BTC spot): 0/24 verificados (Kraken, datos externos)
- Esta es la ÚNICA métrica con fuente externa independiente

### G. Normalizaciones verificadas

| Original | Normalizado | Justificación | Confianza |
|----------|-------------|---------------|-----------|
| 1890 | 1.890 | Contexto ETH ~2.0 | Alta |
| 3906 | 3.906 | Contexto Oro ~3-4 | Alta |
| 3623 | 3.623 | Contexto Oro ~3-4 | Alta |
| 2280 | 2.280 | Contexto Oro ~2-4 | Alta |
| 7139 | 7.139 | Contexto S&P ~7000 | Alta |
| 6544 | 6.544 | Contexto S&P ~6000 | Alta |
| 25400 | 25.400 | Contexto NASDAQ ~25000 | Alta |
| 25479 | 25.479 | Contexto NASDAQ ~25000 | Alta |
| 28000 | 28.000 | Contexto NASDAQ ~28000 | Alta |
| 476 | 74.476 | Truncación verbal, inferido | Baja (inferido) |
| 898 | ARTEFACTO | Probablemente misheard de 78.900 o 78.989 | Baja |
| 2628400 | ARTEFACTO | Concatenación de elementos | Baja |

### H. Errores corregidos de v2

1. Texto residual "+ 3 ... wait" eliminado
2. Categorías mutuamente excluyentes (VERIFICADO, APROXIMADO, SIN_COINCIDENCIA, NO_EVALUABLE, ILEGIBLE)
3. Repeticiones recalculadas: 11 (no 14)
4. Normalizaciones verificadas individualmente
5. "NO BUSCADA" en lugar de "no disponible" para fuentes no consultadas
6. Métricas no demostrables marcadas como NO_CALCULABLE

### I. Limitaciones pendientes

1. OCR: 7 niveles ilegibles (requiere pre-procesamiento de imagen)
2. Futuros CME: 8 niveles sin datos (requiere fuente gratuita)
3. Otros instrumentos: 12 niveles sin datos (requiere búsqueda de fuentes)
4. Independencia: No hay auditor externo
5. Ground truth: Solo 1 video
EOF