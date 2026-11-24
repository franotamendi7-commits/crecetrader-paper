#!/usr/bin/env python3
"""BACKTEST DE LOS 33 PARES — operar A FAVOR del tramo.

Corre hipotesis_lado.correr() sobre todas las criptos del dash y agrega.

    python3 daily_pilot/scripts/backtest_33.py

PAPER_ONLY: mide, no opera.
"""
from __future__ import annotations

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
    from hipotesis_lado import correr
    filas = []
    for par in PARES:
        try:
            r = correr(par, '1d', 150)
        except Exception as e:
            print(f'  {par:<12} ERROR {e}')
            continue
        if not r:
            print(f'  {par:<12} sin datos')
            continue
        s = r['retro_fav']
        filas.append({'par': par, 'tramo_dir': r['tramo']['direccion'],
                      'n': s.get('n', 0),
                      'acierto': s.get('acierto_pct'),
                      'fb': s.get('factor_beneficio'),
                      'esperanza': s.get('esperanza_R'),
                      'dd': s.get('drawdown_R')})
        print(f"  {par:<12} n={s.get('n', 0):<3} acierto {str(s.get('acierto_pct')):>5}% "
              f"FB {str(s.get('factor_beneficio')):>7} esp {str(s.get('esperanza_R')):>7}R")

    con_n = [f for f in filas if f['n'] >= 5]
    positivos = [f for f in con_n if (f['esperanza'] or 0) > 0]
    print(f'\nPARES CON DATOS: {len(con_n)}/{len(filas)}')
    if con_n:
        print(f"  esperanza positiva: {len(positivos)}/{len(con_n)}")
        print(f"  promedio esperanza: "
              f"{round(sum(f['esperanza'] or 0 for f in con_n)/len(con_n), 3)}R")
    out = BASE / 'daily_pilot' / 'datos' / 'backtest_33.json'
    out.write_text(json.dumps(filas, indent=1, ensure_ascii=False))
    print(f'-> {out}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
