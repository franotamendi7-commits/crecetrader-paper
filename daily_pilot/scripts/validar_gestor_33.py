#!/usr/bin/env python3
"""VALIDACION DEL GESTOR DE RACHA (G2) EN LOS 33 PARES.

    python3 daily_pilot/scripts/validar_gestor_33.py --n 2 --factor 0.5

PAPER_ONLY: mide, no opera.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE / 'daily_pilot' / 'core'))
sys.path.insert(0, str(BASE / 'daily_pilot' / 'scripts'))

PARES = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT', 'XRPUSDT', 'ADAUSDT',
         'AVAXUSDT', 'DOGEUSDT', 'LINKUSDT', 'DOTUSDT', 'LTCUSDT', 'ATOMUSDT',
         'NEARUSDT', 'UNIUSDT', 'AAVEUSDT', 'APTUSDT', 'ARBUSDT', 'OPUSDT',
         'SUI', 'FILUSDT', 'HBARUSDT', 'INJUSDT', 'MANAUSDT', 'SANDUSDT',
         'STXUSDT', 'THETAUSDT', 'ALGOUSDT', 'EGLDUSDT', 'FTMUSDT', 'TONUSDT',
         'NEOUSDT', 'ONDOUSDT', 'RUNEUSDT']


def metricas(outs):
    if not outs:
        return {'n': 0, 'acierto_pct': None, 'fb': None, 'esp': None,
                'dd': None, 'max_racha': 0}
    pos = [o for o in outs if o > 0]
    neg = [o for o in outs if o < 0]
    pf = (sum(pos) / abs(sum(neg))) if (neg and sum(neg) != 0) else (
        float('inf') if pos else 0.0)
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
    return {'n': len(outs), 'acierto_pct': round(len(pos) / len(outs) * 100, 1),
            'fb': (round(pf, 3) if pf != float('inf') else None),
            'esp': round(sum(outs) / len(outs), 3), 'dd': round(dd, 2),
            'max_racha': mx}


def correr(par, tf='1d', detalle=150, n_perd=2, factor=0.5, f1=True):
    from backtest_afavor import _tramo_y_niveles, stop_de, target_de
    r = _tramo_y_niveles(par, tf, detalle)
    if not r:
        return None
    v, t, niveles, ini = r
    datos = v[ini:]
    outs = []
    for etq, nivel, tipo in niveles:
        side = 'short' if t['direccion'] == 'bajista' else 'long'
        tgt = target_de(side, nivel, niveles, t)
        for i, x in enumerate(datos):
            if not (x['low'] <= nivel <= x['high']):
                continue
            if f1 and ((side == 'short' and x['close'] > nivel)
                       or (side == 'long' and x['close'] < nivel)):
                continue
            stop = stop_de('pct', side, nivel, datos[:i + 1], 2.0)
            risk = (nivel - stop) if side == 'long' else (stop - nivel)
            if risk <= 0:
                continue
            R = ((tgt - nivel) / risk) if side == 'long' else ((nivel - tgt) / risk)
            oc = -1.0
            for j in range(i + 1, len(datos)):
                y = datos[j]
                if side == 'long':
                    if y['low'] <= stop:
                        break
                    if y['high'] >= tgt:
                        oc = R; break
                else:
                    if y['high'] >= stop:
                        break
                    if y['low'] <= tgt:
                        oc = R; break
            outs.append(round(oc, 3))
    # gestor de racha
    racha = 0
    ajustados = []
    for o in outs:
        tam = factor if racha >= n_perd else 1.0
        ajustados.append(round(o * tam, 3))
        racha = racha + 1 if o < 0 else 0
    return ajustados


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--tf', default='1d')
    ap.add_argument('--detalle', type=int, default=150)
    ap.add_argument('--n', type=int, default=2)
    ap.add_argument('--factor', type=float, default=0.5)
    ap.add_argument('--min-ops', type=int, default=20)
    a = ap.parse_args()

    filas = []
    for par in PARES:
        outs = correr(par, a.tf, a.detalle, a.n, a.factor)
        if outs is None:
            print(f'  {par:<11} sin datos'); continue
        s = metricas(outs)
        filas.append({'par': par, **s})
        print(f"  {par:<11} n={s['n']:<3} acierto {str(s['acierto_pct']):>5}% "
              f"FB {str(s['fb']):>7} esp {str(s['esp']):>7}R dd {s['dd']} "
              f"racha {s['max_racha']}")

    ok = [f for f in filas if f['n'] >= a.min_ops]
    robustos = [f for f in ok if f['esp'] > 0.15 and f['dd'] > -4]
    print(f'\n=== {len(ok)}/{len(filas)} pares con n>={a.min_ops} ===')
    if ok:
        n_tot = sum(f['n'] for f in ok)
        print(f"  esperanza ponderada : {round(sum(f['esp']*f['n'] for f in ok)/n_tot, 3)}R")
        print(f"  ROBUSTOS (esp>0,15R y dd>-4R): {len(robustos)}/{len(ok)} "
              f"= {round(len(robustos)/len(ok)*100)}%")
        print(f"  peor drawdown       : {round(min(f['dd'] for f in ok), 2)}R")
        print(f"  peor racha          : {max(f['max_racha'] for f in ok)} perdidas")
    out = BASE / 'daily_pilot' / 'datos' / f'gestor_N{a.n}_F{int(a.factor*100)}.json'
    out.write_text(json.dumps(filas, indent=1, ensure_ascii=False))
    print(f'-> {out.name}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
