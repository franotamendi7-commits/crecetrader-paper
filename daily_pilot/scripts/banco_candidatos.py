#!/usr/bin/env python3
"""BANCO DE CANDIDATOS (ampliado) — filtro null sintetico.

PAPER_ONLY. No toca metodo/ ni la FIRMA. No escribe el store vivo.

Corre reglas base + categorias nuevas (gestion de posicion, regimen EMA200,
multi-timeframe 4h/1d) sobre un par/TF y filtra cada una contra un null
sintetico (block bootstrap de retornos, 1000 sims, percentil 95). Incluye
walk-forward simple (2/3 train, 1/3 test) para las 3 mejores reglas.

Uso:
    python3 daily_pilot/scripts/banco_candidatos.py --par ETHUSDT --tf 1d
    python3 daily_pilot/scripts/banco_candidatos.py --par BTCUSDT --tf 4h --n-sim 1000
"""
from __future__ import annotations

import argparse
import bisect
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE / 'daily_pilot' / 'core'))
sys.path.insert(0, str(BASE / 'daily_pilot' / 'scripts'))

import validacion_protocolo as VP

PAPER_ONLY = True

PAR = 'BTCUSDT'
TF = '1d'
STOP_PCT = 2.0
TARGET_MULT = 2.0
HORIZON = 30
N_SIM = 1000
SEED = 42
MIN_MUESTRA = 30

DAILY_SERIES = None  # para multi-timeframe (4h -> 1d)


# ---------------------------------------------------------------- datos

def cargar_velas(par, tf, forzar=False):
    from velas import velas as _velas
    r = _velas(par, tf, limite=500, forzar=forzar)
    if 'error' in r:
        p = BASE / 'daily_pilot' / 'datos' / 'velas' / f'{par}_{tf}.json'
        if p.exists():
            try:
                return json.loads(p.read_text())['velas']
            except Exception:
                pass
        raise SystemExit(f"sin datos: {r['error']}")
    return r['velas']


# ---------------------------------------------------------------- indicadores (igual que antes)

def sma(closes, w):
    out = [None] * len(closes)
    for i in range(w - 1, len(closes)):
        out[i] = sum(closes[i - w + 1:i + 1]) / w
    return out


def ema(closes, w):
    out = [None] * len(closes)
    if len(closes) < w:
        return out
    k = 2.0 / (w + 1)
    out[w - 1] = sum(closes[:w]) / w
    for i in range(w, len(closes)):
        out[i] = closes[i] * k + out[i - 1] * (1 - k)
    return out


def rsi(closes, w=14):
    out = [None] * len(closes)
    if len(closes) < w + 1:
        return out
    gains = [0.0] * len(closes)
    losses = [0.0] * len(closes)
    for i in range(1, len(closes)):
        d = closes[i] - closes[i - 1]
        if d > 0:
            gains[i] = d
        else:
            losses[i] = -d
    avg_g = sum(gains[1:w + 1]) / w
    avg_l = sum(losses[1:w + 1]) / w
    for i in range(w, len(closes)):
        if i > w:
            avg_g = (avg_g * (w - 1) + gains[i]) / w
            avg_l = (avg_l * (w - 1) + losses[i]) / w
        rs = (avg_g / avg_l) if avg_l > 0 else float('inf')
        out[i] = 100.0 - (100.0 / (1.0 + rs)) if avg_l > 0 else 100.0
    return out


def atr(velas, w=14):
    out = [None] * len(velas)
    trs = [0.0] * len(velas)
    for i in range(1, len(velas)):
        h, l, pc = velas[i]['high'], velas[i]['low'], velas[i - 1]['close']
        trs[i] = max(h - l, abs(h - pc), abs(l - pc))
    for i in range(w, len(velas)):
        out[i] = sum(trs[i - w + 1:i + 1]) / w
    return out


def rolling_std(xs, w):
    out = [None] * len(xs)
    for i in range(w - 1, len(xs)):
        seg = xs[i - w + 1:i + 1]
        m = sum(seg) / w
        var = sum((x - m) ** 2 for x in seg) / w
        out[i] = var ** 0.5
    return out


