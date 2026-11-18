#!/usr/bin/env python3
"""Tests de liquidez institucional (C06, Francisco). Sin red, PAPER_ONLY."""
import sys
from pathlib import Path

BASE = Path('/Users/franciscootamendi/YouTubeTradingAgent')
sys.path.insert(0, str(BASE / 'daily_pilot' / 'core'))
import liquidez as L

OK = FALLO = 0


def caso(nombre, cond, detalle=''):
    global OK, FALLO
    if cond:
        OK += 1
        print(f'OK    | {nombre} | {detalle}')
    else:
        FALLO += 1
        print(f'FALLO | {nombre} | {detalle}')


# 1. los 3 ingredientes
r = L.calcular({'zonas_compra': {'50%': 66139.0, '61%': 63925.56}}, [60000.0], [69000.0, 71509.0])
caso('tres_componentes', r['n_componentes'] == 3, str(r['componentes_usados']))
caso('componentes_nombres', r['componentes_usados'] == ['zonas_fibo_c05', 'precios_comienzo_ano', 'pools_volumen_order_block'])
caso('liquidez_unica', len(r['liquidez_institucional']) == 5, str(r['liquidez_institucional']))
caso('incluye_fibo', 63925.56 in r['liquidez_institucional'])
caso('incluye_enero', 60000.0 in r['liquidez_institucional'])
caso('incluye_pools', 69000.0 in r['liquidez_institucional'] and 71509.0 in r['liquidez_institucional'])

# 2. sin ingredientes -> vacio
r0 = L.calcular()
caso('sin_ingredientes_vacio', r0['n_componentes'] == 0 and r0['liquidez_institucional'] == [])

# 3. solo fibo
r1 = L.calcular({'zonas_compra': {'50%': 66139.0}})
caso('solo_fibo', r1['n_componentes'] == 1 and r1['liquidez_institucional'] == [66139.0])

# 4. sesion NY
caso('sesion_ny', r['sesion'] == 'Nueva York', r['sesion'])
caso('nota_sesion', 'Nueva York' in r['nota_sesion'], r['nota_sesion'])

# 5. duplicados colapsan
r2 = L.calcular({'zonas_compra': {'50%': 69000.0}}, [], [69000.0])
caso('duplicados_colapsan', r2['liquidez_institucional'] == [69000.0], str(r2['liquidez_institucional']))

# 6. busqueda por tolerancia
r3 = L.calcular({'zonas_compra': {'50%': 66139.0}}, [], [])
cerca = L.busca_liq(r3, 66139.5, tolerancia=1.0)
caso('busca_liq_cercano', cerca == [66139.0], str(cerca))
caso('busca_liq_lejos', L.busca_liq(r3, 70000.0, tolerancia=1.0) == [])

# 7. order block NO es zona de trading (C05) pero SI ingrediente de liquidez
caso('ob_es_ingrediente_no_zona', 'pools_volumen_order_block' in L.COMPONENTES)

# 8. paper only
caso('paper_only', r['paper_only'] is True and L.PAPER_ONLY is True)

print(f'\n{OK}/{OK + FALLO} pruebas OK')
sys.exit(1 if FALLO else 0)
