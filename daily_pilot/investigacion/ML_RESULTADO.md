# ML sobre la estrategia BTC — resultado honesto

Fecha: 2026-11-25. sklearn 1.6.1 en venv aislado (`~/.hermes/cache/scratch/ml_env`).
Modelo: GradientBoostingClassifier, 60 árboles, profundidad 3.
Split TEMPORAL 70/30 (entrena con el pasado, predice el futuro — sin leakage).
2.393 señales, 11 features calculadas solo con velas anteriores a la entrada.

## Qué hace el ML

NO predice precios. Decide **si tomar o no** una señal que ya generó la
estrategia validada, según el régimen (retornos, volatilidad, posición en
rango, pendientes de EMA).

## Resultado en TEST (718 señales que el modelo nunca vio)

| umbral | ops | cobertura | acierto | E(R) | suma R |
|---:|---:|---:|---:|---:|---:|
| 0,00 (sin filtro) | 718 | 100% | 61,0% | +0,109 | **+78,3** |
| 0,50 | 652 | 90,8% | 60,9% | +0,104 | +67,6 |
| 0,60 | 444 | 61,8% | 60,4% | +0,087 | +38,6 |
| **0,65** | 292 | 40,7% | **62,7%** | **+0,125** | +36,4 |

**Veredicto: el ML no aporta.** Mejora la esperanza apenas (+0,109 → +0,125)
pero recorta el total a la mitad. Para "ganar todos los meses" no sirve.

Features más importantes: posición en rango 120 (0,184), pendiente EMA200
(0,143), volatilidad 20 (0,125). O sea: el modelo redescubrió que la
estrategia funciona en tendencia — eso ya lo sabíamos con el filtro `ret_pos`.

## Lo que SÍ se descubrió antes (y el ML confirma)

El mes malo (octubre −7,26R) se arregló con la **salida parcial**, no con
más inteligencia: el DD bajó de −79,9R a −56,0R y la esperanza subió.

## Lo que no se puede prometer

Ningún modelo —ML o regla— genera **rentabilidad todos los meses** con estos
datos. Octubre fue −7,26R y noviembre 0 señales. Eso es información, no un
fallo de código. Un sistema que te promete ganancia mensual con 2.393
operaciones y DD de −56R está mintiendo.

Si querés seguir, el camino no es más ML sobre los mismos features: es
**cambiar el universo** (otro activo con tendencia distinta) o **cambiar el
timeframe**. Pero eso es otra búsqueda, con sus propios números.

PAPER_ONLY. No se ejecutaron órdenes.
