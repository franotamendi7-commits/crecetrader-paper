#!/usr/bin/env python3
"""Test CRUZADO H-07: escenarios.py y risk_manager.py deben dar el MISMO riesgo.
Sin red, PAPER_ONLY.

C11 (Francisco): el riesgo lo define la CONFIANZA, con tope 5%.
Formula unica:  riesgo = confianza x tope   (confianza 0..1, tope 0.05)
"""
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE / 'daily_pilot' / 'core'))
sys.path.insert(0, str(BASE / 'daily_pilot' / 'risk_manager'))
import escenarios as E
import risk_manager as RM

OK = FALLO = 0


def caso(nombre, cond, detalle=''):
    global OK, FALLO
    if cond:
        OK += 1
        print(f'OK    | {nombre} | {detalle}')
    else:
        FALLO += 1
        print(f'FALLO | {nombre} | {detalle}')


# 1. formula base identica en ambos modulos
for conf in (0.02, 0.25, 0.40, 0.50, 0.75, 0.99, 1.00, 1.50):
    caso(f'base_{conf}', abs(E.riesgo_total(conf) - min(conf, 1.0) * 0.05) < 1e-9, str(E.riesgo_total(conf)))

# 2. escenarios
a = E.evaluar(3)
caso('esc_validado_5pct', a['riesgo_sugerido'] == 0.05, str(a['riesgo_sugerido']))
b = E.evaluar(2)
caso('esc_dos_375', b['riesgo_sugerido'] == 0.0375, str(b['riesgo_sugerido']))
c = E.evaluar(1, contradicho=True)
caso('esc_contradecido_125', c['riesgo_sugerido'] == 0.0125, str(c['riesgo_sugerido']))
d = E.evaluar(2, correccion_dentro_de_tendencia=True)
caso('esc_cautela_281', d['riesgo_sugerido'] == 0.0281, str(d['riesgo_sugerido']))

# 3. risk_manager: MISMO valor total que escenarios para la misma confianza
def _senal(**kw):
    base = dict(id='S1', instrument='BTCUSD', direction='compra', entry_low=69000,
                entry_high=71509, invalidation=68500, targets=[72554, 75518],
                evidence=['x'], confidence=0.8, tipo_operacion='long')
    base.update(kw)
    return RM.Signal(**base)

rm = RM.RiskManager(RM.Config(entradas_long=1))   # 1 entrada -> no divide
for conf in (1.0, 0.75, 0.5, 0.25):
    r = rm.evaluar([_senal(confidence=conf)])['senales'][0]['risk']
    caso(f'rm_conf_{conf}', abs(r['riesgo_pct_total'] - E.riesgo_total(conf)) < 1e-4,
         f"rm={r['riesgo_pct_total']} esc={E.riesgo_total(conf)}")

# 4. con 2 entradas, el riesgo por entrada es la mitad del total
rm2 = RM.RiskManager(RM.Config(entradas_long=2))
r2 = rm2.evaluar([_senal(confidence=1.0)])['senales'][0]['risk']
caso('rm_2entradas_mitad', abs(r2['riesgo_pct_efectivo'] - 0.025) < 1e-4, str(r2['riesgo_pct_efectivo']))
caso('rm_2entradas_total', abs(r2['riesgo_pct_total'] - 0.05) < 1e-4, str(r2['riesgo_pct_total']))

# 5. nunca supera el 5%
for n in (1, 2, 3):
    caso(f'esc_tope_{n}', E.evaluar(n)['riesgo_sugerido'] <= E.RIESGO_MAX)
caso('rm_tope', rm.evaluar([_senal(confidence=9.0)])['senales'][0]['risk']['riesgo_pct_total'] <= 0.05)

# 6. paper only
caso('paper_only', E.PAPER_ONLY is True)

print(f'\n{OK}/{OK + FALLO} pruebas OK')
sys.exit(1 if FALLO else 0)
