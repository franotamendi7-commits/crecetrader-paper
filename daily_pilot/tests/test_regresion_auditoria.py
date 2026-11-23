#!/usr/bin/env python3
"""Tests de regression de las correcciones P0/P1 de la auditoria DeepSeek.

Cada test queda traba contra el bug que responde. Si un bug vuelve, esto falla.

    python3 daily_pilot/tests/test_regresion_auditoria.py
"""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE / 'daily_pilot' / 'core'))
sys.path.insert(0, str(BASE / 'daily_pilot' / 'scripts'))

OK = FALLO = 0


def caso(nombre: str, cond, detalle: str = ''):
    global OK, FALLO
    if cond:
        print(f'  OK    {nombre}'); OK += 1
    else:
        print(f'  FALLO {nombre}  {detalle}'); FALLO += 1


# ---------------------------------------------------------------- C01
print('=== C01: 4H en contra de W ===')
from jerarquia import determinar, sin_semanal
for w, d in [('alcista', 'alcista'), ('alcista', 'rango'),
             ('bajista', 'bajista'), ('bajista', 'rango')]:
    h = 'bajista' if w == 'alcista' else 'alcista'
    r = determinar(w, d, h)
    caso(f'{w}/{d}/{h} -> no_operar', r['direccion'] == 'no_operar', str(r))
caso('alineados 3/3 -> long', determinar('alcista', 'alcista', 'alcista')['confianza'] == 0.85)
caso('W/D alineados + 4H rango -> 0.60',
     determinar('alcista', 'alcista', 'rango')['confianza'] == 0.60)
caso('sin_semanal D alcista + 4H bajista -> no_operar',
     sin_semanal('alcista', 'bajista')['direccion'] == 'no_operar')

# ---------------------------------------------------------------- C05
print('=== C05: fibos segun la direccion del tramo ===')
from zonas import zonas
z = zonas(55130.0, 87395.67, plazo='media', direccion='bajista')
caso('BTC 1d bajista retro 0,786 = 62.034,85', z['zonas_compra']['0.786'] == 62034.85,
     str(z['zonas_compra']))
caso('ext 0,50 bajista = retro 0,50', z['extensiones']['0.5'] == z['zonas_compra']['0.5'])
caso('sin niveles <= 0', all(v > 0 for v in z['extensiones'].values()))

# el ticket pasa la direccion real
out = sys.executable and None
import subprocess
r = subprocess.run([sys.executable, str(BASE / 'daily_pilot/scripts/agente_ticket.py'),
                    'BTCUSDT', '--tf', '1d', '--json'],
                   capture_output=True, text=True)
ticket = json.loads(r.stdout)
caso('ticket BTC 1d retro 0,786 = 62.034,85', ticket['retrocesos']['0.786'] == 62034.85,
     str(ticket.get('retrocesos')))

# ---------------------------------------------------------------- backtest
print('=== Backtest: walk-forward + 2x2 ===')
from backtest_niveles import backtest
bt = backtest('BTCUSDT', '1d', detalle=90)
if 'error' in bt:
    caso('backtest corre', False, bt['error'])
else:
    caso('tramo congelado antes de la ventana', bt['ventana_inicio'] > 0)
    caso('el tramo NO incluye velas del test',
         bt['ventana_inicio'] == len(json.loads(
             (BASE / 'daily_pilot/datos/velas/BTCUSDT_1d.json').read_text())['velas']) - 90)
    ok2x2 = all(f['hold'] + f['break'] + f['cont'] + f['rev'] == f['toques']
                for f in bt['niveles'] if f['toques'])
    caso('2x2 suma igual a toques', ok2x2)
    caso('los niveles chicos se marcan suficiente=False',
         any(not f['suficiente'] for f in bt['niveles'] if f['toques']))

# ---------------------------------------------------------------- paper
print('=== Paper: notional = capital x riesgo / stop ===')
spec = importlib.util.spec_from_file_location(
    'pt', BASE / 'daily_pilot/scripts/paper_trading.py')
pt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pt)
tmp = Path(tempfile.mkdtemp()) / 'paper_test.json'
vivo = BASE / 'daily_pilot/datos/paper_trades.json'
antes = vivo.read_bytes() if vivo.exists() else None
pt.ARCHIVO = tmp
op = pt.abrir('long', 'BTCUSDT', 100.0, 90.0, 120.0, 2.0)
caso('notional 200 (capital 1000 x 2% / stop 10%)', op['notional'] == 200.0, str(op))
pt.cerrar(1, 110.0)
usd = pt._cargar()['operaciones'][0]['resultado_usd']
caso('P&L 10% sobre 200 - 0,1% = 19,80', abs(usd - 19.8) < 0.01, str(usd))
pt.ARCHIVO = Path(tempfile.mkdtemp()) / 'p2.json'
pt.abrir('long', 'BTCUSDT', 67304.0, 65000.0, 80179.0, 2.0)
pt.cerrar(1, 70000.0)
usd2 = pt._cargar()['operaciones'][0]['resultado_usd']
caso('BTC 67.304->70.000 riesgo 2% ~ 22,8', abs(usd2 - 22.8) < 0.5, str(usd2))
try:
    pt.abrir('long', 'X', 100.0, 110.0, 120.0)
    caso('valida SL por debajo en long', False)
except SystemExit:
    caso('valida SL por debajo en long', True)
# el archivo vivo no se toco
despues = vivo.read_bytes() if vivo.exists() else None
caso('no toca el paper vivo', antes == despues)

# ---------------------------------------------------------------- alertas
print('=== Alertas: activos baratos y guard ===')
from alertas_niveles import alertas
avisos = alertas({'DOGEUSDT': 0.06, 'ADAUSDT': 0.15},
                 [{'par': 'DOGEUSDT', 'precio': 0.057, 'tipo': 't'},
                  {'par': 'ADAUSDT', 'precio': 0.1489, 'tipo': 't'}], 1.5)
caso('DOGE 0,057 no colapsa', isinstance(avisos, list))
caso('guard precio <= 0', alertas({'X': 1.0}, [{'par': 'X', 'precio': 0.0}], 1.5) == [])

# ---------------------------------------------------------------- dash
print('=== Dash: sin NameError ===')
html = (BASE / 'daily_pilot/dashboard/index.html').read_text()
caso('el HTML no tiene NameError', 'NameError' not in html)
caso('el titulo ya no dice PROBABILIDAD', 'PROBABILIDAD POR PAR' not in html.upper())
caso('dice CONFIANZA', 'CONFIANZA POR PAR' in html)

print(f'\nRESULTADO: {OK} OK · {FALLO} FALLO')
sys.exit(1 if FALLO else 0)
