# FILTRO DE CORRELACION — DESCARTADO + HALLAZGO CRITICO

Fecha: 2026-11-25. PAPER_ONLY.

## 1 · Filtro de correlacion (limitar posiciones simultaneas)

| configuracion | /mes | E | DD | PF |
|---|---:|---:|---:|---:|
| **Sin filtro** | 59,4 | **+0,128** | **−127,6** | 1,34 |
| Max 1 abierta | 42,5 | −0,010 | −240,6 | 0,98 |
| Max 2 abiertas | 55,5 | +0,089 | −153,2 | 1,23 |
| Max 3 abiertas | 58,8 | +0,120 | −134,4 | 1,32 |
| Max 4 abiertas | 59,4 | +0,128 | −127,6 | 1,35 |

**Empeora.** Al saltarse señales se pierden también las ganadoras que
compensaban a las perdedoras. Con max 1 la esperanza se vuelve negativa.

Conclusión: el DD NO se baja recortando señales. La cartera de 4 pares sin
filtro sigue siendo la mejor configuración encontrada.

## 2 · HALLAZGO CRITICO: las velas se sobreescriben

Mientras corría este test descubrí que los archivos 4h de los 4 pares
habían quedado en **1.000 velas (junio 2026 → noviembre 2026)** en lugar de
las 15.000-20.000 velas descargadas.

Causa: `daily_pilot/core/velas.py::velas(par, tf, limite=...)` **escribe la
cache** con las velas que pide. Varios scripts del repo piden `limite=500`
y pisaron el histórico completo.

Esto significa que **cualquier backtest corrido después de esos scripts
estaba usando solo 5 meses de datos** y daba números falsos. De ahí salió
el resultado de 249 señales / 0,2 años que me hizo descartar el test.

**Corregido:** re-descargué la historia completa de los 4 pares:
```
BTCUSDT   20.310 velas  2017-08-17 → 2026-11-25
THETAUSDT 16.716 velas  2019-04-10 → 2026-11-25
HBARUSDT  15.687 velas  2019-09-29 → 2026-11-25
ETCUSDT   18.524 velas  2018-06-12 → 2026-11-25
```

**Pendiente de arreglar en el código:** que `velas()` NO escriba cache cuando
se pide un `limite` menor al histórico guardado, o que use otro nombre de
archivo para la cache corta. Hasta entonces, todo backtest debe leer el
archivo directamente (como hacen los scripts de validación), no vía `velas()`.

## Estado final de la busqueda

| intento | resultado |
|---|---|
| Cartera 4h (4 pares) | ✅ vigente — 59,4/mes, E +0,128R, DD −127,6R |
| Capa 1d | ❌ 90% solapada con 4h |
| Short | ❌ E −0,235R |
| ML | ❌ no mejora |
| Filtro de correlacion | ❌ empeora DD y esperanza |
| ETH | ❌ p=0,217 |

PAPER_ONLY. No se ejecutaron órdenes.
