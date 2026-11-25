# ESTRATEGIA FINAL VALIDADA — Bull-run Pullback (BTC + ETH)

Fecha: 2026-11-25. Archivo ejecutable: `daily_pilot/scripts/estrategia_final.py`.
Estado: `daily_pilot/datos/estrategia_final.json`. PAPER_ONLY.

## RESULTADO (lo que pediste)

| | BTC | ETH | CARTERA |
|---|---:|---:|---:|
| Señales/mes | **21,5** | **13,3** | **35,6** |
| Operaciones (9,3 años) | 2.393 | 1.483 | 3.876 |
| Esperanza | +0,250R | +0,165R | **+0,217R** |
| Acierto | **51,4%** | 38,8% | 46,6% |
| Factor beneficio | 1,58 | 1,30 | 1,45 |
| **Null sintético** | **p=0,000 PASA** | **p=0,050 PASA** | — |
| **Walk-forward test** | **+0,170R** ✅ | **+0,102R** ✅ | — |
| Degradación train→test | −41,4% | −39,3% | — |
| Drawdown | −79,9R | −57,3R | −98,8R |
| **2026** | **+38,98R** | **+56,58R** | **+95,56R** ✅ |

**Es la primera estrategia que: (1) da la frecuencia pedida, (2) pasa el null
sintético, y (3) mantiene esperanza POSITIVA en el test del walk-forward.**

## Parámetros ganadores

```
BTC: ema_rápida=13 · ema_tendencia=200 · swing=5 · régimen=ret_pos
     target=Fib 1.5 del swing · stop a Break-Even al llegar a 1R

ETH: ema_rápida=21 · ema_tendencia=100 · swing=3 · régimen=ret_pos
     target=Fib 1.5 del swing · stop a Break-Even al llegar a 1R
```

## Reglas (tu método, no el mío)

1. **Stop fijo** = swing LOW posterior al cambio de tendencia. Se calcula una vez
   y **nunca se mueve** (salvo a Break-Even cuando el precio alcanza 1R).
2. **Lote** = `riesgo_usd / (entrada − stop)`. Varia la cantidad, nunca el stop.
3. **Riesgo**: 1% por operación (0,5% si querés más colchón). Nunca más del 5%.
4. **Target**: extensión Fibonacci 1.5 del swing (alto − stop).
5. **Régimen**: solo comprar si el retorno de las últimas 30 velas 4h es positivo.
   En caída, no operar. Eso es lo que cortó los años malos.
6. Apalancamiento Quantfury 20x. Sin comisiones ni spread.

## Capital (cartera, $300)

| riesgo | USD/op | DD esperado | Ganancia esperada | Capital mínimo |
|---|---:|---:|---:|---:|
| **0,5%** | $1,50 | **−$148** | +$11,60/mes | $222 ✅ |
| 1,0% | $3,00 | −$296 | +$23,19/mes | $445 |
| 2,0% | $6,00 | −$593 | +$46,39/mes | $889 |

**Con $300 usá 0,5%.** El DD esperado al 1% ($296) es casi todo el capital.

## Años (cartera)

```
2017   +80,96R     2022   −37,24R   ← único año malo fuerte
2018   −25,76R     2023  +115,50R
2019  +150,01R     2024  +123,73R
2020  +206,48R     2025   −12,06R
2021  +145,69R     2026   +95,56R   ← positivo
```

## Limitaciones honestas

- El walk-forward **sí degrada** (~40%), pero el test sigue siendo positivo.
  No es una curva perfecta; es una ventaja real y modesta.
- El drawdown en R es grande porque el stop estructural es lejano. Por eso el
  sizing en dólares es lo que protege la cuenta, no el stop.
- Mean-reversion en rango quedó descartada (RUIDO, p=0,975).

## Estado actual

```
BTC $59.724 · ETH $1.676 · SIN SEÑAL ABIERTA
Últimas señales cerradas: BTC 21/10, ETH 06/10
```

El script `estrategia_final.py` se corre cuando quieras y actualiza el JSON.

PAPER_ONLY. No se ejecutaron órdenes.
