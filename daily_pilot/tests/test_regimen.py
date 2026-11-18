#!/usr/bin/env python3
"""Tests de regimen (C07, Francisco). Sin red, PAPER_ONLY."""
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE / 'daily_pilot' / 'core'))
import regimen as R

OK = FALLO = 0


def caso(nombre, cond, detalle=''):
    global OK, FALLO
    if cond:
        OK += 1
        print(f'OK    | {nombre} | {detalle}')
    else:
        FALLO += 1
        print(f'FALLO | {nombre} | {detalle}')


# 1. tendencia alcista
a = R.detectar([10, 20, 30], [5, 15, 25])
caso('alcista', a['regimen'] == 'TENDENCIA_ALCISTA', a['motivo'])

# 2. tendencia bajista
b = R.detectar([30, 20, 10], [25, 15, 5])
caso('bajista', b['regimen'] == 'TENDENCIA_BAJISTA', b['motivo'])

# 3. rango (mixto)
c = R.detectar([10, 30, 20], [5, 25, 15])
caso('rango', c['regimen'] == 'RANGO', c['motivo'])

# 4. solo maximos crecientes, minimos no -> no es tendencia
d = R.detectar([10, 20, 30], [5, 25, 15])
caso('maximos_solos_no_basta', d['regimen'] == 'RANGO', d['motivo'])

# 5. datos insuficientes
e = R.detectar([10], [5])
caso('insuficiente', e['regimen'] == 'NO_DETERMINADO', e['motivo'])

# 6. correccion no es regimen aparte (esta en la tendencia)
f = R.detectar([10, 20, 15], [5, 15, 10])
caso('correccion_dentro_tendencia', f['regimen'] == 'RANGO', f['motivo'])

# 7. cambio de regimen = reversion
caso('cambio_es_reversion', R.es_cambio('TENDENCIA_ALCISTA', 'TENDENCIA_BAJISTA') is True)
caso('alcista_a_rango_no_es_reversion', R.es_cambio('TENDENCIA_ALCISTA', 'RANGO') is False)
caso('mismo_regimen_no', R.es_cambio('TENDENCIA_ALCISTA', 'TENDENCIA_ALCISTA') is False)

# 8. confirmacion "supera y consolida"
caso('supera_consolida', R.supera_y_consolida(79.0, 78.746, 0.01) is True)
caso('no_supera', R.supera_y_consolida(78.0, 78.746, 0.01) is False)
caso('tolerancia_importa', R.supera_y_consolida(78.75, 78.746, 0.01) is False)

# 9. paper only
caso('paper_only', a['paper_only'] is True and R.PAPER_ONLY is True)

print(f'\n{OK}/{OK + FALLO} pruebas OK')
sys.exit(1 if FALLO else 0)
