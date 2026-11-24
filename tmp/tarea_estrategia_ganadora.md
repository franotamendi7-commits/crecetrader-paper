# TAREA GRANDE — encontrar una estrategia GANADORA (BTC)

Objetivo: UNA estrategia de trading que supere el azar. No importa cuántas
variantes haya que probar. Resultado sincero, con números verificables.

## 0 · REGLAS ABSOLUTIAS

- PAPER_ONLY: nada de ordenes reales. No toques metodo/ ni la FIRMA.
- No escribas el store vivo (~/store-local/store.db).
- No mientas: si nada funciona, decilo con los numeros en la mano.
- Todo script nuevo va en daily_pilot/scripts/ y se commitea.

## 1 · DATOS (prioridad 1)

Hoy solo hay ~500 velas por par. Alcanza:
- BTCUSDT: 1d, 4h, 1h  -> maximo historico que permita Binance (usar klines).
- ETHUSDT: 1d, 4h.
Guardalos en daily_pilot/datos/velas/<PAR>_<TF>.json con el mismo formato que
ya existe (revisar daily_pilot/core/velas.py para respetar el schema).
Verificar integridad: cantidad de velas, primer/ultima fecha, sin huecos grandes.

## 2 · ESTRATEGIA BASE (la operativa real de Francisco)

Entrada al cierre sobre el maximo del tramo (sin look-ahead).
Stop en el minimo del tramo. Target en extension fibo.
Ya existe un motor inicial en daily_pilot/scripts/backtest_ruptura.py
(revisalo, esta recien escrito, puede tener bugs: detectaba muy pocos tramos).

## 3 · ESPACIO DE BUSQUEDA (proba TODO esto, no te limites)

Variá simultaneamente y reportá cada combinacion:

 a) TIMEFRAME: 1h, 4h, 1d
 b) EXTENSION DEL TARGET: 0.5, 1.0, 1.25, 1.5, 1.75, 2.0, 3.0
 c) STOP:
    - minimo del tramo
    - swing previo (n=3,5,8)
    - porcentual (1%, 2%, 3%)
    - MOVIL A BREAKEVEN tras +0.5R / +1R
 d) GESTION:
    - full target
    - cerrar mitad en +1R y dejar correr el resto
    - 3 objetivos escalonados 1R/2R/3R
 e) FILTROS DE REGIMEN:
    - precio sobre/debajo EMA200
    - pendiente de EMA50
    - ATR/precio < 2.5% / > 4%
    - solo si el tramo tiene >= N velas
 f) DIRECCION: long only / short only / ambos
 g) SOLO RANGO vs SOLO TENDENCIA:
    - identificar rango (precio entre EMA50 y EMA200, o ADX bajo) y probar
      mean reversion en rango con MENOR capital.

## 4 · FILTRO DE VERDAD (obligatorio para declarar algo)

Toda variante debe pasar por daily_pilot/scripts/validacion_protocolo.py:
 - null sintetico por block bootstrap -> percentil 95
 - p-valor empirico
 - n >= 30 operaciones (si no, MUESTRA CHICA y NO se declara)
 - walk-forward (2/3 train, 1/3 test): reportar degradacion
 - montecarlo de los resultados

## 5 · ENTREGABLE

daily_pilot/investigacion/ESTRATEGIA_GANADORA.md con:
  1. Tabla de TODAS las variantes probadas (tf, ext, stop, filtro, n, acierto,
     esperanza R, p-valor, veredicto)
  2. Las 3 mejores con sus metricas completas (FB, DD, racha, R)
  3. Walk-forward de la mejor
  4. VEREDICTO final: EXISTE / NO EXISTE estrategia ganadora en este universo
  5. Si existe: parametrizacion exacta + cuanto capital arriesgar (1%/2%/5%)

Y el script reproducible: daily_pilot/scripts/busqueda_estrategia.py

## 6 · NOTAS

- Prioriza la correccion sobre la velocidad: un numero mal medido no sirve.
- Si encontrás una variante que pasa el filtro, validala en ETH antes de declararla.
- Rango: si la mejor configuracion es de rango, decirlo explicitamente
  (el usuario opera rango con menos capital).
- Bull run: si la estrategia solo funciona en tendencia, decirlo explicitamente.
