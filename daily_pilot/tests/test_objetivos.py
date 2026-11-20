#!/usr/bin/env python3
"""Tests de objetivos y toma parcial (C09, Francisco). Sin red, PAPER_ONLY.

Formula corregida 2026-11-20: extension = minimo + rango*e (alcista).
Con e=1 el nivel cae EXACTAMENTE en el maximo; e>1 queda por encima.
"""
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE / 'daily_pilot' / 'core'))
import objetivos as O

OK = FALLO = 0


def caso(nombre, cond, detalle=''):
    global OK, FALLO
    if cond:
        OK += 1
        print(f'OK    | {nombre} | {detalle}')
    else:
        FALLO += 1
        print(f'FALLO | {nombre} | {detalle}')


MIN, MAX, ENTRADA = 56760.0, 75518.0, 64000.0
RANGO = MAX - MIN

# 1. objetivos = extensiones de C05 (0.5, 1, 1.25, 1.5, 1.75, 2, 3)
p = O.plan(ENTRADA, MIN, MAX)
caso('siete_objetivos', len(p['objetivos']) == 7, str(p['objetivos']))
caso('ext_1_es_el_maximo', abs(p['objetivos'][1] - MAX) < 0.01, str(p['objetivos'][1]))
caso('ext_125_arriba', p['objetivos'][2] > MAX, str(p['objetivos'][2]))
caso('ext_150', abs(p['objetivos'][3] - (MIN + RANGO * 1.5)) < 0.01, str(p['objetivos'][3]))
caso('ext_300', abs(p['objetivos'][6] - (MIN + RANGO * 3.0)) < 0.01, str(p['objetivos'][6]))
caso('crecientes', p['objetivos'] == sorted(p['objetivos']))

# 2. VALIDACION con la captura real de BNB (min 537.81 / max 808.24)
pbnb = O.plan(534.82, 537.81, 808.24)
caso('bnb_ext100_es_maximo', abs(pbnb['objetivos'][1] - 808.24) < 0.01, str(pbnb['objetivos'][1]))
caso('bnb_ext125_captura', abs(pbnb['objetivos'][2] - 876.16) < 1.0, str(pbnb['objetivos'][2]))

# 3. bajista: a la inversa (del maximo hacia abajo)
pb = O.plan(ENTRADA, MIN, MAX, direccion='bajista')
caso('bajista_ext1_es_el_minimo', abs(pb['objetivos'][1] - MIN) < 0.01, str(pb['objetivos'][1]))
caso('bajista_ordenada', pb['objetivos'] == sorted(pb['objetivos'], reverse=True), str(pb['objetivos']))
caso('bajista_ext_2_por_debajo', pb['objetivos'][2] <= MIN, str(pb['objetivos']))
caso('bajista_todos_arriba_del_min_3', all(v >= (MIN - RANGO*3) for v in pb['objetivos']), str(pb['objetivos']))

# 4. toma parcial
caso('toma_parcial', p['toma'] == 'parcial')
caso('suma_100', abs(sum(p['tramos_pct']) - 1.0) < 1e-5, str(sum(p['tramos_pct'])))
caso('secuencia_suma_100', abs(sum(x['tramo_pct'] for x in p['secuencia']) - 1.0) < 1e-5, str(sum(x['tramo_pct'] for x in p['secuencia'])))
caso('stop_be_primer', p['secuencia'][0]['accion_stop'] == 'break_even', str(p['secuencia'][0]))

# 5. proximo objetivo
caso('proximo_80000', O.proximo(p['objetivos'], 80000.0)['objetivo'] == 80207.5, str(O.proximo(p['objetivos'], 80000.0)))
caso('proximo_ya_pasados', O.proximo(p['objetivos'], 200000.0) is None)

# 6. validacion
try:
    O.plan(ENTRADA, MAX, MIN)
    caso('min>max_rechazado', False, 'no lanzo error')
except ValueError:
    caso('min>max_rechazado', True)

# 7. paper only
caso('paper_only', p.get('paper_only') is True and O.PAPER_ONLY is True)

print(f'\n{OK}/{OK + FALLO} pruebas OK')
sys.exit(1 if FALLO else 0)
