#!/usr/bin/env python3
"""Autoauditoria fija del piloto (read-only, no escribe en el repo vivo).

Corrida:
    python3 daily_pilot/scripts/autoauditoria.py

Que verifica:
  1. ancla (HEAD, rama, working tree)
  2. integridad de store.db (hashes y conteos)
  3. suite read-only y de integracion (en COPIA temporal)
  4. PAPER_ONLY y ausencia de llamadas de ejecucion / claves
  5. dash: paneles, pares, avisos
  6. metodo: firma, hash del playbook, C01-C12
  7. pares de Quantfury: que todos tengan datos

Sale con un veredicto y una tabla de hallazgos. No modifica nada.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
PILOT = BASE / 'daily_pilot'
PY = sys.executable

OK = FALLO = 0
HALLAZGOS = []


def caso(nombre, cond, detalle=''):
    global OK, FALLO
    if cond:
        OK += 1
        print(f'OK    | {nombre} | {detalle}')
    else:
        FALLO += 1
        HALLAZGOS.append((nombre, detalle))
        print(f'FALLO | {nombre} | {detalle}')


def sh(cmd, cwd=BASE, timeout=300):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    return r.returncode, (r.stdout or '') + (r.stderr or '')


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


# ---------------------------------------------------------------- 1. ancla
print('=== 1 · ANCLA ===')
rc, out = sh(['git', 'rev-parse', 'HEAD'])
head = out.strip()
rc2, rama = sh(['git', 'branch', '--show-current'])
rc3, st = sh(['git', 'status', '--short'])
caso('git_head', rc == 0 and head, head[:12])
caso('rama', rama.strip() == 'crecetrader-limpio', rama.strip())
# el dashboard y las velas son DERIVADOS: cambian al regenerar. Lo que no debe
# aparecer es codigo, tests, playbook ni store.
derivados = ('dashboard/', 'datos/velas/')
sucio = [l for l in st.splitlines() if not any(d in l for d in derivados)]
caso('working_tree_solo_derivados', not sucio, '; '.join(sucio)[:80])

# ------------------------------------------------------- 2. integridad store
print('\n=== 2 · INTEGRIDAD DEL STORE ===')
rc, out = sh([PY, str(PILOT / 'knowledge' / 'verify_integrity.py')])
caso('store_integridad', 'RESULTADO: OK' in out, out.strip().splitlines()[-1][:70] if out.strip() else '')
m = re.search(r'videos/cues/claims\s*:\s*([\d/]+)', out)
caso('store_conteos', bool(m), m.group(1) if m else 'sin conteos')

# --------------------------------------------------------------- 3. suites
print('\n=== 3 · SUITES ===')
rc, out = sh([PY, str(PILOT / 'tests' / 'run_all.py')])
caso('suite_readonly', '0 FALLO' in out, out.strip().splitlines()[-1][:60])

tmp = Path(tempfile.mkdtemp())
try:
    for item in PILOT.rglob('*'):
        if item.is_file() and '__pycache__' not in str(item) and '.bak-' not in str(item):
            rel = item.relative_to(BASE)
            dst = tmp / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, dst)
    rc, out = sh([PY, 'daily_pilot/tests/run_all.py', '--integracion'], cwd=tmp, timeout=600)
    caso('suite_integracion', '0 FALLO' in out, out.strip().splitlines()[-1][:60])
finally:
    shutil.rmtree(tmp, ignore_errors=True)

# ------------------------------------------------------- 4. PAPER_ONLY y claves
print('\n=== 4 · PAPER_ONLY / EJECUCION ===')
cod = ''
for p in PILOT.rglob('*.py'):
    if '__pycache__' in str(p):
        continue
    if p.name == 'autoauditoria.py':     # no auditarse a si mismo
        continue
    cod += p.read_text(errors='ignore')
caso('paper_only_false', 'PAPER_ONLY = False' not in cod and 'PAPER_ONLY=False' not in cod, '')
caso('sin_llamadas_ejecucion',
     not re.search(r'create_order|place_order|new_order|futures_create|send_order', cod), '')
caso('sin_claves', not re.search(r'(api[_-]?key|secret[_-]?key)\s*=\s*[\'"][A-Za-z0-9]{16,}', cod), '')

# --------------------------------------------------------------- 5. dash
print('\n=== 5 · DASH ===')
html = (PILOT / 'dashboard' / 'index.html').read_text()
caso('dash_existe', len(html) > 5000, f'{len(html)} B')
for s in ('MERCADO REAL', 'PROBABILIDAD POR PAR', 'RISK MANAGER', 'VELAS REALES',
          'CONCORDANCIA', 'ESTRATEGIA VISIBLE', 'PAPER ONLY', 'NO ES UNA ORDEN'):
    caso(f'dash_{s[:18]}', s in html, '')
caso('dash_sin_orden', 'OPERACIÓN PROPUESTA' not in html and 'PLAN DE TRADING' not in html, '')
caso('dash_autocontenido', 'fetch(' not in html and not re.search(r'src="http', html), '')

# --------------------------------------------------------------- 6. metodo
print('\n=== 6 · METODO / FIRMA ===')
pb = PILOT / 'metodo' / 'playbook_v0.1.md'
caso('playbook_existe', pb.exists(), f'{len(pb.read_text())} B')
firma = PILOT / 'metodo' / 'FIRMA_C01_C12.md'
ftxt = firma.read_text() if firma.exists() else ''
h_actual = sha(pb)
caso('firma_anclada', h_actual in ftxt, h_actual[:12])
caso('firma_12_reglas', all(f'C{i:02d}' in ftxt for i in range(1, 13)), '')

# --------------------------------------------------------------- 7. pares
print('\n=== 7 · PARES DE QUANTFURY ===')
sys.path.insert(0, str(PILOT / 'scripts'))
sys.path.insert(0, str(PILOT / 'core'))
import importlib.util
spec = importlib.util.spec_from_file_location('gen', PILOT / 'scripts' / 'generar_dashboard_v5.py')
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)
caso('pares_cantidad', len(gen.PARES) >= 30, f'{len(gen.PARES)} pares')
sin_datos = []
for par in gen.PARES:
    from velas import velas as _v
    r = _v(par, '1d', limite=5)
    if 'error' in r or not r['velas']:
        sin_datos.append(par)
caso('pares_con_datos', not sin_datos, ', '.join(sin_datos) or 'todos')
caso('ftm_es_sonic', 'SUSDT' in gen.PARES and 'FTMUSDT' not in gen.PARES, 'FTM -> S (Sonic)')
caso('ton_presente', 'TONUSDT' in gen.PARES, '')

# --------------------------------------------------------------- veredicto
print('\n' + '=' * 60)
print(f'RESULTADO: {OK} OK · {FALLO} FALLO')
if HALLAZGOS:
    print('\nHALLAZGOS:')
    for n, d in HALLAZGOS:
        print(f'  - {n} {("| " + d) if d else ""}')
print('=' * 60)
sys.exit(1 if FALLO else 0)
