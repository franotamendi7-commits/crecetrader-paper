# PASO SIGUIENTE: combinar 4h + 1d — DESCARTADO

Fecha: 2026-11-25. Motivo: se iba a usar la capa 1d (DD bajo) para bajar el
DD de la cartera 4h. Medido antes de aplicar. PAPER_ONLY.

## Resultado

| cartera | /mes | E | DD | PF | DD $300 al 0,35% |
|---|---:|---:|---:|---:|---:|
| Solo 4h (4 pares) | 59,4 | +0,128 | **−127,6** | 1,34 | −$134 |
| Solo 1d (3 pares) | 5,4 | +0,101 | −50,8 | 1,25 | −$53 |
| **Mixto 4h+1d** | 63,9 | +0,126 | **−152,8** ❌ | 1,34 | −$160 |

## Por qué empeora

**Solapamiento:** el 90% de las señales 1d cae dentro de los 3 días de una
señal 4h del mismo par:

```
THETA: 135 de 147 señales 1d se solapan con 4h
ETC:   159 de 189
HBAR:  133 de 151
```

No son dos capas independientes: es **la misma operación contada dos veces**.
Por eso el DD sube de −127,6R a −152,8R y octubre empeora de −1,26R a −7,26R.

La diversificación que sí funcionó fue **entre pares**, no entre timeframes.

## Conclusión

- La capa 1d NO se agrega. Se descarta.
- Se mantiene la cartera 4h de 4 pares, 59,4 señales/mes, DD −127,6R.
- Sobre $300 el riesgo sigue siendo 0,35% ($1,05 por operación).

## Lo que sí ataca el DD (pendiente, no medido todavía)

Como el DD viene de la secuencia de pérdidas, lo único que lo bajaría de
verdad es un **filtro de correlación**: no tomar una nueva señal si ya hay
2-3 posiciones abiertas en la misma dirección. Eso es gestión de cartera,
no más indicadores. Es el próximo paso lógico.

PAPER_ONLY. No se ejecutaron órdenes.
