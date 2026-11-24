#!/usr/bin/env python3
"""COMPARATIVA DE STOPS — ¿cual hace que el metodo sea rentable?

Mismo backtest walk-forward, mismo target (siguiente nivel), cinco stops:

    estructural (swing n=3) · riesgo 1% · riesgo 2% · ATR x0,5 · ATR x1,0

Regla conservadora: si una vela toca stop y target, gana el STOP.
Sin look-ahead: el swing se confirma solo con velas ya vistas ([:i+1]).

    python3 daily_pilot/scripts/backtest_stop.py BTCUSDT --tf 1d --detalle 150

PAPER_ONLY: mide, no opera.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE / 'daily_pilot' / 'core'))

PLAZO = {'1w': 'largo', '1d': 'media', '4h': 'corto'}
CANDIDATOS = (
    ('estructural (swing)', 'estructural', {}),
    ('riesgo 1%', 'pct', {'pct': 1.0}),
    ('riesgo 2%', 'pct', {'pct': 2.0}),
    ('ATR x0.5', 'atr', {'k': 0.5}),
    ('ATR x1.0', 'atr', {'k': 1.0}),
)


def _velas(par: str, tf: str):
    from velas import velas
    r = velas(par, tf, limite=500)
    return None if 'error' in r else r['velas']


def atr(velas: list, n: int = 14) -> float:
    trs = [max(velas[i]['high'] - velas[i]['low'],
               abs(velas[i]['high'] - velas[i - 1]['close']),
               abs(velas[i]['low'] - velas[i - 1]['close']))
           for i in range(1, len(velas))]
    if not trs:
        return velas[-1]['close'] * 0.01
    return sum(trs[-n:]) / min(n, len(trs))


def swings_confirmados(velas: list, n: int = 3):
    """Swings sin look-ahead: exigen n velas a la DERECHA ya vistas."""
    altos, bajos = [], []
    for i in range(len(velas)):
        izq = velas[max(0, i - n):i]
        der = velas[i + 1:i + 1 + n]
        if len(der) < n:
            continue
        if all(velas[i]['high'] >= x['high'] for x in izq + der):
            altos.append((i, velas[i]['high']))
        if all(velas[i]['low'] <= x['low'] for x in izq + der):
            bajos.append((i, velas[i]['low']))
    return altos, bajos


def stop_de(tipo: str, side: str, entry: float, velas_hasta: list, **kw):
    if tipo == 'estructural':
        altos, bajos = swings_confirmados(velas_hasta)
        if side == 'long':
            c = [p for _, p in bajos if p < entry]
            return max(c) if c else None
        c = [p for _, p in altos if p > entry]
        return min(c) if c else None
    if tipo == 'pct':
        pct = kw.get('pct', 2.0)
        return entry * (1 - pct / 100.0) if side == 'long' \
            else entry * (1 + pct / 100.0)
    if tipo == 'atr':
        k = kw.get('k', 1.0)
        a = atr(velas_hasta)
        return entry - k * a if side == 'long' else entry + k * a
    raise ValueError(tipo)


def side_de(tipo_nivel: str, direccion: str) -> str:
    if direccion == 'bajista':
        return 'long' if tipo_nivel == 'retro' else 'short'
    return 'short' if tipo_nivel == 'retro' else 'long'


def target_de(side: str, entry: float, niveles: list, t: dict) -> float:
    precios = [p for (_, p, _) in niveles]
    if side == 'long':
        c = sorted(p for p in precios if p > entry)
        return c[0] if c else t['maximo']
    c = sorted((p for p in precios if p < entry), reverse=True)
    return c[0] if c else t['minimo']


def simular(datos: list, niveles: list, t: dict, tipo: str, **kw) -> list:
    outs = []
    for etq, nivel, tipo_nivel in niveles:
        if nivel <= 0:
            continue
        side = side_de(tipo_nivel, t['direccion'])
        target = target_de(side, nivel, niveles, t)
        for i, x in enumerate(datos):
            if not (x['low'] <= nivel <= x['high']):
                continue
            stop = stop_de(tipo, side, nivel, datos[:i + 1], **kw)
            if stop is None:
                continue
            risk = (nivel - stop) if side == 'long' else (stop - nivel)
            if risk <= 0:
                continue
            R = (target - nivel) / risk if side == 'long' else (nivel - target) / risk
            outcome, hit = 0.0, 'parcial'
            for j in range(i + 1, len(datos)):
                y = datos[j]
                if side == 'long':
                    if y['low'] <= stop:
                        outcome, hit = -1.0, 'stop'; break
                    if y['high'] >= target:
                        outcome, hit = R, 'target'; break
                else:
                    if y['high'] >= stop:
                        outcome, hit = -1.0, 'stop'; break
                    if y['low'] <= target:
                        outcome, hit = R, 'target'; break
            if hit == 'parcial':
                c = datos[-1]['close']
                outcome = ((c - nivel) / risk) if side == 'long' \
                    else ((nivel - c) / risk)
            outs.append({'nivel': round(nivel, 2), 'lado': side,
                         'stop': round(stop, 2), 'target': round(target, 2),
                         'R': round(R, 2), 'outcome': round(outcome, 3), 'hit': hit})
    return outs


def resumen(ops: list) -> dict:
    if not ops:
        return {'n': 0}
    outs = [o['outcome'] for o in ops]
    pos = [o for o in outs if o > 0]
    neg = [o for o in outs if o < 0]
    pf = (sum(pos) / abs(sum(neg))) if (neg and sum(neg) != 0) else (
        float('inf') if pos else 0.0)
    cum = peak = dd = 0.0
    for o in outs:
        cum += o
        peak = max(peak, cum)
        dd = min(dd, cum - peak)
    return {'n': len(outs), 'acierto_pct': round(len(pos) / len(outs) * 100, 1),
            'factor_beneficio': (round(pf, 3) if pf != float('inf') else None),
            'esperanza_R': round(sum(outs) / len(outs), 3),
            'drawdown_R': round(dd, 2),
            'hits': {h: sum(1 for o in ops if o['hit'] == h)
                     for h in ('target', 'stop', 'parcial')}}


def comparar(par: str, tf: str = '1d', detalle: int = 150) -> dict:
    from tramos import tramo_ciclo
    from zonas import zonas
    v = _velas(par, tf)
    if not v:
        return {'error': 'sin velas'}
    inicio = max(20, len(v) - detalle)
    t = tramo_ciclo(v[:inicio], 3, 60)
    if 'error' in t:
        return {'error': t['error']}
    z = zonas(t['minimo'], t['maximo'], plazo=PLAZO.get(tf, 'media'),
              direccion=t['direccion'])
    niveles = ([(k, float(x), 'retro') for k, x in z['zonas_compra'].items()] +
               [(k, float(x), 'ext') for k, x in z['extensiones'].items()])
    niveles = [x for x in niveles if x[1] > 0]
    datos = v[inicio:]
    out = {}
    for nombre, tipo, kw in CANDIDATOS:
        out[nombre] = resumen(simular(datos, niveles, t, tipo, **kw))
    return {'par': par, 'tf': tf, 'detalle': detalle,
            'tramo': {'min': round(t['minimo'], 2), 'max': round(t['maximo'], 2),
                      'direccion': t['direccion']},
            'candidatos': out}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('par')
    ap.add_argument('--tf', default='1d')
    ap.add_argument('--detalle', type=int, default=150)
    a = ap.parse_args()
    r = comparar(a.par.upper(), a.tf, a.detalle)
    if 'error' in r:
        print('ERROR:', r['error']); return 1
    tr = r['tramo']
    print(f"STOPS · {r['par']} {r['tf']} · tramo ({tr['direccion']}) "
          f"{tr['min']} -> {tr['max']} · {r['detalle']} velas")
    print(f"  {'candidato':<22}{'n':>4}{'acierto':>9}{'FB':>8}{'esperanza':>11}{'dd':>8}")
    for nombre, _, _ in CANDIDATOS:
        s = r['candidatos'][nombre]
        if not s.get('n'):
            print(f"  {nombre:<22}{'0':>4}   sin operaciones")
            continue
        print(f"  {nombre:<22}{s['n']:>4}{s['acierto_pct']:>8}%"
              f"{str(s['factor_beneficio']):>8}{str(s['esperanza_R'])+'R':>11}"
              f"{s['drawdown_R']:>8}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
