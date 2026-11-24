#!/usr/bin/env python3
"""BANCO DE CANDIDATOS PARA BTC — filtro null sintetico.

PAPER_ONLY. No toca metodo/ ni la FIRMA. No escribe el store vivo.

Corre >=15 reglas distintas sobre BTCUSDT 1d y filtra cada una contra un
null sintetico (block bootstrap de retornos, 1000 sims, percentil 95).

Uso:
    python3 daily_pilot/scripts/banco_candidatos.py
    python3 daily_pilot/scripts/banco_candidatos.py --n-sim 1000 --out daily_pilot/investigacion/BANCO_CANDIDATOS_BTC.md
"""
from __future__ import annotations

import argparse
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
STOP_PCT = 2.0          # stop fijo 2%
TARGET_MULT = 2.0       # target = 2 * stop = 4%
HORIZON = 30            # barras max para resolver un trade
N_SIM = 1000
SEED = 42
MIN_MUESTRA = 30


# ---------------------------------------------------------------- datos

def cargar_velas(forzar=False):
    from velas import velas as _velas
    r = _velas(PAR, TF, limite=500, forzar=forzar)
    if 'error' in r:
        # fallback cache vieja
        p = BASE / 'daily_pilot' / 'datos' / 'velas' / f'{PAR}_{TF}.json'
        if p.exists():
            try:
                return json.loads(p.read_text())['velas']
            except Exception:
                pass
        raise SystemExit(f"sin datos: {r['error']}")
    return r['velas']


# ---------------------------------------------------------------- indicadores

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
        # r2
        ss_tot = sum((y - my) ** 2 for y in seg)
        ss_res = sum((seg[k] - (my + slope * (k - mx))) ** 2 for k in range(n))
        r2 = 1.0 - (ss_res / ss_tot) if ss_tot > 0 else 0.0
        slopes[i] = slope
        r2s[i] = r2
    return slopes, r2s


def weekday_of(ts_ms):
    return datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc).weekday()


# ---------------------------------------------------------------- resolucion de trades

def resolver(series, signals):
    outcomes = []
    n = len(series)
    closes = [x['close'] for x in series]
    for i, side in signals:
        if i >= n - 1:
            continue
        entry = closes[i]
        if side == 'long':
            stop = entry * (1 - STOP_PCT / 100.0)
            target = entry * (1 + (STOP_PCT * TARGET_MULT) / 100.0)
        else:
            stop = entry * (1 + STOP_PCT / 100.0)
            target = entry * (1 - (STOP_PCT * TARGET_MULT) / 100.0)
        risk = abs(entry - stop)
        if risk <= 0:
            continue
        rmult = abs(target - entry) / risk
        cost = VP.costos_R(entry, risk)
        end = min(n, i + 1 + HORIZON)
        hit = None
        for j in range(i + 1, end):
            bar = series[j]
            if side == 'long':
                if bar['low'] <= stop:
                    hit = 'stop'
                    break
                if bar['high'] >= target:
                    hit = 'target'
                    break
            else:
                if bar['high'] >= stop:
                    hit = 'stop'
                    break
                if bar['low'] <= target:
                    hit = 'target'
                    break
        if hit == 'target':
            raw = rmult
        elif hit == 'stop':
            raw = -1.0
        else:
            last = closes[end - 1]
            if side == 'long':
                raw = (last - entry) / risk
            else:
                raw = (entry - last) / risk
        outcomes.append(raw - cost)
    return outcomes


# ---------------------------------------------------------------- reglas (cada una devuelve lista de (i, side))

def _trigger(cond_series):
    # convierte lista de bool en indices donde pasa de False a True
    out = []
    prev = False
    for i, c in enumerate(cond_series):
        if c and not prev:
            out.append(i)
        prev = bool(c)
    return out


def rule_ma_cross_20_50_long(series):
    closes = [x['close'] for x in series]
    s20 = sma(closes, 20)
    s50 = sma(closes, 50)
    cond = [ (s20[i] is not None and s50[i] is not None and s20[i] > s50[i]) for i in range(len(closes)) ]
    idx = _trigger(cond)
    return [(i, 'long') for i in idx]


def rule_ma_cross_50_200_long(series):
    closes = [x['close'] for x in series]
    s50 = sma(closes, 50)
    s200 = sma(closes, 200)
    cond = [ (s50[i] is not None and s200[i] is not None and s50[i] > s200[i]) for i in range(len(closes)) ]
    idx = _trigger(cond)
    return [(i, 'long') for i in idx]


