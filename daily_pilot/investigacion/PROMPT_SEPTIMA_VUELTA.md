# Septima vuelta — atacar el DRAWDOWN (ancla c464cdb)

Modo: **propuesta, no ejecución.** PAPER_ONLY intacto. No se toca `metodo/` ni la FIRMA.

## Donde estamos

La estrategia **operar A FAVOR del tramo** ya es rentable en esperanza:

| metrica | resultado |
|---|---|
| operaciones | 412 |
| esperanza ponderada | **+0,599R** |
| pares positivos | **16/24 (67%)** |
| acierto > 25% | 6/24 |
| drawdown mejor que -6R | **7/24** |

**El unico problema que queda es el DRAWDOWN.** Peores casos reales:

| par | n | acierto | esperanza | drawdown |
|---|---|---|---|---|
| TONUSDT | 35 | 8,6% | -0,215R | **-32,0R** |
| STXUSDT | 27 | 22,2% | +1,603R | **-16,0R** |
| ALGOUSDT | 23 | 8,7% | +0,536R | **-13,0R** |
| ONDOUSDT | 16 | 6,2% | -0,028R | **-13,0R** |
| NEOUSDT | 9 | 0,0% | -1,0R | **-9,0R** |

Configuracion actual: lado a favor del tramo, **F1 confirmacion**, **stop 2%**,
target = siguiente nivel. Walk-forward, conservador (si toca stop y target, gana el stop).

## Lo que ya probamos contra el drawdown

| propuesta | BTC dd | ETH dd | esperanza |
|---|---|---|---|
| sin nada | -10R | -3R | +0,599R / +3,535R |
| P2 tamano tras racha | **-6R** | -2,5R | +0,655R / +3,635R |
| F1 confirmacion | -7R | -1R | +1,718R / +6,558R |
| P1 parciales (sin medir) | ? | ? | ? |
| P3 solo 0,61/0,786 | -10R | -3R | +0,941R / +3,535R |

P2 mejora el dd de -10 a -6 en BTC **sin bajar la esperanza**. Es lo unico que funciono.

## Lo que quiero que propongas

### 1 · Gestores de posicion medibles

Para cada uno: **codigo exacto + como se mide**.

| candidato | idea |
|---|---|
| **G1 — Parciales + break-even** | Al tocar el primer target cerrar 50%, mover el stop a break-even, dejar correr el resto |
| **G2 — Reduccion tras racha** | Tras N perdidas consecutivas, reducir el tamano (ya probado: N=2, 50%). Probar N=2 con 50% vs N=3 con 60% |
| **G3 — Tamano por conviccion** | Escalar con la jerarquia: 3 marcos alineados -> tamano completo; 2 -> medio |
| **G4 — Solo niveles fuertes** | Operar solo retro 0,61 y 0,786 (probado: no bajo el dd). Probar solo 0,786 |
| **G5 — Filtro de volatilidad** | No operar si el ATR esta por encima de X (evitar los parches de ruido) |
| **G6 — Cierre por tiempo** | Si a los N dias no llego al target, cerrar |

### 2 · La metrica: termina en que numero te quedas?

No alcanza con «dd mejora». Quiero saber:

- **esperanza final** (tiene que seguir > 0,15R)
- **drawdown final** (objetivo: mejor que **-4R**)
- **maximo de la curva** y **racha de perdidas mas larga**
- **cuantas operaciones quedan** (si un filtro deja n<20, no sirve)

### 3 · Validacion

Correr la mejor variante en los **33 pares**. Reportar cuantos quedan con:

```
esperanza > 0,15R   Y   drawdown > -4R   Y   n >= 20
```

Si **ninguna** variante logra bajar el dd a -4R sin matar la esperanza, decilo
y explicá por qué (probablemente la distribucion de retornos: muchas pequenas perdidas
y pocas ganancias grandes).

## Reglas

- Misma ventana walk-forward, mismo lado, mismo target.
- **No optimizar** parametros hasta que el numero quede lindo: 2 valores predefinidos por candidato.
- Reportar tambien los pares donde **empeora**.
- PAPER_ONLY intacto. No se toca `metodo/` ni la FIRMA. No se escribe el store vivo.

## Codigo base

```bash
python3 daily_pilot/scripts/backtest_afavor.py BTCUSDT --detalle 150 --filtros F1
python3 daily_pilot/scripts/validar_33.py --filtros F1 --stop pct
```

`daily_pilot/datos/validacion_33_pct_F1.json` tiene los 33 resultados base.

## Entregable

1. Codigo de cada gestor.
2. Comparativa en BTC y ETH (dd, esperanza, n).
3. La mejor combinacion y su validacion en los 33.
4. Veredicto claro: ¿se puede operar o no, y con que riesgo?
