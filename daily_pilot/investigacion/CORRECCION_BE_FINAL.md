# CORRECCIÓN IMPORTANTE — Bug de Break-Even y nueva estrategia final

Fecha: 2026-11-25. Este archivo **reemplaza** las conclusiones de
`ESTRATEGIA_FINAL_VALIDADA.md` en lo que respecta a ETH y al drawdown.

## El bug que encontré

En `estrategia_bull.py::simular`, el Break-Even se activaba con:

```python
if be_at and lo <= st0 and hi >= e + be_at * risk:
```

Eso exige que **en la misma vela** el precio toque el stop original Y llegue
a 1R. Casi nunca pasa. El BE quedaba inactivo y los números de ETH estaban
inflados.

**Corregido:**
```python
if be_trigger and not be and hi >= be_trigger:
    be = True
    st = e
```

## Con el BE corregido

| | BTC (salida HALF) | BTC (full) | ETH |
|---|---:|---:|---:|
| Señales/mes | 21,5 | 21,5 | 13,3 |
| Esperanza | **+0,311R** | +0,102R | +0,036R |
| Acierto | 41,8% | 41,7% | 26,1% |
| Factor beneficio | **1,88** | 1,29 | 1,08 |
| Drawdown | **−58,4R** | −70,7R | −90,4R |
| Null p | **0,000 PASA** | 0,000 | **0,217 RUIDO** |
| WF train | +0,350 | — | +0,067 |
| WF test | **+0,221R** ✅ | — | −0,116 ❌ |
| Degradación | −36,9% | — | −273% |

**ETH queda DESCARTADA.** Con el simulador correcto no pasa el null y su
test de walk-forward es negativo. Busqué 29 variantes alternativas con
E>0 y test>0; las mejores dan p=0,06 a 0,12 → RUIDO. No hay evidencia.

**BTC mejora de verdad** con el take-profit parcial (50% en 1R, resto al
target Fib 1.5): E de +0,250 a **+0,311**, PF de 1,58 a **1,88**, DD de
−79,9 a **−58,4**. Y el test del walk-forward sube de +0,170 a **+0,221**.

## Estrategia final (única válida)

```
BTC 4h: ema13 / emaT200 / swing5 / ret_pos / Fib 1.5
Stop fijo = swing low post-cambio de tendencia
Entrada: pullback a EMA + retorno 30 velas positivo
Salida: 50% en 1R → stop a Break-Even → resto al target Fib 1.5
Sizing: riesgo_usd / (entrada - stop). 0,5%-1% del capital.
```

## Números finales con $300

| riesgo | DD esperado | Capital mínimo recomendado |
|---|---:|---:|
| **0,5% ($1,50)** | **−$88** ✅ | $150 |
| 1,0% ($3) | −$175 | $300 |

Antes (con el bug): DD −$123 a 0,5%. **Bajó un 29%** arreglando la salida.

## Sobre tu pregunta del DD

Tenías razón en desconfiar. El DD no se arreglaba con sizing: se arreglaba
con la **salida**. El take-profit parcial lo bajó de −79,9R a −58,4R sin
tocar el riesgo, y además subió la esperanza. Eso es lo que buscabas.

PAPER_ONLY. No se ejecutaron órdenes.
