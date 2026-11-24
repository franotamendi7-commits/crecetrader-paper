#!/usr/bin/env python3
"""Descarga historico maximo de klines de Binance (PAPER_ONLY, solo lectura).

Uso:
  python3 daily_pilot/scripts/descargar_velas.py --par BTCUSDT --tf 1d
  python3 daily_pilot/scripts/descargar_velas.py --par BTCUSDT --tf 1h 4h 1d
  python3 daily_pilot/scripts/descargar_velas.py --par ETHUSDT --tf 1d 4h
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
DIR = BASE / 'daily_pilot' / 'datos' / 'velas'
BINANCE = 'https://api.binance.com'

TF_MS = {
    '1m': 60_000, '5m': 300_000, '15m': 900_000, '1h': 3_600_000,
    '4h': 14_400_000, '1d': 86_400_000, '1w': 604_800_000,
}
BINANCE_TF = {'1m': '1m', '5m': '5m', '15m': '15m', '1h': '1h',
              '4h': '4h', '1d': '1d', '1w': '1w'}

PAPER_ONLY = True


def klines_page(par, tf, start_ms, limit=1000):
    url = (f'{BINANCE}/api/v3/klines?symbol={par}&interval={BINANCE_TF[tf]}'
           f'&startTime={start_ms}&limit={limit}')
    for attempt in range(5):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'CreceTrader-pilot/0.1'})
            with urllib.request.urlopen(req, timeout=30) as r:
                data = json.loads(r.read().decode())
            return data
        except Exception as e:
            time.sleep(1 + attempt)
    raise RuntimeError(f'fallo descarga {par} {tf} @ {start_ms}')


def descargar(par, tf):
    ms = TF_MS[tf]
    # empezar desde el origen: 2017-01-01
    start = 1483228800000
    out = []
    seen = set()
    while True:
        page = klines_page(par, tf, start)
        if not page:
            break
        nuevos = 0
        for k in page:
            ts = int(k[0])
            if ts in seen:
                continue
            seen.add(ts)
            out.append({'ts': ts, 'open': float(k[1]), 'high': float(k[2]),
                        'low': float(k[3]), 'close': float(k[4]),
                        'volumen': float(k[5])})
            nuevos += 1
        last_ts = int(page[-1][0])
        # avanzar
        nxt = last_ts + ms
        if nxt <= start:
            break
        start = nxt
        # parar si llegamos a "ahora" (ultima vela cerrada)
        now_ms = int(time.time() * 1000)
        if last_ts >= now_ms - ms:
            break
        if len(page) < 1000:
            # puede ser fin de datos disponibles
            # aun asi, una pagina corta al final es normal; parar si no hubo nuevos
            if nuevos == 0:
                break
        time.sleep(0.2)
        if len(out) > 200_000:
            break
    out.sort(key=lambda x: x['ts'])
    # dedup final
    uniq = []
    seen2 = set()
    for v in out:
        if v['ts'] in seen2:
            continue
        seen2.add(v['ts'])
        uniq.append(v)
    return uniq


def verificar(velas, tf):
    ms = TF_MS[tf]
    n = len(velas)
    if n == 0:
        return {'ok': False, 'motivo': 'sin velas'}
    # gaps grandes: > 2 * intervalo (tolerancia para fines de semana en diario? diario no tiene gaps)
    gaps = []
    for i in range(1, n):
        dt = velas[i]['ts'] - velas[i - 1]['ts']
        if dt > 2 * ms + 1000:
            gaps.append((i, dt // ms))
    first = datetime.fromtimestamp(velas[0]['ts'] / 1000, tz=timezone.utc)
    last = datetime.fromtimestamp(velas[-1]['ts'] / 1000, tz=timezone.utc)
    return {
        'n': n,
        'primera': first.strftime('%Y-%m-%d %H:%M'),
        'ultima': last.strftime('%Y-%m-%d %H:%M'),
        'gaps_grandes': len(gaps),
        'gaps_detalle': gaps[:10],
        'ok': len(gaps) == 0 or (tf in ('1d',) and len(gaps) < 5),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--par', required=True)
    ap.add_argument('--tf', nargs='+', required=True)
    args = ap.parse_args()
    DIR.mkdir(parents=True, exist_ok=True)
    for tf in args.tf:
        print(f'descargando {args.par} {tf}...', flush=True)
        vs = descargar(args.par, tf)
        path = DIR / f'{args.par}_{tf}.json'
        path.write_text(json.dumps({'par': args.par, 'tf': tf,
                                   'fuente': 'binance', 'velas': vs},
                                  indent=1, ensure_ascii=False))
        v = verificar(vs, tf)
        print(f'  -> {v}')
        if not v['ok']:
            print('  ADVERTENCIA: gaps grandes detectados', flush=True)


if __name__ == '__main__':
    main()
