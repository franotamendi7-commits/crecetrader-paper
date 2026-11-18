#!/usr/bin/env python3
"""B4 (NO EJECUTAR sin referencia humana): compara respuestas del modelo contra
la referencia humana normalizada (B4_referencia_humana.csv)."""
import argparse
import csv
import json
import re
from pathlib import Path


def extraer_json(txt):
    if not txt:
        return {}
    m = re.search(r'\{.*\}', txt, re.S)
    if not m:
        return {}
    try:
        return json.loads(m.group(0))
    except Exception:
        return {}


def norm(v):
    return (v or '').strip().lower()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--modelo', required=True)
    ap.add_argument('--referencia', required=True)
    a = ap.parse_args()
    ref = {r['frame']: r for r in csv.DictReader(open(a.referencia))}
    res = json.load(open(a.modelo))
    n = len(res)
    aciertos = {'instrument': 0, 'timeframe': 0, 'market_structure': 0}
    indic_m = indic_h = 0
    prec_m = prec_h = 0
    aluc = 0
    por_frame = []
    for r in res:
        fid = r['frame']
        h = extraer_json(r.get('respuesta_cruda', ''))
        g = ref.get(fid)
        if not g:
            continue
        row = {'frame': fid}
        for campo in ('instrument', 'timeframe', 'market_structure'):
            mv = norm(h.get(campo))
            gv = norm(g.get(campo))
            if gv in ('', 'unknown', 'no legible'):
                row[campo] = 'na'
                continue
            ok = (mv == gv)
            aciertos[campo] += int(ok)
            row[campo] = 'ok' if ok else f'error (modelo={mv} ref={gv})'
        gm = set(x.strip().lower() for x in (g.get('indicators') or '').split(';') if x.strip())
        mm = set(x.strip().lower() for x in (h.get('indicators') or []) if x.strip())
        indic_h += len(gm); indic_m += len(mm & gm)
        gp = set(norm(x) for x in (g.get('price_labels') or '').split(';') if x.strip())
        mp = set()
        for p in (h.get('visible_price_labels') or []):
            if isinstance(p, dict):
                mp.add(norm(p.get('value')))
        prec_h += len(gp); prec_m += len(gp & mp)
        aluc += len(mp - gp) if gp else 0
        por_frame.append(row)
    def pct(x, y):
        return round(100 * x / y, 1) if y else None
    salida = {
        'frames': n,
        'instrument_accuracy': pct(aciertos['instrument'], n),
        'timeframe_accuracy': pct(aciertos['timeframe'], n),
        'market_structure_accuracy': pct(aciertos['market_structure'], n),
        'indicators_precision': pct(indic_m, indic_h),
        'prices_recall': pct(prec_m, prec_h),
        'posibles_alucinaciones_precios': aluc,
        'por_frame': por_frame,
    }
    print(json.dumps({k: v for k, v in salida.items() if k != 'por_frame'}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
