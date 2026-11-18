#!/usr/bin/env python3
"""Tests de escenarios por confianza (C10, Francisco). Sin red, PAPER_ONLY."""
import sys
from pathlib import Path

BASE = Path('/Users/franciscootamendi/YouTubeTradingAgent')
sys.path.insert(0, str(BASE / 'daily_pilot' / 'core'))
import escenarios as E

OK = FALLO = 0


def caso(nombre, cond, detalle=''):
    global OK, FALLO
    if cond:
        OK += 1
        print(f'OK    | {nombre} | {detalle}')
    else:
        FALLO += 1
        print(f'FALLO | {nombre} | {detalle}')


# 1. 3 marcos (semanal+diario+4H) -> VALIDADO 100%
a = E.evaluar(3)
caso('tres_marcos_validado', a['escenario'] == 'VALIDADO', a['escenario'])
caso('confianza_100', a['confianza'] == 1.0, str(a['confianza']))
caso('riesgo_5pct', a['riesgo_sugerido'] == 0.05, str(a['riesgo_sugerido']))

# 2. 2 marcos -> VALIDADO 75%
b = E.evaluar(2)
caso('dos_marcos_validado', b['escenario'] == 'VALIDADO', b['escenario'])
caso('confianza_75', b['confianza'] == 0.75, str(b['confianza']))

# 3. 4H solo y contradicho -> MENOR FIABILIDAD, se puede tradear intradia
c = E.evaluar(1, contradicho=True)
caso('menor_fiabilidad', c['escenario'] == 'MENOR_FIABILIDAD', c['escenario'])
caso('tradear_intradia', c.get('tradear_intradia') is True, str(c))
caso('riesgo_bajado', c['riesgo_sugerido'] == 0.0125, str(c['riesgo_sugerido']))

# 4. correccion dentro de tendencia alcista -> CAUTELA
d = E.evaluar(2, correccion_dentro_de_tendencia=True)
caso('cautela', d['escenario'] == 'CAUTELA', d['escenario'])
caso('cautela_menos_riesgo', d['riesgo_sugerido'] == 0.0281, str(d['riesgo_sugerido']))

# 5. sin marcos -> rechazado
e = E.evaluar(0)
caso('rechazado', e['escenario'] == 'RECHAZADO' and e['riesgo_sugerido'] == 0.0)

# 6. stop y profit
caso('stop_bv', 'break even' in a['stop'], a['stop'])
caso('profit_zona_compra', 'zona de compra' in a['profit'], a['profit'])

# 7. nunca supera el tope 5%
for n in (1, 2, 3):
    r = E.evaluar(n)
    caso(f'riesgo_tope_{n}', r['riesgo_sugerido'] <= E.RIESGO_MAX, str(r['riesgo_sugerido']))

# 8. paper only
caso('paper_only', a['paper_only'] is True and E.PAPER_ONLY is True)

print(f'\n{OK}/{OK + FALLO} pruebas OK')
sys.exit(1 if FALLO else 0)
