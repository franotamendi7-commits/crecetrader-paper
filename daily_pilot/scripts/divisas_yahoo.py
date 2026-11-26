#!/usr/bin/env python3
"""Descargar las 12 divisas de Quantfury desde Yahoo Finance (yfinance).
Guarda 1h y 4h en daily_pilot/datos/velas con el MISMO formato que Binance.
Requiere /usr/bin/python3 (tiene yfinance instalado).
"""
import json, time
from pathlib import Path
import yfinance as yf

BASE = Path(__file__).resolve().parents[2]
OUT = BASE / 'daily_pilot' / 'datos' / 'velas'
PAIRES = ['AUDUSD=X','EURUSD=X','GBPUSD=X','NZDUSD=X','USDBRL=X','USDCAD=X',
          'USDCHF=X','USDCNY=X','USDHKD=X','USDJPY=X','USDMXN=X','USDNOK=X']


def filas(df):
    out = []
    for ts, r in df.iterrows():
        try:
            o, h, l, c = (float(r['Open']), float(r['High']),
                          float(r['Low']), float(r['Close']))
        except Exception:
            continue
        if not all(x == x and x > 0 for x in (o, h, l, c)):
            continue
        out.append({'ts': int(ts.timestamp() * 1000), 'open': o, 'high': h,
                    'low': l, 'close': c, 'volumen': 0})
    return out


def resample(v, horas=4):
    step = horas * 3600 * 1000
    out, cur = [], None
    for x in v:
        b = (x['ts'] // step) * step
        if cur is None or cur['ts'] != b:
            if cur:
                out.append(cur)
            cur = {'ts': b, 'open': x['open'], 'high': x['high'],
                   'low': x['low'], 'close': x['close'], 'volumen': 0}
        else:
            cur['high'] = max(cur['high'], x['high'])
            cur['low'] = min(cur['low'], x['low'])
            cur['close'] = x['close']
    if cur:
        out.append(cur)
    return out


def bajar(t, intentos=4):
    for i in range(intentos):
        try:
            return yf.Ticker(t).history(period='730d', interval='1h', auto_adjust=False)
        except Exception as e:
            if i == intentos - 1:
                raise
            time.sleep(3 + i * 3)


def main():
    for t in PAIRES:
        try:
            df = bajar(t)
            v = filas(df)
            if len(v) < 500:
                print(f'{t}: solo {len(v)} velas, salto', flush=True)
                continue
            v4 = resample(v)
            nombre = t.replace('=X', '')
            for tf, data in (('1h', v), ('4h', v4)):
                p = OUT / f'{nombre}_{tf}.json'
                p.write_text(json.dumps({'par': nombre, 'tf': tf,
                                         'fuente': 'yahoo', 'velas': data},
                                        indent=1, ensure_ascii=False))
            print(f'{nombre}: {len(v)} 1h · {len(v4)} 4h', flush=True)
        except Exception as e:
            print(f'{t}: ERROR {type(e).__name__} {str(e)[:80]}', flush=True)
        time.sleep(1.5)


if __name__ == '__main__':
    main()
