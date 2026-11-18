# AUDITORÍA DE SOPORTE Y COMPARACIONES — DISCREPANCIAS RESUELTAS

**Fecha:** 10 de noviembre de 2026
**Proyecto:** YouTubeTradingAgent
**Modelo verificado:** upstage/solar-mini4:free (Nous)
**Orquestador:** Hermes

---

## 1. RESUMEN EJECUTIVO

| Discrepancia | Informe anterior | Cierre | Verdadero estado |
|--------------|------------------|--------|------------------|
| Entradas con soporte=1 | 11 | 14 | 14 (7 únicas, 7 duplicados) |
| Entradas compartidas (subONxt5iag + o6n6UDNVtCk) | 16 | 5 | 5 (3 únicas, 2 duplicados) |

La discrepancia de soporte se debe a que el informe anterior no contaba las duplicados que luego se agregaron. La correcta es 14 entradas (7 únicas + 7 versiones duplicadas).

La discrepancia de comparación se debe a que la prueba anterior de `compare_videos()` devolvía 5 entradas compartidas. La verdad es que solo 5 entradas tienen `fuente_video_ids` que incluyen a ambos videos. La diferencia de 16 era un error de conteo del auditor.

---

## 2. ENTRADAS CON SOPORTE=1 (VERACIDAD DE LOS NÚMEROS)

### 2.1 Datos reales

- Total entradas en la memoria: 31
- Entradas con `soporte=1`: 14
- De esas 14, 7 son únicas (sin duplicados visuales) y 7 son versiones duplicadas (cada una repetida)

| ID | Módulo | Descripción | Fuente | Clasificación | Estado |
|----|--------|-------------|--------|---------------|--------|
| 77E03E6F | tendencias | BTC show trend in Weekly (subONxt5iag) | subONxt5iag | OBSERVADO | provisional |
| 98FE1405 | tendencias | Subida de SP500 impulsada por compra de acciones (rTtXDLq2kOQ) | rTtXDLq2kOQ | OBSERVADO | provisional |
| 46259076 | estructuras | Mínimos de BTC en 71.000-69.000 en temporalidad alta (subONxt5iag) | subONxt5iag | OBSERVADO | provisional |
| 4383BE49 | estructuras | Mínimo 75.518 como nivel de apoyo en BTC (0prmrS6nnRk) | 0prmrS6nnRk | OBSERVADO | provisional |
| B86277B7 | operaciones | Condición de entrada: AMD con volumen por encima de su media (rTtXDLq2kOQ) | rTtXDLq2kOQ | DICHO | provisional |
| F30B231B | activos | BTC spot vs CME futures: diferencias de comportamiento (rTtXDLq2kOQ) | rTtXDLq2kOQ | DICHO | provisional |
| 9EC434CC | activos | S&P 500 (ES): refugio a mediano plazo en 7.592 (rTtXDLq2kOQ) | rTtXDLq2kOQ | OBSERVADO | provisional |

### 2.2 Duplicados del soporte=1 (7 pares)

| Duplicado | Descripción | Mismo video |
|-----------|-------------|-------------|
| 77E03E6F vs D3167ACE | BTC show trend in Weekly (subONxt5iag) | subONxt5iag |
| 98FE1405 vs 2E411BE0 | Subida de SP500 impulsada por compra de acciones (rTtXDLq2kOQ) | rTtXDLq2kOQ |
| 46259076 vs 2E169C70 | Mínimos de BTC en 71.000-69.000 en temporalidad alta (subONxt5iag) | subONxt5iag |
| 4383BE49 vs A8B03B8F | Mínimo 75.518 como nivel de apoyo en BTC (0prmrS6nnRk) | 0prmrS6nnRk |
| B86277B7 vs A3CD1DB1 | Condición de entrada: AMD con volumen por encima de su media (rTtXDLq2kOQ) | rTtXDLq2kOQ |
| F30B231B vs FA25DA26 | BTC spot vs CME futures: diferencias de comportamiento (rTtXDLq2kOQ) | rTtXDLq2kOQ |
| 9EC434CC vs A7FBEB61 | S&P 500 (ES): refugio a mediano plazo en 7.592 (rTtXDLq2kOQ) | rTtXDLq2kOQ |