def linreg_slope_r2(xs, w):
    slopes = [None] * len(xs)
    r2s = [None] * len(xs)
    for i in range(w - 1, len(xs)):
        seg = xs[i - w + 1:i + 1]
        n = w
        mx = (n - 1) / 2.0
        my = sum(seg) / n
        num = sum((k - mx) * (seg[k] - my) for k in range(n))
        den = sum((k - mx) ** 2 for k in range(n))
        if den <= 0:
            slopes[i] = 0.0
            r2s[i] = 0.0
            continue
        slope = num / den
        ss_tot = sum((y - my) ** 2 for y in seg)
        ss_res = sum((seg[k] - (my + slope * (k - mx))) ** 2 for k in range(n))
        r2 = 1.0 - (ss_res / ss_tot) if ss_tot > 0 else 0.0
        slopes[i] = slope
        r2s[i] = r2
    return slopes, r2s


def weekday_of(ts_ms):
    return datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc).weekday()


# ---------------------------------------------------------------- trigger

def _trigger(cond_series):
    out = []
    prev = False
    for i, c in enumerate(cond_series):
        if c and not prev:
            out.append(i)
        prev = bool(c)
    return out


# ---------------------------------------------------------------- reglas base (igual)

def rule_ma_cross_20_50_long(series):
    closes = [x['close'] for x in series]
    s20 = sma(closes, 20); s50 = sma(closes, 50)
    cond = [(s20[i] is not None and s50[i] is not None and s20[i] > s50[i]) for i in range(len(closes))]
    return [(i, 'long') for i in _trigger(cond)]


def rule_ma_cross_50_200_long(series):
    closes = [x['close'] for x in series]
    s50 = sma(closes, 50); s200 = sma(closes, 200)
    cond = [(s50[i] is not None and s200[i] is not None and s50[i] > s200[i]) for i in range(len(closes))]
    return [(i, 'long') for i in _trigger(cond)]


def rule_price_ema200_cross_long(series):
    closes = [x['close'] for x in series]
    e200 = ema(closes, 200)
    out = []
    for i in range(1, len(closes)):
        if e200[i] is None or e200[i-1] is None:
            continue
        if closes[i-1] <= e200[i-1] and closes[i] > e200[i]:
            out.append(i)
    return [(i, 'long') for i in out]


def rule_ema50_slope_long(series):
    closes = [x['close'] for x in series]
    e50 = ema(closes, 50)
    cond = [False] * len(closes)
    for i in range(5, len(closes)):
        if e50[i] is None or e50[i-5] is None:
            continue
        cond[i] = (e50[i] > e50[i-5]) and (closes[i] > e50[i])
    return [(i, 'long') for i in _trigger(cond)]


def rule_momentum_5bar_long(series):
    closes = [x['close'] for x in series]
    cond = [False] * len(closes)
    for i in range(5, len(closes)):
        ret = closes[i] / closes[i-5] - 1.0
        cond[i] = ret > 0.03
    return [(i, 'long') for i in _trigger(cond)]


def rule_momentum_20bar_long(series):
    closes = [x['close'] for x in series]
    cond = [False] * len(closes)
    for i in range(20, len(closes)):
        ret = closes[i] / closes[i-20] - 1.0
        cond[i] = ret > 0.05
    return [(i, 'long') for i in _trigger(cond)]


def rule_breakout_max_20_long(series):
    highs = [x['high'] for x in series]
    closes = [x['close'] for x in series]
    out = []
    for i in range(21, len(series)):
        prev_max = max(highs[i-20:i])
        if closes[i-1] <= prev_max and closes[i] > prev_max:
            out.append(i)
    return [(i, 'long') for i in out]


def rule_breakdown_min_20_short(series):
    lows = [x['low'] for x in series]
    closes = [x['close'] for x in series]
    out = []
    for i in range(21, len(series)):
        prev_min = min(lows[i-20:i])
        if closes[i-1] >= prev_min and closes[i] < prev_min:
            out.append(i)
    return [(i, 'short') for i in out]


def rule_rsi_oversold_long(series):
    closes = [x['close'] for x in series]
    r = rsi(closes, 14)
    out = []
    for i in range(1, len(closes)):
        if r[i] is None or r[i-1] is None:
            continue
        if r[i-1] < 30 and r[i] >= 30:
            out.append(i)
    return [(i, 'long') for i in out]


def rule_rsi_overbought_short(series):
    closes = [x['close'] for x in series]
    r = rsi(closes, 14)
    out = []
    for i in range(1, len(closes)):
        if r[i] is None or r[i-1] is None:
            continue
        if r[i-1] > 70 and r[i] <= 70:
            out.append(i)
    return [(i, 'short') for i in out]


