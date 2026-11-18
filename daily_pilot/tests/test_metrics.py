#!/usr/bin/env python3
"""Pruebas de metricas (PAPER_ONLY). Sin red, sin datos externos."""
import json
import sys
import tempfile
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE / 'daily_pilot' / 'metrics'))
import metrics as M

OK = FALLO = 0


def caso(nombre, cond, detalle=''):
    global OK, FALLO
    if cond:
        OK += 1
        print(f'OK    | {nombre} | {detalle}')
    else:
        FALLO += 1
        print(f'FALLO | {nombre} | {detalle}')


def tmpdir():
    d = Path(tempfile.mkdtemp(prefix='metrics_test_'))
    M.SENALES = d / 'senales.jsonl'
    M.RESULTADOS = d / 'resultados.jsonl'
    return d


# 1. sin resultados -> NO DISPONIBLE, no inventa
d = tmpdir()
M.registrar_senal({'id': 'A', 'instrument': 'BTCUSD', 'direction': 'compra', 'nivel': 'escenario',
                   'risk': {'r_multiples': [2.0, 3.0]}}, video_id='v1', fecha='2026-11-16')
r = M.calcular()
caso('sin_resultados_no_disponible', r['disponible'] is False and r['tasa_acierto'] is None, r['motivo'])
caso('expectativa_teorica', r.get('expectativa_teorica_r') == 2.5, r.get('expectativa_teorica_r'))

# 2. con resultados reales
M.registrar_senal({'id': 'B', 'instrument': 'ETHUSD', 'direction': 'compra', 'nivel': 'candidata',
                   'risk': {'r_multiples': [1.5]}}, video_id='v1', fecha='2026-11-16')
M.registrar_resultado('A', 'OBJETIVO_ALCANZADO', 2.0)
M.registrar_resultado('B', 'INVALIDADO', -1.0)
r = M.calcular()
caso('tasa_acierto', r['tasa_acierto'] == 0.5, r['tasa_acierto'])
caso('r_medio', r['r_medio'] == 0.5, r['r_medio'])
caso('expectativa', r['expectativa'] == 0.5, r['expectativa'])   # P0-1: golden +2R/-1R
caso('disponible_muestra_insuficiente', r['disponible'] is False and 'insuficiente' in (r.get('motivo') or ''),
     str(r.get('motivo')))

# 3. drawdown
M.registrar_resultado('B', 'INVALIDADO', -1.0)  # repetido: se ignora en pares por id
r2 = M.calcular()
caso('drawdown_presente', r2.get('drawdown_max') is not None, r2.get('drawdown_max'))

# 4. registro real (6 senales) sin resultados
M.SENALES = BASE / 'daily_pilot' / 'metrics' / 'senales.jsonl'
M.RESULTADOS = BASE / 'daily_pilot' / 'metrics' / 'resultados.jsonl'
r3 = M.calcular()
caso('n_senales_real', r3['n_senales'] >= 6, str(r3['n_senales']))   # P2: robusto
caso('no_inventa', r3['tasa_acierto'] is None and bool(r3.get('advertencia')), str(r3.get('motivo')))

# 5. paper only
caso('paper_only', r3['paper_only'] is True)

print(f'\n{OK}/{OK + FALLO} pruebas OK')
sys.exit(1 if FALLO else 0)
