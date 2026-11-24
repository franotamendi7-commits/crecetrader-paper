#!/usr/bin/env python3
"""Busqueda exhaustiva de estrategia ganadora (BTC/ETH) — RUPTURA DE TRAMO.

PAPER_ONLY. No toca metodo/ ni FIRMA. No escribe store vivo.

Uso:
  python3 daily_pilot/scripts/busqueda_estrategia.py --par BTCUSDT --tfs 1d 4h 1h --validar
  python3 daily_pilot/scripts/busqueda_estrategia.py --par ETHUSDT --tfs 1d 4h
"""
from __future__ import annotations

import argparse
import json
import math
import random
import sys
import time
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
PILOT = BASE / 'daily_pilot'
sys.path.insert(0, str(PILOT / 'core'))
sys.path.insert(0, str(PILOT / 'scripts'))

import validacion_protocolo as VP

PAPER_ONLY = True

# ---------------------------------------------------------------- utils

def cargar_velas(par, tf):
    p = PILOT / 'datos' / 'velas' / f'{par}_{tf}.json'
    d = json.loads(p.read_text())
    return d['velas']


def ema(closes, w):
    out = [None] * len(closes)
    if len(closes) < w:
        return out
    k = 2.0 / (w + 1)
    out[w - 1] = sum(closes[:w]) / w
    for i in range(w, len(closes)):
        out[i] = closes[i] * k + out[i - 1] * (1 - k)
    return out


def atr_pct(velas, w=14):
    trs = [0.0] * len(velas)
    for i in range(1, len(velas)):
        h, l, pc = velas[i]['high'], velas[i]['low'], velas[i - 1]['close']
        trs[i] = max(h - l, abs(h - pc), abs(l - pc))
    out = [None] * len(velas)
    for i in range(w, len(velas)):
        out[i] = (sum(trs[i - w + 1:i + 1]) / w) / velas[i]['close'] * 100.0
    return out


def swing_extrema(velas, n):
    altos, bajos = [], []
    for i in range(len(velas)):
        v = velas[i]
        izq = velas[max(0, i - n):i]
        der = velas[i + 1:i + 1 + n]
        if len(der) < n:
            continue
        if all(v['high'] >= x['high'] for x in izq + der):
            altos.append((i, v['high']))
        if all(v['low'] <= x['low'] for x in izq + der):
            bajos.append((i, v['low']))
    return altos, bajos


def comprimir_extremos(altos, bajos):
    pts = sorted([(i, 'max', p) for i, p in altos] + [(i, 'min', p) for i, p in bajos])
    # compress consecutive same type, keep more extreme
    comp = []
    for p in pts:
        if comp and comp[-1][1] == p[1]:
            # keep more extreme
            if p[1] == 'max' and p[2] > comp[-1][2]:
                comp[-1] = p
            elif p[1] == 'min' and p[2] < comp[-1][2]:
                comp[-1] = p
        else:
            comp.append(p)
    return comp


def detectar_tramos(velas, w):
    altos, bajos = swing_extrema(velas, w)
    comp = comprimir_extremos(altos, bajos)
    tramos = []
    for a, b in zip(comp, comp[1:]):
        if a[0] >= b[0]:
            continue
        if a[1] == 'max' and b[1] == 'min':
            tramos.append({
                'dir_tramo': 'bajista',  # peak->trough
                'peak_idx': a[0], 'peak_px': a[2],
                'trough_idx': b[0], 'trough_px': b[2],
                'high': a[2], 'low': b[2],
                'len': b[0] - a[0] + 1,
            })
        elif a[1] == 'min' and b[1] == 'max':
            tramos.append({
                'dir_tramo': 'alcista',  # trough->peak
                'trough_idx': a[0], 'trough_px': a[2],
                'peak_idx': b[0], 'peak_px': b[2],
                'high': b[2], 'low': a[2],
                'len': b[0] - a[0] + 1,
            })
    return tramos