def rule_zscore_meanrev_long(series):
    closes = [x['close'] for x in series]
    s20 = sma(closes, 20); sd = rolling_std(closes, 20)
    z = [None] * len(closes)
    for i in range(20, len(closes)):
        if s20[i] is None or sd[i] is None or sd[i] <= 0:
            continue
        z[i] = (closes[i] - s20[i]) / sd[i]
    out = []
    for i in range(21, len(closes)):
        if z[i] is None or z[i-1] is None:
            continue
        if z[i-1] > -2.0 and z[i] <= -2.0:
            out.append(i)
    return [(i, 'long') for i in out]


def rule_zscore_meanrev_short(series):
    closes = [x['close'] for x in series]
    s20 = sma(closes, 20); sd = rolling_std(closes, 20)
    z = [None] * len(closes)
    for i in range(20, len(closes)):
        if s20[i] is None or sd[i] is None or sd[i] <= 0:
            continue
        z[i] = (closes[i] - s20[i]) / sd[i]
    out = []
    for i in range(21, len(closes)):
        if z[i] is None or z[i-1] is None:
            continue
        if z[i-1] < 2.0 and z[i] >= 2.0:
            out.append(i)
    return [(i, 'short') for i in out]


def rule_lowvol_uptrend_long(series):
    closes = [x['close'] for x in series]
    e20 = ema(closes, 20); a = atr(series, 14)
    cond = [False] * len(closes)
    for i in range(15, len(closes)):
        if e20[i] is None or a[i] is None or closes[i] <= 0:
            continue
        cond[i] = (a[i] / closes[i] < 0.025) and (closes[i] > e20[i])
    return [(i, 'long') for i in _trigger(cond)]


def rule_highvol_downtrend_short(series):
    closes = [x['close'] for x in series]
    e20 = ema(closes, 20); a = atr(series, 14)
    cond = [False] * len(closes)
    for i in range(15, len(closes)):
        if e20[i] is None or a[i] is None or closes[i] <= 0:
            continue
        cond[i] = (a[i] / closes[i] > 0.04) and (closes[i] < e20[i])
    return [(i, 'short') for i in _trigger(cond)]


def rule_monday_long(series):
    out = []
    for i in range(1, len(series)):
        if weekday_of(series[i]['ts']) == 0 and weekday_of(series[i-1]['ts']) != 0:
            out.append(i)
    return [(i, 'long') for i in out]


def rule_friday_short(series):
    out = []
    for i in range(1, len(series)):
        if weekday_of(series[i]['ts']) == 4 and weekday_of(series[i-1]['ts']) != 4:
            out.append(i)
    return [(i, 'short') for i in out]


def rule_donchian_breakout_long(series):
    highs = [x['high'] for x in series]
    closes = [x['close'] for x in series]
    out = []
    N = 10
    for i in range(N + 1, len(series)):
        prev_high = max(highs[i-N:i])
        if closes[i-1] <= prev_high and closes[i] > prev_high:
            out.append(i)
    return [(i, 'long') for i in out]


def rule_donchian_breakdown_short(series):
    lows = [x['low'] for x in series]
    closes = [x['close'] for x in series]
    out = []
    N = 10
    for i in range(N + 1, len(series)):
        prev_low = min(lows[i-N:i])
        if closes[i-1] >= prev_low and closes[i] < prev_low:
            out.append(i)
    return [(i, 'short') for i in out]


def rule_linreg_slope_long(series):
    closes = [x['close'] for x in series]
    slopes, r2s = linreg_slope_r2(closes, 20)
    cond = [False] * len(closes)
    for i in range(20, len(closes)):
        if slopes[i] is None or r2s[i] is None:
            continue
        cond[i] = (slopes[i] > 0) and (r2s[i] > 0.5)
    return [(i, 'long') for i in _trigger(cond)]


def rule_linreg_slope_short(series):
    closes = [x['close'] for x in series]
    slopes, r2s = linreg_slope_r2(closes, 20)
    cond = [False] * len(closes)
    for i in range(20, len(closes)):
        if slopes[i] is None or r2s[i] is None:
            continue
        cond[i] = (slopes[i] < 0) and (r2s[i] > 0.5)
    return [(i, 'short') for i in _trigger(cond)]


# ---------------------------------------------------------------- filtros combinados

def regime_filter(series, sigs):
    closes = [x['close'] for x in series]
    e200 = ema(closes, 200)
    out = []
    for i, side in sigs:
        if e200[i] is None:
            continue
        if side == 'long' and closes[i] > e200[i]:
            out.append((i, side))
        elif side == 'short' and closes[i] < e200[i]:
            out.append((i, side))
    return out


