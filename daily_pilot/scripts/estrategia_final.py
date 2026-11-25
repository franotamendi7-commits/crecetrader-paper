#!/usr/bin/env python3
"""ESTRATEGIA FINAL VALIDADA — Bull-run pullback, cartera BTC + ETH.

Parametros elegidos por busqueda con null sintetico + walk-forward:
  BTC: ema13 / emaT200 / swing5 / ret_pos / fib1.5 / BE@1R
  ETH: ema21 / emaT100 / swing3 / ret_pos / fib1.5 / BE@1R

STOP fijo = swing low post-cambio de tendencia. LOTE = riesgo/(entrada-stop).
Riesgo recomendado: 0,5%-1% por operacion. PAPER_ONLY.

Uso:
    python3 daily_pilot/scripts/estrategia_final.py
"""
from __future__ import annotations

import datetime
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE / 'daily_pilot' / 'scripts'))
import estrategia_bull as Z  # noqa: E402

CONFIG = {
    'BTC': dict(ema_fast=13, ema_trend=200, swing_n=5,
                regimen='ret_pos', fibo_ext=1.5, be_at=1.0),
    'ETH': dict(ema_fast=21, ema_trend=100, swing_n=3,
                regimen='ret_pos', fibo_ext=1.5, be_at=1.0),
}
CAPITAL = 300.0
RIESGO = 0.01     # 1% recomendado (0.5% si queres mas colchon)


def analizar(par: str) -> dict:
    v = Z.E.cargar(par, '4h')
    if not v:
        return {'par': par, 'error': 'sin velas 4h'}
    kw = CONFIG[par]
    det = lambda vv: Z.detectar(vv, **kw)
    sen = det(v)
    out = Z.simular(v, sen)
    m = Z.E.metricas(out)
    A = Z.E.anios(v)
    m['/mes'] = round(m['n'] / A / 12, 1)

    # ultima senal y su estado
    ult = None
    if sen:
        s, o = sen[-1], out[-1]
        i = s['i']
        stop_actual = s['entry'] if v[-1]['high'] >= s['entry'] + (s['entry'] - s['stop']) else s['stop']
        estado = ('ABIERTA' if v[-1]['ts'] == v[i]['ts'] or
                  (v[-1]['low'] > stop_actual and v[-1]['high'] < s['target'])
                  else 'CERRADA')
        sz = Z.E.size_position(CAPITAL * RIESGO, s['entry'], s['stop'])
        ult = {'fecha': datetime.datetime.utcfromtimestamp(v[i]['ts'] / 1000).strftime('%Y-%m-%d %H:%M'),
               'entrada': round(s['entry'], 2), 'stop_fijo': round(s['stop'], 2),
               'target': round(s['target'], 2), 'estado': estado,
               'sizing_1pct': sz}
    return {'par': par, 'precio': round(v[-1]['close'], 2),
            'actualizado': datetime.datetime.utcfromtimestamp(v[-1]['ts'] / 1000).strftime('%Y-%m-%d %H:%M'),
            'backtest': m, 'ultima_senal': ult}


def main():
    res = {'estrategia': 'bull-run pullback · stop swing fijo · target fib1.5 · BE@1R',
           'validacion': 'BTC null p=0.000 / WF test +0.170R · ETH null p=0.050 / WF test +0.102R',
           'capital': CAPITAL, 'riesgo_pct': RIESGO * 100,
           'generado': datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC'),
           'pares': [analizar(p) for p in CONFIG],
           'aviso': 'PAPER ONLY. No ejecuta ordenes.'}
    dest = BASE / 'daily_pilot' / 'datos' / 'estrategia_final.json'
    dest.write_text(json.dumps(res, indent=2), encoding='utf-8')
    print(f'-> {dest}')
    print(json.dumps(res, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
