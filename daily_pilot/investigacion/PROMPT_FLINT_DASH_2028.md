# PROMPT PARA FLINT — Rediseño institucional del dashboard CreceTrader (nivel 2028)

> Copiar y pegar completo en Flint. No es una sugerencia: es un specs con criterios de aceptación.

---

## 0. CONTEXTO (leelo antes de tocar nada)

Repo: `~/YouTubeTradingAgent`, rama `crecetrader-limpio`, commit actual `ec98491`.
Es un sistema de trading **PAPER_ONLY**: muestra, NUNCA ejecuta órdenes. No modificar
`daily_pilot/metodo/`, ni la FIRMA firmada, ni `~/store-local/store.db`.

Estado real del proyecto (no inventar nada de esto):

- **33 criptos operables en Quantfury**. Precios reales de Binance (solo lectura,
  caché 5 min) vía `daily_pilot/core/velas.py::velas(par, tf, limite)`.
  Lista en `generar_dashboard_v6.py::PARES_QUANTFURY`. `SUSDT` = TRADING,
  `TONUSDT` = BREAK.
- **Estrategia validada** (verificada por Hermes, commit `06bb086`):
  ruptura de tramo en 4h, long only, stop swing3, target ext 3.0, gestión full.
  BTC: n=52, E=+1,237R, DD=-6,35R, FB=3,10, p=0,020. ETH: n=53, E=+1,173R,
  DD=-7,42R, p=0,028. Walk-forward ETH degrada -63%. Recomendación: PAPER al 1%.
- **Video vigente**: `hb9YEJMgjAU` (24/11/2026), resumen real en
  `daily_pilot/analisis/resumen_video.json` (13 niveles, 3 escenarios, macro).
- **Monitor**: `daily_pilot/datos/monitor_senales.json` → BTC y ETH SIN señal
  abierta (última cerró STOP el 21/08/2026). Capital de referencia $300, riesgo 1%,
  apalancamiento Quantfury 20x.

Archivos que existen HOY (leelos antes de editar):

```
daily_pilot/scripts/generar_dashboard_v6.py   ← generador principal (CSS inline)
daily_pilot/scripts/panel_resultados.py       ← panel de resultados/backtest
daily_pilot/scripts/panel_video.py            ← panel del resumen del video
daily_pilot/scripts/panel_senales.py          ← panel del monitor de señales
daily_pilot/scripts/monitor_senales.py        ← lógica del monitor
daily_pilot/datos/informe_hoy.json
daily_pilot/datos/monitor_senales.json
daily_pilot/analisis/resumen_video.json
daily_pilot/dashboard/index.html              ← GENERADO. NO editar a mano.
```

---

## 1. OBJETIVO

Rediseñar el dashboard a nivel **institucional 2028**. Debe verse como una terminal
operativa seria, no como un blog. Referencia visual: las capturas que te pasé
(panel de trading con gráfico 4H + análisis técnico + plan + risk manager, y el
command center oscuro con estaciones por dominio).

**Separar dos dominios de forma inequívoca:**

| DOMINIO A — QUANTFURY | DOMINIO B — CRECETRADER |
|---|---|
| Mercado real, 33 criptos | Análisis del canal |
| Precios reales + cambio 24h | Resumen del video + niveles dichos |
| Alertas por precio por par | Estrategia validada + verificación |
| Gestión de riesgo por par | Veredicto y números honestos |

Nada de mezclarlos en la misma card. Nada de "lectura del agente 40/25/35"
genérico: eso se elimina o se convierte en algo con evidencia real.

---

## 2. ARQUITECTURA OBLIGATORIA

1. **No edites `index.html` a mano.** Es generado. Todo cambio va en el
   generador (`generar_dashboard_v6.py` o un `v7` nuevo que lo reemplace) y en
   los módulos `panel_*.py`. Un solo comando debe regenerar el HTML.
2. **Navegación por hiperlink real**: cada uno de los 33 pares debe ser un
   enlace a su propia ventana de detalle (`#/par/BTCUSDT` o `pares/BTCUSDT.html`).
   No vale un `div` con hover. Tiene que poder abrirse, linkarse y volver.
