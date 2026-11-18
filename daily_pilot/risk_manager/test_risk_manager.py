#!/usr/bin/env python3
"""Pruebas sinteticas del Risk Manager. Sin red, sin trading, PAPER_ONLY."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from risk_manager import RiskManager, Config, Signal

OK = 0
FALLO = 0


def caso(nombre, cond, detalle=''):
    global OK, FALLO
    if cond:
        OK += 1
        print(f'OK    | {nombre} | {detalle}')
    else:
        FALLO += 1
        print(f'FALLO | {nombre} | {detalle}')


def senal(**kw):
    base = dict(id='S1', instrument='BTCUSD', direction='compra', entry_low=69000,
                entry_high=71509, invalidation=68500, targets=[72554, 75518],
                evidence=['video 06:26-07:01'], confidence=0.8)
    base.update(kw)
    return Signal(**base)


# 1. completa y valida
rm = RiskManager()
r = rm.evaluar([senal()])
s = r['senales'][0]
caso('senal_completa', r['decision'] == 'ACEPTAR' and s['risk']['perdida_potencial'] is not None,
     f"decision={r['decision']} perdida={s['risk']['perdida_potencial']}")

# 2. falta invalidacion
r = rm.evaluar([senal(invalidation=None)])
caso('falta_invalidation', r['senales'][0]['decision'] == 'RECHAZAR'
     and any('invalidacion' in x for x in r['senales'][0]['razones']),
     r['senales'][0]['razones'])

# 3. contradiccion compra
r = rm.evaluar([senal(entry_low=69000, entry_high=69000, invalidation=70000)])
caso('contradiccion_compra', r['senales'][0]['decision'] == 'RECHAZAR'
     and any('entrada <= invalidacion' in x for x in r['senales'][0]['razones']),
     r['senales'][0]['razones'])

# 4. contradiccion venta
r = rm.evaluar([senal(id='S4', direction='venta', entry_low=3906, entry_high=3906,
                      invalidation=3800, targets=[3623])])
caso('contradiccion_venta', r['senales'][0]['decision'] == 'RECHAZAR'
     and any('entrada >= invalidacion' in x for x in r['senales'][0]['razones']),
     r['senales'][0]['razones'])

# 5. venta valida
r = rm.evaluar([senal(id='S5', direction='venta', entry_low=3906, entry_high=3906,
                      invalidation=3980, targets=[3623])])
caso('venta_valida', r['senales'][0]['decision'] == 'ACEPTAR', f"decision={r['senales'][0]['decision']}")

# 6. exposicion excedida (con el tope C11 del 5%, 2 senales = $1.000)
rm6 = RiskManager(Config(account_balance=10000, max_risk_pct=0.5, max_exposure_pct=0.01))
r = rm6.evaluar([senal(id='A'), senal(id='B')])
caso('exposicion_excedida', r['decision'] == 'REVISION MANUAL'
     and any('exposicion' in x for x in r['razones']), r['razones'])

# 7. exceso de senales por instrumento
rm7 = RiskManager(Config(max_senales_por_instrumento=1))
r = rm7.evaluar([senal(id='A'), senal(id='B')])
caso('exceso_instrumento', any(x['decision'] == 'REVISION MANUAL' for x in r['senales']),
     [(x['id'], x['decision'], x['razones']) for x in r['senales']])

# 8. confianza baja
r = rm.evaluar([senal(confidence=0.2)])
caso('confianza_baja', r['senales'][0]['decision'] == 'REVISION MANUAL'
     and any('confianza' in x for x in r['senales'][0]['razones']), r['senales'][0]['razones'])

# 9. sin operacion
r = rm.evaluar([senal(id='N1', direction='sin_operacion', entry_low=None, entry_high=None,
                      invalidation=None, targets=[], evidence=['sin nivel claro'])])
caso('sin_operacion', r['senales'][0]['decision'] == 'ACEPTAR'
     and r['senales'][0]['risk']['perdida_potencial'] is None, r['senales'][0]['decision'])

# 10. sin evidencia
r = rm.evaluar([senal(evidence=[])])
caso('sin_evidencia', r['senales'][0]['decision'] == 'RECHAZAR'
     and any('evidencia' in x for x in r['senales'][0]['razones']), r['senales'][0]['razones'])

# 11. paper only
r = rm.evaluar([senal()])
caso('paper_only', r['paper_only'] is True and r['senales'][0]['paper_only'] is True)

# 12. r multiples
r = rm.evaluar([senal(entry_low=70000, entry_high=70000, invalidation=69000, targets=[72000])])
rm_ = r['senales'][0]['risk']['r_multiples']
caso('r_multiples', rm_ == [2.0], f"r={rm_}")

# 13. direccion invalida
r = rm.evaluar([senal(direction='alcista')])
caso('direccion_invalida', r['senales'][0]['decision'] == 'RECHAZAR'
     and any('direccion' in x for x in r['senales'][0]['razones']), r['senales'][0]['razones'])

# 14. lista vacia
r = rm.evaluar([])
caso('lista_vacia', r['decision'] == 'REVISION MANUAL', r['razones'])

# 15. invalidacion invalida (0) -> CORREGIDO
r = rm.evaluar([senal(invalidation=0)])
caso('invalidacion_cero', r['senales'][0]['decision'] == 'RECHAZAR'
     and any('invalidacion invalida' in x for x in r['senales'][0]['razones']),
     r['senales'][0]['razones'])

# 16. ZONA_DE_INTERES ahora es evaluable (nivel=escenario)
r = rm.evaluar([senal(tipo='ZONA_DE_INTERES')])
caso('zona_evaluable', r['senales'][0]['decision'] != 'NO_EVALUABLE'
     and r['senales'][0]['nivel'] == 'escenario',
     str((r['senales'][0]['decision'], r['senales'][0]['nivel'])))

# 17. ESCENARIO_CONDICIONAL es evaluable (nivel=escenario)
r = rm.evaluar([senal(tipo='ESCENARIO_CONDICIONAL')])
caso('escenario_evaluable', r['senales'][0]['decision'] != 'NO_EVALUABLE'
     and r['senales'][0]['nivel'] == 'escenario', r['senales'][0]['nivel'])

# 18. resumen por nivel presente
r = rm.evaluar([senal(), senal(id='N', tipo='NIVEL_MENCIONADO', direction='sin_operacion',
                              entry_low=None, entry_high=None, invalidation=None,
                              targets=[], evidence=['nivel'])])
caso('por_nivel', set(r['por_nivel']) == {'nivel_informativo', 'escenario', 'candidata', 'no_operable'}
     and r['por_nivel']['nivel_informativo'] == 1 and r['por_nivel']['candidata'] == 1,
     r['por_nivel'])

# 19. SENAL_EXPLICITA es candidata
r = rm.evaluar([senal()])
caso('candidata_nivel', r['senales'][0]['nivel'] == 'candidata', r['senales'][0]['nivel'])

# 20. C11/C01 (H-07): riesgo = confianza x tope, repartido entre entradas
r = rm.evaluar([senal(confidence=0.99, tipo_operacion='long')])
c99 = r['senales'][0]['risk']['riesgo_pct_efectivo']
caso('tope_long_por_entrada', abs(c99 - 0.02475) < 1e-4, f'confianza 0.99 long -> por entrada {c99}')

r = rm.evaluar([senal(confidence=0.02)])
c02 = r['senales'][0]['risk']['riesgo_pct_efectivo']
caso('riesgo_por_confianza', abs(c02 - 0.0005) < 1e-4, f'confianza 0.02 -> riesgo {c02}')

# 21. el tope no se supera ni con confianza maxima
r = rm.evaluar([senal(confidence=5.0)])
caso('tope_duro', r['senales'][0]['risk']['riesgo_pct_efectivo'] <= 0.05,
     r['senales'][0]['risk']['riesgo_pct_efectivo'])

# 22. C01: long se distribue en 2-3 entradas (2.5% por entrada con 2)
r = rm.evaluar([senal(tipo_operacion='long')])
rl = r['senales'][0]['risk']
caso('long_2_entradas', rl['riesgo_pct_efectivo'] == 0.02 and rl.get('riesgo_total_long') == 0.05,
     f"por entrada {rl['riesgo_pct_efectivo']} | total long {rl.get('riesgo_total_long')}")

# 23. C01: correccion 1-2%
r = rm.evaluar([senal(confidence=0.5, tipo_operacion='correccion')])
rc = r['senales'][0]['risk']
caso('correccion_2pct', rc['riesgo_pct_efectivo'] == 0.01, f"correccion {rc['riesgo_pct_efectivo']}")

# 24. C01: 3 entradas -> 1.667% por entrada
rm3 = RiskManager(Config(entradas_long=3))
r = rm3.evaluar([senal(tipo_operacion='long')])
caso('long_3_entradas', abs(r['senales'][0]['risk']['riesgo_pct_efectivo'] - 0.013333) < 1e-4,
     r['senales'][0]['risk']['riesgo_pct_efectivo'])

print(f'\n{OK}/{OK + FALLO} pruebas OK')
sys.exit(1 if FALLO else 0)
