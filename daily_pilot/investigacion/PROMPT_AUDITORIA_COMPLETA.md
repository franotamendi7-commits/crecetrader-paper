# PROMPT DE AUDITORÍA COMPLETA — YouTubeTradingAgent / CreceTrader

> Pegá esto en DeepSeek. **Read-only**: que no modifique nada.
> **Que audite TODO el código.** Hallazgos con `archivo:línea`, evidencia, reproducción y severidad.
> **No debe aprobar su propio trabajo.** Regla de Francisco: **NO CREER. PROBAR.**

---

## 0. Rol

Sos auditor **read-only** de un sistema que analiza videos de un canal de trading (CreceTrader)
y propone (nunca ejecuta) ideas de operación.

- **No** modifiques código, ni commits, ni `store.db`, `dashboard_data.json`, `estado_hoy.json`,
  `registro.json`, `informe_hoy.json`, ni `dashboard/index.html`.
- **`sellado_integridad.py` ESCRIBE.** No lo corras.
- **`run_all.py --integracion` ESCRIBE** (dashboard + E1). Correl

o en copia.
- Todo hallazgo: **archivo:línea · evidencia · reproducción · severidad (P0/P1/P2)**.
- Si el código está bien y el test pasa, **decilo**. Si el test miente, también.

## 1. Repositorio

- **Repo**: `https://github.com/franotamendi7-commits/harnesstata.git`
- **Rama**: `crecetrader-limpio`
- **Local**: `/Users/franciscootamendi/YouTubeTradingAgent`
- **Fecha**: 2026-11-18

---

## 2. Snapshot CONGELADO

> Verificar PRIMERO. Si `git rev-parse HEAD` no coincide, la auditoría es inválida.

```
commit            <completar con git rev-parse HEAD antes de auditar>
rama              crecetrader-limpio
store.db          <sha256>
dashboard/index   <sha256>
playbook          <sha256>
```

```bash
cd /Users/franciscootamendi/YouTubeTradingAgent
git rev-parse HEAD
shasum -a 256 daily_pilot/knowledge/store.db daily_pilot/dashboard/index.html \
              daily_pilot/metodo/playbook_v0.1.md
```

---

## 3. Qué auditar — **TODO el código**

Árbol (62 archivos `.py` bajo `daily_pilot/`):

```
daily_pilot/
  core/         confluencia, intradia, zonas, liquidez, regimen,
                invalidacion, objetivos, escenarios, allocacion, manager,
                signal_classifier, plan_classifier
  scripts/      daily_pilot, analizar_video, extraer_claims, importar_nocturno,
                importar_nuevos, reanalizar_tf, generar_dashboard_v4, informe_dia,
                motor_dia, leer_grafico, comparar_vision, zonas_reales,
                reconciliar_linaje, control_diario, sellado_integridad, verify_integrity
  risk_manager/ risk_manager.py
  metrics/      metrics.py, registrar_desde_rm.py
  knowledge/    store.py, migrate.py, verify_integrity.py
  metodo/       playbook_v0.1.md  (C01–C12)
  dashboard/    index.html
  tests/        15 suites + risk_manager/test_risk_manager.py
```

### Bloque A — Coherencia del método (playbook ↔ código ↔ corpus)
1. `metodo/playbook_v0.1.md`: las 12 reglas. ¿Cada regla tiene su implementación?
   ¿Alguna regla **no** está implementada o está implementada **al revés**?
2. Verificá **contra `store.db`** que las citas del playbook existan y digan lo afirmado:
   ```bash
   python3 - <<'EOF'
   import re, sqlite3, pathlib
   pb = pathlib.Path('daily_pilot/metodo/playbook_v0.1.md').read_text()
   pares = sorted(set(re.findall(r'`([A-Za-z0-9_-]{11})`\s+(\d{2}:\d{2}:\d{2}(?:\.\d+)?)', pb)))
   c = sqlite3.connect('file:daily_pilot/knowledge/store.db?mode=ro', uri=True)
   for v, s in pares:
       filas = c.execute("SELECT start,texto FROM claims WHERE video_id=? ORDER BY start",(v,)).fetchall()
       i = next((k for k,(st,_) in enumerate(filas) if st.startswith(s)), None)
       if i is None: print('FALTA', v, s); continue
       print('OK', v, s, '|', filas[i][1][:70])
   EOF
   ```
