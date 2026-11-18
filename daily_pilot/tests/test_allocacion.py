#!/usr/bin/env python3
"""Tests de asignacion (C02, Francisco). Sin red, PAPER_ONLY."""
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE / 'daily_pilot' / 'core'))
import allocacion as A

OK = FALLO = 0


def caso(nombre, cond, detalle=''):
    global OK, FALLO
    if cond:
        OK += 1
        print(f'OK    | {nombre} | {detalle}')
    else:
        FALLO += 1
        print(f'FALLO | {nombre} | {detalle}')


# 1. modelo 30/35/35
t = A.distribuir(100.0)
caso('tres_tramos', len(t) == 3, t)
caso('oferta_30', t[0]['porcentaje'] == 0.30 and t[0]['monto'] == 30.0, t[0])
caso('confirmacion_70', t[1]['porcentaje'] == 0.35 and t[2]['porcentaje'] == 0.35, (t[1], t[2]))
caso('suma_100', abs(sum(x['monto'] for x in t) - 100.0) < 0.01, sum(x['monto'] for x in t))

# 2. las 5 del proyecto se compran en oferta; el resto no
caso('btc_oferta', A.oferta_permitida('BTCUSD') is True)
caso('spx_si_oferta', A.oferta_permitida('SPX') is True)   # correccion de Francisco
caso('ada_no_oferta', A.oferta_permitida('ADA') is False)

# 3. topes de cartera
caso('btc_max_45', A.allocacion_maxima('BTCUSD', True) == 0.45, A.allocacion_maxima('BTCUSD', True))
caso('btc_oferta_30', A.allocacion_maxima('BTCUSD', False) == 0.30)
caso('spx_max_10', A.allocacion_maxima('SPX', True) == 0.10)
caso('spx_oferta_10', A.allocacion_maxima('SPX', False) == 0.10)   # correccion de Francisco
caso('desconocido_0', A.allocacion_maxima('XYZ') == 0.0)

# 4. plan BTC: mixto (30/35/35) y los tramos NUNCA superan el tope del activo
p = A.plan('BTCUSD', 1000.0, en_oferta=True)
caso('btc_mixto', p['tipo'] == 'mixto' and len(p['tramos']) == 3, p['tipo'])
caso('btc_max_monto', p['allocacion_maxima_monto'] == 450.0, str(p['allocacion_maxima_monto']))
caso('btc_suma_no_excede', p['suma_tramos'] <= p['allocacion_maxima_monto'], f"{p['suma_tramos']} <= {p['allocacion_maxima_monto']}")
caso('btc_capital_operable', p['capital_operable'] == 450.0, str(p['capital_operable']))

# 4b. H-06: antes el 100% del capital se asignaba a un activo con tope 45%
for inst, tope in (('BTCUSD', 450.0), ('ETHUSD', 200.0), ('SPX', 100.0)):
    q = A.plan(inst, 1000.0, en_oferta=True)
    caso(f'{inst}_no_excede', q['suma_tramos'] <= q['allocacion_maxima_monto'], f"{q['suma_tramos']} <= {q['allocacion_maxima_monto']}")

# 5. plan SPX: mixto tambien (correccion de Francisco)
p = A.plan('SPX', 1000.0, en_oferta=True)
caso('spx_mixto', p['tipo'] == 'mixto' and len(p['tramos']) == 3, p['tipo'])

# 6. ADA: no se compra
p = A.plan('ADA', 1000.0, en_oferta=True)
caso('ada_no_se_compra', p['allocacion_maxima'] == 0.0 and p['oferta_permitida'] is False, p)

# 7. paper only
caso('paper_only', A.PAPER_ONLY is True)

print(f'\n{OK}/{OK + FALLO} pruebas OK')
sys.exit(1 if FALLO else 0)