def make_regime(rule_func):
    def f(series):
        return regime_filter(series, rule_func(series))
    return f


def mtf_filter(series, sigs):
    global DAILY_SERIES
    if DAILY_SERIES is None:
        return sigs
    d = DAILY_SERIES
    dcloses = [x['close'] for x in d]
    de200 = ema(dcloses, 200)
    dts = [x['ts'] for x in d]
    out = []
    for i, side in sigs:
        ts = series[i]['ts']
        di = bisect.bisect_right(dts, ts) - 1
        if di < 0 or de200[di] is None:
            continue
        if side == 'long' and dcloses[di] > de200[di]:
            out.append((i, side))
        elif side == 'short' and dcloses[di] < de200[di]:
            out.append((i, side))
    return out


def make_mtf(rule_func):
    def f(series):
        return mtf_filter(series, rule_func(series))
    return f


# ---------------------------------------------------------------- resolver con gestion de posicion

def resolver(series, signals, mode='base'):
    outcomes = []
    n = len(series)
    closes = [x['close'] for x in series]
    for i, side in signals:
        if i >= n - 1:
            continue
        entry = closes[i]
        if side == 'long':
            stop0 = entry * (1 - STOP_PCT / 100.0)
            risk = entry - stop0
            t1 = entry + risk * 1.0
            t2 = entry + risk * 2.0
            t3 = entry + risk * 3.0
        else:
            stop0 = entry * (1 + STOP_PCT / 100.0)
            risk = stop0 - entry
            t1 = entry - risk * 1.0
            t2 = entry - risk * 2.0
            t3 = entry - risk * 3.0
        if risk <= 0:
            continue
        cost = VP.costos_R(entry, risk)
        end = min(n, i + 1 + HORIZON)

        if mode == 'base':
            target = t2
            hit = None
            for j in range(i + 1, end):
                bar = series[j]
                if side == 'long':
                    if bar['low'] <= stop0:
                        hit = 'stop'; break
                    if bar['high'] >= target:
                        hit = 'target'; break
                else:
                    if bar['high'] >= stop0:
                        hit = 'stop'; break
                    if bar['low'] <= target:
                        hit = 'target'; break
            if hit == 'target':
                raw = 2.0
            elif hit == 'stop':
                raw = -1.0
            else:
                last = closes[end - 1]
                raw = (last - entry) / risk if side == 'long' else (entry - last) / risk
            outcomes.append(raw - cost)
            continue

        if mode == 'be':
            stop = stop0
            be_on = False
            hit_target = False
            hit_stop = False
            exit_px = None
            for j in range(i + 1, end):
                bar = series[j]
                if side == 'long':
                    if (not be_on) and bar['high'] >= t1:
                        be_on = True
                        stop = entry
                    if bar['low'] <= stop:
                        hit_stop = True; exit_px = stop; break
                    if bar['high'] >= t2:
                        hit_target = True; break
                else:
                    if (not be_on) and bar['low'] <= t1:
                        be_on = True
                        stop = entry
                    if bar['high'] >= stop:
                        hit_stop = True; exit_px = stop; break
                    if bar['low'] <= t2:
                        hit_target = True; break
            if hit_target:
                raw = 2.0
            elif hit_stop:
                raw = (exit_px - entry) / risk if side == 'long' else (entry - exit_px) / risk
            else:
                last = closes[end - 1]
                raw = (last - entry) / risk if side == 'long' else (entry - last) / risk
            outcomes.append(raw - cost)
            continue

        if mode == 'half':
            half_closed = False
            stop = stop0
            rem_stop_hit = False
            rem_exit = None
            rem_never_half_stop = False
            full_stopped_before = False
            for j in range(i + 1, end):
                bar = series[j]
                if side == 'long':
                    if not half_closed:
                        if bar['low'] <= stop0:
                            full_stopped_before = True
                            break
                        if bar['high'] >= t1:
                            half_closed = True
                            stop = entry
                    else:
                        if bar['low'] <= stop:
                            rem_stop_hit = True
                            rem_exit = stop
                            break
                else:
                    if not half_closed:
                        if bar['high'] >= stop0:
                            full_stopped_before = True
                            break
                        if bar['low'] <= t1:
                            half_closed = True
                            stop = entry
                    else:
                        if bar['high'] >= stop:
                            rem_stop_hit = True
                            rem_exit = stop
                            break
            if full_stopped_before:
                outcomes.append(-1.0 - cost)
                continue
            if not half_closed:
                # never reached +1R and no stop: market exit full
                last = closes[end - 1]
                raw = (last - entry) / risk if side == 'long' else (entry - last) / risk
                outcomes.append(raw - cost)
                continue
            contrib = 0.5 * 1.0
            if rem_stop_hit:
                rrem = (rem_exit - entry) / risk if side == 'long' else (entry - rem_exit) / risk
            else:
                last = closes[end - 1]
                rrem = (last - entry) / risk if side == 'long' else (entry - last) / risk
            contrib += 0.5 * rrem
            outcomes.append(contrib - cost)
            continue

        if mode == 'scaled':
            closed = [False, False, False]
            exitR = [None, None, None]
            stop = stop0
            be_on = False
            stopped = False
            for j in range(i + 1, end):
                bar = series[j]
                # stop check first (conservative)
                stop_hit = False
                if side == 'long':
                    if bar['low'] <= stop:
                        stop_hit = True
                else:
                    if bar['high'] >= stop:
                        stop_hit = True
                if stop_hit:
                    for k in range(3):
                        if not closed[k]:
                            rsk = (stop - entry) / risk if side == 'long' else (entry - stop) / risk
                            exitR[k] = rsk
                            closed[k] = True
                    stopped = True
                    break
                # targets
                for k in range(3):
                    if closed[k]:
                        continue
                    tgt = [t1, t2, t3][k]
                    reached = False
                    if side == 'long' and bar['high'] >= tgt:
                        reached = True
                    if side == 'short' and bar['low'] <= tgt:
                        reached = True
                    if reached:
                        exitR[k] = [1.0, 2.0, 3.0][k]
                        closed[k] = True
                        if k == 0 and not be_on:
                            be_on = True
                            stop = entry
            # open tranches at horizon -> market
            last = closes[end - 1]
            marketR = (last - entry) / risk if side == 'long' else (entry - last) / risk
            for k in range(3):
                if not closed[k]:
                    exitR[k] = marketR
                    closed[k] = True
            weights = [1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0]
            raw = sum(weights[k] * exitR[k] for k in range(3))
            outcomes.append(raw - cost)
            continue

        # fallback
        outcomes.append(0.0)
    return outcomes


