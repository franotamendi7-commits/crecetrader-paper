#!/usr/bin/env python3
"""Validacion del motor contra las capturas reales de TradingView (2026-11-20).

Fuentes (3 capturas en ~/Downloads/BNBUSDT_2026-11-20_16-36/37-*.png):
  1S = semanal | 1D = diario | 4H = 4 horas, todas BNB/USDT en Binance.

FORMULA (verificada, 12 niveles exactos):
    nivel = minimo + rango * r          (alcista)
    nivel = maximo - rango * r          (bajista)
El fibo se tira "al reves": 0 = minimo, 1 = maximo, y las extensiones
(1, 1,25, 1,5, 1,75, 2, 3) quedan ARRIBA del maximo.
El nivel es 0,61 (no 0,618).
"""
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE / 'daily_pilot' / 'core'))
from zonas import zonas   # noqa: E402

OK = FALLO = 0
TOL = 0.05


def caso(nombre, cond, detalle=''):
    global OK, FALLO
    if cond:
        OK += 1
        print(f'OK    | {nombre} | {detalle}')
    else:
        FALLO += 1
        print(f'FALLO | {nombre} | {detalle}')


CAPTURAS = [
    # (tf, plazo, minimo, maximo, {etiqueta: valor})
    ('1W', 'largo', 537.21, 1371.90,
     {'0.382': 856.06, '0.5': 954.55, '0.61': 1046.37, '1': 1371.90, '0': 537.21}),
    ('1D', 'media', 536.58, 808.24,
     {'0.382': 640.35, '0.5': 672.41, '0.61': 702.29, '1': 808.24, '1.25': 876.16}),
    ('4H', 'corto', 530.54, 809.57,
     {'0.382': 637.13, '0.5': 670.05, '0.61': 700.75, '1': 809.57}),
]

for tf, plazo, mn, mx, niveles in CAPTURAS:
    z = zonas(mn, mx, plazo=plazo)
    caso(f'{tf}_nivel_0_es_minimo', abs(z['minimo'] - niveles.get('0', mn)) < TOL,
         f"{z['minimo']} vs {niveles.get('0')}")
    for etiqueta, valor in niveles.items():
        if etiqueta == '0':
            continue
        real = z['extensiones'].get(etiqueta) if etiqueta in ('1', '1.25') else z['zonas_compra'].get(etiqueta)
        caso(f'{tf}_{etiqueta}', real is not None and abs(real - valor) < TOL, f'{real} vs {valor}')

# la extension 1,25 queda arriba del maximo (1D)
z1 = zonas(536.58, 808.24, plazo='media')
caso('ext_125_arriba', z1['extensiones']['1.25'] > 808.24, str(z1['extensiones']['1.25']))
caso('ext_1_es_maximo', abs(z1['extensiones']['1'] - 808.24) < TOL)

# direccion
caso('alcista', z1['direccion'] == 'alcista', z1['direccion'])

print(f'\n{OK}/{OK + FALLO} pruebas OK')
sys.exit(1 if FALLO else 0)
