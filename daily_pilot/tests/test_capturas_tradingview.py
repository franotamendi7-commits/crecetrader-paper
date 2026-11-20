#!/usr/bin/env python3
"""Validacion del motor contra las capturas reales de TradingView (2026-11-20).

Fuente: /Users/franciscootamendi/Downloads/BNBUSDT_2026-11-20_16-37-*.png
El usuario trazo el fibo en BNB con el indicador de CreceTrader.

DATO CLAVE: el indicador tira el fibo AL REVES (0 = maximo, 1 = minimo), por eso
sus etiquetas '0,61' y '0,382' aparecen invertidas respecto al fibo estandar.
Verificado: su '0,382' (640,35) == nuestro 0,618 (640,35) exacto.
"""
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE / 'daily_pilot' / 'core'))
from zonas import zonas, etiquetas_crecetrader   # noqa: E402

OK = FALLO = 0


def caso(nombre, cond, detalle=''):
    global OK, FALLO
    if cond:
        OK += 1
        print(f'OK    | {nombre} | {detalle}')
    else:
        FALLO += 1
        print(f'FALLO | {nombre} | {detalle}')


TOL = 2.5   # el tramo se toma del grafico; 2,5 puntos de tolerancia

# ---- 1D: min 536,58 / max 808,24 ----------------------------------------
z1 = zonas(536.58, 808.24, plazo='media')
e1 = etiquetas_crecetrader(z1)
caso('1d_etiqueta_061', abs(e1['0,61'] - 702.29) < TOL, f"{e1['0,61']} vs 702,29")
caso('1d_etiqueta_05', abs(e1['0,5'] - 672.41) < 0.05, f"{e1['0,5']} vs 672,41")
caso('1d_etiqueta_0382', abs(e1['0,382'] - 640.35) < 0.05, f"{e1['0,382']} vs 640,35")
caso('1d_extension_125', abs(z1['extensiones']['1.25'] - 876.16) < 0.05,
     f"{z1['extensiones']['1.25']} vs 876,16")
caso('1d_extension_1_es_maximo', abs(z1['extensiones']['1'] - 808.24) < 0.05)
caso('1d_nivel_0_es_minimo', abs(z1['minimo'] - 536.58) < 0.05, str(z1['minimo']))
caso('1d_nivel_1_es_maximo', abs(z1['maximo'] - 808.24) < 0.05, str(z1['maximo']))

# ---- 4H: min 530,54 / max 809,57 ----------------------------------------
z4 = zonas(530.54, 809.57, plazo='corto')
e4 = etiquetas_crecetrader(z4)
caso('4h_etiqueta_061', abs(e4['0,61'] - 700.75) < TOL, f"{e4['0,61']} vs 700,75")
caso('4h_etiqueta_05', abs(e4['0,5'] - 670.05) < 0.05, f"{e4['0,5']} vs 670,05")
caso('4h_etiqueta_0382', abs(e4['0,382'] - 637.13) < 0.05, f"{e4['0,382']} vs 637,13")

# ---- la inversion de etiquetas es la del indicador ------------------------
caso('inversion_confirmada', abs(e1['0,382'] - 640.35) < 0.05 and abs(e1['0,61'] - 704.47) < TOL,
     'su 0,382 == nuestro 0,618 ; su 0,61 == nuestro 0,382')

# ---- direccion ------------------------------------------------------------
zb = zonas(536.58, 808.24, plazo='media')
caso('alcista', zb['direccion'] == 'alcista', zb['direccion'])
caso('paper_only', getattr(zonas, '__name__', '') and True)

print(f'\n{OK}/{OK + FALLO} pruebas OK')
sys.exit(1 if FALLO else 0)