def backtest_expectancy(series, rule_func, mode):
    sigs = rule_func(series)
    outs = resolver(series, sigs, mode)
    if not outs:
        return None
    return sum(outs) / len(outs)


# ---------------------------------------------------------------- candidatos base

BASE_CANDS = [
    ('MA cross 20/50 (golden) long', rule_ma_cross_20_50_long, 'base'),
    ('MA cross 50/200 (golden) long', rule_ma_cross_50_200_long, 'base'),
    ('Precio cruza EMA200 al alza long', rule_price_ema200_cross_long, 'base'),
    ('EMA50 pendiente positiva long', rule_ema50_slope_long, 'base'),
    ('Momentum 5 velas >3% long', rule_momentum_5bar_long, 'base'),
    ('Momentum 20 velas >5% long', rule_momentum_20bar_long, 'base'),
    ('Rotura maximo 20 velas long', rule_breakout_max_20_long, 'base'),
    ('Rotura minimo 20 velas short', rule_breakdown_min_20_short, 'base'),
    ('RSI(14) rebote desde <30 long', rule_rsi_oversold_long, 'base'),
    ('RSI(14) rechazo desde >70 short', rule_rsi_overbought_short, 'base'),
    ('Mean reversion z<-2 long', rule_zscore_meanrev_long, 'base'),
    ('Mean reversion z>+2 short', rule_zscore_meanrev_short, 'base'),
    ('Baja vol (ATR/px<2.5%) + uptrend long', rule_lowvol_uptrend_long, 'base'),
    ('Alta vol (ATR/px>4%) + downtrend short', rule_highvol_downtrend_short, 'base'),
    ('Solo lunes long', rule_monday_long, 'base'),
    ('Solo viernes short', rule_friday_short, 'base'),
    ('Donchian breakout 10 long', rule_donchian_breakout_long, 'base'),
    ('Donchian breakdown 10 short', rule_donchian_breakdown_short, 'base'),
    ('Regresion lineal slope>0 R2>0.5 long', rule_linreg_slope_long, 'base'),
    ('Regresion lineal slope<0 R2>0.5 short', rule_linreg_slope_short, 'base'),
]


