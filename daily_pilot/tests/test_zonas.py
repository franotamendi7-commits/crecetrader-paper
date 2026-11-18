#!/usr/bin/env python3
"""Tests de zonas calculadas (C05, Francisco). Sin red, PAPER_ONLY."""
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE / 'daily_pilot' / 'core'))
import zonas as Z

OK = FALLO = 0


def caso(nombre, cond, detalle=''):
    global OK, FALLO
    if cond:
        OK += 1
        print(f'OK    | {nombre} | {detalle}')
    else:
        FALLO += 1
        print(f'FALLO | {nombre} | {detalle}')


# 1. retrocesos 50 / 61 / 78
z = Z.zonas(56760.0, 75518.0, 'corto')
caso('marco_4h', z['marco'] == '4H', z['marco'])
caso('tres_retrocesos', len(z['zonas_compra']) == 3, str(z['zonas_compra']))
caso('retroceso_50', z['zonas_compra']['50%'] == 66139.0, str(z['zonas_compra']))
caso('retroceso_618', z['zonas_compra']['61%'] == 63925.56, str(z['zonas_compra']))
caso('retroceso_78', z['zonas_compra']['78%'] == 60774.21, str(z['zonas_compra']))
caso('zonas_ordenadas', list(z['zonas_compra'].values())[0] > list(z['zonas_compra'].values())[2])

# 2. extensiones 50 / 100 / 150 / 200
caso('cuatro_extensiones', len(z['extensiones']) == 4, str(z['extensiones']))
caso('ext_100', z['extensiones']['100%'] == 94276.0, str(z['extensiones']))
caso('ext_200', z['extensiones']['200%'] == 113034.0, str(z['extensiones']))
caso('extensiones_arriba', all(v > 75518.0 for v in z['extensiones'].values()))

# 3. marco segun plazo
caso('tf_largo_semanal', Z.tf_para('largo') == 'semanal')
caso('tf_media_diario', Z.tf_para('media') == 'diario')
caso('tf_corto_4h', Z.tf_para('corto') == '4H')

# 4. es nivel calculado, NO soporte/resistencia/OB/FVG
caso('nivel_calculado', z['tipo'] == 'nivel_calculado')
caso('no_es_sr_ob_fvg', z['no_es'] == ['soporte', 'resistencia', 'order_block', 'FVG'], str(z['no_es']))

# 5. cambio de tendencia
caso('sigue_tendencia', Z.cambio_tendencia(True, False) is False)
caso('cambio_tendencia', Z.cambio_tendencia(False, True) is True)
caso('sin_cambio', Z.cambio_tendencia(False, False) is False)

# 5b. en bajista se calcula al reves (de maximo a minimo)
zb = Z.zonas(56760.0, 75518.0, 'corto', direccion='bajista')
caso('bajista_direccion', zb['direccion'] == 'bajista' and zb['minimo'] == 56760.0, f"{zb['direccion']} {zb['minimo']}")
caso('bajista_extensiones_abajo', all(v < 56760.0 for v in zb['extensiones'].values()), str(zb['extensiones']))
caso('bajista_ext_100', zb['extensiones']['100%'] == 38002.0, str(zb['extensiones']))
caso('alcista_extensiones_arriba', all(v > 75518.0 for v in z['extensiones'].values()))

# 6. validacion
try:
    Z.zonas(70000.0, 56000.0)
    caso('min>max_rechazado', False, 'no lanzó error')
except ValueError:
    caso('min>max_rechazado', True)

# 7. paper only
caso('paper_only', z['paper_only'] is True and Z.PAPER_ONLY is True)

print(f'\n{OK}/{OK + FALLO} pruebas OK')
sys.exit(1 if FALLO else 0)