def rule_price_ema200_cross_long(series):
    closes = [x['close'] for x in series]
    e200 = ema(closes, 200)
    cond = []
    for i in range(len(closes)):
        if e200[i] is None:
            cond.append(False)
        else:
            cond.append(closes[i] > e200[i])
    # trigger on crossing above
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
    idx = _trigger(cond)
    return [(i, 'long') for i in idx]


def rule_momentum_5bar_long(series):
    closes = [x['close'] for x in series]
    cond = [False] * len(closes)
    for i in range(5, len(closes)):
        ret = closes[i] / closes[i-5] - 1.0
        cond[i] = ret > 0.03
    idx = _trigger(cond)
    return [(i, 'long') for i in idx]


def rule_momentum_20bar_long(series):
    closes = [x['close'] for x in series]
    cond = [False] * len(closes)
    for i in range(20, len(closes)):
        ret = closes[i] / closes[i-20] - 1.0
        cond[i] = ret > 0.05
    idx = _trigger(cond)
    return [(i, 'long') for i in idx]


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
    s20 = sma(closes, 20)
    sd = rolling_std(closes, 20)
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
    s20 = sma(closes, 20)
    sd = rolling_std(closes, 20)
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
    e20 = ema(closes, 20)
    a = atr(series, 14)
    cond = [False] * len(closes)
    for i in range(15, len(closes)):
        if e20[i] is None or a[i] is None or closes[i] <= 0:
            continue
        cond[i] = (a[i] / closes[i] < 0.025) and (closes[i] > e20[i])
    idx = _trigger(cond)
    return [(i, 'long') for i in idx]


def rule_highvol_downtrend_short(series):
    closes = [x['close'] for x in series]
    e20 = ema(closes, 20)
    a = atr(series, 14)
    cond = [False] * len(closes)
    for i in range(15, len(closes)):
        if e20[i] is None or a[i] is None or closes[i] <= 0:
            continue
        cond[i] = (a[i] / closes[i] > 0.04) and (closes[i] < e20[i])
    idx = _trigger(cond)
    return [(i, 'short') for i in idx]


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
    idx = _trigger(cond)
    return [(i, 'long') for i in idx]


def rule_linreg_slope_short(series):
    closes = [x['close'] for x in series]
    slopes, r2s = linreg_slope_r2(closes, 20)
    cond = [False] * len(closes)
    for i in range(20, len(closes)):
        if slopes[i] is None or r2s[i] is None:
            continue
        cond[i] = (slopes[i] < 0) and (r2s[i] > 0.5)
    idx = _trigger(cond)
    return [(i, 'short') for i in idx]


# ---------------------------------------------------------------- candidatos

CANDIDATOS = [
    ('MA cross 20/50 (golden) long', rule_ma_cross_20_50_long),
    ('MA cross 50/200 (golden) long', rule_ma_cross_50_200_long),
    ('Precio cruza EMA200 al alza long', rule_price_ema200_cross_long),
    ('EMA50 pendiente positiva long', rule_ema50_slope_long),
    ('Momentum 5 velas >3% long', rule_momentum_5bar_long),
    ('Momentum 20 velas >5% long', rule_momentum_20bar_long),
    ('Rotura maximo 20 velas long', rule_breakout_max_20_long),
    ('Rotura minimo 20 velas short', rule_breakdown_min_20_short),
    ('RSI(14) rebote desde <30 long', rule_rsi_oversold_long),
    ('RSI(14) rechazo desde >70 short', rule_rsi_overbought_short),
    ('Mean reversion z<-2 long', rule_zscore_meanrev_long),
    ('Mean reversion z>+2 short', rule_zscore_meanrev_short),
    ('Baja vol (ATR/px<2.5%) + uptrend long', rule_lowvol_uptrend_long),
    ('Alta vol (ATR/px>4%) + downtrend short', rule_highvol_downtrend_short),
    ('Solo lunes long', rule_monday_long),
    ('Solo viernes short', rule_friday_short),
    ('Donchian breakout 10 long', rule_donchian_breakout_long),
    ('Donchian breakdown 10 short', rule_donchian_breakdown_short),
    ('Regresion lineal slope>0 R2>0.5 long', rule_linreg_slope_long),
    ('Regresion lineal slope<0 R2>0.5 short', rule_linreg_slope_short),
]


