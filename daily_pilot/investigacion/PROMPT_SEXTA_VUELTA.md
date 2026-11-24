# Sexta vuelta — robustecer «operar a favor del tramo» (ancla 9335601)

Modo: **propuesta, no ejecución.** PAPER_ONLY intacto. No se toca `metodo/` ni la FIRMA.

## El hallazgo

El retroceso pelado operado **en contra** del tramo pierde. Operado **a favor**,
da positivo:

| par | lado | n | acierto | factor beneficio | esperanza |
|---|---|---|---|---|---|
| BTC 1d | **retrocesos A FAVOR** (short en bajista) | 14 | 21,4% | **2,198** | **+0,941R** |
| BTC 1d | retrocesos EN CONTRA (long en bajista) | 14 | 7,1% | 0,634 | −0,34R |
| ETH 1d | retrocesos A FAVOR | 5 | 40% | 6,891 | +3,535R |
| ETH 1d | retrocesos EN CONTRA | 5 | 20% | 3,257 | +1,806R |

Definiciones usadas (fijas):

- **A favor** = short si el tramo es bajista; long si es alcista.
- **Stop**: 2% del nivel (candidato ganador de la ronda anterior).
- **Target**: el siguiente nivel del método en esa dirección.
- **Walk-forward**: niveles y tramo con velas anteriores a la ventana.
- Conservador: si una vela toca stop y target, gana el **stop**.

## Las debilidades que hay que atacar

1. **Acierto muy bajo** (21,4% en BTC). Funciona por ganancias grandes (FB 2,2),
   pero el drawdown es **−10R**.
2. **ETH con n=5** — muestra chica.
3. **No se probó el stop estructural** sobre este lado.
4. **Sin confirmación** (el método pide 70%).
5. **Solo dos pares.**

## Lo que quiero que propongas

### 1 · Filtros de calidad que suban el acierto sin matar el FB

Proponer **2 o 3 filtros** que se puedan evaluar con los datos que ya tenemos
(velas 1w/1d/4h/1h, volumen, nivel anual):

| candidato | idea |
|---|---|
| F1 | Solo operar cuando el **cierre confirma** (la vela que toca cierra a favor) |
| F2 | Exigir que el tramo sea **largo** (>N velas) o empinado |
| F3 | Solo operar el **primer toque** de cada nivel |
| F4 | Exigir confluencia entre TF (nivel presente en otro marco) |
| F5 | Exigir que el tramo no esté «agotado» (el precio no volvió al extremo) |

Para cada filtro: **código exacto** + cómo se mide (n, acierto, FB, esperanza).

### 2 · Stop estructural aplicado a este lado

El stop de 2% es arbitrario. Proponé un **stop estructural** para el lado corto:
¿la ruptura del último swing? ¿el máximo del tramo? Medir ambas variantes.

### 3 · Gestión del drawdown (−10R)

Con 21% de acierto y FB 2,2, la racha de pérdidas mata la cuenta. Proponé:
¿tomar parciales? ¿reducir tamaño tras racha? ¿solo operar los mejores niveles?

### 4 · Plan de validación en 33 criptos

Hay que testear en **todos los pares del dash** (AAA…: 33 criptos de Quantfury).
Decime:
- Con **cuántas velas** por par (¿150? ¿todo lo disponible?).
- Qué **mínimo de operaciones** exige cada par para ser tenido en cuenta.
- Cómo agregar los resultados (ponderado por n, no promedio de tasas).

## Datos y código base

```bash
python3 daily_pilot/scripts/hipotesis_lado.py BTCUSDT --detalle 150
python3 daily_pilot/scripts/backtest_stop.py BTCUSDT --tf 1d --detalle 150
python3 daily_pilot/scripts/backtest_r.py BTCUSDT --confirmacion
```

Velas cacheadas: `daily_pilot/datos/velas/{PAR}_{TF}.json` (1w/1d/4h; 1h para BTC/ETH).
Los 33 pares están en `generar_dashboard_v5.py`.

## Criterio de decisión

Una variante es **robusta** si:

| condición | umbral |
|---|---|
| esperanza positiva | > 0,15R (no basta con > 0) |
| factor de beneficio | > 1,5 |
| acierto | > 25% |
| drawdown | mejor que −6R |
| se sostiene | en **≥ 60% de los pares** con n suficiente |

Si ningún filtro logra eso, decelo y explicá qué es lo que impide que funcione.

## Restricciones

- No tocar `metodo/` ni la FIRMA.
- PAPER_ONLY: nada manda órdenes.
- No escribir el store vivo (`~/store-local/store.db`).
- No optimizar parámetros hasta que el número quede lindo.
- Reportar también los pares donde **falla**, no solo los que andan.

## Entregable

1. Código de cada filtro.
2. Código del plan de validación sobre los 33 pares.
3. Recomendación final con sus números.
