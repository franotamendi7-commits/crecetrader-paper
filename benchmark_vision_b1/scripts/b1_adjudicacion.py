#!/usr/bin/env python3
"""B1: comparacion de dos anotaciones y generacion de desacuerdos."""
import csv
import json
import sys
from pathlib import Path

BASE = Path('/Users/franciscootamendi/YouTubeTradingAgent')
OUT = BASE / 'benchmark_vision_b1' / 'annotations'
CAMPOS = ['instrument', 'timeframe', 'price_levels', 'indicators', 'structure']


def norm(v):
    return (v or '').strip().lower()


def main():
    if len(sys.argv) != 3:
        print('uso: b1_adjudicacion.py anotador1.csv anotador2.csv')
        sys.exit(1)
    a1 = {r['frame_id']: r for r in csv.DictReader(open(sys.argv[1]))}
    a2 = {r['frame_id']: r for r in csv.DictReader(open(sys.argv[2]))}
    ids = sorted(set(a1) | set(a2))
    filas = []
    des = {}
    for fid in ids:
        r1, r2 = a1.get(fid, {}), a2.get(fid, {})
        fila = {'frame_id': fid}
        desac = []
        for c in CAMPOS:
            v1, v2 = norm(r1.get(c)), norm(r2.get(c))
            if not v1 or not v2:
                est = 'missing'
            elif v1 == v2:
                est = 'agreement'
            elif 'no legible' in v1 or 'no legible' in v2:
                est = 'one_abstain'
            else:
                est = 'disagreement'
            fila[c] = est
            if est in ('disagreement', 'one_abstain'):
                desac.append({'campo': c, 'anotador1': r1.get(c, ''), 'anotador2': r2.get(c, '')})
        fila['n_desacuerdos'] = len(desac)
        filas.append(fila)
        if desac:
            des[fid] = desac
    cols = ['frame_id'] + CAMPOS + ['n_desacuerdos']
    with open(OUT / 'adjudicacion.csv', 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader(); w.writerows(filas)
    (OUT / 'desacuerdos.json').write_text(json.dumps(des, ensure_ascii=False, indent=2))
    n_ag = sum(1 for f in filas for c in CAMPOS if f[c] == 'agreement')
    n_des = sum(1 for f in filas for c in CAMPOS if f[c] == 'disagreement')
    print(f'frames={len(filas)} agreement={n_ag} disagreement={n_des} '
          f'one_abstain={sum(1 for f in filas for c in CAMPOS if f[c] == "one_abstain")}')
    print('sin desacuerdos:', sum(1 for f in filas if f['n_desacuerdos'] == 0))


if __name__ == '__main__':
    main()
