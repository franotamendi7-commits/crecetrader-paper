# PROMPT DE AUDITORÍA — CreceTrader daily_pilot (C01–C12, 2ª ronda)

> Pegá esto en DeepSeek. **Read-only**: que no modifique nada. Hallazgos con `archivo:línea`,
> evidencia, reproducción y severidad (P0/P1/P2). **No debe aprobar su propio trabajo.**
> Regla de Francisco: **NO CREER. PROBAR.**

---

## Rol y reglas

Auditor **read-only** de `daily_pilot`.

- **No** modifiques código, ni commits, ni `store.db`, `dashboard_data.json`, `estado_hoy.json`,
  `registro.json`, ni `dashboard/index.html`.
- **`sellado_integridad.py` ESCRIBE** (`.control.json` + manifiesto). **No lo corras en vivo.**
- **`run_all.py --integracion` ESCRIBE** (dashboard + E1). **Correlo en copia.**
- Entregá: **archivo:línea · evidencia · reproducción · severidad**.

## Repositorio

- **Repo**: `https://github.com/franotamendi7-commits/harnesstata.git`
- **Rama**: `crecetrader-limpio`
- **Local**: `/Users/franciscootamendi/YouTubeTradingAgent`
- **Fecha**: 2026-11-18

---

## Bloque 1 — Citas del playbook contra el corpus

Las citas se **generan del playbook**. Verificá que cada una exista y que la frase afirmada aparezca
en el cue o en los **±3 cues contiguos** (el transcript se corta en cues).

```bash
cd /Users/franciscootamendi/YouTubeTradingAgent
python3 - <<'EOF'
import re, sqlite3, pathlib
pb = pathlib.Path('daily_pilot/metodo/playbook_v0.1.md').read_text()
pares = sorted(set(re.findall(r'`([A-Za-z0-9_-]{11})`\s+(\d{2}:\d{2}:\d{2}(?:\.\d+)?)', pb)))
print('pares en el playbook:', len(pares))
c = sqlite3.connect('file:daily_pilot/knowledge/store.db?mode=ro', uri=True)
mal = 0
for v, s in pares:
    filas = c.execute("SELECT start, texto FROM claims WHERE video_id=? ORDER BY start", (v,)).fetchall()
    idx = next((i for i, (st, _) in enumerate(filas) if st.startswith(s)), None)
    if idx is None:
        print('FALTA   ', v, s); mal += 1; continue
    ventana = ' '.join(x for _, x in filas[max(0, idx-1): idx+4])
    print('OK      ', v, s, '|', filas[idx][1][:60])
    print('        ventana:', ventana[:110])
print('faltantes:', mal, 'de', len(pares))
EOF
```

**Reportá**: cuántos pares tiene el playbook, cuántos existen, y si la **frase citada** está en la
ventana. Si una cita **no** se sostiene, es un hallazgo P1.

## Bloque 2 — Motor de reglas: que los tests no mientan

```bash
cd /Users/franciscootamendi/YouTubeTradingAgent
python3 -B daily_pilot/tests/run_all.py            # 12 suites READ-ONLY
python3 -B daily_pilot/tests/run_all.py --integracion   # 2 suites (escriben)
```

**Estructura real**: **12 suites read-only + 2 suites de integración**. El runner imprime
`RESULTADO: 14 OK` = 12 + 2. **No** hay 14 suites de integración.

Verificá que **cada valor esperado en los tests** coincide con la **definición del experto**, no con lo
que el código produce. Si un test pasa pero contradice al playbook, es P1.

## Bloque 3 — Consistencia numérica (los puntos críticos)

- **C02/C09**: `30% oferta / 70% confirmación` (2×35%) y `4 tramos × 25%`. Verificá que **la suma de
  tramos nunca supere el tope del activo** (`allocacion.plan`) y que no haya doble conteo.
- **C04**: punto cero = **cierre diario 00:00 UTC (21 hs Argentina)**, abanico **9 niveles**
  (hasta ±1.00), paso **0.25**. Verificá **la unidad** del abanico (está como **pregunta abierta**).
- **C05**: retrocesos **50/61/78**, extensiones **50/100/150/200**; bajista **al inverso**.
  Con `min=56760, max=75518` → retrocesos **66139,00 / 63925,56 / 60774,21**.
- **C11**: **una sola fórmula** en `core/escenarios.py` y `risk_manager/risk_manager.py`:
  `riesgo = confianza × tope` (tope 5%). El **test cruzado** `tests/test_c11_cruzado.py` debe dar el
  mismo valor en ambos módulos.

## Bloque 4 — Integridad de E1

```bash
python3 -B daily_pilot/knowledge/verify_integrity.py     # READ-ONLY
```
**NO corras `sellado_integridad.py` en vivo** (escribe `.control.json` y el manifiesto).
Verificá `store.db` = 42 vídeos / 34.061 cues / 6.831 claims y que `.control.json` cierre.

## Bloque 5 — Líneas de separación (lo viejo FUERA)

- `PAPER_ONLY=true` en `risk_manager/risk_manager.py` y `core/allocacion.py` — ¿se respeta?
- Verificá:
  - `crontab -l` → **solo** `rss_4h_scheduler.sh`
  - `launchctl list | grep -iE 'harness|chief'` → **vacío**
    (`application.com.quantfury…` es la **app GUI**, no un cron: aclaralo, no lo cuentes como fallo)
  - `~/.hermes/cron/jobs.json` → los 3 jobs viejos con `enabled: false`
  - `ls ~/.hermes/composer-pastes` → **no existe**
  - `ls ~/.hermes/skills | grep -iE 'telegram|harness|trading-strategy'` → **vacío**
  - `~/.hermes/.env` **existe** (tiene `NOUS_ACCESS_TOKEN`, que sí hace falta). **No lo cuentes como fallo.**
- **Backup**: `~/backups-limpieza-20261118/` (142 MB).
- **Discord queda para después** (cuando el sistema esté validado). No debe correr nada.

## Bloque 6 — Aprobación del playbook (H-01, lo más importante)

`daily_pilot/metodo/playbook_v0.1.md` ahora distingue `aprobado_en_conversacion` de
`aprobado_por_francisco`. Verificá que:
1. El encabezado **no** afirme que todo está aprobado.
2. No queden reglas marcadas `aprobado_por_francisco` sin firma.
3. C12 use el enum correcto.

**Este es el punto que define si el playbook puede ser ground truth.**

## Entregable

1. **Veredicto**.
2. **Hallazgos** con `archivo:línea`, evidencia, reproducción, severidad.
3. **Afirmaciones del playbook que el corpus no sostiene** (lo más valioso).
4. **Lo que NO pudiste verificar** y por qué.

## Snapshot CONGELADO

> **Ver `daily_pilot/investigacion/SNAPSHOT_R3.md`** (commit + sha256 completos).
> Si `git rev-parse HEAD` no es `939440c…`, la auditoría es inválida.

```
commit            939440c4431f6568b96bcec0753a9a063d0a9017
store.db          6826b7e148fe13da9ecf58841d6a0f30627b2bc191541252d7411cdcedc76976
dashboard/index   4c73f494b46682c2f92b7d004a120b4eb94337b8c8c97d20224d2e90a611d9a6
estado_hoy.json   e530689e5b9e8eb70e1dbce92cacd88c08cfa56096bad55212eb901d4cba9475
dashboard_data    d92faf246999b87635ad7114b53ead7fbf8ab8cce7eb6f88e7f639b7a17b5f7e
tests             14 read-only OK · 2 integracion (en copia) · 0 fallos
```