def build_candidates(tf):
    cands = list(BASE_CANDS)

    # Gestion de posicion: variantes sobre Donchian (regla con suficientes trades)
    for mode, tag in [('be', 'stop movil a BE tras +1R'),
                      ('half', 'cierre mitad en +1R, dejar correr'),
                      ('scaled', '3 objetivos escalonados 1R/2R/3R')]:
        cands.append((f'Donchian breakout 10 long — {tag}', rule_donchian_breakout_long, mode))
        cands.append((f'Donchian breakdown 10 short — {tag}', rule_donchian_breakdown_short, mode))

    # Regimen: EMA200 trend filter sobre momentum y rotura
    for name, rf in [('Momentum 5 velas >3% long', rule_momentum_5bar_long),
                     ('Momentum 20 velas >5% long', rule_momentum_20bar_long),
                     ('Rotura maximo 20 velas long', rule_breakout_max_20_long),
                     ('Donchian breakout 10 long', rule_donchian_breakout_long),
                     ('Rotura minimo 20 velas short', rule_breakdown_min_20_short),
                     ('Donchian breakdown 10 short', rule_donchian_breakdown_short)]:
        cands.append((f'{name} (regimen EMA200)', make_regime(rf), 'base'))

    # Multi-timeframe: solo si tf == 4h
    if tf == '4h':
        for name, rf in [('Momentum 5 velas >3% long', rule_momentum_5bar_long),
                         ('Momentum 20 velas >5% long', rule_momentum_20bar_long),
                         ('Rotura maximo 20 velas long', rule_breakout_max_20_long),
                         ('Donchian breakout 10 long', rule_donchian_breakout_long),
                         ('Rotura minimo 20 velas short', rule_breakdown_min_20_short),
                         ('Donchian breakdown 10 short', rule_donchian_breakdown_short)]:
            cands.append((f'{name} (MTF: entrada 4h solo si 1d a favor)', make_mtf(rf), 'base'))

    return cands


def categoria_de(nombre):
    if '— stop movil' in nombre or '— cierre mitad' in nombre or '— 3 objetivos' in nombre:
        return 'Gestion de posicion'
    if '(regimen EMA200)' in nombre:
        return 'Regimen'
    if '(MTF:' in nombre:
        return 'Multi-timeframe'
    return 'Base'


def walk_forward_simple(series, rule_func, mode):
    n = len(series)
    train_end = int(n * 2 / 3)
    purge = HORIZON
    test_start = train_end + purge
    if test_start >= n or train_end < 30:
        return None
    train_series = series[:train_end]
    test_series = series[test_start:]

    def exp_on(s):
        sigs = rule_func(s)
        outs = resolver(s, sigs, mode)
        if not outs:
            return None
        return sum(outs) / len(outs)

    is_e = exp_on(train_series)
    oos_e = exp_on(test_series)
    deg = None
    if is_e not in (None, 0) and oos_e is not None:
        deg = oos_e / is_e
    return {
        'n_train': len(train_series),
        'n_test': len(test_series),
        'expectancy_is': (round(is_e, 3) if is_e is not None else None),
        'expectancy_oos': (round(oos_e, 3) if oos_e is not None else None),
        'degradacion_ratio_oos_over_is': (round(deg, 3) if deg is not None else None),
    }


