#!/usr/bin/env python3
"""Estrategias de ALTA FRECUENCIA (PAPER_ONLY).

  1 · Mean-reversion en rango: comprar soporte, vender mitad/todo el rango.
  2 · Pullback en tendencia: comprar el retorno a EMA rápida con tendencia a favor.

Mide frecuencia real (señales/mes), expectancy en R, drawdown y factor beneficio.
Valida con null sintético (block bootstrap) y walk-forward train/test.

NO ejecuta ordenes. Solo lee velas y escribe resultados.
"""
from __future__ import annotations

import json
import math
import random
import statistics
import sys
from pathlib import Path

SCRATCH = Path.home() / '.hermes/cache/scratch/verif'


def cargar(par: str, tf: str):
    p = SCRATCH / f'{par}_{tf}.json'
    if not p.exists():
        return None
    return json.loads(p.read_text())['velas']


def ema(vals, n):
    k = 2 / (n + 1)
    out = [None] * len(vals)
    e = None
    for i, x in enumerate(vals):
        e = x if e is None else x * k + e * (1 - k)
        out[i] = e
    return out


def prev_min(vals, n):
    out = [None] * len(vals)
    for i in range(n, len(vals)):
        out[i] = min(vals[i - n:i])
    return out


def prev_max(vals, n):
    out = [None] * len(vals)
    for i in range(n, len(vals)):
        out[i] = max(vals[i - n:i])
    return out


def swing_lows(velas, n=3):
    """Bajos swing reales: un minimo es swing si es el mas bajo de n velas a cada lado."""
    bajos = []
    for i in range(len(velas)):
        der = velas[i + 1:i + 1 + n]
        izq = velas[max(0, i - n):i]
        if len(der) < n:
            continue
        if all(velas[i]['low'] <= x['low'] for x in izq + der):
            bajos.append((i, velas[i]['low']))
    return bajos


def stop_swing_entry(entry_idx, lows, velas, n=3):
    """STOP FIJO: el ultimo swing LOW antes de la entrada.

    Es el bajo posterior al cambio de tendencia (estructura), no un minimo
    movil de las ultimas N velas. Se calcula UNA VEZ y no se mueve.
    """
    cand = [p for (i, p) in lows if i < entry_idx]
    return cand[-1] if cand else None


def size_position(riesgo_usd, entry, stop):
    """Cantidad segun el stop FIJO: unidades = riesgo_usd / distancia_al_stop.

    Devuelve ademas notional y margen a 20x. Nunca se mueve el stop para
    cambiar el tamano: siempre se mueve la cantidad.
    """
    dist = entry - stop
    if dist <= 0:
        return None
    und = riesgo_usd / dist
    return {'unidades': round(und, 6),
            'notional': round(und * entry, 2),
            'margen_20x': round(und * entry / 20, 2),
            'dist_stop': round(dist, 4)}


# ------------------------------------------------------------------ detector 1
def detectar_rango(v, lookback=30, max_rango_pct=0.12, tol=0.001,
                   target_k=0.5, swing_n=3):
    """Long: el precio toca el soporte del rango y cierra por encima."""
    lows = [x['low'] for x in v]
    highs = [x['high'] for x in v]
    closes = [x['close'] for x in v]
    sups = prev_min(lows, lookback)
    ress = prev_max(highs, lookback)
    sw = swing_lows(v, swing_n)
    out = []
    for i in range(lookback + swing_n, len(v) - 1):
        sup, res = sups[i], ress[i]
        if not sup or not res or sup <= 0:
            continue
        rng = res - sup
        if rng / sup > max_rango_pct:      # hay tendencia, no rango
            continue
        if lows[i] > sup * (1 + tol):      # no touchó soporte
            continue
        if closes[i] <= sup:               # no recuperó
            continue
        entry = closes[i]
        stop = stop_swing_entry(i, sw, v, swing_n)
        if stop is None or stop >= entry:
            continue
        target = sup + rng * target_k
        if target <= entry:
            continue
        out.append({'i': i, 'entry': entry, 'stop': stop, 'target': target})
    return out


# ------------------------------------------------------------------ detector 2
def detectar_pullback(v, ema_fast=21, ema_trend=200, tol=0.002,
                      swing_n=3, target_R=2.0, regimen=None):
    """Long: tendencia alcista + precio que vuelve a EMA rápida y cierra arriba.

    regimen=None       → sin filtro extra
    regimen='ema50_up' → EMA50 con pendiente positiva (10 velas)
    regimen='strong'   → precio >= 3% sobre EMA200
    """
    lows = [x['low'] for x in v]
    closes = [x['close'] for x in v]
    ef = ema(closes, ema_fast)
    et = ema(closes, ema_trend)
    e50 = ema(closes, 50) if regimen == 'ema50_up' else None
    sw = swing_lows(v, swing_n)
    out = []
    for i in range(ema_trend + swing_n, len(v) - 1):
        if et[i] is None or ef[i] is None:
            continue
        if closes[i] <= et[i] or ef[i] <= et[i]:   # sin tendencia alcista
            continue
        if regimen == 'ema50_up' and (e50[i] is None or e50[i - 10] is None or e50[i] <= e50[i - 10]):
            continue
        if regimen == 'strong' and closes[i] < et[i] * 1.03:
            continue
        if lows[i] > ef[i] * (1 + tol):            # no hizo pullback
            continue
        if closes[i] <= ef[i]:                     # no recuperó
            continue
        entry = closes[i]
        stop = stop_swing_entry(i, sw, v, swing_n)
        if stop is None or stop >= entry:
            continue
        target = entry + target_R * (entry - stop)
        out.append({'i': i, 'entry': entry, 'stop': stop, 'target': target})
    return out


