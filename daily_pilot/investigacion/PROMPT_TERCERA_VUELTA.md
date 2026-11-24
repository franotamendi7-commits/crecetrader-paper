# Tercera vuelta — probar el RESTO del método (ancla 0416cb1)

Modo: **propuesta, no ejecución.** PAPER_ONLY intacto. No se toca `metodo/` ni la FIRMA.

## Lo que ya está probado (y descartado)

| hipótesis | resultado |
|---|---|
| **H1** confluencia entre TF (tol 0,5%) | 0 niveles confluentes — no hay evidencia |
| **H2** zona con ancho ATR ×0,5 | mejora solo con ese ancho; con ×1,0 empeora (BTC 42%→30%, SOL 38%→18%) → **sobreajuste** |
| **H5** primer toque vs resto | muestra chica, no concluyente |

El **backtest base** hoy da: BTC 1d retro 0,61 = 5/12 (42%), retro 0,786 = 0/2.

Conclusión hasta acá: **el nivel pelado no alcanza**. Falta probar las partes del
método que el backtest actual no cubre.

## Las partes del método que aún NO medimos

El playbook define más cosas que los retrocesos. Proponé y medí **dos o tres** de
estas (o las tuyas):

| # | parte del método | qué habría que medir |
|---|---|---|
| **A** | **Abanico intradía de 9 niveles** (±0,25, ±0,50, ±0,75, ±1,00, ±1,25 del cierre de las 21:00) | ¿el precio respeta esos niveles? ¿cuántos toques y cuántos hold? |
| **B** | **Liquidez institucional** (fibo + 1 enero + pools, sesión NY) | ¿los niveles cercanos a esos puntos resisten más? |
| **C** | **Niveles dichos por el canal** (los que repite CreceTrader) contra el precio posterior | ¿los niveles que menciona el canal se tocan más que los calculados? |
| **D** | **Régimen confirmado** (`supera_y_consolida`) antes de entrar | ¿respetan más los niveles cuando el régimen está confirmado? |
| **E** | **Combinación**: retroceso + confluencia de TF + régimen confirmado | ¿la intersección mejora algo? |

## Reglas del juego (las mismas de antes)

- Walk-forward: el tramo se congela antes de la ventana de test.
- **hold** = no cruza, sin cambiar la definición.
- Reportar **n** siempre. Si n < 15, decir «muestra chica» y no sacar conclusión.
- Validar en **por lo menos dos pares** (BTC + ETH o SOL). Si solo funciona en BTC, no sirve.
- No ajustar parámetros hasta que el número quede lindo.
- Si algo no está en los datos que tenemos, decilo y proponé qué dato haría falta.

## Datos disponibles

```bash
python3 daily_pilot/scripts/hipotesis_estrategia.py --par BTCUSDT --tf 1d --detalle 150
python3 daily_pilot/scripts/backtest_niveles.py BTCUSDT --tf 1d --detalle 150
python_pilot/scripts/agente_ticket.py BTCUSDT --tf 4h --json
```

Velas cacheadas en `daily_pilot/datos/velas/{PAR}_{TF}.json` (Binance público,
1w/1d/4h). Los niveles del canal están en
`daily_pilot/investigacion/AGENTE_*.json` (`niveles_dichos`).

## Qué quiero de vos

1. **Elegí 2 o 3** de la tabla (A–E) y decí **por qué** tendrían sentido según el
   playbook (citá la regla si existe).
2. **Código Python exacto** para cada una (funciones con firma clara), listo para
   meter en `daily_pilot/scripts/`.
3. **La métrica de decisión**: con qué número aceptamos que sirve. Te sugiero:
   - mejora ≥ 10 puntos sobre el baseline,
   - n ≥ 15 por grupo,
   - que se sostenga en el segundo par.
4. **Qué descartás de entrada** (si algo necesita datos que no tenemos).

## Entregable

Por cada opción elegida: **código + expectativa + criterio de decisión +
qué dato falta (si falta)**. Si las que quedan tampoco funcionan, decime cuál estuvo
más cerca y qué probarías después.

Nada de prosa: código y criterios.