3. **Conteos**: el playbook declara un criterio de conteo. Verificá que los números sean
   reproducibles con ese criterio.

### Bloque B — El motor de reglas
Para cada módulo de `core/`: ¿la función hace lo que el playbook dice? ¿Los **tests** verifican
valores del **experto** o solo lo que el código produce?
Puntos críticos:
- **C02**: 30% oferta + 70% confirmación; solo los 5 pares en oferta; ¿la suma de tramos
  **nunca** supera el tope del activo?
- **C11**: **una sola fórmula** en `escenarios`, `risk_manager` y `manager` (`confianza × tope`).
- **C05**: retrocesos 50/61/78; extensiones 50/100/150/200; bajista al inverso.
- **C04**: 9 niveles ±0.25; punto cero = cierre 00 UTC (21 hs ARG).

### Bloque C — Los tests no mienten
```bash
python3 -B daily_pilot/tests/run_all.py            # read-only
python3 -B daily_pilot/tests/run_all.py --integracion
```
¿Los valores esperados en los tests coinciden con la definición del experto?
¿Algún test **siempre** pasa por construcción (ej. compara un hash consigo mismo)?

### Bloque D — Integridad y aislamiento
- `verify_integrity.py` → ¿cierra? ¿`.control.json` coincide?
- `run_all.py --integracion` en **copia** (los scripts usan `Path(__file__)`):
  ```bash
  TMP=$(mktemp -d); rsync -a --exclude=.venv --exclude=.git ./ "$TMP"/
  cd "$TMP" && python3 -B daily_pilot/tests/run_all.py --integracion
  ```
  ¿Escribe en la copia o en el repo vivo?
- `PAPER_ONLY=true` en `risk_manager` y `allocacion`: ¿se respeta?

### Bloque E — El dashboard
```bash
python3 -B daily_pilot/scripts/generar_dashboard_v4.py
```
- ¿Es autocontenido (0 fetch, 0 refs http)?
- ¿Muestra **solo el último video** y nunca el histórico?
- ¿**No** tiene datos inventados (velas simuladas, precios de pares sin feed)?
- ¿Los paneles dicen **NO DISPONIBLE** donde no hay datos?

### Bloque F — Límites declarados (lo más importante)
`daily_pilot/investigacion/LIMITES_CORPUS.md` afirma:
- niveles con TF: **15,3%**
- niveles con instrumento: **6,8%**
**Reproducilo** con `reanalizar_tf.py` y el script del informe. Si no da, es un **P0**.

### Bloque G — Separación de lo viejo
- `crontab -l` → solo `rss_4h_scheduler.sh`
- `launchctl list | grep -iE 'harness|chief'` → vacío
- `~/.hermes/cron/jobs.json` → los 3 jobs viejos `enabled: false`
- `~/.hermes/composer-pastes` → no existe (si existe, aclaralo)
- `~/Harness` → no existe (respaldado en `~/backups-limpieza-20261118`)
- `~/.hermes/.env` **existe** (tiene `NOUS_ACCESS_TOKEN`) — **no es un fallo**.

---

## 4. Entregable

1. **Veredicto** (¿el sistema es coherente y defendible?).
2. **Hallazgos** con `archivo:línea`, evidencia, reproducción, severidad.
3. **Afirmaciones que el corpus NO sostiene** (lo más valioso).
4. **Lo que NO pudiste verificar** y por qué.
5. **Qué hay que cambiar antes de operar en serio**.

## 5. Contexto que ya se sabe (para no repetir)

- **E1**: 102 vídeos · 105.275 cues · 18.562 claims.
- **Sin feed de mercado**: el precio es el del video.
- **Sensor visual**: `qwen3-vl:8b-instruct` local; ground truth de 19 frames anotados a mano.
- **No hay «precios calculados por plazo»**: el corpus no tiene TF (15,3%) ni instrumento (6,8%).
- **PAPER_ONLY**: el sistema propone, nunca ejecuta.
- **Sistema viejo** (Harness/CHIEF/Quantfury/Telegram/Discord) **fuera**, respaldado.

## 6. Expectativa honesta

El sistema **no** es un oráculo. Es: **transcripción fiel + lo que el canal dice con contexto +
un método (C01–C12) codificado + un sensor visual medido**. Si algo de eso no se sostiene,
**quiero saberlo**, no que me lo maquillen.
