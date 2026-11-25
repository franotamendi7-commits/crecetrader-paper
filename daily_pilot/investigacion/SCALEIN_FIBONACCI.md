# SCALE-IN FIBONACCI — la idea de Francisco (25/11)

## La idea (de sus capturas reales)

Entrada en 1h con:

- **Cambio de estructura confirmado en 1h** (cierre sobre el último swing high)
  y **validación en 4h** (tendencia alcista).
- Entrada en la zona del **mínimo de rango / Fibo 0.382-0.5**.
- **Recompra en 0.5 y 0.61** de Fibo, agregando capital (promediar la entrada).
- **Stop fijo** estructural bajo el mínimo del rango.
- **Riesgo TOTAL 5%** del capital para todas las piernas juntas (no 5% por pierna).
- Target extensión Fibo 1.25 / 1.5.

Datos reales de la captura: capital $5.680,38, entrada $59.192,81,
stop $56.400, posición 0,00540606 BTC, retorno +0,94%.

## Por qué no la había encontrado

Todos mis simuladores asumen **una sola entrada**. Nunca implementé scale-in.
Por eso buscaba entradas perfectas en vez de entradas que se mejoran.

## Resultados (BTC 1h, 81.153 velas, 9 años)

| config | n | retorno $ | win | DD $ | legs |
|---|---:|---:|---:|---:|---:|
| look12 / rango8% / stop2% / T1.25 | 265 | **+$7.825 (137,8%)** | **86,4%** | −$783 | 2,54 |
| **look24 / rango12% / stop3% / T1.25** | 124 | **+$2.713 (47,8%)** | **81,5%** | −$568 | 2,66 |
| look24 / rango12% / stop3% / T1.5 | 118 | +$2.871 (50,5%) | 75,4% | −$642 | 2,73 |

Config conservadora (look24, la más parecida a la captura) por año:

```
2017 +$189   2019 −$16    2021 −$100   2023 +$540   2025 +$803
2018 +$15   2020 +$327   2022 +$72    2024 +$41    2026 +$841
```

**8 de 10 años positivos, y los dos últimos son los mejores.**

## Validación (honesta)

| prueba | resultado |
|---|---|
| Null 3 seeds (4h real) | p=0,00 ✅ |
| **Null 20 seeds (4h real)** | **p=0,05** ⚠️ límite |
| **Null 20 seeds (4h sintético)** | **p=0,10** ❌ no pasa |
| Walk-forward (look12) | train $4.432 → test $3.393 (no degrada) |
| Walk-forward (look24) | train $1.139 → test $1.574 (**mejora**) |

El null más estricto no la confirma del todo (p=0,10). Pero **rompe la
estructura de Fibonacci** al permutar signos, así que puede no ser un
contrafactual justo para este setup — el mismo problema que tuve con la
reversión. No puedo decidir con la herramienta actual.

## Veredicto

Es la **mejor idea nueva en precisión** (81-86% de acierto, contra 58% de la
cartera actual) y la única que gana de forma clara en 2025 y 2026.

Pero no la meto al tracker: el null estricto da p=0,10 y el sizing al 5% del
capital es mucho más agresivo que el 0,35% actual (DD −$568 vs −$86).

## Próximo paso

Probar el scale-in con **riesgo total 1% y 2%** para ver si mantiene la ventaja
con un drawdown aceptable. Si pasa, puede convivir con la cartera actual.

PAPER_ONLY. No se ejecutaron órdenes.
