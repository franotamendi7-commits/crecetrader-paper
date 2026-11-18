# B4 — Esquema de anotación (definición no ambigua de campos)

Objetivo: que cada elemento se registre **una sola vez** y con su legibilidad individual (1 claro · 2 parcial · 3 no legible · 4 no presente).

## Reglas de asignación

| Campo | Qué contiene | NO contiene |
|---|---|---|
| `instrument` | Símbolo exacto del gráfico (BTCUSD, ETHUSD, ES, NQ, XAUUSD, AMD, MDT, SPX, OTHER) | — |
| `exchange` | Exchange/fuente si es legible (Coinbase, etc.) | — |
| `timeframe` | Weekly, Daily, 4H, 1H, 15m, 5m | — |
| `visible_price_labels` | **Solo valores con etiqueta escrita** en la imagen, con ubicación. | Niveles sin etiqueta, valores deducidos |
| `horizontal_levels` | Líneas **horizontales** (soporte/resistencia/zona), con su rol y si tienen etiqueta. | Directrices con pendiente |
| `trendlines` | Directrices **con pendiente** (ascendente/descendente), con descripción. | Líneas horizontales |
| `market_structure` | trend / range / support / resistance | — |
| `liquidity_zones` | Zonas de liquidez **visibles** (líneas o áreas que las marcan). | Suposiciones de liquidez |
| `indicators` | MA, Fibonacci, Volume (solo lo visible). | Indicadores no visibles |
| `visible_candlestick_information` | OHLC/cuerpo/mecha legibles, o NO LEGIBLE | — |
| `unreadable_information` | Elementos que **existen** pero no se pueden leer. | Elementos inexistentes |
| `abstentions` | Campos que el anotador **no valoró** por no poder determinarlos. | — |
| `legibility_*` | Estado 1-4 **por campo** (instrument, timeframe, prices, horizontal_levels, trendlines, indicators, structure, liquidity). | — |

## Desambiguación

- Una línea horizontal **con etiqueta**: se registra en `horizontal_levels` (con `etiquetada=si`) **y** su valor en `visible_price_labels`. No es duplicidad: una es la línea, la otra es el texto.
- Una línea horizontal **sin etiqueta**: solo `horizontal_levels` con `etiquetada=no`. **No** va en `visible_price_labels`.
- Una línea con pendiente: solo `trendlines`.
- Si una línea podría ser horizontal o directriz: registrala una vez, en el campo que mejor describa su función, y aclará la duda en `notes`.
- Si un indicador está tapado: `indicators` sin esa entrada + el elemento en `unreadable_information`.

## Estados de legibilidad (los cuatro)

| Código | Significado | Uso |
|---|---|---|
| 1 | Claro | El dato se lee sin duda |
| 2 | Parcial | Se entiende con duda razonable |
| 3 | No legible | Existe pero no se puede leer |
| 4 | No presente | El elemento no existe en la imagen |

Regla: si el código es 2 (parcial), el valor **no** se considera verificado; debe marcarse en `abstentions` si la duda es sobre el valor exacto.

## Prohibido

- Deducir precios o niveles por contexto.
- Completar dígitos por intuición.
- Registrar el mismo elemento en dos campos (salvo la excepción línea-etiqueta).
- Usar conocimiento de trading para reconstruir información.