def construir_setups(velas, tf, tramo_n):
    closes = [x['close'] for x in velas]
    e200 = ema(closes, 200)
    e50 = ema(closes, 50)
    atrp = atr_pct(velas, 14)
    setups = []
    tramos = detectar_tramos(velas, tramo_n)
    # swing extrema for stop candidates: precompute for n=3,5,8
    swing_cache = {}
    for n in (3, 5, 8):
        swing_cache[n] = swing_extrema(velas, n)

    def last_swing_before(idx, n, tipo):
        # tipo 'low' for long (bajos), 'high' for short (altos)
        lst = swing_cache[n][0] if tipo == 'high' else swing_cache[n][1]
        cand = [p for (i, p) in lst if i < idx]
        return cand[-1] if cand else None

    for tr in tramos:
        # LONG candidate: tramo bajista, breakout above high after trough
        if tr['dir_tramo'] == 'bajista':
            peak_idx = tr['peak_idx']; trough_idx = tr['trough_idx']
            high = tr['high']; low = tr['low']
            rng = high - low
            if rng <= 0:
                continue
            # entry search after trough
            entry_idx = None
            for j in range(trough_idx + 1, len(velas)):
                if velas[j]['close'] > high:
                    entry_idx = j
                    break
            if entry_idx is None:
                continue
            entry = velas[entry_idx]['close']
            # metadata
            ei = entry_idx
            ema200v = e200[ei]
            ema50v = e50[ei]
            ema50prev = e50[ei - 5] if ei - 5 >= 0 else None
            atrv = atrp[ei]
            # ema50 slope
            slope_up = (ema50v is not None and ema50prev is not None and ema50v > ema50prev)
            slope_down = (ema200v is not None and ema50v is not None and ema50v < ema50prev) if (ema50v is not None and ema50prev is not None) else False
            # regime: range if price between ema50 and ema200
            if ema50v is not None and ema200v is not None:
                lo_e, hi_e = sorted([ema50v, ema200v])
                in_range = lo_e < entry < hi_e
            else:
                in_range = False
            trend_up = (ema200v is not None and entry > ema200v and slope_up)
            trend_down = (ema200v is not None and entry < ema200v and slope_down)
            setups.append({
                'side': 'long',
                'entry_idx': ei,
                'entry': entry,
                'high': high, 'low': low, 'range': rng,
                'tramo_len': tr['len'],
                'base_stop': low,
                'swing3': last_swing_before(ei, 3, 'low'),
                'swing5': last_swing_before(ei, 5, 'low'),
                'swing8': last_swing_before(ei, 8, 'low'),
                'ema200': ema200v,
                'ema50': ema50v,
                'ema50slope_up': slope_up,
                'atr_pct': atrv,
                'in_range': in_range,
                'trend_up': trend_up,
                'trend_down': trend_down,
                'tramo_n': tramo_n,
            })
        # SHORT candidate: tramo alcista, breakout below low after peak
        if tr['dir_tramo'] == 'alcista':
            peak_idx = tr['peak_idx']; trough_idx = tr['trough_idx']
            high = tr['high']; low = tr['low']
            rng = high - low
            if rng <= 0:
                continue
            entry_idx = None
            for j in range(peak_idx + 1, len(velas)):
                if velas[j]['close'] < low:
                    entry_idx = j
                    break
            if entry_idx is None:
                continue
            entry = velas[entry_idx]['close']
            ei = entry_idx
            ema200v = e200[ei]
            ema50v = e50[ei]
            ema50prev = e50[ei - 5] if ei - 5 >= 0 else None
            atrv = atrp[ei]
            slope_up = (ema50v is not None and ema50prev is not None and ema50v > ema50prev)
            slope_down = (ema50v is not None and ema50prev is not None and ema50v < ema50prev)
            if ema50v is not None and ema200v is not None:
                lo_e, hi_e = sorted([ema50v, ema200v])
                in_range = lo_e < entry < hi_e
            else:
                in_range = False
            trend_up = (ema200v is not None and entry > ema200v and slope_up)
            trend_down = (ema200v is not None and entry < ema200v and slope_down)
            setups.append({
                'side': 'short',
                'entry_idx': ei,
                'entry': entry,
                'high': high, 'low': low, 'range': rng,
                'tramo_len': tr['len'],
                'base_stop': high,
                'swing3': last_swing_before(ei, 3, 'high'),
                'swing5': last_swing_before(ei, 5, 'high'),
                'swing8': last_swing_before(ei, 8, 'high'),
                'ema200': ema200v,
                'ema50': ema50v,
                'ema50slope_up': slope_up,
                'ema50slope_down': slope_down,
                'atr_pct': atrv,
                'in_range': in_range,
                'trend_up': trend_up,
                'trend_down': trend_down,
                'tramo_n': tramo_n,
            })
    return setups


