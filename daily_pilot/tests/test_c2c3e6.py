#!/usr/bin/env python3
"""Pruebas C2 (relaciones) + C3/E5 (escenarios) + E6 (temporalidad) + seguimiento."""
import json
import subprocess
import sys
from pathlib import Path

BASE = Path('/Users/franciscootamendi/YouTubeTradingAgent')
PY = sys.executable   # reproducible fuera de la maquina de Hermes
OK = FALLO = 0


def caso(nombre, cond, detalle=''):
    global OK, FALLO
    if cond:
        OK += 1
        print(f'OK    | {nombre} | {detalle}')
    else:
        FALLO += 1
        print(f'FALLO | {nombre} | {detalle}')


def run(p):
    return subprocess.run([PY, str(BASE / p)], capture_output=True, text=True, timeout=300)


# --- C2 ---
r = run('daily_pilot/relaciones/relaciones.py')
caso('c2_ejecuta', r.returncode == 0, r.stdout.strip()[:70])
d = json.loads((BASE / 'daily_pilot/relaciones/relaciones.json').read_text())
caso('c2_repetidos', len(d['niveles_repetidos']) >= 3, len(d['niveles_repetidos']))
caso('c2_descarta_falsos', d['niveles_descartados'] > 0, d['niveles_descartados'])
caso('c2_sin_anios', all(x['nivel_aproximado'] not in range(1990, 2036)
                         for x in d['niveles_repetidos']))
caso('c2_linea_tiempo', len(d['linea_de_tiempo']) >= 10, len(d['linea_de_tiempo']))

# --- C3/E5 ---
r = run('daily_pilot/escenarios/construir_escenarios.py')
caso('c3_ejecuta', r.returncode == 0, r.stdout.strip()[:70])
h = json.loads((BASE / 'daily_pilot/escenarios/historial.json').read_text())
v = json.loads((BASE / 'daily_pilot/escenarios/vigentes.json').read_text())
caso('c3_historial', sum(len(x) for x in h['instrumentos'].values()) >= 20,
     sum(len(x) for x in h['instrumentos'].values()))
caso('c3_vigentes', sum(len(x) for x in v['vigentes'].values()) >= 5,
     sum(len(x) for x in v['vigentes'].values()))
caso('c3_no_borra', len(h['instrumentos']) >= 3, list(h['instrumentos']))

# --- E6 ---
r = run('daily_pilot/scripts/anadir_temporalidad.py')
caso('e6_ejecuta', r.returncode == 0, r.stdout.strip().splitlines()[0] if r.stdout else '')
import sqlite3
c = sqlite3.connect(f"file:{BASE / 'daily_pilot/knowledge/store.db'}?mode=ro", uri=True)
tipos = dict(c.execute('SELECT temporalidad, COUNT(*) FROM claims GROUP BY temporalidad').fetchall())
c.close()
caso('e6_clasificados', sum(tipos.values()) >= 6831, str(tipos))   # P2: robusto, no exacto
caso('e6_tiene_4h', tipos.get('4h', 0) > 0, tipos.get('4h'))

# --- seguimiento ---
sys.path.insert(0, str(BASE / 'daily_pilot/seguimiento'))
import seguimiento as SG
s = SG.resumen()
caso('seg_vacio', s['n_registros'] == 0 and s['paper_only'] is True, s['n_registros'])
caso('seg_estados', set(s['por_estado']) == set(SG.ESTADOS), len(s['por_estado']))

print(f'\n{OK}/{OK + FALLO} pruebas OK')
sys.exit(1 if FALLO else 0)
