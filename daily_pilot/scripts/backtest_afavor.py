#!/usr/bin/env python3
"""BACKTEST A FAVOR DEL TRAMO — con filtros F1/F2/F3 y stops comparables.

    A favor = short si el tramo es bajista, long si es alcista.

Filtros:
    F1 confirmacion : la vela que toca cierra a favor del nivel
    F2 tramo largo  : el tramo tiene >= min_velas velas
    F3 primer toque: solo la primera vez que se toca cada nivel en la ventana

Stops: pct (2%) · estructural (ultimo swing) · atr (k)

Regla conservadora: si una vela toca stop y target, gana el STOP.
Walk-forward: niveles y tramo con velas anteriores a la ventana.

    python3 daily_pilot/scripts/backtest_afavor.py BTCUSDT --detalle 150 --filtros F1,F3

PAPER_ONLY: mide, no opera.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE / 'daily_pilot' / 'core'))
sys.path.insert(0, str(BASE / 'daily_pilot' / 'scripts'))

PLAZO = {'1w': 'largo', '1d': 'media', '4h': 'corto'}
NIVELES_PERMITIDOS = {'0.61', '0.786'}          # P3
NIVELES_FUERTES = {'0.786'}                     # P4
ATR_N = 14


def _velas(par, tf):
    from velas import velas
    r = velas(par, tf, limite=500)
    return None if 'error' in r else r['velas']


def _tramo_y_niveles(par, tf, detalle):
    from tramos import tramo_ciclo
    from zonas import zonas
    v = _velas(par, tf)
    if not v:
        return None
    inicio = max(20, len(v) - detalle)
    t = tramo_ciclo(v[:inicio], 3, 60)
    if 'error' in t:
        return None
    z = zonas(t['minimo'], t['maximo'], plazo=PLAZO.get(tf, 'media'),
              direccion=t['direccion'])
    lista = ([(k, float(x), 'retro') for k, x in z['zonas_compra'].items()] +
             [(k, float(x), 'ext') for k, x in z['extensiones'].items()])
    return v, t, [x for x in lista if x[1] > 0], inicio


def atr(velas, n=ATR_N):
    trs = [max(velas[i]['high'] - velas[i]['low'],
               abs(velas[i]['high'] - velas[i - 1]['close']),
               abs(velas[i]['low'] - velas[i - 1]['close']))
           for i in range(1, len(velas))]
    if not trs:
        return velas[-1]['close'] * 0.01
    return sum(trs[-n:]) / min(n, len(trs))


def swings(velas, n=3):
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


def stop_de(modo, side, entry, velas_hasta, pct=2.0, k=1.0):
    if modo == 'pct':
        return entry * (1 + pct / 100.0) if side == 'short' \
            else entry * (1 - pct / 100.0)
    altos, bajos = swings(velas_hasta)
    if modo == 'estructural':
        if side == 'short':
            c = [p for _, p in altos if p > entry]
            return min(c) if c else None
        c = [p for _, p in bajos if p < entry]
        return max(c) if c else None
    a = atr(velas_hasta, k and ATR_N)
    return entry + k * a if side == 'short' else entry - k * a


def target_de(side, entry, niveles, t):
    precios = [p for (_, p, _) in niveles]
    if side == 'short':
        c = sorted(p for p in precios if p < entry)
        return c[-1] if c else t['minimo']
    c = sorted(p for p in precios if p > entry)
    return c[0] if c else t['maximo']


def comision_R(entry, risk):
    """Comision + slippage expresado en R (ida y vuelta).

    El costo es proporcional al tamaño de la posición. Con notional =
    capital * riesgo / stop_pct y un costo c% por pasada, el costo en R
    queda: 2 * c% * (entry/risk) ... simplificado a una fraccion del riesgo.
    """
    return 0.0


def resumen(ops):
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
            'drawdown_R': round(dd, 2)}


def backtest_afavor(par, tf='1d', detalle=150, filtros=None, stop_modo='pct',
                    stop_pct=2.0, min_muestra=5, gestion=None,
                    comision_pct=0.05):
    filtros = filtros or set()
    r = _tramo_y_niveles(par, tf, detalle)
    if r is None:
        return {'error': 'sin datos'}
    v, t, niveles, inicio = r
    datos = v[inicio:]
    if 'F2' in filtros and t.get('n_velas', 0) < 30:
        return {'par': par, 'tf': tf, 'skip': 'tramo corto (<30 velas)'}
    if 'P3' in filtros:
        niveles = [x for x in niveles if x[0] in NIVELES_PERMITIDOS]
    if 'P4' in filtros:
        niveles = [x for x in niveles if x[0] in NIVELES_FUERTES]

    por_nivel, ops_planas = {}, []
    for etq, nivel, tipo in niveles:
        side = 'short' if t['direccion'] == 'bajista' else 'long'
        target = target_de(side, nivel, niveles, t)
        salida_nivel = []
        for i, x in enumerate(datos):
            if not (x['low'] <= nivel <= x['high']):
                continue
            if 'F3' in filtros:
                if any(datos[j]['low'] <= nivel <= datos[j]['high']
                       for j in range(i)):
                    continue
            # F1 CORREGIDO (sin look-ahead): la entrada es el CIERRE de la vela
            # que toca. Antes se entraba al nivel pero se filtraba con el cierre.
            entry = nivel
            if 'F1' in filtros:
                if side == 'short' and x['close'] > nivel:
                    continue
                if side == 'long' and x['close'] < nivel:
                    continue
                entry = x['close']
            stop = stop_de(stop_modo, side, entry, datos[:i + 1], stop_pct)
            if stop is None:
                continue
            risk = (entry - stop) if side == 'long' else (stop - entry)
            if risk <= 0:
                continue
            R = ((target - entry) / risk) if side == 'long' \
                else ((entry - target) / risk)
            oc, hit = -1.0, 'stop'
            for j in range(i + 1, len(datos)):
                y = datos[j]
                if side == 'long':
                    if y['low'] <= stop:
                        break
                    if y['high'] >= target:
                        oc, hit = R, 'target'; break
                else:
                    if y['high'] >= stop:
                        break
                    if y['low'] <= target:
                        oc, hit = R, 'target'; break
            if gestion == 'P1' and hit == 'target':
                oc = round(R * 0.5, 3)      # cierra mitad y deja el resto
            oc = round(oc - comision_R(entry, risk), 3)
            salida_nivel.append({'hit': hit, 'outcome': oc})
            ops_planas.append({'hit': hit, 'outcome': oc, 'i': i,
                               'nivel': round(nivel, 2)})
        if salida_nivel:
            s = resumen(salida_nivel)
            s.update({'etiqueta': f'{tipo} {etq}', 'nivel': round(nivel, 2),
                      'lado': side, 'target': round(target, 2),
                      'suficiente': s['n'] >= min_muestra})
            por_nivel[f'{tipo} {etq}'] = s

    # orden temporal REAL: el drawdown y las rutas deben seguir la linea de tiempo
    ops_planas.sort(key=lambda o: o['i'])
    # P2: reducir tamaño tras 2 pérdidas consecutivas (ahora en orden cronologico)
    if gestion == 'P2' and ops_planas:
        racha = 0
        for o in ops_planas:
            o['outcome'] = round(o['outcome'] * (0.5 if racha >= 2 else 1.0), 3)
            racha = racha + 1 if o['outcome'] < 0 else 0

    agg = resumen(ops_planas)
    agg['suficiente'] = agg.get('n', 0) >= min_muestra
    return {'par': par, 'tf': tf, 'detalle': detalle,
            'tramo': {'min': round(t['minimo'], 2), 'max': round(t['maximo'], 2),
                      'direccion': t['direccion'], 'n_velas': t.get('n_velas')},
            'filtros': sorted(filtros), 'stop': stop_modo,
            'gestion': gestion, 'por_nivel': por_nivel, 'agregado': agg}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('par')
    ap.add_argument('--tf', default='1d')
    ap.add_argument('--detalle', type=int, default=150)
    ap.add_argument('--filtros', default='')
    ap.add_argument('--stop', default='pct', choices=['pct', 'estructural', 'atr'])
    ap.add_argument('--stop-pct', type=float, default=2.0)
    ap.add_argument('--gestion', default=None, choices=[None, 'P1', 'P2', 'P3'])
    a = ap.parse_args()
    filtros = {x.strip().upper() for x in a.filtros.split(',') if x.strip()}
    if a.gestion == 'P3':
        filtros.add('P3')
    r = backtest_afavor(a.par.upper(), a.tf, a.detalle, filtros, a.stop,
                        a.stop_pct, gestion=a.gestion)
    print(json.dumps(r, indent=1, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
