#!/usr/bin/env python3
"""Tests del parser de precios (core/precios.py). Sin red, PAPER_ONLY."""
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE / 'daily_pilot' / 'core'))
from precios import parsear_precio, precios_de_texto

OK = FALLO = 0


def caso(nombre, cond, detalle=''):
    global OK, FALLO
    if cond:
        OK += 1
        print(f'OK    | {nombre} | {detalle}')
    else:
        FALLO += 1
        print(f'FALLO | {nombre} | {detalle}')


# 1. separador de miles
caso('78.580 -> 78580', parsear_precio('78.580') == 78580.0)
caso('75.471 -> 75471', parsear_precio('75.471') == 75471.0)
caso('65,520 -> 65520', parsear_precio('65,520') == 65520.0)
caso('2,286 -> 2286', parsear_precio('2,286') == 2286.0)
caso('1.780 -> 1780', parsear_precio('1.780') == 1780.0)
caso('64.620 -> 64620', parsear_precio('64.620') == 64620.0)

# 2. decimales reales
caso('123 -> 123', parsear_precio('123') == 123.0)
caso('1.209,5 -> 1209.5', parsear_precio('1.209,5') == 1209.5, str(parsear_precio('1.209,5')))
caso('78.580,50 -> 78580.5', parsear_precio('78.580,50') == 78580.5, str(parsear_precio('78.580,50')))

# 3. basura
caso('vacio None', parsear_precio('') is None)
caso('None None', parsear_precio(None) is None)
caso('texto None', parsear_precio('abc') is None)

# 4. extraccion de un texto
ps = precios_de_texto('el precio es 75.471 y tambien 65,520; el 1.209,5 es volumen')
caso('extrae 3 precios', len(ps) == 3, str(ps))
caso('no trae <1000', all(p > 1000 for p in ps), str(ps))

print(f'\n{OK}/{OK + FALLO} pruebas OK')
sys.exit(1 if FALLO else 0)