def costo_R(entry, risk):
    return VP.costos_R(entry, risk, comision_pct=0.10, slippage_pct=0.05)


def aplicar_filtros(s, filters):
    # filters: set of strings
    if 'ema200' in filters:
        if s['side'] == 'long':
            if not (s['ema200'] is not None and s['entry'] > s['ema200']):
                return False
        else:
            if not (s['ema200'] is not None and s['entry'] < s['ema200']):
                return False
    if 'ema50slope' in filters:
        if s['side'] == 'long':
            if not s.get('ema50slope_up', False):
                return False
        else:
            if not s.get('ema50slope_down', False):
                return False
    if 'atr_low' in filters:
        if not (s['atr_pct'] is not None and s['atr_pct'] < 2.5):
            return False
    if 'atr_high' in filters:
        if not (s['atr_pct'] is not None and s['atr_pct'] > 4.0):
            return False
    if 'tramo_min10' in filters:
        if s['tramo_len'] < 10:
            return False
    if 'tramo_min20' in filters:
        if s['tramo_len'] < 20:
            return False
    if 'tramo_min30' in filters:
        if s['tramo_len'] < 30:
            return False
    if 'regime_trend' in filters:
        if s['side'] == 'long':
            if not s.get('trend_up', False):
                return False
        else:
            if not s.get('trend_down', False):
                return False
    if 'regime_range' in filters:
        if not s.get('in_range', False):
            return False
    return True


def stop_price(s, stop_mode):
    entry = s['entry']
    if stop_mode == 'tramo':
        return s['base_stop']
    if stop_mode == 'swing3':
        v = s['swing3']
        return v if v is not None else s['base_stop']
    if stop_mode == 'swing5':
        v = s['swing5']
        return v if v is not None else s['base_stop']
    if stop_mode == 'swing8':
        v = s['swing8']
        return v if v is not None else s['base_stop']
    if stop_mode == 'pct1':
        return entry * (1 - 0.01) if s['side'] == 'long' else entry * (1 + 0.01)
    if stop_mode == 'pct2':
        return entry * (1 - 0.02) if s['side'] == 'long' else entry * (1 + 0.02)
    if stop_mode == 'pct3':
        return entry * (1 - 0.03) if s['side'] == 'long' else entry * (1 + 0.03)
    raise ValueError(stop_mode)


def simular_trade(s, velas, ext, stop_mode, be_trigger, gestion):
    entry = s['entry']
    side = s['side']
    ei = s['entry_idx']
    sp = stop_price(s, stop_mode)
    if sp is None:
        return None
    if side == 'long':
        risk = entry - sp
    else:
        risk = sp - entry
    if risk <= 0:
        return None
    # target fibo
    rng = s['range']
    if side == 'long':
        target_fibo = s['low'] + rng * ext
    else:
        target_fibo = s['high'] - rng * ext
    R_target = (target_fibo - entry) / risk if side == 'long' else (entry - target_fibo) / risk
    cost = costo_R(entry, risk)
    # exit sim
    stop = sp
    be_done = False
    partial_done = False
    realized = 0.0
    remaining = 1.0
    tranches = [False, False, False]
    t_targets = [entry + risk, entry + 2 * risk, entry + 3 * risk] if side == 'long' else \
                [entry - risk, entry - 2 * risk, entry - 3 * risk]
    # helper to check target hit for side
    def high_ge(price, level):
        return price >= level if side == 'long' else price <= level
    # We'll iterate bars
    n = len(velas)
    for j in range(ei + 1, n):
        y = velas[j]
        hi = y['high']; lo = y['low']
        # BE trigger
        if be_trigger is not None and not be_done:
            trig_level = entry + be_trigger * risk if side == 'long' else entry - be_trigger * risk
            if (hi >= trig_level) if side == 'long' else (lo <= trig_level):
                be_done = True
                stop = entry
        # scaled tranche TP
        if gestion == 'scaled':
            for ti in range(3):
                if not tranches[ti]:
                    if (hi >= t_targets[ti]) if side == 'long' else (lo <= t_targets[ti]):
                        tranches[ti] = True
                        realized += (1.0 / 3.0) * (ti + 1)
                        remaining -= (1.0 / 3.0)
            if all(tranches):
                return realized - cost
        # half partial at +1R
        if gestion == 'half' and not partial_done:
            lvl = entry + risk if side == 'long' else entry - risk
            if (hi >= lvl) if side == 'long' else (lo <= lvl):
                partial_done = True
                realized += 0.5 * 1.0
                remaining = 0.5
        # stop check
        stop_hit = (lo <= stop) if side == 'long' else (hi >= stop)
        # target check (fibo) for full/half
        target_hit = False
        if gestion in ('full', 'half'):
            target_hit = (hi >= target_fibo) if side == 'long' else (lo <= target_fibo)
        # pessimistic: stop first if both
        if stop_hit:
            if gestion == 'scaled':
                for ti in range(3):
                    if not tranches[ti]:
                        realized += (1.0 / 3.0) * (-1.0)
                return realized - cost
            if gestion == 'half':
                if partial_done:
                    if stop == entry:
                        realized += 0.0
                    else:
                        realized += remaining * (-1.0)
                else:
                    realized = 0.0 if stop == entry else -1.0
                return realized - cost
            # full
            return (0.0 if stop == entry else -1.0) - cost
        if target_hit:
            if gestion == 'half':
                if partial_done:
                    realized += remaining * R_target
                else:
                    realized = R_target
                return realized - cost
            if gestion == 'full':
                return R_target - cost
    # no hit by end: pessimistic stop
    if gestion == 'scaled':
        for ti in range(3):
            if not tranches[ti]:
                realized += (1.0 / 3.0) * (-1.0)
        return realized - cost
    if gestion == 'half':
        if partial_done:
            realized += remaining * (0.0 if stop == entry else -1.0)
        else:
            realized = 0.0 if stop == entry else -1.0
        return realized - cost
    return (0.0 if stop == entry else -1.0) - cost


