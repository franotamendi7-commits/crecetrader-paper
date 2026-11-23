# Segunda vuelta — correcciones puntuales para el piloto CreceTrader

Ancla: `653cdfe` (rama `crecetrader-limpio`) · 2026-11-23
Modo: **solo lectura y propuesta. No corregir nada todavía.**

## Contexto

Ya entregaste la auditoría "Auditoría — 5 herramientas nuevas" sobre la ancla
`df2e6e3`. La contrasté contra el código real y **confirmé tus P0-1, P0-2,
P1-1 y P1-6**:

| hallazgo | mi comprobación |
|---|---|
| C01: W/D alcistas + 4H bajista → `long 0.85` con motivo falso | reproduce las 4 combinaciones |
| C05: BTC 1d tramo bajista, fibos calculados alcistas | 0,786 da 80.490,82 en vez de 62.034,85 |
| paper: `res% × 1000 × riesgo/2` | 100→90→110 da $100 en vez de $20 |
| dash: `{cuerpo}` no definido | NameError real en `panel_cuenta:278` |

No encontré un hallazgo falso. Ahora necesito **las correcciones exactas**.

## Qué quiero de vos

Un plan de corrección **archivo por archivo, línea por línea**, que pueda
ejecutar sin interpretar. Para cada corrección:

1. **Archivo:línea** exacto.
2. **Diff o snippet** del código nuevo (Python real, no pseudocódigo).
3. **Por qué** resuelve el hallazgo.
4. **Qué test de regresión** lo deja trabadó.

## Orden de corrección

### 1 · `daily_pilot/core/jerarquia.py` — P0-1 (C01)
El bug: `determinar()` no mira `h == BAJISTA` en la rama alcista ni `h == ALCISTA`
en la bajista. Casos contradictorios confirmados:

```
ALCISTA/ALCISTA/BAJISTA   -> long  0.85  "W, D y 4H alcistas: a favor de los 3"
ALCISTA/RANGO/BAJISTA     -> long  0.6   "W alcista; D/4H sin confirmar del todo"
BAJISTA/BAJISTA/ALCISTA   -> short 0.85  "W, D y 4H bajistas: a favor de los 3"
BAJISTA/RANGO/ALCISTA     -> short 0.6   "W bajista; D/4H sin confirmar del todo"
```

Además: el docstring dice «cualquier rango / no determinado -> NO OPERAR» pero
`:57-59` devuelve LONG 0.60. Hay que decidir una de las tres y dejarla escrita.

**Decisión ya tomada por Francisco:** ante 4H en contra de W y D, **no operar**
(el motivo tiene que decir la verdad). Con W o D en rango y el 4H a favor,
operar con **0.60** y motivo explícito.

Necesito:
- el `if` exacto que evalúa `h` y su return;
- cómo queda `sin_semanal()` (mismo error);
- la tabla de verdad 5×5×5 completa que debe salir en el test.

### 2 · `core/zonas.py` + los 4 llamadores — P0-2 (C05)
Los 4 llamadores no pasan `direccion`:
- `scripts/agente_ticket.py:71`
- `scripts/alertas_niveles.py:60`
- `scripts/backtest_niveles.py:38-39`
- `scripts/generar_dashboard_v5.py:118`

`tramo_ciclo()` sí devuelve `direccion` (`core/tramos.py:261`).

Necesito:
- el snippet que pasa `direccion=t['direccion']`;
- la fórmula bajista exacta en `zonas()` (el playbook C05-A dice
  `nivel = maximo - rango * r`);
- el filtro de niveles `<= 0` (BTC 1d bajista ext 3,00 = -9.401,34).

### 3 · `scripts/backtest_niveles.py` — P0-3 y P0-4
Problemas: in-sample (tramo con 500 velas incluidas las 90 de test) y "rebote"
que cuenta continuaciones.

Necesito:
- cómo congelar el tramo al inicio de la ventana (walk-forward simple);
- la definición 2×2 (hold / break / cont / rev) implementada en Python;
- el reporte con `n`, clusters e IC95 (fórmula que uses);
- `--detalle` expuesto en el CLI;
- el mínimo de muestra para mostrar un número (¿n < 5 se oculta?).

### 4 · `scripts/paper_trading.py` — P1-1
Fórmula actual: `res/100 * 1000 * (riesgo_pct/2)`.
Corrección pedida: `notional = capital × riesgo_pct / stop_pct`,
`pnl = res/100 × notional`.

Necesito:
- el snippet completo de `cerrar()`;
- validación de SL/TP (SL debajo de la entrada en long, etc.);
- el campo `stop_pct` y cómo se calcula;
- si hay que sumar comisión/slippage (decime cuánto);

### 5 · `scripts/alertas_niveles.py` — P1-2
`round(float(pr), 0)` colapsa DOGE/ADA a 0.0; todo nivel se asigna a BTC.

Necesito:
- cómo redondear sin romper (¿tick por activo? ¿Decimal? ¿cuántos decimales?);
- cómo preservar el par de cada nivel (el JSON no lo trae);
- el guard `precio <= 0`;
- el default de umbral unificado (¿1.0 o 1.5?).

### 6 · `scripts/generar_dashboard_v5.py` — P1-6 y P2-2
Confirmado: `:267` arma `filas`, `:278` usa `{cuerpo}` → NameError.

Necesito:
- el fix exacto;
- el panel BACKTEST sin cherry-picking: ¿mostrar todos los niveles con n, o
  solo los que tengan n >= umbral?;
- el panel ALERTAS con los niveles del ciclo y no solo concordancia;
- qué hacer con el panel PROBABILIDAD: ¿número de la tabla
  {3:1.00, 2:0.75, 1:0.50} o sacarlo?;
- borrar `panel_grafico` / `grafico_velas` (código muerto).

### 7 · `tests/test_herramientas.py` — P1-5
Necesito los tests de regresión: C01, C05 bajista, backtest, paper, alertas con
DOGE, NameError del dash. Usá `sys.executable` y un archivo temporal, **sin
borrar `datos/paper_trades.json` vivo**.

### 8 · `canal_acierta.py` — P0-5
Sabemos que el 6,1% no sirve. Decime únicamente:
- cómo levantar la fecha real de publicación (¿campo del JSON? ¿YouTube API?);
- cómo mapear cada nivel a su par;
- el mínimo de videos/días para reportar algo.

## Restricciones

- `PAPER_ONLY` intacto: ninguna corrección puede mandar órdenes.
- Nada escribe el store vivo (`~/store-local/store.db`).
- No tocar `daily_pilot/metodo/` ni la FIRMA.
- Commits atómicos por corrección.

## Entregable

Para cada punto: **archivo:línea + snippet + justificación + test**. Nada de
prosección. Si algo no se puede corregir sin cambiar el método, decilo y
proponé la alternativa.
