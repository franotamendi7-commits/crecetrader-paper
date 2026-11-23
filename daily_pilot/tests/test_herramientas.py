#!/usr/bin/env python3
"""Tests de las 5 herramientas nuevas."""
import sys
import subprocess
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
PY = '/Users/franciscootamendi/.hermes/hermes-agent/venv/bin/python3'
OK = FALLO = 0


def test(nombre, cond):
    global OK, FALLO
    if cond:
        print(f'  OK    {nombre}'); OK += 1
    else:
        print(f'  FALLO {nombre}'); FALLO += 1


def corre(args, **kw):
    r = subprocess.run([PY] + args, capture_output=True, text=True, cwd=BASE, **kw)
    return r.stdout + r.stderr


print('=== 1 · ticket ===')
out = corre(['daily_pilot/scripts/agente_ticket.py', 'BTCUSDT', '--tf', '4h'])
test('ticket corre', 'TICKET BTCUSDT' in out)
test('da regimen W/D/4H', all(x in out for x in ['W=', 'D=', '4H=']))
test('da tramo y niveles', 'tramo' in out and 'retrocesos' in out)

print('=== 2 · alertas ===')
out = corre(['daily_pilot/scripts/alertas_niveles.py', '--umbral', '1.5'])
test('alertas corre', 'ALERTAS DE NIVEL' in out)
test('trae concordancia', 'concordancia' in out or 'ningun nivel' in out)

print('=== 3 · backtest ===')
out = corre(['daily_pilot/scripts/backtest_niveles.py', 'BTCUSDT', '--tf', '1d'])
test('backtest corre', 'BACKTEST BTCUSDT' in out)
test('da toques y rebotes', 'toques' in out and 'rebotes' in out)

print('=== 4 · canal acierta ===')
out = corre(['daily_pilot/scripts/canal_acierta.py'])
test('corre sin romper', '¿EL CANAL ACIERTA?' in out or 'sin datos' in out)

print('=== 5 · paper ===')
P = BASE / 'daily_pilot/datos/paper_trades.json'
if P.exists():
    P.unlink()
out = corre(['daily_pilot/scripts/paper_trading.py', '--abrir', 'long',
             'BTCUSDT', '100', '--sl', '90', '--tp', '120'])
test('abre operacion', '#1 LONG BTCUSDT' in out)
out = corre(['daily_pilot/scripts/paper_trading.py', '--cerrar', '1', '--precio', '110'])
test('cierra con ganancia', '+10.00%' in out)
out = corre(['daily_pilot/scripts/paper_trading.py', '--resumen'])
test('resumen tiene resultado', 'resultado acumulado' in out)
if P.exists():
    P.unlink()

print(f'\nRESULTADO: {OK} OK · {FALLO} FALLO')
sys.exit(1 if FALLO else 0)
