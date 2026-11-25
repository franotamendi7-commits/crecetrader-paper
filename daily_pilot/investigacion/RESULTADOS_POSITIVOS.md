# ⚠️ OBSOLETO — reemplazado por STOP_CORREGIDO_RESULTADOS.md

Estos números se calcularon con `stop = min(lows[i-5:i+1])` ( STOP MÓVIL ),
que NO es el método de Francisco. El stop correcto es el **swing low fijo
posterior al cambio de tendencia**, y el lote se calcula desde ahí.
Ver `STOP_CORREGIDO_RESULTADOS.md` para los números válidos.

---

# MEJORES RESULTADOS POSITIVOS ENCONTRADOS (búsqueda de frecuencia)

Fecha: 2026-11-25. Grid de 216 combinaciones de pullback (ema 8/13/21/34,
target 2R/3R/4R, stop 3/5/8 velas, 3 regímenes) en BTC y ETH 4h, 9,3 años.
Validación: null sintético 60 sims + walk-forward 70/30. PAPER_ONLY.

## RESULTADO 1 · MejorQuality: BTC ema34 tR2 stop5

```
señales:  1.395  → 12,5 por mes
esperanza: +0,220R
acierto:   40,1%
factor beneficio: 1,38
drawdown:  -43R
NULL sintético: p=0,000 → PASA (azar da -0,102R de media)
walk-forward: train +0,294 → test +0,054  (-81,6%)
```

## RESULTADO 2 · Mejor frecuencia: cartera BTC + ETH ema13 tR2 stop5

```
señales:  5.556  → 51,2 por mes
esperanza: +0,168R
factor beneficio: 1,28
drawdown:  -133R
2026: +79R  ← positivo en el año actual
```

Detalle anual de la cartera:

| año | ops | resultado |
|---|---:|---:|
| 2017 | 245 | +119,00R |
| 2018 | 282 | −42,00R |
| 2019 | 695 | +212,00R |
| 2020 | 877 | +293,00R |
| 2021 | 713 | +190,00R |
| 2022 | 226 | −18,00R |
| 2023 | 829 | +34,00R |
| 2024 | 657 | +29,00R |
| 2025 | 493 | +40,00R |
| **2026** | **539** | **+79,00R** |

## RESULTADO 3 · Frecuencia media: BTC ema13 tR3 stop3 + régimen EMA50↑

```
21,6 señales/mes · E=+0,208R · PF=1,30 · NULL p=0,000 PASA
walk-forward: train +0,293 → test +0,011 (-96,2%)
```

## Lo que NO puedo decir (honestidad)

Ninguna de las estrategias de alta frecuencia tiene walk-forward estable.
El mejor train+test parecido fue ETH ema13 tR2 del informe anterior
(−51%), y aun así degrada. La razón: el pullback solo funciona en
régimen de tendencia; el 30% final de la serie incluye 2022 (bear) y
laterales donde la esperanza se cae.

El pullback es **realmente mejor que el azar** (p=0,000 en las tres
mejores) y da la frecuencia pedida, pero su ventaja es pequeña
(+0,17 a +0,22R por operación) y su drawdown es grande.

## Con $300 al 1% ($3 por operación)

| estrategia | resultado esperado/mes | DD esperado |
|---|---:|---:|
| BTC ema34 | +$8,25 | −$129 |
| Cartera BTC+ETH | +$25,76 | −$399 |

**El drawdown esperado supera el capital en la cartera.** No es operable
con $300. Necesitaría ~$1.500 para soportar el DD al 1%.

## Veredicto

Traje resultados positivos verificados: **sí existen**, con p=0,000 y
frecuencia de 12 a 51 señales/mes. Pero ninguno es robusto en walk-forward
y ninguno es operable con $300 al 1%.

La estrategia lenta sigue siendo la única con perfil riesgo/recompensa
sano (E=+1,237R, DD=−6,3R), aunque dé 6 señales/año.

Siguiente paso si querés seguir: probar **filtro de régimen externo**
(operar pullback solo cuando la estrategia lenta está en tendencia) para
cortar los años malos. Eso sí podría arreglar el walk-forward.

PAPER_ONLY. No se ejecutaron órdenes.
