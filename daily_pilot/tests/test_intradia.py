#!/usr/bin/env python3
"""Tests de niveles intradia (C04, Francisco). Sin red, PAPER_ONLY."""
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE / 'daily_pilot' / 'core'))
import intradia as I

OK = FALLO = 0


def caso(nombre, cond, detalle=''):
    global OK, FALLO
    if cond:
        OK += 1
        print(f'OK    | {nombre} | {detalle}')
    else:
        FALLO += 1
        print(f'FALLO | {nombre} | {detalle}')


# 1. VALIDACION CON LA CAPTURA REAL (BTC 2026-11-20, cierre 61.910)
a = I.abanico(61910.0)
n = [round(x, 0) for x in a['niveles']]
caso('punto_cero', a['punto_cero'] == 61910.0, str(a['punto_cero']))
caso('ancho_fijo_1000', a['ancho_unidad'] == 1000.0, str(a['ancho_unidad']))
caso('nivel_+619', 62529.0 in n, str(n))
caso('nivel_+383', 62293.0 in n, str(n))
caso('nivel_+237', 62147.0 in n, str(n))
caso('nivel_-236', 61674.0 in n, str(n))
caso('nivel_-383', 61527.0 in n, str(n))
caso('nivel_-619', 61291.0 in n, str(n))
caso('nivel_-929', 60981.0 in n, str(n))
caso('nivel_-1238', 60672.0 in n, str(n))

# 2. se resetea cada dia
b = I.resetear(61000.0)
caso('reset_nuevo_cierre', b['punto_cero'] == 61000.0, str(b['punto_cero']))
caso('reset_misma_amplitud', round(b['niveles'][-1] - b['niveles'][0]) == round(a['niveles'][-1] - a['niveles'][0]), str(b['niveles'][-1] - b['niveles'][0]))

# 3. no depende del precio (ancho fijo)
c = I.abanico(57000.0)
caso('ancho_independiente_del_precio', round(c['niveles'][-1] - c['niveles'][0]) == round(a['niveles'][-1] - a['niveles'][0]))
caso('proporciones_fibo', list(I.NIVELES) == [0.236, 0.382, 0.618, 0.929, 1.238], str(I.NIVELES))
caso('es_scalping', a['tipo'] == 'scalping' and a['confirmacion_4h_o_diario'] is False)
caso('paper_only', a['paper_only'] is True)
