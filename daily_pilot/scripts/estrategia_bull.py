#!/usr/bin/env python3
"""ESTRATEGIA BULL — pullback en tendencia con filtro de regimen.

Metodo de Francisco:
  - STOP fijo = swing LOW posterior al cambio de tendencia (no se mueve).
  - LOTE = riesgo_usd / (entrada - stop). Riesgo 1-5%.
  - TARGET = extension Fibonacci del swing (1.0 / 1.5 / 2.0).
  - Opcional: mover stop a Break-Even al llegar a 1R.
  - Solo opera en BULLRUN: precio cerca de maximos + pendiente alcista.

PAPER_ONLY: calcula, no ejecuta.
"""
from __future__ import annotations

import json
import math
import random
import statistics
import sys
from pathlib import Path

sys.path.insert(0, '/Users/franciscootamendi/YouTubeTradingAgent/daily_pilot/scripts')
import estrategias_frecuencia as E  # noqa: E402

SCRATCH = Path.home() / '.hermes/cache/scratch/verif'


def ema(vals, n):
    k = 2 / (n + 1)
    out = [None] * len(vals)
    e = None
    for i, x in enumerate(vals):
        e = x if e is None else x * k + e * (1 - k)
        out[i] = e
    return out


def swing_points(v, n=5):
    altos, bajos = [], []
    for i in range(len(v)):
        izq = v[max(0, i - n):i]
        der = v[i + 1:i + 1 + n]
        if len(der) < n:
            continue
        if all(v[i]['high'] >= x['high'] for x in izq + der):
            altos.append((i, v[i]['high']))
        if all(v[i]['low'] <= x['low'] for x in izq + der):
            bajos.append((i, v[i]['low']))
    return altos, bajos


def detectar(v, ema_fast=13, ema_trend=200, swing_n=5, regimen='new_high',
             look_high=120, tol_high=0.03, ret_min=0.0, fibo_ext=1.5,
             be_at=1.0, max_bars=120):
    closes = [x['close'] for x in v]
    highs = [x['high'] for x in v]
    lows = [x['low'] for x in v]
    ef = ema(closes, ema_fast)
    et = ema(closes, ema_trend)
    altos, bajos = swing_points(v, swing_n)
    out = []
    start = ema_trend + swing_n + look_high
    for i in range(start, len(v) - 1):
        if et[i] is None or ef[i] is None:
            continue
        # --- tendencia base
        if closes[i] <= et[i] or ef[i] <= et[i]:
            continue
        # --- filtro de REGIMEN (bullrun)
        if regimen == 'new_high':
            ref = max(highs[i - look_high:i])
            if closes[i] < ref * (1 - tol_high):
                continue
        elif regimen == 'ret_pos':
            if closes[i] / closes[i - 30] - 1 < ret_min:
                continue
        elif regimen == 'slope':
            if et[i] <= et[i - 20]:
                continue
        elif regimen == 'combo':
            if et[i] <= et[i - 20]:
                continue
            if closes[i] < max(highs[i - look_high:i]) * (1 - tol_high):
                continue
            if closes[i] / closes[i - 30] - 1 < ret_min:
                continue
        # --- pullback a EMA rápida y cierre por encima
        if lows[i] > ef[i] * 1.003:
            continue
        if closes[i] <= ef[i]:
            continue
        # --- STOP FIJO = ultimo swing low (bajo post-cambio de tendencia)
        cand = [p for (j, p) in bajos if j < i]
        if not cand:
            continue
        stop = cand[-1]
        entry = closes[i]
        if stop >= entry:
            continue
        # --- TARGET = extension Fibonacci del swing
        cand_h = [p for (j, p) in altos if j < i]
        if cand_h:
            sh = cand_h[-1]
            rng = sh - stop
        else:
            rng = entry - stop
        if rng <= 0:
            continue
        target = stop + rng * fibo_ext
        if target <= entry:
            continue
        out.append({'i': i, 'entry': entry, 'stop': stop, 'target': target,
                    'be_at': be_at, 'max_bars': max_bars})
    return out


def simular(v, senales):
    res = []
    for s in senales:
        i, e, st0, tg = s['i'], s['entry'], s['stop'], s['target']
        risk = e - st0
        if risk <= 0:
            continue
        R = (tg - e) / risk
        be_at = s.get('be_at')
        st = st0
        outcome = 0.0
        for j in range(i + 1, min(i + s.get('max_bars', 120), len(v))):
            hi, lo = v[j]['high'], v[j]['low']
            if be_at and lo <= st0 and hi >= e + be_at * risk:
                st = e
            if lo <= st:
                outcome = 0.0 if st == e else -1.0
                break
            if hi >= tg:
                outcome = R
                break
        res.append(outcome)
    return res


def evaluar(v, detector, n_sim=0, seed=41):
    sen = detector(v)
    out = simular(v, sen)
    m = E.metricas(out)
    A = E.anios(v)
    m['/mes'] = round(m['n'] / A / 12, 1)
    if n_sim:
        m['null'] = E.null_sintetico(v, detector, out, n_sim=n_sim, seed=seed)
    return m


def walk(v, detector, frac=0.7):
    k = int(len(v) * frac)
    a = evaluar(v[:k], detector)
    b = evaluar(v[k:], detector)
    return {'train': {x: a[x] for x in ('n', 'E', 'DD', 'win')},
            'test': {x: b[x] for x in ('n', 'E', 'DD', 'win')},
            'deg_%': round((b['E'] - a['E']) / abs(a['E']) * 100, 1) if a['E'] else None}