def metricas(outs):
    if not outs:
        return {'n': 0}
    pos = [o for o in outs if o > 0]
    neg = [o for o in outs if o < 0]
    pf = (sum(pos) / abs(sum(neg))) if (neg and sum(neg) != 0) else (float('inf') if pos else 0.0)
    cum = peak = dd = 0.0
    for o in outs:
        cum += o
        peak = max(peak, cum)
        dd = min(dd, cum - peak)
    racha = mx = 0
    for o in outs:
        if o < 0:
            racha += 1
            mx = max(mx, racha)
        else:
            racha = 0
    return {
        'n': len(outs),
        'acierto_pct': round(len(pos) / len(outs) * 100, 1),
        'factor_beneficio': (round(pf, 3) if pf != float('inf') else None),
        'esperanza_R': round(sum(outs) / len(outs), 4),
        'total_R': round(cum, 2),
        'drawdown_R': round(dd, 2),
        'max_racha_perdidas': mx,
    }


def montecarlo(outs, n_sim=500, seed=7):
    if not outs:
        return {}
    rnd = random.Random(seed)
    medias, dds = [], []
    for _ in range(n_sim):
        muestra = [rnd.choice(outs) for _ in outs]
        m = metricas(muestra)
        medias.append(m['esperanza_R'])
        dds.append(m['drawdown_R'])
    medias.sort(); dds.sort()
    def q(a, p):
        return a[min(len(a) - 1, int(p * len(a)))]
    return {
        'sims': n_sim,
        'esp_media': round(sum(medias) / len(medias), 4),
        'esp_p5': round(q(medias, 0.05), 4),
        'esp_p50': round(q(medias, 0.50), 4),
        'esp_p95': round(q(medias, 0.95), 4),
        'dd_p95': round(q(dds, 0.95), 2),
        'prob_esp_negativa': round(sum(1 for m in medias if m < 0) / len(medias), 3),
    }


