#!/usr/bin/env python3
"""PROTOCOLO DE VALIDACION - null sintetico + walk-forward (PAPER_ONLY).

Sin dependencias externas (solo stdlib). Implementa:
  1. NULL SINTETICO: 1.000 random walks calibrados a vol/autocorrelacion del par
     (block bootstrap de retornos). Corre la MISMA regla y compara la esperanza
     real contra la distribucion nula. Si no supera el percentil 95 -> ruido.
  2. WALK-FORWARD REAL: rolling o anchored, con purga (H+1) y embargo (1%).
  3. Deflated Sharpe simple, PBO simple, costos en R, percentiles.

Uso:
    python3 daily_pilot/scripts/validacion_protocolo.py BTCUSDT --tf 1d --detalle 150
"""
from __future__ import annotations

import argparse
import json
import math
import random
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE / 'daily_pilot' / 'core'))
sys.path.insert(0, str(BASE / 'daily_pilot' / 'scripts'))

import backtest_afavor as BA  # noqa: E402

PAPER_ONLY = True


# ---------------------------------------------------------------- estadistica stdlib

def _percentil(xs, p):
    if not xs:
        return float('nan')
    xs = sorted(xs)
    if len(xs) == 1:
        return xs[0]
    k = (len(xs) - 1) * (p / 100.0)
    lo = int(math.floor(k))
    hi = int(math.ceil(k))
    if lo == hi:
        return xs[lo]
    frac = k - lo
    return xs[lo] * (1 - frac) + xs[hi] * frac


def _media(xs):
    return (sum(xs) / len(xs)) if xs else 0.0


def _desvio(xs, ddof=1):
    if len(xs) < 2:
        return 0.0
    m = _media(xs)
    var = sum((x - m) ** 2 for x in xs) / max(1, len(xs) - ddof)
    return var ** 0.5


def _skew(xs):
    n = len(xs)
    if n < 3:
        return 0.0
    m = _media(xs)
    m2 = sum((x - m) ** 2 for x in xs) / n
    m3 = sum((x - m) ** 3 for x in xs) / n
    if m2 <= 0:
        return 0.0
    return m3 / (m2 ** 1.5)


def _kurtosis(xs):
    n = len(xs)
    if n < 4:
        return 3.0
    m = _media(xs)
    m2 = sum((x - m) ** 2 for x in xs) / n
    m4 = sum((x - m) ** 4 for x in xs) / n
    if m2 <= 0:
        return 3.0
    return m4 / (m2 ** 2)


def _norm_ppf_moro(p):
    if p <= 0:
        return -8.0
    if p >= 1:
        return 8.0
    if p < 0.5:
        return -_norm_ppf_moro(1.0 - p)
    t = math.sqrt(-2.0 * math.log(1.0 - p))
    c0, c1, c2 = 2.515517, 0.802853, 0.010328
    d1, d2, d3 = 1.432788, 0.189269, 0.001308
    x = t - (c0 + c1 * t + c2 * t * t) / (1 + d1 * t + d2 * t * t + d3 * t * t * t)
    return x


