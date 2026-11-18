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


# 1. abanico por defecto: 9 niveles (n=4, hasta +/-1.00)
a = I.abanico(64000.0)
caso('nueve_niveles', len(a['niveles']) == 9, len(a['niveles']))
caso('punto_cero_en_medio', a['niveles'][4] == 64000.0, str(a['niveles']))
caso('escala_025', a['niveles'][2] == 63999.5 and a['niveles'][6] == 64000.5, str(a['niveles']))
caso('incluye_100', 63999.0 in a['niveles'] and 64001.0 in a['niveles'], str(a['niveles']))
caso('incluye_075', 63999.25 in a['niveles'] and 64000.75 in a['niveles'], str(a['niveles']))

# 2. con n=3 -> 7 niveles (hasta +/-0.75)
b = I.abanico(64000.0, n=3)
caso('siete_niveles_n3', len(b['niveles']) == 7, len(b['niveles']))
caso('n3_sin_100', 64001.0 not in b['niveles'], str(b['niveles']))

# 3. se resetea cada dia
c = I.resetear(65000.0)
caso('reset_diario', c['precio_base'] == 65000.0 and c['niveles'][4] == 65000.0, str(c['precio_base']))

# 4. hora ancla 21
caso('hora_ancla_21', a['hora_ancla'] == 21 and I.HORA_ANCLA_UTC == 0, f"{a['hora_ancla']} / {I.HORA_ANCLA_UTC}UTC")

# 5. es scalping, NO confirmacion de 4h/daily
caso('es_scalping', a['tipo'] == 'scalping' and a['confirmacion_4h_o_diario'] is False)

# 6. paper only
caso('paper_only', a['paper_only'] is True and I.PAPER_ONLY is True)

print(f'\n{OK}/{OK + FALLO} pruebas OK')
sys.exit(1 if FALLO else 0)