def walk_forward_simple(velas, tf, params, n_splits=3):
    # 2/3 train, 1/3 test by time, using setups filtered; approximate by splitting velas
    n = len(velas)
    cut = int(n * 2 / 3)
    train_v = velas[:cut]
    test_v = velas[cut:]
    def run(vs):
        setups = []
        for tn in params['tramo_ns']:
            setups += construir_setups(vs, tf, tn)
        outs = []
        for s in setups:
            if params['direction'] not in ('both', s['side']):
                # direction filter: if direction long, only long
                if params['direction'] == 'long' and s['side'] != 'long':
                    continue
                if params['direction'] == 'short' and s['side'] != 'short':
                    continue
            if not aplicar_filtros(s, params['filters']):
                continue
            o = simular_trade(s, vs, params['ext'], params['stop_mode'], params['be'], params['gestion'])
            if o is not None:
                outs.append(o)
        return outs
    oos_train = run(train_v)
    oos_test = run(test_v)
    return {
        'train': metricas(oos_train),
        'test': metricas(oos_test),
        'degradacion_pct': (round((metricas(oos_test)['esperanza_R'] - metricas(oos_train)['esperanza_R']) /
                                 (abs(metricas(oos_train)['esperanza_R']) + 1e-9) * 100, 1)
                            if oos_train and oos_test else None),
    }


