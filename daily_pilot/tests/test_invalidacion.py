#!/usr/bin/env python3
"""Tests de invalidacion (C08, Francisco). Sin red, PAPER_ONLY."""
import sys
from pathlib import Path

BASE = Path('/Users/franciscootamendi/YouTubeTradingAgent')
sys.path.insert(0, str(BASE / 'daily_pilot' / 'core'))
import invalidacion as I

OK = FALLO = 0


def caso(nombre, cond, detalle=''):
    global OK, FALLO
    if cond:
        OK += 1
        print(f'OK    | {nombre} | {detalle}')
    else:
        FALLO += 1
        print(f'FALLO | {nombre} | {detalle}')


# 1. se esperaba cambio y no ocurrio -> INVALIDADO
r = I.evaluar(True, False, False)
caso('invalidado', r['estado'] == 'INVALIDADO', r['motivo'])
caso('cerrar_posicion', r['accion'] == 'CERRAR POSICION', r['accion'])
caso('esperar_nuevo_escenario', r['esperar_nuevo_escenario'] is True)

# 2. ocurrio -> vigente
r2 = I.evaluar(True, True, False)
caso('vigente', r2['estado'] == 'VIGENTE' and r2['accion'] == 'MANTENER', r2['motivo'])

# 3. no se esperaba cambio -> no aplica
r3 = I.evaluar(False, False, False)
caso('sin_cambio_esperado', r3['estado'] == 'SIN_CAMBIO_ESPERADO', r3['motivo'])

# 4. invalidado pero ya hay escenario nuevo claro -> no hay que esperar
r4 = I.evaluar(True, False, True)
caso('escenario_nuevo_claro', r4['estado'] == 'INVALIDADO' and r4['esperar_nuevo_escenario'] is False, r4['motivo'])

# 5. la invalidacion NO es perder un nivel (es no-ocurrencia del cambio)
caso('no_es_perder_nivel', 'pierde' not in r['motivo'].lower(), r['motivo'])

# 6. paper only
caso('paper_only', r['paper_only'] is True and I.PAPER_ONLY is True)

print(f'\n{OK}/{OK + FALLO} pruebas OK')
sys.exit(1 if FALLO else 0)
