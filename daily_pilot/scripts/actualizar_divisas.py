#!/usr/bin/env python3
"""Actualizar velas de divisas (Yahoo/yfinance) de forma incremental.

Se usa SOLO para USDBRL mientras este en la cartera. Las otras 11 quedan
descargadas para investigacion. Requiere /usr/bin/python3 (tiene yfinance).
"""
from __future__ import annotations
import json, sys
from pathlib import Path
BASE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE / 'daily_pilot' / 'scripts'))
from divisas_yahoo import OUT, resample, bajar  # noqa: E402

PAIRES = ['USDBRL=X']


def main():
    import yfinance as yf
    total = 0
    for t in PAIRES:
        par = t.replace('=X', '')
        p1 = OUT / f'{par}_1h.json'
        try:
            df = bajar(t)
            velas = []
            for ts, r in df.iterrows():
                try:
                    velas.append({'ts': int(ts.timestamp()*1000),
                                  'open': float(r['Open']), 'high': float(r['High']),
                                  'low': float(r['Low']), 'close': float(r['Close']),
                                  'volumen': 0})
                except Exception:
                    continue
            prev = json.loads(p1.read_text())['velas'] if p1.exists() else []
            ultimo = prev[-1]['ts'] if prev else 0
            nuevas = [v for v in velas if v['ts'] > ultimo]
            if nuevas:
                todas = prev + nuevas
                p1.write_text(json.dumps({'par':par,'tf':'1h','fuente':'yahoo',
                                          'velas':todas}, indent=1, ensure_ascii=False))
                p4 = OUT / f'{par}_4h.json'
                v4 = resample(todas)
                p4.write_text(json.dumps({'par':par,'tf':'4h','fuente':'yahoo',
                                          'velas':v4}, indent=1, ensure_ascii=False))
            total += len(nuevas)
            print(f'{par}: +{len(nuevas)} velas', flush=True)
        except Exception as e:
            print(f'{par}: ERROR {type(e).__name__} {str(e)[:60]}', flush=True)
    print(f'total: +{total}', flush=True)


if __name__ == '__main__':
    main()
