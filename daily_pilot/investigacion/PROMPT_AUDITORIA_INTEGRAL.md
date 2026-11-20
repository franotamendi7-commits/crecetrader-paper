# PROMPT — Auditoría integral del piloto CreceTrader (antes del dash)

> Copiá **TODO** este archivo en DeepSeek. Es de **solo lectura**: no debe
> modificar nada. Tiene que verificar y entregar evidencia.

---

## 0 · Contexto

Repo: `/Users/franciscootamendi/YouTubeTradingAgent`
Rama auditada: **`crecetrader-limpio`** · HEAD **`a3b7c0c`** · working tree limpio.

Es un piloto **PAPER_ONLY** (no opera dinero real). Reglas C01–C12 del método
CreceTrader, **firmadas por Francisco** el 2026-11-19 (`daily_pilot/metodo/FIRMA_C01_C12.md`).

**Verdad del usuario: «NO CREER. PROBAR.»** — si el código afirma algo, hay que
ejecutarlo y comprobar que es cierto.

## 1 · Prohibiciones (innegociables)

- **NO modifiques nada.** Ni código, ni config, ni skills, ni modelos, ni providers.
- **NO corras el pipeline de videos** (`extraer_claims.py`, `vision_lote.py`, `importar_nuevos.py`).
- **NO regeneres `store.db`** ni `dashboard/index.html`.
- **NO uses servicios pagos, no descargues modelos, no uses Gemini.**
- **NO envíes datos a servicios externos.**
- Si un chequeo exige escribir, hacelo en una **copia temporal**:
  ```bash
  TMP=$(mktemp -d)
  rsync -a --exclude=.git --exclude=__pycache__ \
    /Users/franciscootamendi/YouTubeTradingAgent/ "$TMP"/
  ```

## 2 · Ancla (verificá primero, si no coincide, PARÁ y avisá)

```bash
cd /Users/franciscootamendi/YouTubeTradingAgent
git rev-parse HEAD                     # debe ser a3b7c0c
git branch --show-current              # crecetrader-limpio
git status --short                     # vacío
shasum -a 256 daily_pilot/dashboard/index.html
shasum -a 256 daily_pilot/knowledge/store.db
```

## 3 · Integridad y suite

```bash
cd /Users/franciscootamendi/YouTubeTradingAgent
~/.hermes/hermes-agent/venv/bin/python3 daily_pilot/knowledge/verify_integrity.py
~/.hermes/hermes-agent/venv/bin/python3 daily_pilot/tests/run_all.py
~/.hermes/hermes-agent/venv/bin/python3 daily_pilot/tests/run_all.py --integracion
```

**Esperado:** `verify_integrity` → OK · `run_all` → **15 OK · 0 FALLO · FUENTES
INTACTAS** · `--integracion` → **17 OK · 0 FALLO**.
Si la cuenta de tests difiere, **listá cuál falta** y por qué.

**Criterio:** la suite es read-only. Si `run_all.py` escribe el dashboard o el
store, es **P0**.

## 4 · Falsedades (lo más importante)

Buscá strings en el código que **afirmen algo que el código no hace**, y
verificalo ejecutando:

```bash
cd /Users/franciscootamendi/YouTubeTradingAgent
grep -rn "C01-C12\|aplica C0\|el motor\|RECOMPRA\|OPERACIÓN PROPUESTA\|PLAN DE TRADING\|LONG\|SHORT" daily_pilot/ \
  --include=*.py --include=*.html --include=*.json --include=*.md
grep -rn "confianza.*100\|riesgo 5%\|alta (" daily_pilot/ --include=*.py --include=*.html --include=*.json
grep -rn "direccion': 'alcista'\|direccion.*=.*'alcista'" daily_pilot/ --include=*.py
```

**Conocidos (verificar que sigan resueltos):**
- `daily_pilot/scripts/informe_dia.py` no debe afirmar «El motor aplica C01-C12»
  (el pipeline no ejecuta ese motor) ni forzar `direccion='alcista'`.
- `daily_pilot/dashboard/index.html` no debe tener `LONG`, `100%`, `OPERACIÓN
  PROPUESTA`, `PLAN DE TRADING`.
- `daily_pilot/datos/informe_hoy.json` no debe tener `direccion: alcista` forzada
  ni el string falso.

**Criterio:** cualquier afirmación falsa = **P0**.

