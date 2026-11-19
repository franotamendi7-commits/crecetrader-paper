# PROMPT DE VERIFICACIÓN — ¿los fixes están bien y no hay errores?

> Pegá esto en DeepSeek. **Read-only.** Verificá los cambios de la auditoría anterior.
> Si algo **no** se sostiene, decilo con `archivo:línea` y una reproducción.

---

## Rol

Verificador **read-only**. Ya auditaste este sistema y encontraste P0-1, P0-3, P1-1 y P1-8.
**Ahora comprobá si los fixes son reales** o si son maquillaje.

- **No** modifiques nada.
- **`sellado_integridad.py` ESCRIBE** — no lo corras.
- **`run_all.py --integracion` escribe el dashboard** — corral

o en copia si querés.
- Todo hallazgo: **archivo:línea · evidencia · reproducción**.

## Snapshot

```
commit            7c36cab
rama              crecetrader-limpio
store.db          24e5dd246c8be39421d3f9c3643d599b55152d37568af34df8b290874ccf8876
dashboard/index   <correr shasum despues de regenerar>
precios.py        3c77fe7983a180a87ad4a4da277d6c2663ebd7539131bbec80ab979373104128
run_all.py        df7afe20787e475d6d7335bfbeaff5ae3474e2e09a520cc75613789bd5e0ae0d
```

```bash
cd /Users/franciscootamendi/YouTubeTradingAgent
git rev-parse HEAD
shasum -a 256 daily_pilot/knowledge/store.db daily_pilot/core/precios.py daily_pilot/tests/run_all.py
```

---

## Los 4 fixes a verificar

### F-1 (P0-1) · La suite read-only ya NO escribe
**Afirmación**: `test_dashboard_v4.py` salió de `HERMETICOS` y está en `INTEGRACION`.
Verificá:
```bash
grep -n "test_dashboard_v4" daily_pilot/tests/run_all.py
shasum -a 256 daily_pilot/dashboard/index.html
python3 -B daily_pilot/tests/run_all.py ; echo "exit=$?"
shasum -a 256 daily_pilot/dashboard/index.html
```
**Es real si**: el hash es **idéntico** y el exit es **0** (FUENTES INTACTAS).

### F-2 (P0-3) · El precio ya no viene del video del 16-11
**Afirmación**: `informe_dia.py` saca el precio del **último video**, o dice NO_DISPONIBLE.
Verificá:
```bash
python3 - <<'EOF'
import json
i=json.load(open('daily_pilot/datos/informe_hoy.json'))
print('video:', i['video_id'])
print('precio:', i.get('precio_referencia'))
print('procedencia:', i.get('precio_procedencia'))
EOF
grep -n "dashboard_data" daily_pilot/scripts/informe_dia.py || echo "NO hereda del viejo"
```
**Es real si**: la procedencia dice el **último video** y **no** hay lectura de `dashboard_data.json`.

### F-3 (P1-1) · El dashboard no inventa la decisión
**Afirmación**: fuera `LONG`, `100%`, `5%`, `OPERACIÓN PROPUESTA`.
Verificá:
```bash
python3 -B daily_pilot/scripts/generar_dashboard_v4.py
grep -c "OPERACIÓN PROPUESTA\|PLAN DE TRADING\|alta (100%)" daily_pilot/dashboard/index.html
grep -o "NIVELES MENCIONADOS\|NO ES UNA ORDEN" daily_pilot/dashboard/index.html | sort -u
```
**Es real si**: 0 ocurrencias de lo hardcodeado y está «NIVELES MENCIONADOS».

### F-4 (P1-8) · Parser determinista de precios
**Afirmación**: `core/precios.py` resuelve el separador de miles.
Verificá:
```bash
python3 - <<'EOF'
import sys; sys.path.insert(0,'daily_pilot/core')
from precios import parsear_precio
for s, esperado in [('78.580',78580),('75.471',75471),('65,520',65520),('2,286',2286),('1.780',1780)]:
    v=parsear_precio(s); print(s, v, 'OK' if v==esperado else 'FALLO')
EOF
grep -n "precios_de_texto" daily_pilot/scripts/informe_dia.py
```
**Es real si**: los 5 casos dan el número entero y `informe_dia` usa el parser.

---

## Además: ¿no hay errores?

### A. Suite completa
```bash
python3 -B daily_pilot/tests/run_all.py
python3 -B daily_pilot/tests/run_all.py --integracion
```
**Es real si**: `0 FALLO` y **FUENTES INTACTAS** en ambos.

### B. Idempotencia del dashboard
```bash
shasum -a 256 daily_pilot/dashboard/index.html
python3 -B daily_pilot/scripts/generar_dashboard_v4.py
shasum -a 256 daily_pilot/dashboard/index.html
```
**Es real si**: el hash **no cambia** (antes dió MODIFICADAS por el timestamp).

### C. Integridad de E1
```bash
python3 -B daily_pilot/knowledge/verify_integrity.py
```

### D. Autocontención
```bash
grep -c "fetch(" daily_pilot/dashboard/index.html
grep -c 'src="http' daily_pilot/dashboard/index.html
```

### E. Lo que DEBE quedar abierto (no lo des por cerrado)
- **P0-2** (firma de las 12 reglas) — depende de Francisco.
- **P1-2** (Manager confianza 1.0) — **sin fix**.
- **P1-3** (C07 corrección→RANGO), **P1-4** (C04 dólares), **P1-5** (C09 solo alcista),
  **P1-6** (C10 sin respaldo), **P1-7** (conteos del playbook), **P2**.
- **P1-9** (LaunchAgent): el huérfano está **muerto**, pero el job en memoria
  sigue apuntando al script viejo — falta recargar el plist.

## Entregable

1. Por cada fix (F-1..F-4): **REAL** o **FALSO**, con la reproducción.
2. Por cada check (A..E): resultado real.
3. **Hallazgos nuevos**, si aparecen.
4. Frase final: ¿el sistema ya **no miente** en el dashboard?
