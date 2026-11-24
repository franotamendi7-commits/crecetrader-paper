# Quinta vuelta — definir el STOP (ancla 5b632dd)

Modo: **propuesta, no ejecución.** PAPER_ONLY intacto. No se toca `metodo/` ni la FIRMA.

## El problema (con números reales)

Mimos la operación completa: entrada al nivel, stop en el extremo del tramo,
target en el siguiente nivel. Resultado:

| par | n | acierto | factor beneficio | esperanza |
|---|---|---|---|---|
| BTC 1d | 17 | 5,9% | **0,063** | **−0,725R** |
| ETH 1d | 5 | 20% | 0,266 | −0,455R |

La causa está en la geometría. BTC 1d, tramo bajista **58.115 → 126.199**:

| nivel | entrada | stop (extremo) | distancia | target | R |
|---|---|---|---|---|---|
| retro 0,382 | 100.191 | 58.115 | −42% | 126.199 | 0,62 |
| retro 0,5 | 92.157 | 58.115 | −37% | 100.191 | 0,24 |
| retro 0,61 | 84.668 | 58.115 | **−31%** | 92.157 | **0,28** |
| retro 0,786 | 72.685 | 58.115 | −20% | 84.668 | 0,82 |

Con **R = 0,28** hacen falta **78% de aciertos** para empatar.

## La tensión sin resolver

El playbook dice dos cosas que chocan:

- **C05 / C01**: el tramo es el límite, el máximo/mínimo define la estructura.
- **C11**: el riesgo es **1–2%** del capital (corrección), 5% en tendencia.

Un stop a −31% **no puede** dar un riesgo del 1–2%. Hay que elegir una definición
de stop que sea coherente con ambos.

## Lo que quiero que propongas

**Tres definiciones candidatas de stop**, cada una con su justificación y su código:

### Candidato 1 — Stop estructural
El stop es la **ruptura del último swing** a favor del trade (el último mínimo si
comprás, el último máximo si vendés), por debajo/encima del nivel.

- Ventaja: usa la estructura, no un número inventado.
- Pregunta: ¿cómo se define «último swing» sin look-ahead? (el swing se confirma
  con N velas a la derecha).

### Candidato 2 — Stop por riesgo (%)
El stop se coloca a un **% fijo** del capital arriesgado (1% o 2%), sin importar
la estructura.

- Ventaja: cumple C11 al pie de la letra.
- Pregunta: ¿qué pasa con R si el stop queda **lejos** del nivel (o demasiado cerca)?

### Candidato 3 — Stop por volatilidad
Stop a **k × ATR** del nivel (k = 0,5 / 1,0).

- Ventaja: se adapta al activo.
- Pregunta: ¿queda el stop siempre del lado correcto?

## Reglas de simulación (para comparar los tres)

- Misma ventana walk-forward, mismos niveles, mismo target (siguiente nivel).
- Dentro de una vela, si toca stop y target, **gana el stop** (conservador).
- Reportar: **R teórico, n, % acierto, factor de beneficio, esperanza, drawdown**.
- Validar en **BTC y ETH** (mínimo), y **SOL** si podés.
- No ajustar el parámetro hasta que el número quede lindo: probar **2 valores
  predefinidos** por candidato y reportar ambos.

## Datos y código base

```bash
python3 daily_pilot/scripts/backtest_r.py BTCUSDT --tf 1d --detalle 150
python3 daily_pilot/scripts/backtest_r.py BTCUSDT --confirmacion
```

El archivo base es `daily_pilot/scripts/backtest_r.py` (funciones `stop_de`,
`target_de`, `simular`, `backtest_r`). Podés reescribirlo.

Velas: `daily_pilot/datos/velas/{PAR}_{TF}.json` (1w/1d/4h; 1h para BTC/ETH).

## Qué quiero de vos

1. **Código Python exacto** para cada candidato (función `stop_*`).
2. **Justificación** de cuál encaja con el método (citá la regla del playbook).
3. **La tabla comparativa** de los tres, en BTC y ETH.
4. **Recomendación final**: qué stop usarías y por qué, y **qué R resulta**.
5. Si **ninguno** da esperanza positiva, decelo claro y explicá qué habría que
   cambiar del método (target más lejos, entrada mejor, o menos operaciones).

## Restricciones

- No tocar `metodo/` ni la FIRMA.
- PAPER_ONLY: nada manda órdenes.
- No escribir el store vivo (`~/store-local/store.db`).
- Si el stop estructural necesita las velas siguientes (look-ahead), decilo y
  proponé cómo confirmarlo sin mirar el futuro.

Si el resultado es negativo en los tres, esa es la respuesta que necesitamos.
