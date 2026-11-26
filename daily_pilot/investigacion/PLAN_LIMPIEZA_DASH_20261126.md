# PLAN DE LIMPIEZA DEL DASH — propuesta, NO aplicada

2026-11-26 · Auditoría de lectura. El dash NO fue modificado.

## DECISIONES DEL USUARIO (en orden, esperando las próximas capturas)

1. ✅ **MERCADO QUANTFURY + header + barra HOY** → SE MANTIENE TAL CUAL.
2. ⚠️ **ANÁLISIS CRECETRADER (bloque actual: 33/67, niveles xN menciones, soportes/resistencias/escenarios)** → **UNIFICAR Y SIMPLIFICAR**. Es prácticamente la misma info repetida en dos lugares. Hacer **un resumen del video diario** abajo de todo (al final del dash), con:
   - **Niveles** (solo los importante, sin "x24 menciones" ni contexto crudo)
   - **Tendencia** (alcista/bajista, simple)
   - **Posibles entradas según CreceTrader**
   - **Sin tantos números** — informe simple, legible, no un volcado de datos
   - Irá **al último**, después de todo lo demás
3. (Faltan las próximas capturas / decisiones — agregar acá.)

> Instrucción del usuario: "si preferis guarda todo lo que digo y despues hace todo junto". **NO aplicar nada hasta que diga que ya mandó todas las capturas.**

## Inventario de lo que hoy muestra el dash

| # | Bloque | Clase/origen | Qué muestra | Naturaleza |
|---|---|---|---|---|
| 1 | **Mercado Quantfury** | `mercado()` | 13 pares, precio real 24h | ✅ **OPERATIVO** — precio en vivo |
| 2 | **Detalle por par** (13 modales) | `.pdetail` | Precio, niveles del video, estado, estrategia, regla, métricas backtest, sizing | ⚠️ **MIXTO** — precio operativo + backtest |
| 3 | **Análisis CreceTrader** | `.vid` / `panel_video.py` | Video nuevo, tesis, niveles, escenarios | ⚠️ **INFORMATIVO** — no es señal |
| 4 | **Panel operativo** | `.op` / `panel_operativo.py` | Pares, señales, acierto, $, DD, riesgo, forward | ✅ **OPERATIVO** — lee trackers |
| 5 | **Señales · paper trading** | `.sg` / `panel_senales_vivo.py` | ACTIVAS (0) / CERRADAS (577), entry/stop/target/resultado | ✅ **OPERATIVO** — lee trackers |
| 6 | **Cartera mixta** | `panel_senales.py` | 13 pares, 63,9 señales/mes, E +0,142R, PF, DD, tabla por par con WF | ❌ **BACKTEST** — números de histórico |
| 7 | **Tracker paper** | `panel_tracker.py` | 286 ops, E replay +0,009R, E backtest +0,128R, PF, DD, tabla por par | ❌ **BACKTEST** — duplica #6 con otro formato |

## Hallazgo principal

Los bloques **6 y 7 son la misma información** (286 operaciones, E, PF, DD de la cartera) presentada dos veces. Juntos son el 90% del ruido de backtesting del dash.

Además, dentro del **detalle por par** (#2) cada modal muestra métricas de backtest:
```
Señales/mes · E(R) · Acierto · DD(R) · PF · regla · validación
```
Eso es información nuestra, no de operación.

## Propuesta — dash limpio tipo "paper trader desde cero"

### Mantener
- ✅ **1. Mercado Quantfury** — precio real, es lo único que cambia en vivo
- ✅ **4. Panel operativo** — qué estrategias están corriendo y su resultado paper
- ✅ **5. Señales** — activas y cerradas, con entry/stop/target
- ✅ **2. Detalle por par SOLO la parte operativa**: precio, estado, niveles de alerta (si los hay), señal activa

### Sacar o mover a pestaña "Backtesting"
- ❌ **6. Cartera mixta** completa
- ❌ **7. Tracker paper** completo
- ❌ De los modales: `Señales/mes`, `E(R)`, `Acierto`, `DD(R)`, `PF`, `regla`, `validación`, `Null seeds`, `WF train→test`
- ⚠️ **3. Análisis del video**: evaluar — es informativo, no operativo. Candidato a pestaña "Notas".

### Resultado esperado
```
Antes: 15 secciones, 54.565 bytes
Después: ~4 bloques + 13 modales livianos, ~20-25 KB
```

## Cómo se haría (cuando des autorización)

1. No se toca CSS ni layout: se comentan los `html_*()` en `generar_dashboard_v6.py`.
2. Se mueven los paneles a un archivo `panel_backtest.py` separado (o se dejan importados pero sin llamar).
3. Se regenera el HTML con el generador (nunca editar `index.html` a mano).
4. Se verifican los mismos 7 casos: HTTP 200, 13 pares, 0 "sin estrategia", PAPER ONLY, suite 15/15, sin secretos, unlocked jobs.

## Lo que NO se toca

`store.db`, `daily_pilot/metodo/`, FIRMA, `~/.hermes/.env`, trackers, estrategias, velas.

---

## Estado

**NO APLICADO.** Esperando que Francisco confirme qué se mantiene y qué se va con capturas.
