#!/usr/bin/env python3
"""Tests de C01 — jerarquia W > D > 4H. Sin red, PAPER_ONLY."""
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE / 'daily_pilot' / 'core'))
import jerarquia as J   # noqa: E402

OK = FALLO = 0


def caso(nombre, cond, detalle=''):
    global OK, FALLO
    if cond:
        OK += 1
        print(f'OK    | {nombre} | {detalle}')
    else:
        FALLO += 1
        print(f'FALLO | {nombre} | {detalle}')


A, B, R, N = J.ALCISTA, J.BAJISTA, J.RANGO, J.NO_DETERMINADO

# los 3 a favor
caso('3 alcistas -> long', J.determinar(A, A, A)['direccion'] == J.LONG)
caso('3 bajistas -> short', J.determinar(B, B, B)['direccion'] == J.SHORT)

# la correccion manda sobre el micro
caso('W alcista + D correccion -> correccion',
     J.determinar(A, J.CORRECCION, A)['direccion'] == J.CORRECCION)
caso('W alcista + 4h correccion -> correccion',
     J.determinar(A, A, J.CORRECCION)['direccion'] == J.CORRECCION)
caso('W alcista + D bajista -> correccion fuerte',
     J.determinar(A, B, A)['direccion'] == J.CORRECCION)

# sin tendencia macro no se opera
caso('W rango -> no operar', J.determinar(R, A, A)['direccion'] == J.NO_OPERAR)
caso('W no determinado -> no operar', J.determinar(N, A, A)['direccion'] == J.NO_OPERAR)

# la confianza es menor en correccion que en tendencia
caso('confianza correccion < tendencia',
     J.determinar(A, J.CORRECCION, A)['confianza'] < J.determinar(A, A, A)['confianza'])
caso('confianza rango = 0', J.determinar(R, A, A)['confianza'] == 0.0)

# sin D ni 4h: igual opera con el semanal
caso('solo W alcista -> long', J.determinar(A)['direccion'] == J.LONG)

# paper only
caso('paper_only', J.PAPER_ONLY is True)

print(f'\n{OK}/{OK + FALLO} pruebas OK')
sys.exit(1 if FALLO else 0)
