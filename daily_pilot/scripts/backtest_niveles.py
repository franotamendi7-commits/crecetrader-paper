#!/usr/bin/env python3
"""BACKTEST DE NIVELES — ¿el precio respeta los niveles del metodo?

Para cada nivel del tramo del ciclo mide:
  · toques: cuantas velas tocaron el nivel (low <= n <= high)
  · rebotes: de esas, cuantas cerraron del lado contrario al que entraron
  · tasa = rebotes / toques

    python3 daily_pilot/scripts/backtest_niveles.py BTCUSDT
    python3 daily_pilot/scripts/backtest_niveles.py AVAXUSDT --tf 4h

PAPER_ONLY: mide, no opera.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE / 'daily_pilot' / 'core'))


def backtest(par: str, tf: str = '1d', ventana: int = 60, detalle: int = 90) -> dict:
    from velas import velas
    from tramos import tramo_ciclo
    from zonas import zonas

    r = velas(par, tf, limite=500)
    if 'error' in r:
        return {'error': r['error']}
    v = r['velas']
    if len(v) < 20:
        return {'error': 'pocas velas'}
    t = tramo_ciclo(v, 3, ventana)
    if 'error' in t:
        return {'error': t['error']}
    z = zonas(t['minimo'], t['maximo'],
              plazo={'1w': 'largo', '1d': 'media', '4h': 'corto'}.get(tf, 'media'))

    # ventana de estudio: las ultimas `detalle` velas
    datos = v[-detalle:]
    filas = []
    for etiqueta, valores, tipo in (('retroceso', z['zonas_compra'].items(), 'retro'),
                                    ('extension', z['extensiones'].items(), 'ext')):
        for k, nivel in valores:
            fl = float(nivel)
            toques = rebotes = 0
            for i in range(len(datos) - 1):
                x, sg = datos[i], datos[i + 1]
                if x['low'] <= fl <= x['high']:
                    toques += 1
                    # rebota si la vela siguiente cierra en el sentido opuesto
                    entro_abajo = x['close'] >= fl
                    if entro_abajo and sg['close'] > fl:
                        rebotes += 1
                    elif (not entro_abajo) and sg['close'] < fl:
                        rebotes += 1
            filas.append({'nivel': round(fl, 4), 'etiqueta': f'{tipo} {k}',
                          'toques': toques, 'rebotes': rebotes,
                          'tasa': round(rebotes / toques * 100, 1) if toques else None})
    con_toques = [f for f in filas if f['toques'] > 0]
    return {'par': par, 'tf': tf, 'tramo': {'min': round(t['minimo'], 4),
                                            'max': round(t['maximo'], 4)},
            'niveles': filas, 'con_toques': len(con_toques),
            'promedio_tasa': round(sum(f['tasa'] for f in con_toques
                                       if f['tasa'] is not None) / len(con_toques), 1)
            if con_toques else None}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('par')
    ap.add_argument('--tf', default='1d')
    ap.add_argument('--ventana', type=int, default=60)
    a = ap.parse_args()
    r = backtest(a.par.upper(), a.tf, a.ventana)
    if 'error' in r:
        print('ERROR:', r['error'])
        return 1
    print(f"BACKTEST {r['par']} {r['tf']} · tramo {r['tramo']['min']} -> {r['tramo']['max']}")
    print(f"  niveles con toque: {r['con_toques']} · tasa media de rebote: {r['promedio_tasa']}%")
    for f in sorted(r['niveles'], key=lambda x: -(x['tasa'] or 0)):
        if f['toques']:
            print(f"   {f['etiqueta']:<14} {f['nivel']:>12.4f}  "
                  f"toques {f['toques']:>3}  rebotes {f['rebotes']:>3}  {f['tasa']}%")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
