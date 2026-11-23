# Mejora de la estrategia — qué probar contra los niveles (ancla d5ce88f)

Modo: **propuesta, no ejecución.** PAPER_ONLY intacto. Solo lectura de datos.

## El punto de partida (números reales, ya corregidos)

El backtest ahora está bien construido pero da bajo:

```
BTCUSDT 1d · tramo (bajista) 57.800 -> 107.500 · test 90 velas
respetados (hold) con n>=5: 23,2%
  retro 0.61  toques 18  hold 7   cont 5   38,9%  IC38.6-79.7
  retro 0.5   toques 13  hold 2   cont 6   15,4%  IC12.7-57.6
  retro 0.786 toques  2  hold 1   cont 1   50,0%  (muestra chica)
```

Definiciones que ya están fijadas y **no se discuten**:

- **hold**: el precio toca el nivel y no lo cruza.
- **cont**: cruza y sigue (NO es respeto).
- Tramo = máximo más alto → piso más bajo posterior; fibo al revés (0 = mínimo).
- Retrocesos 0,382 / 0,5 / 0,61 / 0,786; extensiones 1 / 1,25 / 1,5 / 1,75 / 2 / 3.
- Walk-forward: el tramo se congela antes de la ventana de test.

## La pregunta

**¿Qué condición, si se agrega al método, sube la tasa de respeto sin
sobreajustar?** No buscamos «que dé más alta»; buscamos una regla con lógica
propia que después se pueda testear fuera de muestra.

## Hipótesis para evaluar (orden sugerido)

| # | hipótesis | qué medir |
|---|---|---|
| H1 | **Confluencia temporal**: el nivel solo cuenta si está en el tramo de **dos** TF (W+D, D+4H) | tasa de hold con y sin filtro |
| H2 | **Zona, no línea**: el nivel tiene un ancho (¿ATR? ¿%/fijo?) y se mide si el precio rechaza dentro de la zona | tasa por ancho (0,5% / 1% / ATR/2) |
| H3 | **C07**: solo operar cuando el régimen está **confirmado** (`supera_y_consolida`) | tasa con y sin confirmación |
| H4 | **Pendiente del tramo**: el respeto depende de si el tramo es empinado o plano | correlación pendiente vs hold |
| H5 | **Número de toques previos**: el primer toque respeta más que el cuarto | tasa por orden de toque |
| H6 | **Horario/sesión**: el respeto cambia según la sesión (NY, asiática) | tasa por hora de la vela |
| H7 | **Liquidez institucional** (fibo + 1 ene + pools, como dice el playbook) | tasa cerca de esos puntos |

## Datos con los que podés trabajar

```bash
python3 daily_pilot/scripts/backtest_niveles.py BTCUSDT --tf 1d --detalle 150
python3 daily_pilot/scripts/backtest_niveles.py ETHUSDT --tf 1d --detalle 150
python3 daily_pilot/scripts/agente_ticket.py BTCUSDT --tf 1d --json
```

Datos cacheados en `daily_pilot/datos/velas/*.json` (Binance público).

## Qué quiero de vos

1. **Elegí 3 hipótesis** de la tabla (o proponé las tuyas) y di **por qué**
   tendrían sentido en el método de CreceTrader (citá el playbook si corresponde).
2. Para cada una: **el código Python exacto** que la implementa (función
   `filtro_*(...)` con firma clara), para poder probarla sin reescribir.
3. **La métrica de éxito**: con qué número decidimos si sirve. Te sugiero:
   - n ≥ 30 por grupo,
   - mejora de hold ≥ 10 puntos,
   - que se mantenga en **otro par** (BTC → ETH o SOL).
4. **Qué NO hacer**: ninguna regla que necesite datos que no tenemos, ni que
   ajuste parámetros hasta que el número quede lindo.

## Restricciones

- No se toca `daily_pilot/metodo/` ni la FIRMA.
- PAPER_ONLY: nada manda órdenes.
- Nada escribe el store vivo (`~/store-local/store.db`).
- Commits atómicos por hipótesis.

## Entregable

Para cada hipótesis elegida: **código + expectativa + criterio de decisión**.
Si las tres pierden, decime cuál estuvo más cerca y por qué.
