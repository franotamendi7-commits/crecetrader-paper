#!/usr/bin/env python3
"""Tests del modulo Binance SOLO LECTURA. Sin escribir, PAPER_ONLY."""
import inspect
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE / 'daily_pilot' / 'core'))

OK = FALLO = 0


def caso(nombre, cond, detalle=''):
    global OK, FALLO
    if cond:
        OK += 1
        print(f'OK    | {nombre} | {detalle}')
    else:
        FALLO += 1
        print(f'FALLO | {nombre} | {detalle}')


import binance_readonly as B   # noqa: E402

# 1. no existe ninguna funcion para operar
fuentes = inspect.getsource(B)
prohibidas = ('create_order', 'place_order', 'new_order', 'futures_create',
              'send_order', 'post_order', '/api/v3/order')
caso('sin_funciones_de_orden', not any(p in fuentes for p in prohibidas),
     ', '.join(p for p in prohibidas if p in fuentes) or 'ninguna')

# 2. solo hay GETs
llamadas = [l.strip() for l in fuentes.splitlines() if "urlopen(" in l or "_get(" in l]
caso('solo_get', '_get(\'/api/v3/account\'' in fuentes and '_get(\'/api/v3/ticker/price\'' in fuentes,
     f'{len(llamadas)} llamadas')

# 3. paper only declarado
caso('paper_only', getattr(B, 'PAPER_ONLY', None) is True)

# 4. la clave NO esta en el repo
env = B.ENV_PATH
caso('env_fuera_del_repo', '.hermes' in str(env) and 'YouTubeTradingAgent' not in str(env),
     str(env))
caso('env_existe', env.exists())

# 5. el .env no debe estar trackeado por git
import subprocess
r = subprocess.run(['git', '-C', str(BASE), 'ls-files', '--error-unmatch', str(env)],
                   capture_output=True, text=True)
caso('env_no_trackeado', r.returncode != 0, 'fuera del repo' if r.returncode else 'PELIGRO')

# 6. si la clave no esta, el error es claro y no rompe
try:
    B._credenciales()
    hay_key = True
except Exception:
    hay_key = False
print(f'\n(clave cargada ahora mismo: {"SI" if hay_key else "NO"})')

print(f'\n{OK}/{OK + FALLO} pruebas OK')
sys.exit(1 if FALLO else 0)
