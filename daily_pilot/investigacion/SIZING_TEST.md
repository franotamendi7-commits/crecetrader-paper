# TEST DE SIZING: ¿SUBIR AL 5% ARREGLA EL DRAWDOWN?

Fecha: 2026-11-25. Misma señal (estrategia final validada), distinto sizing.
Capital $300. Cartera BTC+ETH, 3.876 operaciones, 9,3 años.

## Resultado

| modo | riesgo base | máx | retorno final | DD $ | DD % |
|---|---:|---:|---:|---:|---:|
| **fijo** | **0,5%** | 0,5% | +$1.264 (421%) | **−$206** | **−68,6%** |
| fijo | 1% | 1% | +$2.529 (843%) | −$412 | −137,2% |
| fijo | 1% | 5% | +$2.529 (843%) | −$412 | −137,2% |
| fijo | 3% | 5% | +$7.586 | −$1.235 | −411,6% |
| step (más riesgo si stop cerca) | 1% | 5% | +$3.833 | −$555 | −184,9% |
| inverso (más riesgo si stop lejos) | 1% | 5% | +$3.652 | −$1.136 | −378,7% |

## Respuesta directa: NO

**Subir al 5% no vuelve positiva la estrategia — ya es positiva, lo que hace
es aumentar el drawdown proporcionalmente.** El DD pasa de −69% a −137% a
−412%. No hay ningún punto donde el DD mejore subiendo el riesgo.

La razón es aritmética: si ganás +0,217R por operación y perdés −1R en el
stop, multiplicar el riesgo por N multiplica **tanto** la ganancia como la
pérdida por N. El ratio riesgo/recompensa no cambia. El sizing no arregla un
DD; solo lo escala.

## Lo que SÍ cambia el DD

El DD de −98,8R viene de la **secuencia de pérdidas**, no del tamaño.
Para bajarlo hay que actuar sobre la entrada o la salida:

1. **Riesgo fijo 0,5%**: DD −68,6%. Es lo único sensato con $300.
2. **Take-profit Take-profit parcial** en 1R y dejar correr el resto: reduce la
   dispersión de resultados.
3. **Filtro de régimen más estricto**: saltear los años malos (2018, 2022,
   2025) — pero eso es sobreajuste si se calibra mirando el histórico.

## Distribución real de la distancia al stop (BTC)

```
p10   1,30%     p50   3,30%     p90   9,15%
p25   2,01%     p75   5,44%     p95  12,41%
mín 0,23%                        máx 33,88%
```

La mitad de las operaciones tiene el stop entre 2% y 5,4% de distancia.
Elevar el máximo al 5% solo afecta al ~25% de las señales con stop más
cercano — y ahí es donde el riesgo relativo es mayor, por eso el modo
`step` empeora el DD a −185%.

## Conclusión

Con $300: **0,5% de riesgo por operación**. DD esperado −$206, retorno
esperado +$1.264 en 9,3 años (421% acumulado, no anual).

Si querés menos DD todavía, el camino no es subir el riesgo: es reducir el
tamaño a 0,25% o mejorar el filtro de entrada. Lo que no podés hacer es
pedirle al sizing que convierta un DD de −99R en algo chico — eso es
trabajo del stop y de la selección de señales.

PAPER ONLY.
