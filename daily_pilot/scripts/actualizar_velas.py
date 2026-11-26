#!/usr/bin/env python3
"""ACTUALIZAR VELAS — incremental, 13 pares operativos, 1h y 4h.

Solo baja desde la ultima vela guardada. Corre cada 15 min.
Los trackers leen estos archivos: sin esto el forward esta congelado.
"""
from __future__ import annotations
import argparse, datetime, json, sys, time, urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE / 'daily_pilot' / 'scripts'))
from descargar_velas import BINANCE, BINANCE_FALLBACK, BINANCE_TF, DIR, klines_page  # noqa: E402

PARESES = [
    'BTCUSDT','XRPUSDT','HBARUSDT','LINKUSDT','AVAXUSDT','FILUSDT','NEARUSDT',
    'THETAUSDT','ETCUSDT','ARBUSDT','INJUSDT','DOGEUSDT','DOTUSDT',
]
LIM = 1000


def fetch(par: str, tf: str, desde: int | None):
    return klines_page(par, tf, desde or 1483228800000, LIM)


def actualizar(par: str, tf: str, verbose=False) -> dict:
    path = DIR / f'{par}_{tf}.json'
    data = json.loads(path.read_text()) if path.exists() else {'velas': []}
    velas = data.get('velas', [])
    desde = (velas[-1]['ts'] + 1) if velas else None
    nuevas = []
    for _ in range(5):
        lote = fetch(par, tf, desde)
        if not lote:
            break
        nuevas += [{'ts': int(k[0]), 'open': float(k[1]), 'high': float(k[2]),
                    'low': float(k[3]), 'close': float(k[4]), 'volumen': float(k[5])}
                   for k in lote]
        if len(lote) < LIM:
            break
        desde = int(lote[-1][0]) + 1
        time.sleep(0.12)
    if nuevas:
        velas += [v for v in nuevas if not velas or v['ts'] > velas[-1]['ts']]
        path.write_text(json.dumps({'par':par,'tf':tf,'fuente':'binance',
                                    'velas':velas}, indent=1, ensure_ascii=False))
    return {'par':par,'tf':tf,'nuevas':len(nuevas),'total':len(velas),
            'ultima':datetime.datetime.utcfromtimestamp(velas[-1]['ts']/1000).strftime('%Y-%m-%d %H:%M') if velas else ''}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--pares',nargs='*',default=PARESES)
    ap.add_argument('--tf',nargs='+',default=['1h','4h'])
    a=ap.parse_args()
    res=[]
    for par in a.pares:
        for tf in a.tf:
            try:
                r=actualizar(par,tf)
            except Exception as e:
                r={'par':par,'tf':tf,'nuevas':-1,'error':f'{type(e).__name__}: {e}'}
            res.append(r)
            print(f"{r['par']:>10} {r['tf']:>3} +{r['nuevas']:>4} · {r.get('ultima','')} "
                  f"{r.get('error','')}", flush=True)
    ok=sum(1 for r in res if r['nuevas']>=0)
    tot=sum(max(0,r['nuevas']) for r in res)
    print(f"OK {ok}/{len(res)} · {tot} velas nuevas", flush=True)


if __name__=='__main__': main()
