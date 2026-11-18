#!/usr/bin/env python3
"""Pruebas del nucleo v1.1: clasificador de planes (9 tipos) + Manager."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from core.plan_classifier import clasificar_escenario  # noqa: E402
from core.manager import Manager  # noqa: E402

OK = FALLO = 0


def caso(nombre, cond, detalle=''):
    global OK, FALLO
    if cond:
        OK += 1
        print(f'OK    | {nombre} | {detalle}')
    else:
        FALLO += 1
        print(f'FALLO | {nombre} | {detalle}')


def esc(**kw):
    base = dict(id='E1', video_id='v', instrumento='BTCUSD', direccion='alcista')
    base.update(kw)
    return base


# --- clasificador (9 tipos) ---
caso('nivel_referenciado', clasificar_escenario(esc(nivel={'valor': 69000}))['clasificacion'] == 'NIVEL_REFERENCIADO',
     clasificar_escenario(esc(nivel={'valor': 69000}))['clasificacion'])
caso('zona_de_interes', clasificar_escenario(esc(nivel={'valor': 65520}, justificacion='vigilar'))['clasificacion'] == 'ZONA_DE_INTERES',
     clasificar_escenario(esc(nivel={'valor': 65520}, justificacion='vigilar'))['clasificacion'])
caso('escenario_condicional',
     clasificar_escenario(esc(nivel={'valor': 56750}, condicion_activacion={'valor': 'si cae'},
                             justificacion='en caso de caida'))['clasificacion'] == 'ESCENARIO_CONDICIONAL',
     clasificar_escenario(esc(nivel={'valor': 56750}, condicion_activacion={'valor': 'si cae'},
                             justificacion='en caso de caida'))['clasificacion'])
caso('plan_incompleto_sin_stop',
     clasificar_escenario(esc(condicion_activacion={'valor': 'x'}, entrada={'valor': 69000},
                             objetivos=[{'valor': 72554}]))['clasificacion'] == 'PLAN_OPERATIVO_INCOMPLETO',
     'sin stop -> incompleto')
caso('plan_incompleto_sin_entrada',
     clasificar_escenario(esc(condicion_activacion={'valor': 'x'},
                             objetivos=[{'valor': 72554}]))['clasificacion'] == 'ESCENARIO_CONDICIONAL',
     'sin entrada -> condicional')
caso('plan_completo',
     clasificar_escenario(esc(condicion_activacion={'valor': 'x'}, entrada={'valor': 69000},
                             stop={'valor': 68500}, objetivos=[{'valor': 72554}]))['clasificacion'] == 'PLAN_OPERATIVO_COMPLETO',
     'condicion+entrada+stop+objetivos')
caso('indeterminado', clasificar_escenario(esc())['clasificacion'] == 'INDETERMINADO', 'vacio')

# --- Manager ---
m = Manager()
v = m.evaluar(esc(nivel={'valor': 65520}, justificacion='vigilar'))
caso('manager_zona', v['veredicto'] == 'FALTA_INFORMACION', v['veredicto'])

v = m.evaluar(esc(nivel={'valor': 56750}, condicion_activacion={'valor': 'si cae'}))
caso('manager_condicional', v['veredicto'] == 'ESPERAR_CONFIRMACION', v['veredicto'])

v = m.evaluar(esc(condicion_activacion={'valor': 'x'}, entrada={'valor': 69000},
                 objetivos=[{'valor': 72554}]))
caso('manager_plan_incompleto', v['veredicto'] == 'ESPERAR_CONFIRMACION'
     and v['dimensiones']['completitud_plan'] == 'incompleto', v['veredicto'])
caso('manager_propone_stop_D', bool(v['propuesta_stop']) and v['propuesta_stop']['procedencia'] == 'D',
     str(v.get('propuesta_stop')))
caso('manager_que_se_necesita', 'invalidacion' in v['que_se_necesita'], str(v['que_se_necesita']))

v = m.evaluar(esc(condicion_activacion={'valor': 'x'}, entrada={'valor': 69000},
                 stop={'valor': 68500}, objetivos=[{'valor': 72554}]))
caso('manager_completo_apto', v['veredicto'] == 'APTO_PARA_EVALUACION'
     and v['dimensiones']['completitud_plan'] == 'completo', v['veredicto'])

v = m.evaluar(esc(condicion_activacion={'valor': 'x'}, entrada={'valor': 69000},
                 stop={'valor': 68900}, objetivos=[{'valor': 69050}]))
caso('manager_rb_bajo', v['veredicto'] == 'RIESGO_INADECUADO', v['veredicto'])

v = m.evaluar(esc(condicion_activacion={'valor': 'x'}, entrada={'valor': 69000},
                 stop={'valor': 70000}, objetivos=[{'valor': 72554}]))
caso('manager_contradiccion', v['veredicto'] == 'NO_OPERABLE'
     and v['dimensiones']['viabilidad_tecnica'] == 'con contradicciones', v['veredicto'])

v = m.evaluar(esc(seguimiento='INVALIDADO'))
caso('manager_invalidado', v['veredicto'] == 'ESCENARIO_INVALIDADO'
     and v['clasificacion'] == 'DESCARTADO', v['veredicto'])

e = esc(nivel={'valor': 71509, 'procedencia': 'A'},
        entrada={'valor': 69000, 'procedencia': 'A'},
        stop={'valor': 68441, 'procedencia': 'C', 'metodo': '0.5% bajo la entrada'})
caso('procedencias_distintas', e['nivel']['procedencia'] == 'A' and e['stop']['procedencia'] == 'C'
     and e['stop']['metodo'] != '', 'A y C separadas')

v = m.evaluar(esc(condicion_activacion={'valor': 'x'}, entrada={'valor': 69000},
                 stop={'valor': 68500}, objetivos=[{'valor': 72554}]))
caso('capital_simulado', v['capital']['disponible'] == 10000.0 and v['paper_only'] is True)

print(f'\n{OK}/{OK + FALLO} pruebas OK')
sys.exit(1 if FALLO else 0)
