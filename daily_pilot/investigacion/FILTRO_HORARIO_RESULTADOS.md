# FILTRO HORARIO y DOBLE FILTRO — resultados

Fecha: 2026-11-25. PAPER_ONLY.

## Filtro horario 04h/16h UTC — par por par (null corregido)

| par | n | E sin | E con | null | WF train→test |
|---|---:|---:|---:|---:|---|
| **BTC** | 774 | +0,161 | +0,187 | 3/4 ✅ | +0,223 → +0,102 |
| **ARB** | 68 | +0,367 | **+0,457** | 4/4 ✅ | +0,336 → **+0,728** |
| **XRP** | 124 | +0,270 | **+0,358** | 3/4 ✅ | +0,331 → **+0,419** |
| THETA | 465 | +0,177 | +0,223 | 2/4 ❌ | — |
| HBAR | 397 | +0,079 | +0,126 | 0/4 ❌ | — |
| ETC | 467 | +0,061 | +0,085 | 0/4 ❌ | — |

ARB y XRP mejoran muchísimo su E con el filtro horario (+0,457 y +0,358),
pero son pocas señales (68 y 124 en 9 años).

## Filtro de riesgo por día (martes 0.5x, jue/vie 1.5x)

```
E +0,169R (vs +0,140) pero DD −118,5R (vs −98,1R) → DESCARTADO
Subir riesgo en días buenos aumenta el drawdown más que la ganancia.
```

## Doble filtro (hora para BTC/ARB/XRP, día para THETA)

| | Original | Con doble filtro |
|---|---:|---:|
| Señales/mes | 64,3 | 38,3 |
| E | +0,140R | +0,142R |
| DD | −98,1R | −92,4R |
| **WF test** | **+0,086R** | **+0,060R** ❌ |
| **2026** | **+23R** | **−14R** ❌ |

**Aunque los pares validaron individualmente, la combinación NO mejora.**
El test de walk-forward empeora y 2026 pasa a negativo.

## Conclusión

La cartera original sigue siendo la mejor configuración global:

```
6 pares · 64 señales/mes · E +0,140R · DD −98,1R · PF 1,38
```

Los filtros por hora/día son mejoras **locales** de algunos pares, no mejoras
de cartera. No se aplican al tracker.

El conmutador `config_cartera.py` queda listo con las dos versiones para
decidir con datos del forward cuando lleguen.

PAPER_ONLY. No se ejecutaron órdenes.
