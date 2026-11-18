#!/usr/bin/env python3
"""Tests de confluencia (C03, Francisco). Sin red, PAPER_ONLY."""
import sys
from pathlib import Path

BASE = Path('/Users/franciscootamendi/YouTubeTradingAgent')
sys.path.insert(0, str(BASE / 'daily_pilot' / 'core'))
import confluencia as C

OK = FALLO = 0


def caso(nombre, cond, detalle=''):
    global OK, FALLO
    if cond:
        OK += 1
        print(f'OK    | {nombre} | {detalle}')
    else:
        FALLO += 1
        print(f'FALLO | {nombre} | {detalle}')


# 1. los 4 componentes -> LONG
r = C.evaluar(True, True, True, True)
caso('long_completo', r['senal'] == 'LONG', r['motivo'])
caso('componentes_trazables', len(r['componentes']) == 4, str(r['componentes']))

# 1b. H-10: sin zona de compra NO hay LONG (C10: se juntan precios calculados y zonas)
r_nz = C.evaluar(True, True, True, False)
caso('sin_zona_no_es_long', r_nz['senal'] != 'LONG', r_nz['motivo'])

# 2. 4H + niveles calculados, sin confirmacion diaria -> decision de entrada
r = C.evaluar(True, True, False, False)
caso('decision_entrada', r['senal'] == 'DECISION_ENTRADA', r['motivo'])  # sin zona: decision, no long

# 3. sin cambio de fase -> sin senal
r = C.evaluar(False, True, True, True)
caso('sin_cambio_fase_no_hay_senal', r['senal'] == 'SIN_SENAL', r['motivo'])

# 4. solo diario + zona -> sin senal (falta 4H)
r = C.evaluar(False, False, True, True)
caso('sin_4h_no_hay_senal', r['senal'] == 'SIN_SENAL', r['motivo'])

# 5. niveles calculados sin cambio de fase -> sin senal
r = C.evaluar(False, True, False, False)
caso('niveles_sin_fase', r['senal'] == 'SIN_SENAL', r['motivo'])

# 7. C03 secuencia exacta de giro ( Francisco )
caso('sec_correccion', C.secuencia(minimos_decrecientes=True) == 'CORRECCION')
caso('sec_rango', C.secuencia(rango=True) == 'RANGO')
caso('sec_ruptura', C.secuencia(ruptura=True) == 'RUPTURA')
caso('sec_no_confirmado', C.secuencia(ruptura=True, vela_verde_sobre_roja=True) == 'CAMBIO_NO_CONFIRMADO')
caso('sec_confirmado', C.secuencia(vela_verde_sobre_roja=True, maximos_crecientes=2) == 'CONFIRMADO')
caso('sec_un_maximo_no_basta', C.secuencia(vela_verde_sobre_roja=True, maximos_crecientes=1) == 'CAMBIO_NO_CONFIRMADO')
caso('sec_sin_estructura', C.secuencia() == 'SIN_ESTRUCTURA')

# 8. paper only
caso('paper_only', r['paper_only'] is True and C.PAPER_ONLY is True)

print(f'\n{OK}/{OK + FALLO} pruebas OK')
sys.exit(1 if FALLO else 0)