def _phi(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


# ---------------------------------------------------------------- datos

def _cargar_velas(par, tf):
    p = BASE / 'daily_pilot' / 'datos' / 'velas' / f'{par}_{tf}.json'
    if not p.exists():
        return None
    try:
        d = json.loads(p.read_text())
        return d.get('velas')
    except Exception:
        return None


# ---------------------------------------------------------------- evaluacion sobre serie de velas

def _patch_velas(series):
    def _velas(par, tf):
        return [dict(x) for x in series]
    BA._velas = _velas


def evaluar_expectancy(series, tf='1d', detalle=150, filtros=None, stop_modo='pct',
                       stop_pct=2.0, min_muestra=1):
    filtros = filtros or set()
    if len(series) < 30:
        return None
    _patch_velas(series)
    try:
        r = BA.backtest_afavor('SYNTHUSDT', tf, detalle, filtros, stop_modo,
                               stop_pct, min_muestra=min_muestra)
    except Exception:
        return None
    if not isinstance(r, dict) or 'error' in r:
        return None
    agg = r.get('agregado', {})
    if not agg or agg.get('n', 0) == 0:
        return None
    e = agg.get('esperanza_R')
    if e is None:
        return None
    try:
        v = float(e)
    except (TypeError, ValueError):
        return None
    if math.isnan(v) or math.isinf(v):
        return None
    return v


# ---------------------------------------------------------------- 1. NULL SINTETICO

def generar_sintetica(velas, seed=None, block=None):
    rng = random.Random(seed)
    closes = [float(x['close']) for x in velas]
    n = len(closes)
    if n < 5:
        return list(velas)
    rets = [closes[i] / closes[i - 1] - 1.0 for i in range(1, n)]
    m = len(rets)
    if block is None:
        block = max(2, int(round(m ** (1.0 / 3.0))))
    block = max(2, min(block, m))
    synth_rets = []
    while len(synth_rets) < m:
        start = rng.randrange(0, max(1, m - block + 1))
        for k in range(block):
            idx = start + k
            if idx < m and len(synth_rets) < m:
                synth_rets.append(rets[idx])
    synth_closes = [closes[0]]
    for r in synth_rets:
        synth_closes.append(synth_closes[-1] * (1.0 + r))
    out = []
    for i in range(n):
        c = synth_closes[i]
        prev = synth_closes[i - 1] if i > 0 else c
        o = prev
        hi = max(o, c) * (1.0 + 0.003)
        lo = min(o, c) * (1.0 - 0.003)
        out.append({'ts': velas[i]['ts'], 'open': o, 'high': hi,
                    'low': lo, 'close': c, 'volumen': velas[i].get('volumen', 0.0)})
    return out


def null_sintetico(velas, backtest_fn=None, n_sim=1000, block=None, seed=42,
                   tf='1d', detalle=150, filtros=None, stop_modo='pct',
                   stop_pct=2.0, alpha=0.05):
    if backtest_fn is None:
        def backtest_fn(s):
            return evaluar_expectancy(s, tf=tf, detalle=detalle, filtros=filtros,
                                     stop_modo=stop_modo, stop_pct=stop_pct)

    real = backtest_fn(list(velas))
    nulls = []
    for i in range(n_sim):
        synth = generar_sintetica(velas, seed=seed + i, block=block)
        e = backtest_fn(synth)
        if e is None:
            continue
        nulls.append(e)

    if not nulls:
        return {'error': 'null vacio: la estrategia no produjo trades en ninguna serie',
                'real': real, 'n_sim': n_sim, 'n_validas': 0}

    thr = _percentil(nulls, 100 * (1 - alpha))
    if real is None:
        p = 1.0
    else:
        p = sum(1 for x in nulls if x >= real) / len(nulls)

    if real is None:
        veredicto = 'sin trades reales -> no evaluable'
    elif real > thr:
        veredicto = 'REAL SUPERA EL NULL (p<%.2f): posible edge' % alpha
    else:
        veredicto = 'RUIDO: la esperanza real no supera el percentil %.0f del null' % (100 * (1 - alpha))

    return {
        'real_expectancy_R': real,
        'n_sim': n_sim,
        'n_validas': len(nulls),
        'null_media': round(_media(nulls), 4),
        'null_sd': round(_desvio(nulls), 4),
        'null_p05': round(_percentil(nulls, 5), 4),
        'null_p50': round(_percentil(nulls, 50), 4),
        'null_p95': round(thr, 4),
        'null_p99': round(_percentil(nulls, 99), 4),
        'p_valor_empirico': round(p, 4),
        'umbral_percentil': 100 * (1 - alpha),
        'veredicto': veredicto,
    }


# ---------------------------------------------------------------- 2. WALK-FORWARD

def _to_n(x, n):
    if isinstance(x, float) and 0 < x < 1:
        return max(10, int(round(n * x)))
    return int(x)


def walk_forward(candles, train=0.6, test=0.15, purge=6, embargo=0.01,
                 mode='rolling', step=None, max_folds=None, tf='1d',
                 filtros=None, stop_modo='pct', stop_pct=2.0, detalle_is_frac=0.25):
    filtros = filtros or set()
    n = len(candles)
    train_n = _to_n(train, n)
    test_n = _to_n(test, n)
    purge_n = int(purge)
    embargo_n = _to_n(embargo, n)
    gap = purge_n + embargo_n
    if step is None:
        step = test_n
    else:
        step = _to_n(step, n)

    folds = []

    if mode == 'rolling':
        pos = 0
        while pos + train_n + gap + test_n <= n:
            tr = candles[pos:pos + train_n]
            te = candles[pos + train_n + gap:pos + train_n + gap + test_n]
            combined = tr + te
            oos = evaluar_expectancy(combined, tf=tf, detalle=len(te),
                                    filtros=filtros, stop_modo=stop_modo,
                                    stop_pct=stop_pct, min_muestra=1)
            is_det = max(1, int(len(tr) * detalle_is_frac))
            is_e = evaluar_expectancy(tr, tf=tf, detalle=is_det,
                                     filtros=filtros, stop_modo=stop_modo,
                                     stop_pct=stop_pct, min_muestra=1)
            folds.append({
                'fold': len(folds) + 1,
                'train_start': pos,
                'train_end': pos + train_n,
                'test_start': pos + train_n + gap,
                'test_end': pos + train_n + gap + test_n,
                'n_train': len(tr),
                'n_test': len(te),
                'expectancy_is': is_e,
                'expectancy_oos': oos,
                'wfe_fold': (oos / is_e) if (is_e not in (None, 0) and oos is not None) else None,
            })
            pos += step
            if max_folds and len(folds) >= max_folds:
                break
    elif mode == 'anchored':
        train_n_cur = train_n
        fold_idx = 0
        while True:
            gap = purge_n + embargo_n
            te_s = train_n_cur + gap
            te_e = te_s + test_n
            if te_e > n:
                break
            tr = candles[0:train_n_cur]
            te = candles[te_s:te_e]
            combined = tr + te
            oos = evaluar_expectancy(combined, tf=tf, detalle=len(te),
                                    filtros=filtros, stop_modo=stop_modo,
                                    stop_pct=stop_pct, min_muestra=1)
            is_det = max(1, int(len(tr) * detalle_is_frac))
            is_e = evaluar_expectancy(tr, tf=tf, detalle=is_det,
                                     filtros=filtros, stop_modo=stop_modo,
                                     stop_pct=stop_pct, min_muestra=1)
            folds.append({
                'fold': fold_idx + 1,
                'train_start': 0,
                'train_end': train_n_cur,
                'test_start': te_s,
                'test_end': te_e,
                'n_train': len(tr),
                'n_test': len(te),
                'expectancy_is': is_e,
                'expectancy_oos': oos,
                'wfe_fold': (oos / is_e) if (is_e not in (None, 0) and oos is not None) else None,
            })
            train_n_cur += step
            fold_idx += 1
            if max_folds and fold_idx >= max_folds:
                break
    else:
        raise ValueError("mode debe ser 'rolling' o 'anchored'")

    oos_vals = [f['expectancy_oos'] for f in folds if f['expectancy_oos'] is not None]
    is_vals = [f['expectancy_is'] for f in folds if f['expectancy_is'] is not None]
    n_pos = sum(1 for x in oos_vals if x > 0)
    resumen = {
        'mode': mode,
        'n_folds': len(folds),
        'folds_positivos_oos': n_pos,
        'pct_folds_positivos': (round(100.0 * n_pos / len(oos_vals), 1) if oos_vals else 0.0),
        'mean_expectancy_oos': (round(_media(oos_vals), 4) if oos_vals else None),
        'mean_expectancy_is': (round(_media(is_vals), 4) if is_vals else None),
        'wfe_global': (round(_media(oos_vals) / _media(is_vals), 3)
                      if (oos_vals and is_vals and _media(is_vals) != 0) else None),
        'folds': folds,
    }
    return resumen


# ---------------------------------------------------------------- 3. SIGNIFICANCIA

def sharpe(returns):
    n = len(returns)
    if n < 2:
        return 0.0
    sd = _desvio(returns, ddof=1)
    if sd == 0:
        return 0.0
    return _media(returns) / sd


def deflated_sharpe(returns, n_trials=1):
    n = len(returns)
    if n < 3:
        return {'sharpe': 0.0, 'dsr': 0.0, 'p_valor': 1.0, 'n_trials': n_trials}
    sr = sharpe(returns)
    sk = _skew(returns)
    ku = _kurtosis(returns)
    se = math.sqrt(max(1e-12, (1.0 + (sk * sr) / 6.0 +
                               (ku - 3.0) * sr * sr / 24.0) / n))
    if n_trials and n_trials > 1:
        g = 0.5772156649
        z1 = _norm_ppf_moro(1.0 - 1.0 / n_trials)
        z2 = _norm_ppf_moro(1.0 - 1.0 / (n_trials * math.e))
        emax = (1 - g) * z1 + g * z2
    else:
        emax = 0.0
    sr0 = emax * se
    dsr = (sr - sr0) / se if se > 0 else 0.0
    p = 1.0 - _phi(dsr)
    return {
        'sharpe': round(sr, 4),
        'dsr': round(dsr, 4),
        'p_valor': round(p, 4),
        'n_trials': n_trials,
        'n_obs': n,
        'veredicto': 'SIGNIFICATIVO (DSR>0)' if dsr > 0 else 'no significativo (DSR<=0)',
    }


def pbo_simple(perf):
    configs = list(perf.keys())
    if not configs:
        return {'pbo': None, 'n_folds': 0}
    n_folds = len(perf[configs[0]])
    if n_folds == 0:
        return {'pbo': None, 'n_folds': 0}
    malos = 0
    for f in range(n_folds):
        best = None
        best_score = None
        for c in configs:
            otros = [perf[c][k] for k in range(n_folds) if k != f]
            if not otros:
                continue
            sc = _media(otros)
            if best_score is None or sc > best_score:
                best_score = sc
                best = c
        if best is None:
            continue
        oos_best = perf[best][f]
        oos_todos = sorted(perf[c][f] for c in configs)
        med = _percentil(oos_todos, 50)
        if oos_best < med:
            malos += 1
    pbo = malos / n_folds
    return {'pbo': round(pbo, 4), 'n_folds': n_folds,
            'veredicto': 'OK (PBO<=0.20)' if pbo <= 0.20 else 'ALTO (PBO>0.20)'}


def costos_R(entry, risk, comision_pct=0.10, slippage_pct=0.05):
    if risk <= 0 or entry <= 0:
        return 0.0
    pct_total = 2.0 * (comision_pct + slippage_pct) / 100.0
    return pct_total * entry / risk


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description='Protocolo de validacion (null + walk-forward)')
    ap.add_argument('par')
    ap.add_argument('--tf', default='1d')
    ap.add_argument('--detalle', type=int, default=150)
    ap.add_argument('--filtros', default='')
    ap.add_argument('--stop', default='pct', choices=['pct', 'estructural', 'atr'])
    ap.add_argument('--stop-pct', type=float, default=2.0)
    ap.add_argument('--null-sim', type=int, default=1000)
    ap.add_argument('--null-block', type=int, default=None)
    ap.add_argument('--null-seed', type=int, default=42)
    ap.add_argument('--wf-mode', default='rolling', choices=['rolling', 'anchored'])
    ap.add_argument('--wf-train', default='0.6')
    ap.add_argument('--wf-test', default='0.15')
    ap.add_argument('--wf-purge', type=int, default=6)
    ap.add_argument('--wf-embargo', default='0.01')
    ap.add_argument('--wf-step', default=None)
    ap.add_argument('--wf-max-folds', type=int, default=None)
    ap.add_argument('--n-trials', type=int, default=1)
    ap.add_argument('--skip-null', action='store_true')
    ap.add_argument('--skip-wf', action='store_true')
    a = ap.parse_args()

    par = a.par.upper()
    filtros = {x.strip().upper() for x in a.filtros.split(',') if x.strip()}
    velas = _cargar_velas(par, a.tf)
    if not velas:
        print(json.dumps({'error': f'sin datos para {par} {a.tf}'}, ensure_ascii=False))
        return 1

    def _parse_frac(s):
        try:
            return float(s)
        except (TypeError, ValueError):
            return s

    out = {'par': par, 'tf': a.tf, 'n_velas': len(velas), 'paper_only': True}

    if not a.skip_null:
        print(f'[null] {a.null_sim} simulaciones...', file=sys.stderr)
        null_res = null_sintetico(
            velas, n_sim=a.null_sim, block=a.null_block, seed=a.null_seed,
            tf=a.tf, detalle=a.detalle, filtros=filtros, stop_modo=a.stop,
            stop_pct=a.stop_pct)
        out['null_sintetico'] = null_res

    if not a.skip_wf:
        print(f'[wf] mode={a.wf_mode}...', file=sys.stderr)
        wf_res = walk_forward(
            velas, train=_parse_frac(a.wf_train), test=_parse_frac(a.wf_test),
            purge=a.wf_purge, embargo=_parse_frac(a.wf_embargo),
            mode=a.wf_mode, step=(_parse_frac(a.wf_step) if a.wf_step else None),
            max_folds=a.wf_max_folds, tf=a.tf, filtros=filtros,
            stop_modo=a.stop, stop_pct=a.stop_pct)
        out['walk_forward'] = wf_res

    if 'walk_forward' in out and out['walk_forward'].get('folds'):
        series = [f['expectancy_oos'] for f in out['walk_forward']['folds']
                  if f['expectancy_oos'] is not None]
        if series:
            out['deflated_sharpe'] = deflated_sharpe(series, n_trials=a.n_trials)

    last = velas[-1]['close']
    risk = last * 0.02
    out['costos_R_ejemplo'] = round(costos_R(last, risk), 4)

    print(json.dumps(out, indent=1, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