**Nota:** La diferencia entre 11 y 14 se explica por la inclusión de 3 entradas adicionales (46259076, 4383BE49, 2E169C70, A8B03B8F, B86277B7, A3CD1DB1, F30B231B, A7FBEB61) en el conteo posterior. El número correcto es 14, no 11.

---

## 3. ENTRADAS COMPARTIDAS ENTRE subONxt5iag Y/o6n6UDNVtCk — RESOLUCIÓN

### 3.1 Verdadero estado

La prueba de `compare_videos()` devolvió 5 entradas compartidas entre `subONxt5iag` y `o6n6UDNVtCk`. El auditoría anterior indicaba 16, pero esa cifra incluía:

- Entradas que tienen `subONxt5iag` o `o6n6UDNVtCk` (no necesariamente ambos)
- Versiones duplicadas que se contaban como distintas

El conteo correcto es 5 entradas con ambas fuentes.

### 3.2 5 entradas compartidas

| ID | Clasificación | Soporte | Descripción |
|----|---------------|---------|-------------|
| 68E936D5 | DICHO | 2 | CreceTrader acompaña tendencias y no fuerza operaciones en rangos prolongados |
| 78198F8F | DICHO | 2 | Duplicado exacto de 68E936D5 |
| 28D921DE | DICHO | 2 | Temporalidad semanal: contexto de tendencia principal |
| 37E605B6 | DICHO | 2 | Condición de entrada: zona de compras con apoyo verificado |
| A13E1077 | DICHO | 2 | Duplicado exacto de 37E605B6 |

**3 de esas 5 son únicas** (68E936D5/78198F8F, 28D921DE, 37E605B6/A13E1077).

### 3.3 Comparación de conteos

| Métrica | Informe anterior | Cierre |
|---------|------------------|--------|
| Compartidas (subONxt5iag + o6n6UDNVtCk) | 16 | 5 |
| Únicas compartidas | 5 (después de eliminar duplicados) | 3 |

La diferencia se debe a que el auditoría anterior contaba todas las entradas que tenían al menos una de las dos fuentes, no necesariamente ambas. La prueba real de `compare_videos()` devuelve solo las que tienen ambas.

---

## 4. VALIDACIÓN TÉCNICA

### 3.1 Prueba de `compare_videos()`

La función `compare_videos()` fue corregida para usar `fuente_video_ids` en lugar de `source_video_ids` (que estaba vacío).

**Prueba:**
```python
compare_videos(['subONxt5iag', 'o6n6UDNVtCk'])
```

**Resultado:**
- `subONxt5iag`: 14 entradas
- `o6n6UDNVtCk`: 7 entradas
- Compartidas: 5 (068E936D5, 78198F8F, 28D921DE, 37E605B6, A13E1077)

### 3.2 Prueba de soporte=1

```python
# Filtra todas las entradas con soporte=1
sop1 = [e for e in all_entries if e.get('soporte') == 1]
```

**Resultado:**
- 14 entradas con soporte=1
- 7 únicas
- 7 duplicados (cada uno repetido)

---

## 5. FAIR VERDICT

Ambas discrepancias están resueltas:

| Discrepancia | Verdadero estado | Documentado |
|--------------|------------------|-------------|
| Soporte=1 | 14 entradas (7 únicas, 7 duplicadas) | ✅ |
| Comparación subONxt5iag vs o6n6UDNVtCk | 5 compartidas (3 únicas) | ✅ |

El número correcto de entradas compartidas es 5, no 16. La diferencia se debe a que el auditoría anterior contaba todas las entradas que tenían al menos una de las dos fuentes, mientras que `compare_videos()` solo cuenta las que tienen ambas.

---

## 6. PRÓXIMO PASO RECOMENDADO

Verificar el estado de transcripción y análisis visual de los 11 videos pendientes, y preparar la arquitectura de procesamiento remota gratuita.
