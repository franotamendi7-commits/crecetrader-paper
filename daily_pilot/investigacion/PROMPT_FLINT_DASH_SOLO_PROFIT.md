# FLINT — DASH SOLO PARES RENTABLES + SCALE-IN (NO tocar CSS)

El diseño está aprobado: **no cambies CSS, colores, tipografía ni animaciones.**
Solo contenido.

ARCHIVO NUEVO (leelo): `daily_pilot/datos/universo_profit.json`

## Cambios

1) **Mercado Quantfury: mostrar SOLO los 9 pares del JSON**, no los 33.
   Borrar del tablero los 25 pares sin estrategia validada. Si querés, un
   pie de sección: "25 pares sin estrategia validada — ocultos".

2) **Dos bloques de estrategia claramente separados** (no mezclar):
   - PULLBACK 4h · riesgo 0,35% · 6 pares · 64,3 señales/mes · E +0,140R · DD −98,1R
   - SCALE-IN FIBO 1h+4h · riesgo 2% · 5 pares · 208 ops · 97,1% win · +$6.709 · DD −$17,18

3) **Modal por par**: mostrar TODAS las estrategias que aplican a ese par
   (BTC y XRP tienen las dos). El scale-in explica la regla del JSON:
   "Fase1 → Fase2 retroceso 38,2% → Fase3 entradas en 61,8% y 100%, stop fijo, filtro R≥4%".
   Estado VALIDADA / DÉBIL según el JSON.

4) **Nuevo panel de forward**: leer `daily_pilot/datos/tracker_scalein.json`
   y `tracker_paper.json`, mostrar `forward_n` y total $ de cada uno.
   Hoy ambos dicen forward 0 (recién arrancan). Etiquetar: "FORWARD EN CURSO".

5) Mantener el panel del video y el de resultados.

## Reglas duras
- Todos los números del JSON. No inventar.
- No tocar CSS. No tocar index.html a mano: regenerar con generar_dashboard_v6.py.
- PAPER_ONLY visible.
- No romper panel_video / panel_resultados / panel_senales.

## Verificación
1) python3 daily_pilot/scripts/generar_dashboard_v6.py → sin errores
2) python3 daily_pilot/tests/run_all.py → 15 OK
3) Browser + screenshot: 9 pares listados, dos bloques de estrategia,
   modal BTC con AMBAS estrategias, panel forward visible.
4) Commitear en crecetrader-limpio con identidad franotamendi7-commits.
5) Reportar archivos, salida de suite y screenshot.