## 5 · PAPER_ONLY

```bash
grep -rn "PAPER_ONLY" daily_pilot/core/*.py | head -30
grep -rn "PAPER_ONLY\s*=\s*False" daily_pilot/ --include=*.py
grep -rn "create_order\|place_order\|new_order\|futures_create\|send_order\|api_key\|secret" \
  daily_pilot/ --include=*.py --include=*.pine --include=*.json
```

**Criterio:** todo módulo de decisión debe tener `PAPER_ONLY = True`. Cualquier
llamada a API de ejecución = **P0**. Si aparece una clave/token, escribí
`[REDACTED]` y avisá.

## 6 · Consistencia del método (motor Python ↔ capturas ↔ Pine)

**6.1** Los 12 niveles contra las capturas de BNB (2026-11-20):

```bash
~/.hermes/hermes-agent/venv/bin/python3 daily_pilot/tests/test_capturas_tradingview.py
```

**Esperado 19/19.** Verificá en el código que la fórmula sea
`nivel = minimo + rango * r` (alcista) y que `RETROCESOS` incluya **0,61** (no 0,618).

**6.2** El tramo del ciclo en los 3 TF:

```bash
~/.hermes/hermes-agent/venv/bin/python3 -c "
import sys; sys.path.insert(0,'daily_pilot/core')
from velas import velas; from tramos import tramo_ciclo
for tf in ['1w','1d','4h']:
    v=velas('BNBUSDT',tf,limite=500,forzar=True)['velas']
    r=tramo_ciclo(v)
    print(tf, round(r['minimo'],2), '->', round(r['maximo'],2))
"
```

**Esperado:** `1w 530.00 -> 1375.11` · `1d 530.00 -> 809.99` · `4h 530.00 -> 809.99`
(nótese que el piso es el de **hoy**, puede diferir del de la captura del 20/11 16:36).

**6.3** El Pine: `daily_pilot/tradingview/crecetrader_niveles.pine` — verificar que
el `for` del piso sea `k = 0 to nBarras` con tope **4999** (un `for k = maxBar to
bar_index` con `low[k]` es **P0**: Pine acepta 0..5000).

## 7 · Cobertura C01–C12

Para cada regla, indicá: **¿está implementada? ¿tiene test? ¿el test pasa?**

| Regla | Módulo |
|---|---|
| C01 | `core/regimen.py` |
| C02 | `core/allocacion.py` |
| C03 | `core/confluencia.py` |
| C04 | `core/intradia.py` |
| C05 | `core/zonas.py`, `core/tramos.py`, `core/objetivos.py` |
| C06 | `core/liquidez.py` |
| C07 | `core/regimen.py` |
| C08 | `core/invalidacion.py` |
| C09 | `core/objetivos.py` |
| C10 | `core/escenarios.py` |
| C11 | `tests/test_c11_cruzado.py` |
| C12 | `core/manager.py` |

Cotejá contra `daily_pilot/metodo/playbook_v0.1.md`. **Marcá toda regla que el
código no implemente fielmente.**

## 8 · Pendientes conocidos (confirmar que siguen abiertos)

1. **`daily_pilot/tradingview/README.md` → PENDIENTE**: en 4H el indicador dibuja
   los niveles de 1D. No investigado (pedido de Francisco).
2. **Dash**: `daily_pilot/dashboard/index.html` muestra un precio de BTC que puede
   no ser el real y un solo par. Francisco pidió: solo el **último vídeo** y **sin
   gráfico inventado**.
3. **`migrate.py`** no actualiza filas `videos` ya existentes.
4. **Binance/Quantfury** sin conectar. **B4/B5** sin anotadores.

## 9 · Entregable

Un informe con:

1. **Veredicto** (1 párrafo): es apto para pasar al dash, o no, y por qué.
2. **Tabla de hallazgos** con columnas:
   `ID | Severidad (P0/P1/P2) | Archivo:línea | Qué dice el código | Qué pasa | Evidencia (comando + salida)`
3. **Chequeos que pasaron** (con la salida real, no «OK»).
4. **Lo que NO pudiste verificar** y por qué.
5. **Confirmación** de que no modificaste nada (salida de `git status --short` y
   los dos `shasum` de la sección 2, antes y después).

**Reglas:** no especular. Si no lo comprobaste, escribí «no verificado». No
mezcles opinión con evidencia.
