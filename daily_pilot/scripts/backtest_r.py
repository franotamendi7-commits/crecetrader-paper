#!/usr/bin/env python3
"""BACKTEST DE RESULTADO (R) — rentabilidad, no «hold».

Para cada toque de un nivel del metodo simula la operacion completa:

    entrada : el nivel (el toque)
    stop    : el extremo del tramo en la direccion que invalida
    target  : el siguiente nivel del metodo en la direccion del trade

Walk-forward: los niveles se calculan con velas ANTERIORES a la ventana.
Dentro de una vela, si toca stop y target a la vez, gana el STOP (conservador).

    python3 daily_pilot/scripts/backtest_r.py BTCUSDT --tf 1d --detalle 150
    python3 daily_pilot/scripts/backtest_r.py BTCUSDT --confirmacion

PAPER_ONLY: mide, no opera.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE / 'daily_pilot' / 'core'))

PLAZO = {'1w': 'largo', '1d': 'media', '4h': 'corto'}


def _wilson(k: int, n: int):
    if not n:
        return None
    z = 1.96
    den = 1 + z * z / n
    c = (k / n + z * z / (2 * n)) / den
    h = z * math.sqrt(k / n * (1 - k / n) / n + z * z / (4 * n * n)) / den
    return round(max(0.0, c - h) * 100, 1), round(min(1.0, c + h) * 100, 1)


def _velas(par: str, tf: str) -> list | None:
    from velas import velas
    r = velas(par, tf, limite=500)
    return None if 'error' in r else r['velas']


def tramo_y_niveles(par: str, tf: str, detalle: int):
    from tramos import tramo_ciclo
    from zonas import zonas
    v = _velas(par, tf)
    if not v:
        return None, None, None, None
    inicio = max(20, len(v) - detalle)
    t = tramo_ciclo(v[:inicio], 3, 60)
    if 'error' in t:
        return None, None, None, None
    z = zonas(t['minimo'], t['maximo'], plazo=PLAZO.get(tf, 'media'),
              direccion=t['direccion'])
    niveles = ([(k, float(x), 'retro') for k, x in z['zonas_compra'].items()] +
               [(k, float(x), 'ext') for k, x in z['extensiones'].items()])
    niveles = [x for x in niveles if x[1] > 0]
    return v, t, niveles, inicio


def side_de(tipo: str, direccion: str) -> str:
    """Retroceso en bajista -> long; extension en bajista -> short."""
    if direccion == 'bajista':
        return 'long' if tipo == 'retro' else 'short'
    return 'short' if tipo == 'retro' else 'long'


def stop_de(side: str, entry: float, t: dict) -> float:
    mn, mx = t['minimo'], t['maximo']
    if side == 'long':
        cands = [x for x in (mn, mx) if x < entry]
        return max(cands) if cands else mn
    cands = [x for x in (mn, mx) if x > entry]
    return min(cands) if cands else mx


def target_de(side: str, entry: float, niveles: list, t: dict) -> float:
    precios = [p for (_, p, _) in niveles]
    if side == 'long':
        cands = sorted(p for p in precios if p > entry)
        return cands[0] if cands else t['maximo']
    cands = sorted((p for p in precios if p < entry), reverse=True)
    return cands[0] if cands else t['minimo']


def simular(datos: list, i: int, side: str, entry: float, stop: float,
            target: float, risk: float) -> tuple:
    """Devuelve (outcome_en_R, como_salio) desde el toque en i."""
    R = (target - entry) / risk if side == 'long' else (entry - target) / risk
    for j in range(i + 1, len(datos)):
        x = datos[j]
        if side == 'long':
            toco_stop = x['low'] <= stop
            toco_target = x['high'] >= target
            if toco_stop:                       # conservador: si toca ambos, gana el stop
                return -1.0, 'stop'
            if toco_target:
                return R, 'target'
        else:
            toco_stop = x['high'] >= stop
            toco_target = x['low'] <= target
            if toco_stop:
                return -1.0, 'stop'
            if toco_target:
                return R, 'target'
    c = datos[-1]['close']
    parc = ((c - entry) / risk) if side == 'long' else ((entry - c) / risk)
    return round(parc, 3), 'parcial'


def backtest_r(par: str, tf: str = '1d', detalle: int = 90,
               min_muestra: int = 5) -> dict:
    v, t, niveles, inicio = tramo_y_niveles(par, tf, detalle)
    if v is None or t is None:
        return {'error': 'sin datos'}
    datos = v[inicio:]
    out_niveles, flat = [], []
    for etq, nivel, tipo in niveles:
        side = side_de(tipo, t['direccion'])
        stop = stop_de(side, nivel, t)
        target = target_de(side, nivel, niveles, t)
        risk = (nivel - stop) if side == 'long' else (stop - nivel)
        if risk <= 0:
            continue
        R = (target - nivel) / risk if side == 'long' else (nivel - target) / risk
        ops = []
        for i, x in enumerate(datos):
            if not (x['low'] <= nivel <= x['high']):
                continue
            o, hit = simular(datos, i, side, nivel, stop, target, risk)
            ops.append({'hit': hit, 'outcome': o})
        if not ops:
            continue
        outs = [o['outcome'] for o in ops]
        out_niveles.append(_resumen(nivel, f'{tipo} {etq}', side, stop, target,
                                    R, ops, min_muestra))
        flat.extend(outs)
    agg = _agregado(flat) if flat else {}
    return {'par': par, 'tf': tf, 'detalle': detalle,
            'tramo': {'min': round(t['minimo'], 2), 'max': round(t['maximo'], 2),
                      'direccion': t['direccion']},
            'niveles': out_niveles, 'agregado': agg}


def _resumen(nivel, etiqueta, side, stop, target, R, ops, min_muestra) -> dict:
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
    return {'nivel': round(nivel, 2), 'etiqueta': etiqueta, 'lado': side,
            'stop': round(stop, 2), 'target': round(target, 2), 'R_teorico': round(R, 2),
            'n': len(ops), 'acierto_pct': round(len(pos) / len(ops) * 100, 1),
            'factor_beneficio': (round(pf, 3) if pf != float('inf') else None),
            'esperanza': round(sum(outs) / len(outs), 3),
            'drawdown_R': round(dd, 2),
            'hits': {h: sum(1 for o in ops if o['hit'] == h) for h in ('target', 'stop', 'parcial')},
            'suficiente': len(ops) >= min_muestra,
            'ic95': _wilson(len(pos), len(ops))}


def _agregado(flat: list) -> dict:
    pos = [o for o in flat if o > 0]
    neg = [o for o in flat if o < 0]
    pf = (sum(pos) / abs(sum(neg))) if (neg and sum(neg) != 0) else (
        float('inf') if pos else 0.0)
    return {'n': len(flat), 'acierto_pct': round(len(pos) / len(flat) * 100, 1),
            'factor_beneficio': (round(pf, 3) if pf != float('inf') else None),
            'esperanza': round(sum(flat) / len(flat), 3),
            'ic95': _wilson(len(pos), len(flat))}


def confirmacion(par: str, tf: str = '1d', detalle: int = 90) -> dict:
    """Compara entrar al toque vs. entrar cuando la vela cierra a favor."""
    v, t, niveles, inicio = tramo_y_niveles(par, tf, detalle)
    if v is None or t is None:
        return {'error': 'sin datos'}
    datos = v[inicio:]
    res = {}
    for modo in ('toque', 'confirmacion'):
        outs = []
        for etq, nivel, tipo in niveles:
            side = side_de(tipo, t['direccion'])
            stop = stop_de(side, nivel, t)
            target = target_de(side, nivel, niveles, t)
            for i, x in enumerate(datos):
                if not (x['low'] <= nivel <= x['high']):
                    continue
                if modo == 'confirmacion':
                    # la vela que toca debe cerrar a favor del nivel
                    if side == 'long' and x['close'] < nivel:
                        continue
                    if side == 'short' and x['close'] > nivel:
                        continue
                    entry = x['close']
                else:
                    entry = nivel
                risk = (entry - stop) if side == 'long' else (stop - entry)
                if risk <= 0:
                    continue
                o, _ = simular(datos, i, side, entry, stop, target, risk)
                outs.append(o)
        res[modo] = _agregado(outs) if outs else {}
    return {'par': par, 'tf': tf, 'comparacion': res}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('par')
    ap.add_argument('--tf', default='1d')
    ap.add_argument('--detalle', type=int, default=150)
    ap.add_argument('--confirmacion', action='store_true')
    a = ap.parse_args()
    par, tf = a.par.upper(), a.tf
    if a.confirmacion:
        r = confirmacion(par, tf, a.detalle)
        print(json.dumps(r, indent=1, ensure_ascii=False))
        return 0
    r = backtest_r(par, tf, a.detalle)
    if 'error' in r:
        print('ERROR:', r['error']); return 1
    tr = r['tramo']
    print(f"BACKTEST DE R · {r['par']} {r['tf']} · tramo ({tr['direccion']}) "
          f"{tr['min']} -> {tr['max']} · {r['detalle']} velas")
    ag = r['agregado']
    if ag:
        print(f"  AGREGADO: n={ag['n']} acierto {ag['acierto_pct']}% "
              f"factor beneficio {ag['factor_beneficio']} esperanza {ag['esperanza']}R "
              f"IC{ag['ic95']}")
    for f in sorted(r['niveles'], key=lambda x: -(x['n'])):
        marca = '' if f['suficiente'] else '  (muestra chica)'
        print(f"   {f['etiqueta']:<12}{f['lado']:<6} n={f['n']:<3} R={f['R_teorico']:<6}"
              f" acierto {f['acierto_pct']:>5}%  FB {str(f['factor_beneficio']):>7}"
              f"  esp {f['esperanza']:>6}R  dd {f['drawdown_R']:>6}{marca}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
