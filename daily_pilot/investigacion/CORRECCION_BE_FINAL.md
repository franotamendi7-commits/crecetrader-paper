# CORRECCIÓN DEFINITIVA — Bug de Break-Even + salida parcial

Fecha: 2026-11-25. Reemplaza las conclusiones de `ESTRATEGIA_FINAL_VALIDADA.md`.
Todos los números de este archivo salen del código que queda en el repo
(`estrategia_bull.py::simular` con `salida='half'`), verificado dos veces.

## El bug

```python
# ANTES (mal): exigia tocar el stop original en LA MISMA VELA que llega a 1R
if be_at and lo <= st0 and hi >= e + be_at * risk:
# AHORA (bien): BE se activa al alcanzar 1R, punto
if be_trigger and not be and hi >= be_trigger:
```

## NÚMEROS FINALES (BTC 4h, 9,3 años, 2.393 operaciones)

| | **HALF (final)** | FULL (comparación) |
|---|---:|---:|
| Señales/mes | **21,5** | 21,5 |
| Esperanza | **+0,157R** | +0,105R |
| Acierto | **62,1%** | 41,0% |
| Factor beneficio | **1,45** | 1,30 |
| Drawdown | **−56,0R** | −72,3R |
| **Null sintético** | **p=0,013 PASA** ✅ | p=0,075 RUIDO ❌ |
| WF train | +0,178R | +0,137R |
| **WF test** | **+0,107R** ✅ | +0,031R |
| Degradación | −39,9% | −77,4% |

**La salida parcial es lo que hace que la estrategia valide.** Sin ella es
RUIDO (p=0,075) y el test del walk-forward casi cero. Con ella pasa el null
y el test queda en +0,107R.

## ETH: descartada

Con el BE corregido, ETH da E=+0,036R, PF=1,08, **null p=0,217 (RUIDO)** y
walk-forward test −0,116R. Busqué 29 variantes alternativas con E>0 y test>0:
las mejores dan p=0,06 a 0,12 → tampoco pasan. No hay evidencia de ventaja.

## Estrategia final única

```
BTC 4h · ema13 / emaT200 / swing5 / ret_pos / target Fib 1.5
STOP fijo  = swing low posterior al cambio de tendencia
ENTRADA    = pullback a EMA con retorno 30 velas positivo
SALIDA     = 50% en 1R → stop a Break-Even → resto al target Fib 1.5
SIZING     = riesgo_usd / (entrada − stop)
RIESGO     = 0,5% a 1% del capital (nunca más del 5%)
```

## $300

| riesgo | por operación | DD esperado | Capital mínimo |
|---|---:|---:|---:|
| **0,5%** | $1,50 | **−$84** ✅ | $150 |
| 1,0% | $3,00 | −$168 | $300 |

El DD bajó de −79,9R a **−56,0R** arreglando la salida, sin tocar el riesgo.
Esa era tu pregunta: no era el sizing, era la salida.

## Aviso

La ventaja es real pero modesta (+0,157R por operación) y el walk-forward
sigue degradando ~40%. Es Papel, no dinero real. No se ejecutaron órdenes.
