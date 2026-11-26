# AUDITORÍA COMPLETA PARA FLINT — CreceTrader PAPER_ONLY

Fecha: 2026-11-26 · Rama: `crecetrader-limpio` · HEAD: `6f203ea` (cadencia operativa final + auditoría; working tree limpio e in sync con origin).
**NO tocar: `daily_pilot/metodo/`, la FIRMA, `store.db`, velas de `datos/velas/`.**
**NO escribir en el repo el webhook de Discord** (vive en `~/.hermes/.env`, permisos 600).

---

## 1. Objetivo

Auditar que el sistema operativo **paper-trade** sea coherente: que las señales que ve el usuario en Discord sean las mismas que ve en el dash, que no se pierdan por lectura de velas sin cerrar, y que ningún número del dash esté inventado.

---

## 2. Cadenda temporal (REVISAR CON CUIDADO)

Orden correcto — no invertir:

```
:00 :15 :30 :45  → actualizar_velas.py (baja SOLO velas nuevas, 13 pares, 1h+4h)
:01              → tracker_scalein.py
:02              → tracker_paper.py
:03              → tracker_bos.py
:05 cada hora    → alertas_senales.py → Discord #señales-crecetrader
cada 5 min       → dash-refresh (generar_dashboard_v6.py) → precio en vivo
```

**Trampa ya detectada y corregida:** correr los trackers a las `:59` (antes del cierre) es ERRÓNEO. La última vela aún no cerró y `tracker_scalein.py` líneas 57-58 la descarta (`if v1[-1]['ts'] + 3600*1000 > ahora: v1 = v1[:-1]`). Resultado: se pierde la señal. Verificar que ese guard siga existiendo y que ningún cambio lo haya quitado.

Chequear los 6 plists en `~/Library/LaunchAgents/com.crecetrader.*.plist`:
- `plutil -lint` → OK en los 6
- `launchctl list | grep crecetrader` → 6 jobs cargados
- `alertas-senales.plist` debe tener **24 entradas** Hour 0..23, todas Minute 5 (ya se corrigió un `replace_all` que tocó Hour 15 y borró Hour 16)

---

## 3. Archivos a revisar

### Generales
| Archivo | Qué revisar |
|---|---|
| `daily_pilot/scripts/generar_dashboard_v6.py` | `PARES_QUANTFURY` = 13 pares; imports de paneles; que no haya `33 criptos` quedado |
| `daily_pilot/scripts/actualizar_velas.py` | incremental: `desde = última ts + 1`; 13 pares; 1h+4h; manejo de errores por par |
| `daily_pilot/scripts/alertas_senales.py` | 3 trackers en el loop; `User-Agent` presente (sin él Discord da 403); idempotencia por `(par, senal_ts)`; `PAPER ONLY` en el mensaje |
| `daily_pilot/scripts/tracker_scalein.py` | guards de vela sin cerrar; `RIESGO_TOTAL = 0.02`; idempotencia |
| `daily_pilot/scripts/tracker_paper.py` | idempotencia; lectura directa de JSON |
| `daily_pilot/scripts/tracker_bos.py` | idempotencia; 3 pares INJ/DOGE/DOT |
| `daily_pilot/scripts/panel_operativo.py` | números leídos de los JSON, NO hardcodeados |
| `daily_pilot/scripts/panel_senales_vivo.py` | 2 columnas activas/cerradas; clasificación por `estado` |
| `daily_pilot/scripts/panel_senales.py`, `panel_tracker.py`, `panel_video.py`, `panel_resultados.py` | no tocar |

### Estrategias (NO modificar parámetros)
- `scalein_fibo.py`: `RIESGO_TOTAL=0.02`, `MIN_R=0.04`, 7 pares validados, `CAPITAL=5680.38`
- `estrategias_validadas.py`: PULLBACK 4 pares, REVERSION 2 pares, riesgo 0.35%
- `test_bos.py`: detector BOS 4h + confirmación 1h, 3 pares
- **`test_robusto.py`, `test_pullback_reversion.py`, `test_bos.py` son de TEST, no de producción** — no cambiar los umbrales de validación (20 seeds, p<0.05, WF test>0)

---

## 4. Datos esperados (no inventar)

| Concepto | Valor esperado |
|---|---|
| Pares en dash | 13 (ARB AVAX BTC DOT DOGE ETC FIL HBAR INJ LINK NEAR THETA XRP) |
| Estrategias | 4: scale-in (7), pullback (4), reversión (2), BOS (3) — con superposición |
| Scale-in | 291 ops · 97,9% win · +$11.138,82 · DD −$17,18 · riesgo 2% |
| BOS | 768 ops · 50% win · +49,75R · DD −27,50R |
| Test robusto | 29 pares → 7 validan / 22 descartan |
| Pullback/reversión | 44 pruebas → 43 descartan, 1 reserva (INJ, WF colapsa) |
| BOS en 22 | 3 validan (INJ DOGE DOT), 19 descartan |
| Suite | 15 OK · 0 FALLO · FUENTES INTACTAS |

---

## 5. Casos de prueba

1. **Idempotencia:** correr cada tracker 2 veces seguidas → la 2ª debe decir `+0 nuevas`.
2. **Sin duplicados en Discord:** correr `alertas_senales.py --preview` dos veces → 2ª sin mensajes.
3. **Sin vela sin cerrar:** con `date -u`, verificar que el tracker no procesó la vela en formación.
4. **Dash:** HTTP 200 en `http://localhost:8765/index.html`, 13 `.mcard`, 0 "sin estrategia validada", `PAPER ONLY` visible.
5. **Números:** TODO lo que muestra el panel operativo debe salir de `tracker_*.json`. Si un número no está en un JSON, es un bug.
6. **Suite:** `python3 daily_pilot/tests/run_all.py` → 15 OK.
7. **Secreto:** `git grep -l 'discord.com/api/webhooks' -- . ':!daily_pilot/investigacion'` → 0 resultados. Excluir `investigacion/` porque el propio spec menciona el patrón y da un falso positivo.

---

## 6. Problemas YA corregidos (no revertir)

- Webhook Discord: 403 por falta de `User-Agent` → agregado `CreceTrader-Paper/1.0`
- Test robusto: glob sin `.json` → 0 resultados → corregido
- Pullback/rev: `simular()` devuelve floats, no dicts → corregido
- `estado_hoy.json`: timestamp lo escribe `com.hermes.youtube-2h-check` cada 2h → descartar, no commitear
- Trackers corriendo cada 4h sobre velas congeladas → forward frenado → agregado `actualizar_velas.py`

---

## 7. Entregable de Flint

1. Lista de hallazgos: `[P0/P1/P2] archivo:línea — problema — corrección`.
2. Confirmación de los 7 casos de prueba con salida real.
3. **NO modificar nada** — auditoría de lectura. Si algo está mal, reportar y esperar autorización.
4. Reportar si los números del dash coinciden con los JSON.
