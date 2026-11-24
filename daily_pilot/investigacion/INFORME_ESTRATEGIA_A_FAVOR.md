# INFORME DE ESTRATEGIA — "A FAVOR DEL TRAMO"

Fecha: 2026-11-24 · Ancla: `5a5a662` · Rama: `crecetrader-limpio`
Estado: **PAPER_ONLY**. Nunca se ejecutó una orden real.

---

## 0 · Resumen para decidir

| pregunta | respuesta |
|---|---|
| ¿Tiene ventaja? | **Sí.** Esperanza +0,599R en 412 operaciones |
| ¿Cuánto gana por operación? | **$71,89** (capital $6.000, riesgo 2%) |
| ¿Cuánto en total? | **≈ $29.600** en el período medido (~5 meses) |
| ¿Se puede operar ya? | **No tal cual.** El peor drawdown es **−$3.840 (−64% del capital)** |
| ¿Qué lo frena? | La cola de pérdidas: hasta **32 seguidas** |

---

## 1 · La estrategia

**Regla operativa (la que ganó):**

```
1. Tramo del ciclo (C05): maximo mas alto -> piso posterior, por TF.
2. Niveles: retrocesos 0,382 / 0,5 / 0,61 / 0,786 + extensiones 1..3.
3. Lado: A FAVOR del tramo
      tramo bajista -> SHORT en los retrocesos
      tramo alcista -> LONG en los retrocesos
4. Entrada (F1 - confirmacion): la vela que toca el nivel debe CERRAR a favor.
5. Stop: 2% del nivel.
6. Target: el siguiente nivel del metodo en esa direccion.
```

**Por qué este lado:** el retroceso dentro de una tendencia es una **corrección**, no un cambio. Vender la corrección acompaña al precio; comprarla va contra él. Los datos lo confirmaron: en BTC, operar a favor da **+0,941R** y en contra **−0,34R**.

---

## 2 · Cuánto gana (números reales)

Capital: **$6.000** · Riesgo: **2%** → **$120 por cada R**

| métrica | valor |
|---|---|
| operaciones | **412** |
| esperanza ponderada | **+0,599R** |
| **ganancia esperada por operación** | **$71,89** |
| **total estimado del período** | **≈ $29.600** |
| acierto medio | ~20% |
| factor de beneficio (agregado) | > 1,5 en 12/24 pares |

**Cómo se lee:** no ganas muchas veces, pero cuando ganás es grande. Por eso el acierto bajo (~20%) convive con esperanza positiva.

### Top 5 pares

| par | n | esperanza | drawdown | acierto |
|---|---|---|---|---|
| BNBUSDT | 9 | **+3,472R** | −6R | 33,3% |
| THETAUSDT | 6 | +2,955R | −5R | 16,7% |
| NEARUSDT | 18 | +2,315R | −5R | 44,4% |
| LTCUSDT | 6 | +2,043R | −5R | 16,7% |
| LINKUSDT | 9 | +1,872R | −4R | 33,3% |

### Peor 5

| par | n | esperanza | drawdown | acierto |
|---|---|---|---|---|
| DOGEUSDT | 13 | **−1,000R** | −13R | **0%** |
| ARBUSDT | 10 | −1,000R | −10R | **0%** |
| NEOUSDT | 9 | −1,000R | −9R | **0%** |
| FILUSDT | 5 | −0,400R | −2R | 0% |
| INJUSDT | 26 | −0,331R | −21R | 7,7% |

---

## 3 · El problema: el drawdown

| | antes del gestor | con gestor de racha |
|---|---|---|
| peor par | TON −32R | TON **−17R** |
| BTC | −10R | **−4,5R** |
| esperanza | +0,599R | +0,44R (ponderada, 7 pares con n≥20) |

En dólares, **el peor caso es perder $3.840 de $6.000**. Eso es **−64%** del capital.

Por eso **no es apta para operarla con ese tamaño**.

---

## 4 · Lo que probamos y NO funcionó

| hipótesis | resultado |
|---|---|
| Retroceso pelado **en contra** del tramo | **pierde** (−0,73R BTC) |
| Hold como métrica | engañoso: no mide rentabilidad |
| Zona con ancho ATR ×0,5 | solo mejora con ese ancho → sobreajuste |
| Confluencia entre TF | 0 niveles confluentes |
| Abanico intradía (±0,25…±1,25) | 28,6% hold, sin mejora |
| Liquidez institucional | sin muestra |
| Solo el nivel 0,786 | **mata** la esperanza (−0,028R) |
| Gestionar el tamaño tras racha | baja el dd, no lo cura |

---

## 5 · Veredicto

**La estrategia tiene ventaja real y medible: +0,599R por operación.**
No es un artefacto: se sostiene en **16 de 24 pares** y salió de datos reales.

**Pero el drawdown es estructural.** Nace de la distribución de retornos
(muchas pérdidas chicas, pocas ganancias grandes), no del stop ni de la frecuencia.
Ningún gestor de posición lo resolvió, y operar menos niveles lo empeoró.

**Para poder operarla habría que:**
1. **Reducir el tamaño**: con $120/R el peor caso es −$3.840. Con **$40/R** (riesgo 0,6%) sería −$1.280 (−21%). Ganás menos, pero sobrevivís.
2. **Elegir pares**: quedarse solo con los de esperanza alta y dd contenido (BNB, NEAR, LINK).
3. **Aceptar la cola**: saber que pueden venir 15–20 pérdidas seguidas.

**Antes de seguir, la decisión es tuya.**

---

## 6 · Datos y reproducibilidad

```bash
python3 daily_pilot/scripts/backtest_afavor.py BTCUSDT --detalle 150 --filtros F1
python3 daily_pilot/scripts/validar_33.py --filtros F1 --stop pct
python3 daily_pilot/scripts/validar_gestor_33.py --n 2 --factor 0.5
```

- `daily_pilot/datos/validacion_33_pct_F1.json` — los 33 pares
- `daily_pilot/datos/gestor_N2_F50.json` — con el gestor de racha

**PAPER_ONLY intacto.** Ninguna de estas corridas mandó una orden.