3. **Vista por par (micro-diseño propio)** con, como mínimo:
   - Ticker, precio real, cambio 24h, estado (TRADING / BREAK).
   - Gráfico real de velas si hay datos 4h/1d (canvas o SVG dibujado con los
     datos de `velas()`). Si no hay velas, decí "sin datos", **no dibujes nada falso**.
   - Niveles clave del par (si existen en los JSON). Si no existen: "sin niveles
     configurados". **Prohibido inventar niveles.**
   - **Alertas por par**: tabla con `precio disparador`, `dirección` (COMPRA /
     VENTA / ATENCIÓN) y `estado` (DISTANTE / CERCA ≤1% / TOCADO). Margen visual
     claro cuando está CERCA o TOCADO.
   - **Gestión de riesgo propia**: capital $300, riesgo 1%, stop, target, R:R,
     unidades, notional, margen 20x. Si no hay señal, mostrar la última señal
     cerrada y su resultado, no un ticket inventado.
4. **Modo servidor**: entregá cómo correrlo en un puerto de la Mac, además de
   `file://`. Ejemplo: `python3 -m http.server 8765 --directory daily_pilot/dashboard`
   o un `serve_dashboard.py` con stdlib. Documentalo arriba del generador.

---

## 3. ESTÉTICA INSTITUCIONAL (exigencia máxima)

- Dark theme. Tokens CSS: `--bg:#080c12`, `--bg2:#0d1420`, `--card:#131b28`,
  `--bd:#232f42`, `--fg:#eaf1f9`, `--muted:#7f8ea3`, `--acc:#5aa2ff`,
  `--ok:#3ecf7a`, `--bad:#ff6b63`, `--warn:#e0aa4c`.
- Tipografía SF Pro / Inter, `font-variant-numeric: tabular-nums` en TODOS los
  números. Alineación de decimales. Sin fuentes externas que rompan offline.
- Jerarquía visual: 1 header global → 2 dominios claramente diferenciados por
  color de borde/barra → 3 vista por par con layout tipo terminal
  (gráfico izquierda / análisis-plan-risk derecha).
- Glassmorphism sutil, micro-interacciones en hover, transiciones <150ms.
  Nada de emojis decorativos en la UI. Nada de GIFs. Nada de gradients
  arcoíris. Soberbia visual, no infantil.
- Responsive real: de 1440px a 390px sin romperse. Probalo en ambos.
- **PAPER ONLY visible** en el header y en el footer, siempre.

---

## 4. DATOS — REGLAS DURAS

- Todos los números vienen de archivos reales o de `velas()`. **Cero datos demo.**
- Si un JSON falta o está corrupto: mostrar "sin datos", no romper el dash.
- El resumen del video es transcription real; no lo resumas vos de nuevo: leelo.
- La estrategia mostrada es la verificada (n=52 etc.). Si mostrás probabilidad
  de acierto, es 44,2% para BTC — no 68% inventado como en la captura de
  referencia. La referencia es de estilo, **no de números**.
- Si el monitor dice "SIN SEÑAL", el dash dice "SIN SEÑAL". Punto.

---

## 4B. CORRECCIONES DE FLINT — YA VERIFICADAS POR HERMES (ejecutar, no discutir)

Flint propuso 6 arreglos. Hermes los contrastó contra el código real. Resultado:

| # | Recomendación | Veredicto | Evidencia |
|---|---|---|---|
| 1 | Veredicto incompleto | **CIERTO** | HTML real: `<div class="verdict no">RESULTADO DE LA BÚSQUEDA</div>`. Causa: `_veredicto()` en `panel_resultados.py` solo detecta líneas que arrancan con `VEREDICTO`, pero el MD dice `## 6. VEREDICTO FINAL` → no matchea. Arreglar el parser para que encuentre `VEREDICTO FINAL` y muestre el resultado real: `PASA (p=0.020)` / `RUIDO`. |
| 2 | `class="badge "` con espacio | **CIERTO** | HTML real: `class="badge "`. Causa: `badge_cls = '' if vid else 'no'` interpolado con espacio. Normalizar con `.strip()` o armar la clase condicionalmente. |
| 3 | Tabla mezcla mantenimiento con estrategia | **CIERTO** | HTML real: una sola `<table class="rtab">` con filas `BTCUSDT 1d 3387 2017-08-17...` (mantenimiento de datos) junto a `4h 8 3.0 swing3 full long ... PASA (p=0.020)`. Separar en DOS tablas: "Análisis de mercado" (cobertura de velas) y "Resultados de estrategia" (variantes), cada una con su header. |
| 4 | CSS muerto `.vid .esc`, `ul`, `blockquote`, `.vid .link` | **FALSO** | Conteo real en el HTML generado: `class="esc"`=1, `<ul>`=1, `<blockquote>`=5, `class="link"`=1. Se usan. NO eliminar. Si querés simplificar, primero verificá con grep, no por inspección visual. |
| 5 | Fecha hardcodeada | **CIERTO (parcial)** | No es literal hardcodeada: viene de `info.get('publicado')` del JSON del video. Pero muestra SOLO la fecha del video. Mostrar además `generado` del monitor y etiquetar cada una: "Video: 24/11 10:16 · Tablero: 25/11 14:07". |
| 6 | Reparto Alcista/Bajista/Lateral 33/67/66 | **CIERTO** | HTML real confirma 33% / 67% / 66% (suma 166%). Causa: `lateral = 100 - abs(pct_ar - pct_ab)` es una métrica de simetría, no un reparto. Reemplazar por un reparto que sume 100% con significado claro, o sacar la card y mostrar evidencia textual. **Prohibido mostrar porcentajes que no sumen 100** sin explicar qué miden. |

