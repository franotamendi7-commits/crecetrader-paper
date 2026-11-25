# PARTE 2 PARA FLINT — Meter las estrategias validadas al dash (NO tocar el CSS)

El diseño actual me gusta: **no cambies nada del CSS, del layout ni del click por par**.
Solo reemplazá el CONTENIDO de los paneles con los datos reales.

## Archivo de datos (ya existe, leelo)

```
daily_pilot/datos/estrategias_validadas.json
```

Ese JSON tiene todo: regla, 4 pares con sus métricas, cartera y aviso.

## Cambios de contenido

1. **Panel "MONITOR DE SEÑALES" — está OBSOLETO.** Hoy muestra la estrategia
   vieja (`ruptura tramo 4h · n=52 · E=+1,237R · 6 señales/año`). Reemplazalo
   por la estrategia validada del JSON:
   - Título: `ESTRATEGIA VALIDADA · 4 PARES · 59,4 señales/mes`
   - KPIs: E=+0,128R · acierto 60,4% · PF 1,34 · DD −127,6R
   - Tabla con los 4 pares: THETA (VALIDADA), BTC (CON RESERVA), HBAR y ETC (DÉBILES)
   - Mostrar `null p`, `seeds`, `WF test` y el estado de cada uno.
   - Agregar: octubre cartera −1,26R vs BTC solo −7,26R.

2. **Click por par — rellenar los 4 pares que tienen estrategia.** Hoy dicen
   "sin alertas ni señales". Con los datos del JSON, mostrar por par:
   - Estado (VALIDADA / CON RESERVA / DÉBIL)
   - Señales/mes, esperanza, acierto, DD, PF
   - Regla resumida (stop swing fijo · 50% en 1R → BE → Fib 1.5)
   - Riesgo correcto: **0,35% de $300 = $1,05 por operación** (hoy dice "riesgo uno al uno", mal).
   - Los otros 30 pares siguen como están: "sin estrategia validada".

3. **Panel de resultados** — agregar una línea: `19 de 34 pares con E>0 · solo THETA valida estrictamente`.

## Reglas duras

- NO inventar números: todos salen del JSON.
- NO tocar CSS, colores, tipografía ni animaciones (el diseño ya está aprobado).
- NO tocar `index.html` a mano: regenerar con `generar_dashboard_v6.py`.
- PAPER_ONLY visible.
- Verificar: `python3 daily_pilot/tests/run_all.py` → 15 OK, y screenshot del
  click en THETAUSDT y BTCUSDT mostrando los datos nuevos.

Cuando termine, decime qué archivos tocó y pegá la salida de la suite.
