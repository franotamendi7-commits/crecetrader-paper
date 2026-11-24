# Cuarta vuelta — medir R, no «hold» (ancla d1d8c9f)

Modo: **propuesta, no ejecución.** PAPER_ONLY intacto. No se toca `metodo/` ni la FIRMA.

## El replanteo (esto es lo importante)

Seis hipótesis medidas hasta ahora, todas sobre **«hold» = el precio no cruza el nivel**:

| hipótesis | resultado |
|---|---|
| H1 confluencia entre TF | 0 niveles confluentes |
| H2 zona ATR ×0,5 / ×1,0 | mejora solo con un ancho → sobreajuste |
| H5 primer toque vs resto | muestra chica |
| A abanico intradía | BTC 21 toques → 28,6% hold; ETH 0 toques |
| B liquidez institucional | 1 solo nivel de liquidez → n=0 |
| D régimen confirmado | n=3 y n=14 → muestra chica |

**El problema puede no ser la estrategia: puede ser la métrica.**
Hold mide disciplina visual, no rentabilidad. Una entrada con 28,6% de hold puede ganar
plata si el stop está cerca y el target lejos. **Nunca medimos el resultado de una operación.**

## Lo que quiero que propongas

### 1 · Backtest de RESULTADO (lo principal)

Para cada toque de un retroceso/extensión, simular la operación completa:

- **Entrada**: al toque del nivel.
- **Stop**: el extremo del tramo (el máximo o el mínimo, según dirección).
- **Target**: el siguiente nivel del método (siguiente retroceso o extensión).

Y calcular:

| métrica | definición |
|---|---|
| **R** | (target − entrada) / (entrada − stop), con signo según el lado |
| **factor de beneficio** | ganancia bruta / pérdida bruta |
| **esperanza** | Σ(R) / n operaciones |
| **drawdown** | peor racha en R |
| **% acierto** | operaciones con R > 0 |

Reportar **por nivel** (0,382 / 0,5 / 0,61 / 0,786 / extensiones) y **agregado**.

Preguntas concretas: ¿con el nivel pelado, sin ningún filtro, cuál es el factor de
beneficio? ¿Hay algún nivel con esperanza positiva?

### 2 · Entrada al toque vs. entrada en confirmación

El método dice **30% oferta / 70% confirmación**. Hoy medimos la oferta.

Proponer cómo medir la **confirmación**: la vela cierra a favor del nivel antes de entrar.
Comparar R de ambas entradas (con la misma ventana walk-forward).

### 3 · Liquidez con datos de verdad

En B, `liquidez.calcular()` devolvió **un solo nivel**. Decime por qué (¿el tramo
congelado queda lejos? ¿faltan pools?) y qué **datos harían falta** para tener una
muestra útil (n ≥ 15 por par). Si hay que cachear más temporalides o bajar el umbral,
decilo.

## Reglas (las mismas de siempre)

- Walk-forward: los niveles y el tramo usan solo velas **anteriores** al test.
- **No cambiar la definición de nivel** ni el método.
- Reportar **n** y marcar muestras chicas.
- Validar en **BTC y ETH** (y SOL si podés).
- Nada de ajustar parámetros hasta que el número quede lindo.
- Si algo no se puede medir con los datos actuales, decilo y lista el dato.

## Datos disponibles

```bash
python3 daily_pilot/scripts/backtest_niveles.py BTCUSDT --tf 1d --detalle 150
python3 daily_pilot/scripts/hipotesis_estrategia.py --par BTCUSDT --tf 1d --detalle 150
python3 daily_pilot/scripts/hipotesis_tres.py --par BTCUSDT --detalle 150
```

Velas: `daily_pilot/datos/velas/{PAR}_{TF}.json` (1w/1d/4h, y 1h para BTC/ETH).

## Qué quiero de vos

1. **Código Python exacto** para el backtest de R (funciones con firma clara),
   listo para meter en `daily_pilot/scripts/`.
2. **Cómo definir el stop y el target** con justificación del playbook.
3. **Cómo medir la confirmación** (el 70%) de forma simple y sin look-ahead.
4. **Qué falta para la liquidez** (dato concreto).
5. **Criterio de decisión**: ¿con qué números diríamos que la estrategia es rentable?
   (sugerencia: factor de beneficio > 1,5 y esperanza > 0 con n ≥ 20).

Si el R sale **negativo** con todo, decelo claro: esa es la respuesta que necesitamos.
