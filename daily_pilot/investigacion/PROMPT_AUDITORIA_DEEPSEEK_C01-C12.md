# PROMPT DE AUDITORÍA — CreceTrader daily_pilot (playbook C01–C12)

> Pegá esto en DeepSeek. Es **read-only**: que no modifique nada, que entregue hallazgos con
> `archivo:línea`, evidencia y severidad. **No debe aprobar su propio trabajo.**

---

## Rol y reglas

Auditor **read-only** del sistema `daily_pilot` (CreceTrader / YouTubeTradingAgent).

- **No** modifiques código, no hagas commits, no toques `store.db`, `dashboard_data.json`,
  `estado_hoy.json`, `registro.json` ni E1.
- Si encontrás algo, entregá: **archivo:línea · evidencia · reproducción · severidad (P0/P1/P2)**.
- **No apruebes tu propio trabajo.** Si el código está bien y el test pasa, decilo; si el test miente, también.
- **NO CREER. PROBAR.** Verificá cada afirmación contra el corpus (`store.db`) o contra una corrida real.

## Repositorio

- **Repo**: `https://github.com/franotamendi7-commits/harnesstata.git`
- **Rama**: `crecetrader-limpio` @ `6424381` (huérfana, limpia)
- **Local**: `/Users/franciscootamendi/YouTubeTradingAgent`
- **Fecha**: 2026-11-18

## Qué auditar (en este orden)

### 1. Coherencia del playbook con el corpus
`daily_pilot/metodo/playbook_v0.1.md` — 12 reglas (C01–C12), todas `aprobado_por_francisco`.
Verificá **contra `daily_pilot/knowledge/store.db`** que cada cita (`video_id` + `start`) exista y diga
lo que el playbook afirma. Reportá las citas que **no existan** o que **digan otra cosa**.

```bash
python3 - <<'EOF'
import sqlite3
c=sqlite3.connect('file:daily_pilot/knowledge/store.db?mode=ro',uri=True)
for v,s in [('LzPTdClLo_w','00:02:15'),('bCc--rvyHpY','00:04:42'),('i0qXzL0eSYs','00:15:11'),
            ('LFHkc5dUoLw','00:02:19'),('0prmrS6nnRk','00:07:25'),('LFHkc5dUoLw','00:09:34'),
            ('subONxt5iag','00:09:58'),('EJoLhxbwYxo','00:04:31'),('0prmrS6nnRk','00:06:59'),
            ('j06_M-fADjM','00:01:03'),('XLgPycsN0ls','00:15:33'),('Vm7nUxLCMZQ','00:03:22'),
            ('bCc--rvyHpY','00:00:12'),('_Lxz34x7eGg','00:02:31'),('DnwM-2nuS4s','00:07:32')]:
    r=c.execute("SELECT texto FROM claims WHERE video_id=? AND start LIKE ?",(v,s+'%')).fetchone()
    print(('OK  ' if r else 'FALTA'), v, s, (r[0][:90] if r else ''))
EOF
```

### 2. Motor de reglas — que los tests no mientan
`daily_pilot/core/{confluencia,intradia,zonas,liquidez,regimen,invalidacion,objetivos,escenarios,allocacion}.py`
Corré cada suite y verificá que los valores esperados en los tests coincidan con la **definición del
experto** (no con lo que el código produce):

```bash
cd /Users/franciscootamendi/YouTubeTradingAgent
python3 -B daily_pilot/tests/run_all.py            # read-only
python3 -B daily_pilot/tests/run_all.py --integracion
```

### 3. Consistencia numérica (los 4 puntos críticos)
- **C02/C09**: `30% oferta / 70% confirmación` y `4 tramos × 25%` — ¿suman 100% sin doble conteo?
- **C04**: punto cero = **21:00 Argentina (00 UTC)**, abanico **9 niveles** (hasta ±1.00), paso **0.25**.
- **C05**: retrocesos **50/61/78** y extensiones **50/100/150/200**; en **bajista** al inverso.
  Verificá con `min=56760, max=75518`: retrocesos esperados **66139,00 / 63925,56 / 60774,21**.
- **C11**: riesgo = confianza × tope **5%**, y **nunca** puede superar 5%.

### 4. Integridad de E1 y de los artefactos
```bash
python3 -B daily_pilot/knowledge/verify_integrity.py
python3 -B daily_pilot/knowledge/sellado_integridad.py
```
Verificá `store.db` = 42 vídeos / 34.061 cues / 6.831 claims y que `.control.json` cierre.

### 5. Líneas de separación (lo que **NO** debe estar mezclado)
- `PAPER_ONLY=true` en `risk_manager/risk_manager.py` y `core/allocacion.py` — ¿se respeta?
- El **sistema viejo** (Harness/CHIEF/Quantfury/Telegram) debe estar **fuera**: sin cron, sin
  LaunchAgents, sin `.env` activo. Verificá:
  - `crontab -l` → solo `rss_4h_scheduler.sh`
  - `launchctl list | grep -iE 'harness|chief|quantfury'` → **vacío**
  - `~/.hermes/cron/jobs.json` → los 3 jobs viejos con `enabled: false`
- **Backup**: `~/backups-limpieza-20261118/` (`harness_completo.tar.gz` 119 MB + hermes + LaunchAgents).

## Entregable

Un informe con:
1. **Veredicto** (¿el sistema es coherente?).
2. **Hallazgos** con `archivo:línea`, evidencia, reproducción, severidad.
3. **Puntos que el playbook afirma y el corpus no sostiene** (esto es lo más valioso).
4. **Lo que NO pudiste verificar** y por qué.

## Snapshot de referencia (2026-11-18T16:28:43Z)

```
store.db          6826b7e148fe13da   (42 / 34.061 / 6.831)
dashboard/index   271f5c67978fa71d
estado_hoy.json   8ffd071826c4c185
dashboard_data    d92faf246999b876
rama              crecetrader-limpio @ 6424381
tests             12 read-only OK · 14 integración OK · 0 fallos · FUENTES INTACTAS
```
