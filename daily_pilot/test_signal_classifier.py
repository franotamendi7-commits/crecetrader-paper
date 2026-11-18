#!/usr/bin/env python3
"""Pruebas del clasificador con los 4 casos del informe del 16/11 + casos base."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from signal_classifier import clasificar

OK = FALLO = 0


def caso(nombre, cond, detalle=''):
    global OK, FALLO
    if cond:
        OK += 1
        print(f'OK    | {nombre} | {detalle}')
    else:
        FALLO += 1
        print(f'FALLO | {nombre} | {detalle}')


# --- Los 4 ejemplos del informe del 16/11: ninguno puede ser operacion ---
r = clasificar({'nivel': '69.000-71.509',
                'texto': 'la llegada a los 69.000 y 71.509 no era una señal de compra'})
caso('69.000-71.509_negado', r['tipo'] == 'SIN_OPERACION' and not r['es_candidata_operativa'], r['tipo'])

r = clasificar({'nivel': '65.520', 'texto': 'había que vigilar el precio en los 65.520'})
caso('65.520_vigilancia', r['tipo'] == 'ZONA_DE_INTERES' and not r['es_candidata_operativa'], r['tipo'])

r = clasificar({'nivel': '56.750', 'texto': 'en caso de caída, los 56.750'})
caso('56.750_condicional', r['tipo'] == 'ESCENARIO_CONDICIONAL' and not r['es_candidata_operativa'], r['tipo'])

r = clasificar({'nivel': '3.906-3.623', 'texto': 'el oro podría corregir hasta los 3.623'})
caso('oro_correccion', r['tipo'] == 'ESCENARIO_CONDICIONAL' and not r['es_candidata_operativa'], r['tipo'])

# --- casos base ---
r = clasificar({'nivel': '64.620', 'texto': 'está cotizando en 64.620'})
caso('nivel_mencionado', r['tipo'] == 'NIVEL_MENCIONADO', r['tipo'])

r = clasificar({'nivel': '69.000', 'texto': 'comprar en 69.000 con stop en 68.500'})
caso('senal_explicita', r['tipo'] == 'SENAL_EXPLICITA' and r['es_candidata_operativa'], r['tipo'])

r = clasificar({'texto': 'no hay confirmación de nada'})
caso('sin_confirmacion', r['tipo'] == 'SIN_OPERACION' or r['tipo'] == 'NO_DETERMINABLE', r['tipo'])

r = clasificar({'texto': ''})
caso('vacio', r['tipo'] == 'NO_DETERMINABLE', r['tipo'])

r = clasificar({'nivel': None, 'texto': 'zona de compras en 70.000', 'entrada': True})
caso('entrada_con_zona', r['tipo'] == 'SENAL_EXPLICITA', r['tipo'])

# ninguna puede ser operativa sin entrada explicita
caso('ninguna_automatica', all(not clasificar(x)['es_candidata_operativa'] for x in [
    {'nivel': '69.000-71.509', 'texto': 'no era una señal de compra'},
    {'nivel': '65.520', 'texto': 'vigilar'},
    {'nivel': '56.750', 'texto': 'en caso de caída'},
    {'nivel': '3.906', 'texto': 'podría corregir'},
]), 'los 4 ejemplos no son operativos')

print(f'\n{OK}/{OK + FALLO} pruebas OK')
sys.exit(1 if FALLO else 0)
