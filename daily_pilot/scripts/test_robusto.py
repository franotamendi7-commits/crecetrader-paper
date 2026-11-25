#!/usr/bin/env python3
"""TEST ROBUSTO scale-in Fibo — todos los pares, 20 seeds, resultados a JSONL.

Por par:
  · backtest completo (filtro R>=4%, riesgo 2%)
  · null sintético: 20 seeds, permutación de signos conservando magnitudes
  · p矫正 = (# nulls >= real + 1) / (seeds + 1)  -> piso 1/21 = 0.048
  · WF temporal 60/40 sobre operaciones
  · VÁLIDA si p<0.05 y test>0

Escribe resultado por par a resultados_test_robusto.jsonl (append, idempotente).
"""
from __future__ import annotations
import datetime, json, math, random, statistics, sys
from pathlib import Path

BASE = Path('/Users/franciscootamendi/YouTubeTradingAgent')
sys.path.insert(0, str(BASE / 'daily_pilot' / 'scripts'))
import scalein_fibo as S

V = S.V
OUT = BASE / 'daily_pilot' / 'datos' / 'resultados_test_robusto.jsonl'
S.RIESGO_TOTAL = 0.02
CFG = dict(look=24, max_rango=0.12, stop_pct=0.03, target=1.25, swing_n=5, max_bars=72)
SEEDS = 20


def sint(v, seed):
    c = [x['close'] for x in v]
    rets = [math.log(c[i] / c[i - 1]) for i in range(1, len(c))]
    sg = [1 if r >= 0 else -1 for r in rets]
    mg = [abs(r) for r in rets]
    rh = [x['high'] / x['close'] for x in v]
    rl = [x['low'] / x['close'] for x in v]
    rng = random.Random(seed)
    s2 = sg[:]
    rng.shuffle(s2)
    cl = [c[0]]
    for s, m in zip(s2, mg):
        cl.append(cl[-1] * math.exp(s * m))
    return [{'ts': x['ts'], 'open': cl[i], 'high': cl[i] * rh[i],
             'low': cl[i] * rl[i], 'close': cl[i], 'volumen': 0}
            for i, x in enumerate(v)]


def probar(par):
    a, b = V / f'{par}_1h.json', V / f'{par}_4h.json'
    if not a.exists() or not b.exists():
        return None
    v1 = json.loads(a.read_text())['velas']
    v4 = json.loads(b.read_text())['velas']
    ops = [o for o in S.detectar(v1, v4, CFG) if o.get('R', 0) >= 0.04]
    if not ops:
        return {'par': par, 'n': 0, 'veredicto': 'SIN_SEÑALES'}
    real = sum(o['pnl'] for o in ops)
    eq = peak = dd = 0.0
    for o in ops:
        eq += o['pnl']; peak = max(peak, eq); dd = min(dd, eq - peak)
    sims = []
    for sd in range(SEEDS):
        s1, s4 = sint(v1, 7000 + sd), sint(v4, 7000 + sd)
        sims.append(sum(o['pnl'] for o in S.detectar(s1, s4, CFG) if o.get('R', 0) >= 0.04))
    p = (sum(1 for s in sims if s >= real) + 1) / (SEEDS + 1)
    k = int(len(ops) * 0.6)
    tr = sum(o['pnl'] for o in ops[:k])
    te = sum(o['pnl'] for o in ops[k:])
    ini = datetime.datetime.utcfromtimestamp(ops[0]['ts'] / 1000).strftime('%Y-%m')
    fin = datetime.datetime.utcfromtimestamp(ops[-1]['ts'] / 1000).strftime('%Y-%m')
    win = 100 * sum(1 for o in ops if o['pnl'] > 0) / len(ops)
    ok = p < 0.05 and te > 0
    return {'par': par, 'n': len(ops), 'win': round(win, 1),
            'real': round(real, 2), 'dd': round(dd, 2),
            'null_media': round(statistics.mean(sims), 2),
            'null_max': round(max(sims), 2), 'p': round(p, 4),
            'train': round(tr, 2), 'test': round(te, 2),
            'desde': ini, 'hasta': fin, 'seeds': SEEDS,
            'veredicto': 'VALIDAR' if ok else 'DESCARTAR'}


def ya_hecho():
    if not OUT.exists():
        return set()
    out = set()
    for line in OUT.read_text().splitlines():
        try:
            d = json.loads(line)
            if d.get('seeds') == SEEDS:
                out.add(d['par'])
        except Exception:
            pass
    return out


def main():
    pares = sys.argv[1:] if len(sys.argv) > 1 else sorted(
        p.stem.replace('_1h', '') for p in V.glob('*_1h.json')
        if (V / (p.stem.replace('_1h', '_4h') + '.json')).exists())
    done = ya_hecho()
    for par in pares:
        if par in done:
            print(f'{par}: ya probado, salto')
            continue
        r = probar(par)
        if not r:
            continue
        with OUT.open('a') as f:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
        print(f"{par:12} n={r.get('n',0):>3} win={r.get('win',0):>5}% "
              f"real=${r.get('real',0):>9} DD=${r.get('dd',0):>8} "
              f"p={r.get('p',1):.3f} test=${r.get('test',0):>8} "
              f"-> {r['veredicto']}", flush=True)


if __name__ == '__main__':
    main()