def null_sintetico_propio(velas, params, tf, n_sim=300, seed=42):
    def backtest_fn(series):
        setups = []
        for tn in params['tramo_ns']:
            setups += construir_setups(series, tf, tn)
        outs = []
        for s in setups:
            if params['direction'] == 'long' and s['side'] != 'long':
                continue
            if params['direction'] == 'short' and s['side'] != 'short':
                continue
            if not aplicar_filtros(s, params['filters']):
                continue
            o = simular_trade(s, series, params['ext'], params['stop_mode'], params['be'], params['gestion'])
            if o is not None:
                outs.append(o)
        if not outs:
            return None
        return sum(outs) / len(outs)
    real = backtest_fn(list(velas))
    nulls = []
    for i in range(n_sim):
        synth = VP.generar_sintetica(velas, seed=seed + i)
        e = backtest_fn(synth)
        if e is None:
            continue
        nulls.append(e)
    if not nulls:
        return {'error': 'null vacio', 'real': real}
    thr = VP._percentil(nulls, 95)
    p = sum(1 for x in nulls if x >= real) / len(nulls) if real is not None else 1.0
    veredicto = 'REAL SUPERA NULL' if (real is not None and real > thr) else 'RUIDO'
    return {
        'real_expectancy_R': real,
        'n_sim': n_sim,
        'n_validas': len(nulls),
        'null_p95': round(thr, 4),
        'null_media': round(VP._media(nulls), 4),
        'p_valor_empirico': round(p, 4),
        'veredicto': veredicto,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--par', default='BTCUSDT')
    ap.add_argument('--tfs', nargs='+', default=['1d', '4h', '1h'])
    ap.add_argument('--validar', action='store_true', help='validar top variantes')
    ap.add_argument('--top', type=int, default=5)
    ap.add_argument('--max-variants', type=int, default=None)
    args = ap.parse_args()

    par = args.par.upper()
    t0 = time.time()

    # grid dimensions
    tramo_ns_list = [3, 5, 8]
    exts = [0.5, 1.0, 1.25, 1.5, 1.75, 2.0, 3.0]
    stop_modes = ['tramo', 'swing3', 'swing5', 'swing8', 'pct1', 'pct2', 'pct3']
    bes = [None, 0.5, 1.0]
    gestiones = ['full', 'half', 'scaled']
    directions = ['long', 'short', 'both']
    filter_profiles = {
        'none': set(),
        'ema200': {'ema200'},
        'ema50slope': {'ema50slope'},
        'atr_low': {'atr_low'},
        'atr_high': {'atr_high'},
        'tramo_min10': {'tramo_min10'},
        'tramo_min20': {'tramo_min20'},
        'tramo_min30': {'tramo_min30'},
        'regime_trend': {'regime_trend'},
        'regime_range': {'regime_range'},
        'trend_combo': {'ema200', 'ema50slope', 'regime_trend'},
        'range_combo': {'regime_range', 'atr_low'},
        'ema200+atr_low': {'ema200', 'atr_low'},
    }

    all_results = []
    for tf in args.tfs:
        print(f'=== TF {tf} ===', flush=True)
        velas = cargar_velas(par, tf)
        # precompute setups per tramo_n
        setups_by_tn = {}
        for tn in tramo_ns_list:
            setups_by_tn[tn] = construir_setups(velas, tf, tn)

        # iterate grid
        variant_count = 0
        for tramo_n in tramo_ns_list:
            setups = setups_by_tn[tramo_n]
            for ext in exts:
                for stop_mode in stop_modes:
                    for be in bes:
                        for gestion in gestiones:
                            for direction in directions:
                                for fp_name, fset in filter_profiles.items():
                                    params = {
                                        'tramo_ns': [tramo_n],
                                        'ext': ext,
                                        'stop_mode': stop_mode,
                                        'be': be,
                                        'gestion': gestion,
                                        'direction': direction,
                                        'filters': set(fset),
                                    }
                                    outs = []
                                    for s in setups:
                                        if direction == 'long' and s['side'] != 'long':
                                            continue
                                        if direction == 'short' and s['side'] != 'short':
                                            continue
                                        if not aplicar_filtros(s, fset):
                                            continue
                                        o = simular_trade(s, velas, ext, stop_mode, be, gestion)
                                        if o is not None:
                                            outs.append(o)
                                    m = metricas(outs)
                                    if m['n'] == 0:
                                        continue
                                    rec = {
                                        'par': par, 'tf': tf,
                                        'tramo_n': tramo_n,
                                        'ext': ext,
                                        'stop': stop_mode,
                                        'be': be,
                                        'gestion': gestion,
                                        'direction': direction,
                                        'filtro': fp_name,
                                        **m,
                                    }
                                    all_results.append(rec)
                                    variant_count += 1
        print(f'  variantes con trades: {variant_count}', flush=True)

    # sort by expectancy then n
    all_results.sort(key=lambda r: (r['esperanza_R'], r['n']), reverse=True)

    out_path = PILOT / 'investigacion' / f'resultados_busqueda_{par}.json'
    out_path.write_text(json.dumps(all_results, indent=1, ensure_ascii=False))
    print(f'guardado {out_path} ({len(all_results)} variantes) en {time.time()-t0:.1f}s', flush=True)

    # top 10
    print('\nTOP 10 por esperanza R (n>=30):')
    shown = 0
    for r in all_results:
        if r['n'] < 30:
            continue
        print(f"  {r['tf']} ext{r['ext']} stop{r['stop']} be{r['be']} gest{r['gestion']} dir{r['direction']} filt{r['filtro']} -> n={r['n']} win={r['acierto_pct']}% E={r['esperanza_R']} FB={r['factor_beneficio']} DD={r['drawdown_R']} racha={r['max_racha_perdidas']}")
        shown += 1
        if shown >= 10:
            break

    # validacion de top variantes
    if args.validar:
        print('\n=== VALIDACION ===', flush=True)
        # unique top by (tf, params) with n>=30
        seen = set()
        to_validate = []
        for r in all_results:
            if r['n'] < 30:
                continue
            key = (r['tf'], r['tramo_n'], r['ext'], r['stop'], r['be'], r['gestion'], r['direction'], r['filtro'])
            if key in seen:
                continue
            seen.add(key)
            to_validate.append(r)
            if len(to_validate) >= args.top:
                break
        for r in to_validate:
            tf = r['tf']
            velas = cargar_velas(par, tf)
            params = {
                'tramo_ns': [r['tramo_n']],
                'ext': r['ext'],
                'stop_mode': r['stop'],
                'be': r['be'],
                'gestion': r['gestion'],
                'direction': r['direction'],
                'filters': set(filter_profiles[r['filtro']]),
            }
            print(f"\n-- {tf} ext{r['ext']} stop{r['stop']} be{r['be']} gest{r['gestion']} dir{r['direction']} filt{r['filtro']} --", flush=True)
            ns = null_sintetico_propio(velas, params, tf, n_sim=300, seed=42)
            print('  null:', json.dumps(ns), flush=True)
            wf = walk_forward_simple(velas, tf, params)
            print('  wf:', json.dumps(wf), flush=True)
            # montecarlo on real trades
            # recompute outs
            setups = construir_setups(velas, tf, r['tramo_n'])
            outs = []
            for s in setups:
                if r['direction'] == 'long' and s['side'] != 'long':
                    continue
                if r['direction'] == 'short' and s['side'] != 'short':
                    continue
                if not aplicar_filtros(s, params['filters']):
                    continue
                o = simular_trade(s, velas, r['ext'], r['stop'], r['be'], r['gestion'])
                if o is not None:
                    outs.append(o)
            mc = montecarlo(outs, n_sim=500, seed=7)
            print('  mc:', json.dumps(mc), flush=True)


if __name__ == '__main__':
    main()