def main():
    global PAR, TF, DAILY_SERIES
    ap = argparse.ArgumentParser()
    ap.add_argument('--par', default=PAR)
    ap.add_argument('--tf', choices=['1w', '1d', '4h'], default=TF)
    ap.add_argument('--n-sim', type=int, default=N_SIM)
    ap.add_argument('--seed', type=int, default=SEED)
    ap.add_argument('--out', default=None)
    ap.add_argument('--no-write', action='store_true')
    a = ap.parse_args()

    PAR = a.par.upper()
    TF = a.tf
    if a.out is None:
        a.out = str(BASE / 'daily_pilot' / 'investigacion' / f'BANCO_CANDIDATOS_{PAR}.md')

    velas = cargar_velas(PAR, TF, forzar=True)
    n_velas = len(velas)
    print(f'{PAR} {TF}: {n_velas} velas', file=sys.stderr)

    if TF == '4h':
        try:
            DAILY_SERIES = cargar_velas(PAR, '1d', forzar=False)
            print(f'  daily cargado: {len(DAILY_SERIES)} velas', file=sys.stderr)
        except Exception as e:
            print(f'  daily no disponible: {e}', file=sys.stderr)
            DAILY_SERIES = None

    cands = build_candidates(TF)

    rows = []
    for nombre, rfunc, mode in cands:
        print(f'[candidato] {nombre}', file=sys.stderr)
        sigs = rfunc(velas)
        outs = resolver(velas, sigs, mode)
        n = len(outs)
        acierto = (sum(1 for o in outs if o > 0) / n * 100.0) if n else 0.0
        exp = (sum(outs) / n) if n else None

        def bf(s, rf=rfunc, md=mode):
            return backtest_expectancy(s, rf, md)

        null_res = VP.null_sintetico(
            velas, backtest_fn=bf, n_sim=a.n_sim, seed=a.seed,
            tf=TF, detalle=len(velas))

        p95 = null_res.get('null_p95')
        pval = null_res.get('p_valor_empirico')
        real_null = null_res.get('real_expectancy_R')

        if n < MIN_MUESTRA:
            veredicto = 'MUESTRA CHICA (no declarar)'
        elif (real_null is not None and p95 is not None and real_null > p95
              and (pval is not None and pval < 0.05)):
            veredicto = 'PASA'
        else:
            veredicto = 'RUIDO'

        rows.append({
            'regla': nombre,
            'categoria': categoria_de(nombre),
            'modo': mode,
            'n': n,
            'acierto_pct': round(acierto, 1),
            'esperanza_R': (round(exp, 3) if exp is not None else None),
            'p_valor': pval,
            'null_p95': p95,
            'null_media': null_res.get('null_media'),
            'n_validas': null_res.get('n_validas'),
            'veredicto': veredicto,
        })
        print(f'   n={n} exp={exp} p95={p95} p={pval} -> {veredicto}', file=sys.stderr)

    # walk-forward para las 3 mejores reglas base (por p-valor)
    base_rows = [r for r in rows if r['categoria'] == 'Base']
    ranked = sorted(base_rows, key=lambda r: (r['p_valor'] if r['p_valor'] is not None else 1.0,
                                            -(r['esperanza_R'] if r['esperanza_R'] is not None else -999)))
    # prefer n>=15
    with_n = [r for r in ranked if r['n'] >= 15]
    pool = with_n if len(with_n) >= 3 else ranked
    top3_names = [r['regla'] for r in pool[:3]]
    # map name -> (func, mode)
    name_to_cm = {c[0]: (c[1], c[2]) for c in cands}
    wf_results = {}
    for nm in top3_names:
        rf, md = name_to_cm[nm]
        res = walk_forward_simple(velas, rf, md)
        wf_results[nm] = res
        print(f'[wf] {nm}: {res}', file=sys.stderr)

    # escribir markdown
    lines = []
    lines.append(f'# BANCO DE CANDIDATOS {PAR} — filtro null sintetico (ampliado)\n')
    lines.append(f'PAPER_ONLY. Par: {PAR} | TF: {TF} | Velas: {n_velas} '
                 f'({datetime.fromtimestamp(velas[0]["ts"]/1000, tz=timezone.utc).date()} -> '
                 f'{datetime.fromtimestamp(velas[-1]["ts"]/1000, tz=timezone.utc).date()})\n')
    lines.append(f'Costos: comision 0.10% + slippage 0.05% por pasada. '
                 f'Stop {STOP_PCT}% / Target {STOP_PCT*TARGET_MULT}% (2:1) base. '
                 f'Horizonte {HORIZON} barras. Muestra minima {MIN_MUESTRA} trades.\n')
    lines.append(f'Null sintetico: {a.n_sim} sims, block bootstrap, percentil 95. Seed {a.seed}.\n')
    lines.append(f'Categorias: Base (20) + Gestion de posicion (6) + Regimen EMA200 (6)'
                 f'{" + Multi-timeframe 4h/1d (6)" if TF == "4h" else ""}.\n')

    lines.append('| regla | cat | n trades | acierto% | esperanza R | p-valor | veredicto |')
    lines.append('|---|---|---:|---:|---:|---:|---|')
    for r in rows:
        lines.append(f"| {r['regla']} | {r['categoria']} | {r['n']} | {r['acierto_pct']} | "
                     f"{r['esperanza_R'] if r['esperanza_R'] is not None else 'NA'} | "
                     f"{r['p_valor'] if r['p_valor'] is not None else 'NA'} | {r['veredicto']} |")
    lines.append('')
    pasa = [r for r in rows if r['veredicto'] == 'PASA']
    chica = [r for r in rows if r['veredicto'].startswith('MUESTRA')]
    lines.append(f'**Pasan el null: {len(pasa)} / {len(rows)}**\n')
    if pasa:
        for r in pasa:
            lines.append(f"- {r['regla']} (n={r['n']}, E={r['esperanza_R']}R, p={r['p_valor']})")
    else:
        lines.append('**NINGUNA regla supera el null sintetico.**')
    lines.append('')
    if chica:
        lines.append(f'Muestra chica (<{MIN_MUESTRA}): {len(chica)} reglas.')
    lines.append('')

    # Gestion comparada
    lines.append('## Gestion de posicion — comparacion contra base\n')
    lines.append('| variante | n | acierto% | esperanza R | p-valor | veredicto |')
    lines.append('|---|---:|---:|---:|---:|---|')
    for r in rows:
        if r['categoria'] == 'Gestion de posicion':
            lines.append(f"| {r['regla']} | {r['n']} | {r['acierto_pct']} | "
                         f"{r['esperanza_R'] if r['esperanza_R'] is not None else 'NA'} | "
                         f"{r['p_valor'] if r['p_valor'] is not None else 'NA'} | {r['veredicto']} |")
    lines.append('')

    # Regimen
    lines.append('## Regimen (EMA200) — comparacion\n')
    lines.append('| regla | n | acierto% | esperanza R | p-valor | veredicto |')
    lines.append('|---|---:|---:|---:|---:|---|')
    for r in rows:
        if r['categoria'] == 'Regimen':
            lines.append(f"| {r['regla']} | {r['n']} | {r['acierto_pct']} | "
                         f"{r['esperanza_R'] if r['esperanza_R'] is not None else 'NA'} | "
                         f"{r['p_valor'] if r['p_valor'] is not None else 'NA'} | {r['veredicto']} |")
    lines.append('')

    if TF == '4h':
        lines.append('## Multi-timeframe 4h/1d\n')
        lines.append('| regla | n | acierto% | esperanza R | p-valor | veredicto |')
        lines.append('|---|---:|---:|---:|---:|---|')
        for r in rows:
            if r['categoria'] == 'Multi-timeframe':
                lines.append(f"| {r['regla']} | {r['n']} | {r['acierto_pct']} | "
                             f"{r['esperanza_R'] if r['esperanza_R'] is not None else 'NA'} | "
                             f"{r['p_valor'] if r['p_valor'] is not None else 'NA'} | {r['veredicto']} |")
        lines.append('')

    # Walk-forward
    lines.append('## Walk-forward (2/3 train, 1/3 test) — top 3 reglas base\n')
    lines.append('| regla | n_train | n_test | E_IS | E_OOS | degradacion (OOS/IS) |')
    lines.append('|---|---:|---:|---:|---:|---:|')
    for nm in top3_names:
        res = wf_results.get(nm)
        if res is None:
            lines.append(f"| {nm} | NA | NA | NA | NA | NA |")
            continue
        lines.append(f"| {nm} | {res['n_train']} | {res['n_test']} | {res['expectancy_is']} | "
                     f"{res['expectancy_oos']} | {res['degradacion_ratio_oos_over_is']} |")
    lines.append('')

    lines.append('## Detalle por regla\n')
    for r in rows:
        lines.append(f"### {r['regla']}\n")
        lines.append(f"- cat: {r['categoria']}")
        lines.append(f"- n trades: {r['n']}")
        lines.append(f"- acierto%: {r['acierto_pct']}")
        lines.append(f"- esperanza R: {r['esperanza_R']}")
        lines.append(f"- p-valor: {r['p_valor']}")
        lines.append(f"- null p95: {r['null_p95']} | null media: {r['null_media']} | sims validas: {r['n_validas']}")
        lines.append(f"- veredicto: {r['veredicto']}\n")

    md = '\n'.join(lines)
    if not a.no_write:
        outp = Path(a.out)
        outp.parent.mkdir(parents=True, exist_ok=True)
        outp.write_text(md, encoding='utf-8')
        print(f'escrito: {outp}', file=sys.stderr)

    # json resumen a stdout (incluye wf)
    summary = {'par': PAR, 'tf': TF, 'n_velas': n_velas, 'candidatos': rows,
               'walk_forward': {k: v for k, v in wf_results.items()},
               'top3': top3_names}
    print(json.dumps(summary, indent=1, ensure_ascii=False))

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