Regla general derivada: antes de eliminar CSS o cambiar una fórmula, verificar con
grep/conteo sobre el HTML generado. No asumir por mirada.

---

## 5. VERIFICACIÓN OBLIGATORIA (no termines sin esto)

1. `python3 daily_pilot/scripts/generar_dashboard_v6.py` (o el v7) → sin errores.
2. `python3 daily_pilot/tests/run_all.py` → **15 OK · 0 FALLO · FUENTES INTACTAS**.
3. Abrir el HTML en browser y comprobar, con evidencia:
   - 33 pares listados y cada uno clickeable.
   - Vista por par abre, cierra y vuelve al listado.
   - Alertas por par con umbral y estado reales.
   - Dominios QUANTFURY y CRECETRADER separados visualmente.
   - Gráfico con datos reales (o cartel "sin datos" donde corresponda).
   - Sin números inventados.
   - Servidor en puerto funcionando si lo implementaste.
4. Commitear en `crecetrader-limpio` con:
   `git -c user.name="franotamendi7-commits" -c user.email="franotamendi7-commits@users.noreply.github.com" commit -m "..."`
5. Reportar: archivos tocados, salida de la suite, screenshot, y qué NO se tocó.

---

## 6. CRITERIOS DE ACEPTACIÓN (checklist — si falta uno, no está terminado)

- [ ] 33 criptos, cada una con hiperlink a su vista propia.
- [ ] Vista por par con precio real, gráfico real o cartel "sin datos", niveles reales.
- [ ] Alertas por par: disparador, dirección, estado DISTANTE/CERCA/TOCADO.
- [ ] Gestión de riesgo por par: $300, 1%, stop, target, R:R, 20x.
- [ ] QUANTFURY y CRECETRADER en bloques separados y reconocibles.
- [ ] Resumen del video + verificación de la estrategia visibles en su dominio.
- [ ] Sin números de demostración. Sin "68%" inventado. Sin niveles inventados.
- [ ] PAPER_ONLY siempre visible.
- [ ] Responsive 1440 → 390.
- [ ] Suite 15/15 y fuentes intactas.
- [ ] `index.html` regenerado por el generador, nunca editado a mano.
- [ ] Veredicto real visible (`PASA (p=0.020)` o `RUIDO`), no texto genérico.
- [ ] Sin `class="badge "` con espacio en el HTML generado.
- [ ] Dos tablas separadas: cobertura de mercado y resultados de estrategia.
- [ ] Clases `.esc`, `ul`, `blockquote`, `.link` conservadas (se usan).
- [ ] Fechas etiquetadas: video y tablero por separado.
- [ ] Reparto con porcentajes que sumen 100 o evidencia textual en su lugar.
- [ ] Commit en rama correcta con identidad correcta.

---

## 7. LO QUE NO QUERO QUE HAGAS

- No toques `daily_pilot/metodo/`, la FIRMA, ni `~/store-local/store.db`.
- No ejecutes órdenes ni escribas código que pueda ejecutarlas.
- No inventes precios, niveles, probabilidades ni señales.
- No rompas los paneles existentes (`panel_resultados`, `panel_video`, `panel_senales`).
- No dejes el dash dependiente de internet/CDN para funcionar.
- No me digas "listo" sin la salida real de la suite y el screenshot.

Estamos en 2028. Esto se hace una vez y no se toca más. Exigite vos también.
