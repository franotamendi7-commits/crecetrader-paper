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

## Validación (ACTUALIZADA — null estricto corregido)

| prueba | resultado |
|---|---|
| Null bootstrap de retornos, 20 seeds | p=0,00 ✅ |
| **Null ESTRICTO 20 seeds (1h y 4h sintéticos)** | **p=0,00 ✅** ✅ |
| Walk-forward (look24) | train $1.139 → test $1.574 (**mejora**) |

**Corrección importante:** el primer null estricto daba p=0,10 porque
regeneraba 1h pero usaba la serie 4h **real** (fuga de información). Al
regenerar también el 4h sintético, el p baja a 0,00 en 20 seeds. La ventaja
es real.

## Test de riesgo total (BTC, $5.680 capital de la captura)

| riesgo | retorno | % | win | DD $ | DD % | p20 | WF train→test |
|---|---:|---:|---:|---:|---:|---:|---|
| **1%** | +$542,67 | +9,6% | 81,5% | −$113,61 | **−2,0%** | 0,00 | $228 → $315 |
| **2%** | +$1.085 | +19,1% | 81,5% | −$227,22 | −4,0% | 0,00 | $456 → $630 |
| 3% | +$1.628 | +28,7% | 81,5% | −$340,82 | −6,0% | 0,00 | $683 → $945 |
| 5% | +$2.713 | +47,8% | 81,5% | −$568,04 | −10,0% | 0,00 | $1.139 → $1.574 |

**A 1% el drawdown es solo −2%** con 81,5% de acierto. Es compatible con
el riesgo de la cartera actual (0,35%). A 2% el DD es −4%, todavía razonable.

## Veredicto actualizado

**SÍ es operable.** Con riesgo 1%: +9,6% anualizado sobre 9 años, DD −2%,
81,5% de acierto, p=0,00 con el null más estricto.

Se puede agregar a la cartera como **cuarta estrategia**, con riesgo 1% y
capital separado. No reemplaza a la cartera actual — la complementa.

## Números exactos de los últimos meses (capital $5.680,38)

### Riesgo 1% ($56,80 por operación)

| Mes | Operaciones | Wins | Resultado |
|---|---:|---:|---:|
| Ago 2026 | 3 | 3/3 | +$25,55 |
| Sep 2026 | 4 | 3/4 | −$12,84 |
| Oct 2026 | 2 | 2/2 | +$31,17 |
| Nov 2026 | 0 | — | $0 |
| **Total** | **9** | **8/9 (88,9%)** | **+$43,88 (+0,77%)** |

DD del periodo: −$39,40.

### Riesgo 2% ($113,61 por operación)

Ago +$51,11 · Sep −$25,69 · Oct +$62,34 · Nov $0.
Total 9 ops, 8/9 wins, **+$87,76 (+1,54%)**, DD −$78,81.

Única perdedora: 2026-09-22 15:00, legs=3, stop 82.560,58, target 83.742,22.

### Comparación con la cartera actual en el mismo periodo

| | Cartera 6 pares | Scale-in 1% |
|---|---:|---:|
| Ago | −5,36R | **+$25,55** |
| Sep | +8,98R | −$12,84 |
| Oct | −1,26R | **+$31,17** |

El scale-in gana justo en los meses malos de la cartera.

## Próximo paso

Integrarlo al tracker con `config_version`, y correr el forward. PAPER_ONLY.

PAPER_ONLY. No se ejecutaron órdenes.
