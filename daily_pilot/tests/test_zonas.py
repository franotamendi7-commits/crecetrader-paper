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


# 1. retrocesos 50 / 61 / 78  (formulacion: maximo - rango*r)
z = Z.zonas(56760.0, 75518.0, 'corto')
caso('marco_4h', z['marco'] == '4H', z['marco'])
caso('tres_retrocesos', len(z['zonas_compra']) == 3, str(z['zonas_compra']))
caso('retroceso_50', z['zonas_compra']['0.5'] == 66139.0, str(z['zonas_compra']))
caso('retroceso_618', z['zonas_compra']['0.618'] == 63925.56, str(z['zonas_compra']))
caso('retroceso_78', z['zonas_compra']['0.786'] == 60774.21, str(z['zonas_compra']))
caso('zonas_ordenadas', list(z['zonas_compra'].values())[0] > list(z['zonas_compra'].values())[2])

# 2. extensiones: 1.0 = el maximo; 1.25 por encima (captura BNB)
caso('siete_extensiones', len(z['extensiones']) == 7, str(z['extensiones']))
caso('ext_100_es_el_maximo', abs(z['extensiones']['1'] - 75518.0) < 0.01, str(z['extensiones']['1']))
caso('ext_125_arriba', z['extensiones']['1.25'] > 75518.0, str(z['extensiones']['1.25']))
caso('ext_300', '3' in z['extensiones'], str(z['extensiones']))
caso('extensiones_arriba_del_minimo', all(v >= 56760.0 for v in z['extensiones'].values()))
caso('ext_1_arriba_del_maximo', abs(z['extensiones']['1'] - 75518.0) < 0.01, str(z['extensiones']['1']))

# 2b. VALIDACION con la captura real de BNB (min 537.81 / max 808.24)
zbnb = Z.zonas(537.81, 808.24, 'media')
caso('bnb_1_es_maximo', abs(zbnb['extensiones']['1'] - 808.24) < 0.01, str(zbnb['extensiones']['1']))
caso('bnb_125_captura', abs(zbnb['extensiones']['1.25'] - 876.16) < 1.0, str(zbnb['extensiones']['1.25']))

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
caso('bajista_extensiones_abajo', zb['extensiones']['2'] < 56760.0 and zb['extensiones']['3'] < zb['extensiones']['2'], str(zb['extensiones']))
caso('bajista_ext_1_es_el_minimo', abs(zb['extensiones']['1'] - 56760.0) < 0.01, str(zb['extensiones']['1']))
caso('bajista_ext_2', abs(zb['extensiones']['2'] - 38002.0) < 0.01, str(zb['extensiones']['2']))
caso('alcista_extensiones_arriba', all(v >= 56760.0 for v in z['extensiones'].values()))

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