# ------------------------------------------------------------------ simulacion
def simular(v, senales, max_bars=120):
    res = []
    for s in senales:
        i, e, st, tg = s['i'], s['entry'], s['stop'], s['target']
        risk = e - st
        if risk <= 0:
            continue
        R = (tg - e) / risk
        outcome = 0.0
        for j in range(i + 1, min(i + max_bars, len(v))):
            if v[j]['low'] <= st:
                outcome = -1.0
                break
            if v[j]['high'] >= tg:
                outcome = R
                break
        res.append(outcome)
    return res


def metricas(out):
    if not out:
        return {'n': 0, 'E': 0.0, 'win': 0.0, 'total': 0.0, 'DD': 0.0, 'PF': 0.0}
    eq = peak = 0.0
    dd = 0.0
    for o in out:
        eq += o
        peak = max(peak, eq)
        dd = min(dd, eq - peak)
    wins = [o for o in out if o > 0]
    losses = [o for o in out if o <= 0]
    sw, sl = sum(wins), abs(sum(losses))
    return {'n': len(out),
            'E': round(statistics.mean(out), 3),
            'win': round(100 * len(wins) / len(out), 1),
            'total': round(eq, 1),
            'DD': round(dd, 1),
            'PF': round(sw / sl, 2) if sl else None}


def anios(v):
    return (v[-1]['ts'] - v[0]['ts']) / (1000 * 86400 * 365.25)


def evaluar(v, detector, n_sim=0, seed=7, block=24):
    sen = detector(v)
    out = simular(v, sen)
    m = metricas(out)
    A = anios(v)
    m['/año'] = round(m['n'] / A, 1)
    m['/mes'] = round(m['n'] / A / 12, 1)
    if n_sim:
        m['null'] = null_sintetico(v, detector, out, n_sim=n_sim, seed=seed, block=block)
    return m


# ------------------------------------------------------------------ null sintetico
def null_sintetico(v, detector, out_real, n_sim=150, seed=7, block=24):
    """Block bootstrap de retornos: re-construye la serie y vuelve a correr el detector."""
    closes = [x['close'] for x in v]
    rets = [math.log(closes[i] / closes[i - 1]) for i in range(1, len(closes))]
    rng = random.Random(seed)
    real_E = statistics.mean(out_real) if out_real else 0.0
    sims = []
    ratios_h = [x['high'] / x['close'] if x['close'] else 1.0 for x in v]
    ratios_l = [x['low'] / x['close'] if x['close'] else 1.0 for x in v]
    for _ in range(n_sim):
        nr = []
        while len(nr) < len(rets):
            s = rng.randrange(0, max(1, len(rets) - block))
            nr.extend(rets[s:s + block])
        nr = nr[:len(rets)]
        c = closes[0]
        cls = [c]
        for r in nr:
            c *= math.exp(r)
            cls.append(c)
        vv = [{'ts': x['ts'], 'open': cls[i], 'high': cls[i] * ratios_h[i],
               'low': cls[i] * ratios_l[i], 'close': cls[i],
               'volumen': x.get('volumen', 0)} for i, x in enumerate(v)]
        so = simular(vv, detector(vv))
        sims.append(statistics.mean(so) if so else 0.0)
    sims.sort()
    p = sum(1 for s in sims if s >= real_E) / len(sims)
    return {'real': round(real_E, 3),
            'p50': round(sims[len(sims) // 2], 3),
            'p95': round(sims[int(0.95 * len(sims))], 3),
            'p': round(p, 3),
            'veredicto': 'PASA' if p <= 0.05 else 'RUIDO'}


# ------------------------------------------------------------------ walk forward
def walk_forward(v, detector, frac=0.7):
    k = int(len(v) * frac)
    # separar en velas, recalculando indicadores dentro de cada segmento
    a = evaluar(v[:k], detector)
    b = evaluar(v[k:], detector)
    return {'train': {x: a[x] for x in ('n', 'E', 'DD', 'win')},
            'test': {x: b[x] for x in ('n', 'E', 'DD', 'win')},
            'degradacion_%': round((b['E'] - a['E']) / abs(a['E']) * 100, 1) if a['E'] else None}
