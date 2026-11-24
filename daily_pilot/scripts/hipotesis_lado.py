#!/usr/bin/env python3
"""A FAVOR O EN CONTRA DEL TRAMO — ¿donde esta la ventaja?

El retroceso se puede operar de dos maneras:

    long   : comprar el rebote (en contra del tramo bajista)
    short  : vender el rebote (a favor del tramo bajista)

Este script mide las dos, con stop de riesgo 2% y target en el siguiente nivel.
Walk-forward: los niveles usan solo velas anteriores a la ventana.

    python3 daily_pilot/scripts/hipotesis_lado.py BTCUSDT --tf 1d

PAPER_ONLY: mide, no opera. No cambia el metodo.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE / 'daily_pilot' / 'core'))
sys.path.insert(0, str(BASE / 'daily_pilot' / 'scripts'))

PLAZO = {'1w': 'largo', '1d': 'media', '4h': 'corto'}


def _velas(par, tf):
    from velas import velas
    r = velas(par, tf, limite=500)
    return None if 'error' in r else r['velas']


def _niveles(par, tf, detalle):
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


def correr(par: str, tf: str = '1d', detalle: int = 150, pct_stop: float = 2.0):
    r = _niveles(par, tf, detalle)
    if not r:
        return None
    v, t, niveles, inicio = r
    datos = v[inicio:]
    precios = [p for _, p, _ in niveles]
    retro_fav, retro_contra, ext_fav, ext_contra = [], [], [], []

    for etq, nivel, tipo in niveles:
        abajo = sorted(p for p in precios if p < nivel)
        arriba = sorted(p for p in precios if p > nivel)
        lado_favor = 'short' if t['direccion'] == 'bajista' else 'long'
        lado_contra = 'long' if lado_favor == 'short' else 'short'
        tgt_f = (abajo[-1] if abajo else None) if lado_favor == 'short' \
            else (arriba[0] if arriba else None)
        tgt_c = (abajo[-1] if abajo else None) if lado_contra == 'short' \
            else (arriba[0] if arriba else None)
        for i, x in enumerate(datos):
            if not (x['low'] <= nivel <= x['high']):
                continue
            for lado, tgt, bucket in ((lado_favor, tgt_f, 'fav'),
                                      (lado_contra, tgt_c, 'contra')):
                if tgt is None:
                    continue
                stop = (nivel * (1 - pct_stop / 100.0)) if lado == 'long' \
                    else (nivel * (1 + pct_stop / 100.0))
                risk = (nivel - stop) if lado == 'long' else (stop - nivel)
                if risk <= 0:
                    continue
                R = ((tgt - nivel) / risk) if lado == 'long' \
                    else ((nivel - tgt) / risk)
                oc, hit = -1.0, 'stop'
                for j in range(i + 1, len(datos)):
                    y = datos[j]
                    if lado == 'long':
                        if y['low'] <= stop:
                            break
                        if y['high'] >= tgt:
                            oc, hit = R, 'target'; break
                    else:
                        if y['high'] >= stop:
                            break
                        if y['low'] <= tgt:
                            oc, hit = R, 'target'; break
                op = {'outcome': round(oc, 3), 'hit': hit}
                if tipo == 'retro':
                    (retro_fav if bucket == 'fav' else retro_contra).append(op)
                else:
                    (ext_fav if bucket == 'fav' else ext_contra).append(op)

    def res(ops):
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

    return {'par': par, 'tf': tf, 'detalle': detalle,
            'tramo': {'min': round(t['minimo'], 2), 'max': round(t['maximo'], 2),
                      'direccion': t['direccion']},
            'retro_fav': res(retro_fav), 'retro_contra': res(retro_contra),
            'ext_fav': res(ext_fav), 'ext_contra': res(ext_contra)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('par')
    ap.add_argument('--tf', default='1d')
    ap.add_argument('--detalle', type=int, default=150)
    ap.add_argument('--stop', type=float, default=2.0)
    a = ap.parse_args()
    r = correr(a.par.upper(), a.tf, a.detalle, a.stop)
    if not r:
        print('sin datos'); return 1
    tr = r['tramo']
    print(f"LADO · {r['par']} {r['tf']} · tramo ({tr['direccion']}) "
          f"{tr['min']} -> {tr['max']} · stop {a.stop}%")
    for etiqueta, clave in (('retrocesos A FAVOR', 'retro_fav'),
                            ('retrocesos EN CONTRA', 'retro_contra'),
                            ('extensiones A FAVOR', 'ext_fav'),
                            ('extensiones EN CONTRA', 'ext_contra')):
        s = r[clave]
        if not s.get('n'):
            print(f"  {etiqueta:<22} sin operaciones"); continue
        print(f"  {etiqueta:<22} n={s['n']:<3} acierto {s['acierto_pct']:>5}%  "
              f"FB {str(s['factor_beneficio']):>7}  esp {str(s['esperanza_R'])+'R':>8}"
              f"  dd {s['drawdown_R']}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