def backtest_expectancy(series, rule_func):
    sigs = rule_func(series)
    outs = resolver(series, sigs)
    if not outs:
        return None
    return sum(outs) / len(outs)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n-sim', type=int, default=N_SIM)
    ap.add_argument('--seed', type=int, default=SEED)
    ap.add_argument('--out', default=str(BASE / 'daily_pilot' / 'investigacion' / 'BANCO_CANDIDATOS_BTC.md'))
    ap.add_argument('--no-write', action='store_true')
    a = ap.parse_args()

    velas = cargar_velas(forzar=True)
    n_velas = len(velas)
    print(f'BTCUSDT 1d: {n_velas} velas', file=sys.stderr)

    rows = []
    for nombre, rfunc in CANDIDATOS:
        print(f'[candidato] {nombre}', file=sys.stderr)
        sigs = rfunc(velas)
        outs = resolver(velas, sigs)
        n = len(outs)
        acierto = (sum(1 for o in outs if o > 0) / n * 100.0) if n else 0.0
        exp = (sum(outs) / n) if n else None

        # null sintetico
        def bf(s, rf=rfunc):
            return backtest_expectancy(s, rf)

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

    # escribir markdown
    lines = []
    lines.append('# BANCO DE CANDIDATOS BTC — filtro null sintetico\n')
    lines.append(f'PAPER_ONLY. Par: {PAR} | TF: {TF} | Velas: {n_velas} '
                 f'({datetime.fromtimestamp(velas[0]["ts"]/1000, tz=timezone.utc).date()} -> '
                 f'{datetime.fromtimestamp(velas[-1]["ts"]/1000, tz=timezone.utc).date()})\n')
    lines.append(f'Costos: comision 0.10% + slippage 0.05% por pasada (costos_R de validacion_protocolo.py). '
                 f'Stop {STOP_PCT}% / Target {STOP_PCT*TARGET_MULT}% (2:1) para todos los candidatos. '
                 f'Horizonte de resolucion {HORIZON} barras. Muestra minima para declarar: {MIN_MUESTRA} trades.\n')
    lines.append(f'Null sintetico: {a.n_sim} sims, block bootstrap de retornos, percentil 95. '
                 f'Seed {a.seed}.\n')
    lines.append('| regla | n trades | acierto% | esperanza R | p-valor | veredicto (PASA/RUIDO) |')
    lines.append('|---|---:|---:|---:|---:|---|')
    for r in rows:
        lines.append(f"| {r['regla']} | {r['n']} | {r['acierto_pct']} | "
                     f"{r['esperanza_R'] if r['esperanza_R'] is not None else 'NA'} | "
                     f"{r['p_valor'] if r['p_valor'] is not None else 'NA'} | {r['veredicto']} |")
    lines.append('')
    pasa = [r for r in rows if r['veredicto'] == 'PASA']
    chica = [r for r in rows if r['veredicto'].startswith('MUESTRA')]
    lines.append(f'**Pasan el null: {len(pasa)} / {len(rows)}**\n')
    if pasa:
        lines.append('Candidatos que superan el percentil 95 del null:')
        for r in pasa:
            lines.append(f"- {r['regla']} (n={r['n']}, E={r['esperanza_R']}R, p={r['p_valor']})")
    else:
        lines.append('**NINGUNA regla supera el null sintetico. Ese es un resultado valido: '
                     'no hay edge detectable en este universo de candidatos para BTC 1d.**')
    lines.append('')
    if chica:
        lines.append(f'Muestra chica (<{MIN_MUESTRA} trades): {len(chica)} reglas — no declarar edge.')
        for r in chica:
            lines.append(f"- {r['regla']} (n={r['n']})")
    lines.append('')
    lines.append('## Detalle por regla\n')
    for r in rows:
        lines.append(f"### {r['regla']}\n")
        lines.append(f"- n trades: {r['n']}")
        lines.append(f"- acierto%: {r['acierto_pct']}")
        lines.append(f"- esperanza R: {r['esperanza_R']}")
        lines.append(f"- p-valor (empirico vs null): {r['p_valor']}")
        lines.append(f"- null p95: {r['null_p95']} | null media: {r['null_media']} | sims validas: {r['n_validas']}")
        lines.append(f"- veredicto: {r['veredicto']}\n")

    md = '\n'.join(lines)
    if not a.no_write:
        outp = Path(a.out)
        outp.parent.mkdir(parents=True, exist_ok=True)
        outp.write_text(md, encoding='utf-8')
        print(f'escrito: {outp}', file=sys.stderr)

    # tambien imprimir json resumen a stdout
    print(json.dumps({'n_velas': n_velas, 'candidatos': rows}, indent=1, ensure_ascii=False))


if __name__ == '__main__':
    raise SystemExit(main())