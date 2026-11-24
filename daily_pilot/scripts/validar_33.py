#!/usr/bin/env python3
"""VALIDACION EN LOS 33 PARES — «a favor del tramo» con filtros.

    python3 daily_pilot/scripts/validar_33.py
    python3 daily_pilot/scripts/validar_33.py --filtros F1 --stop pct

PAPER_ONLY: mide, no opera. Reporta tambien los pares donde falla.
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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--tf', default='1d')
    ap.add_argument('--detalle', type=int, default=150)
    ap.add_argument('--filtros', default='')
    ap.add_argument('--stop', default='pct', choices=['pct', 'estructural', 'atr'])
    ap.add_argument('--min-ops', type=int, default=5)
    ap.add_argument('--gestion', default=None, choices=[None, 'P1', 'P2', 'P3'])
    a = ap.parse_args()

    from backtest_afavor import backtest_afavor
    filtros = {x.strip().upper() for x in a.filtros.split(',') if x.strip()}
    if a.gestion == 'P3':
        filtros.add('P3')

    filas = []
    for par in PARES:
        try:
            r = backtest_afavor(par, a.tf, a.detalle, filtros, a.stop, 2.0,
                                min_muestra=a.min_ops, gestion=a.gestion)
        except Exception as e:
            print(f'  {par:<11} ERROR {type(e).__name__}: {e}')
            continue
        if 'agregado' not in r:
            print(f'  {par:<11} {r.get("skip") or r.get("error")}')
            continue
        s = r['agregado']
        filas.append({'par': par, 'dir': r['tramo']['direccion'], 'n': s.get('n', 0),
                      'acierto': s.get('acierto_pct'), 'fb': s.get('factor_beneficio'),
                      'esp': s.get('esperanza_R'), 'dd': s.get('drawdown_R')})
        print(f"  {par:<11} n={s.get('n', 0):<3} acierto {str(s.get('acierto_pct')):>5}% "
              f"FB {str(s.get('factor_beneficio')):>7} esp {str(s.get('esperanza_R')):>7}R "
              f"dd {s.get('drawdown_R')}")

    ok = [f for f in filas if f['n'] >= a.min_ops]
    print(f'\n=== RESUMEN ({len(ok)}/{len(filas)} pares con n>={a.min_ops}) ===')
    if ok:
        n_tot = sum(f['n'] for f in ok)
        print(f"  operaciones totales : {n_tot}")
        print(f"  esperanza ponderada : "
              f"{round(sum((f['esp'] or 0)*f['n'] for f in ok)/n_tot, 3)}R")
        print(f"  pares positivos     : "
              f"{sum(1 for f in ok if (f['esp'] or 0) > 0)}/{len(ok)}")
        print(f"  FB > 1,5            : "
              f"{sum(1 for f in ok if (f['fb'] or 0) > 1.5)}/{len(ok)}")
        print(f"  acierto > 25%       : "
              f"{sum(1 for f in ok if (f['acierto'] or 0) > 25)}/{len(ok)}")
        print(f"  drawdown > -6R      : "
              f"{sum(1 for f in ok if (f['dd'] or 0) > -6)}/{len(ok)}")
    out = BASE / 'daily_pilot' / 'datos' / (
        f"validacion_33_{a.stop}_{'_'.join(sorted(filtros)) or 'base'}.json")
    out.write_text(json.dumps({'por_par': filas, 'resumen': ok}, indent=1,
                              ensure_ascii=False))
    print(f'-> {out.name}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
