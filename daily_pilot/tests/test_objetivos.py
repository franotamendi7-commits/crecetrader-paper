#!/usr/bin/env python3
"""Tests de objetivos y toma parcial (C09, Francisco). Sin red, PAPER_ONLY."""
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


# 1. cuatro objetivos = extensiones de C05
p = O.plan(64000.0, 56760.0, 75518.0)
caso('cuatro_objetivos', len(p['objetivos']) == 4, str(p['objetivos']))
caso('objetivo_50', p['objetivos'][0] == 84897.0, str(p['objetivos']))
caso('objetivo_100', p['objetivos'][1] == 94276.0, str(p['objetivos']))
caso('objetivo_150', p['objetivos'][2] == 103655.0, str(p['objetivos']))
caso('objetivo_200', p['objetivos'][3] == 113034.0, str(p['objetivos']))
caso('crecientes', p['objetivos'] == sorted(p['objetivos']))

# 2. toma parcial 25% x 4
caso('toma_parcial', p['toma'] == 'parcial')
caso('cuatro_tramos', p['tramos_pct'] == [0.25, 0.25, 0.25, 0.25], str(p['tramos_pct']))
caso('suma_100', abs(sum(p['tramos_pct']) - 1.0) < 1e-9)

# 3. stop a break even tras el primer objetivo
caso('stop_be_primer', p['secuencia'][0]['accion_stop'] == 'break_even', str(p['secuencia'][0]))
caso('stop_be_texto', 'break_even' in p['stop'], p['stop'])
caso('stop_be_solo_una_vez', [s['accion_stop'] for s in p['secuencia']].count('break_even') == 1)

# 4. secuencia completa
caso('secuencia_4', len(p['secuencia']) == 4)
caso('cada_tramo_25', all(s['tramo_pct'] == 0.25 for s in p['secuencia']))

# 5. proximo objetivo
caso('proximo_80000', O.proximo(p['objetivos'], 80000.0)['objetivo'] == 84897.0)
caso('proximo_ya_pasados', O.proximo(p['objetivos'], 200000.0) is None)
caso('proximo_distancia', O.proximo(p['objetivos'], 80000.0)['distancia_pct'] > 0)

# 6. validacion
try:
    O.plan(64000.0, 75518.0, 56760.0)
    caso('min>max_rechazado', False, 'no lanzó error')
except ValueError:
    caso('min>max_rechazado', True)

# 7. paper only
caso('paper_only', p['paper_only'] is True and O.PAPER_ONLY is True)

print(f'\n{OK}/{OK + FALLO} pruebas OK')
sys.exit(1 if FALLO else 0)
