#!/usr/bin/env python3
"""BACKTEST DE NIVELES — ¿el precio respeta los niveles del metodo?

Walk-forward simple: el tramo se congela con velas ANTERIORES a la ventana de
test (no usa el futuro). Para cada toque clasifica en 2x2:

    hold : no cruzo y la siguiente sigue del mismo lado
    break: no cruzo y la siguiente cruza
    cont  : cruzo y la siguiente sigue del lado nuevo (NO es rebote)
    rev   : cruzo y la siguiente vuelve

Se reporta `hold` como "respetado" y el IC95 de Wilson. Los niveles con
toques < min_muestra se marcan suficiente=False y no entran al promedio.

    python3 daily_pilot/scripts/backtest_niveles.py BTCUSDT
    python3 daily_pilot/scripts/backtest_niveles.py AVAXUSDT --tf 4h --detalle 120

PAPER_ONLY: mide, no opera.
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE / 'daily_pilot' / 'core'))


def _wilson(k: int, n: int):
    """IC95 de Wilson en puntos porcentuales."""
    if not n:
        return None
    z = 1.96
    den = 1 + z * z / n
    c = (k / n + z * z / (2 * n)) / den
    h = z * math.sqrt(k / n * (1 - k / n) / n + z * z / (4 * n * n)) / den
    return round(max(0.0, c - h) * 100, 1), round(min(1.0, c + h) * 100, 1)


def backtest(par: str, tf: str = '1d', ventana: int = 60, detalle: int = 90,
             min_muestra: int = 5) -> dict:
    from velas import velas
    from tramos import tramo_ciclo
    from zonas import zonas

    r = velas(par, tf, limite=500)
    if 'error' in r:
        return {'error': r['error']}
    v = r['velas']
    if len(v) < 20:
        return {'error': 'pocas velas'}

    # el tramo se calcula SOLO con velas anteriores a la ventana de test
    inicio = max(20, len(v) - detalle)
    t = tramo_ciclo(v[:inicio], 3, ventana)
    if 'error' in t:
        return {'error': t['error']}
    z = zonas(t['minimo'], t['maximo'],
              plazo={'1w': 'largo', '1d': 'media', '4h': 'corto'}.get(tf, 'media'),
              direccion=t['direccion'])

    datos = v[inicio:]
    filas = []
    for etiqueta, valores, tipo in (('retroceso', z['zonas_compra'].items(), 'retro'),
                                    ('extension', z['extensiones'].items(), 'ext')):
        for k, nivel in valores:
            fl = float(nivel)
            hold = brk = cont = rev = toques = 0
            for i in range(len(datos) - 1):
                x, sg = datos[i], datos[i + 1]
                if not (x['low'] <= fl <= x['high']):
                    continue
                toques += 1
                prev = datos[i - 1]['close'] if i > 0 else x['open']
                prev_arriba = prev >= fl
                x_arriba = x['close'] >= fl
                sg_arriba = sg['close'] >= fl
                cruzo = prev_arriba != x_arriba
                if not cruzo:
                    if x_arriba == sg_arriba:
                        hold += 1
                    else:
                        brk += 1
                else:
                    if x_arriba == sg_arriba:
                        cont += 1
                    else:
                        rev += 1
            filas.append({
                'nivel': round(fl, 4), 'etiqueta': f'{tipo} {k}',
                'toques': toques, 'hold': hold, 'break': brk, 'cont': cont, 'rev': rev,
                'tasa_hold': round(hold / toques * 100, 1) if toques else None,
                'ic95': _wilson(hold + rev, toques),
                'suficiente': toques >= min_muestra,
            })

    con_toques = [f for f in filas if f['toques'] > 0]
    suf = [f for f in con_toques if f['suficiente']]
    return {'par': par, 'tf': tf,
            'tramo': {'min': round(t['minimo'], 4), 'max': round(t['maximo'], 4),
                      'direccion': t['direccion']},
            'ventana_inicio': inicio, 'n_velas_test': len(datos),
            'niveles': filas, 'con_toques': len(con_toques),
            'promedio_hold': (round(sum(f['tasa_hold'] for f in suf) / len(suf), 1)
                              if suf else None),
            'min_muestra': min_muestra}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('par')
    ap.add_argument('--tf', default='1d')
    ap.add_argument('--ventana', type=int, default=60)
    ap.add_argument('--detalle', type=int, default=90)
    ap.add_argument('--min-muestra', type=int, default=5, dest='min_muestra')
    a = ap.parse_args()
    r = backtest(a.par.upper(), a.tf, a.ventana, a.detalle, a.min_muestra)
    if 'error' in r:
        print('ERROR:', r['error'])
        return 1
    tr = r['tramo']
    print(f"BACKTEST {r['par']} {r['tf']} · tramo ({tr['direccion']}) "
          f"{tr['min']} -> {tr['max']} · test {r['n_velas_test']} velas")
    print(f"  niveles con toque: {r['con_toques']} · respetados (hold) con "
          f"n>={r['min_muestra']}: {r['promedio_hold']}%")
    for f in sorted(r['niveles'], key=lambda x: -(x['toques'])):
        if not f['toques']:
            continue
        ic = f"{f['ic95'][0]}-{f['ic95'][1]}" if f['ic95'] else '-'
        marca = '' if f['suficiente'] else '  (muestra chica)'
        print(f"   {f['etiqueta']:<14} {f['nivel']:>12.4f}  toques {f['toques']:>3}  "
              f"hold {f['hold']:>3}  cont {f['cont']:>3}  {f['tasa_hold']}%  IC{ic}{marca}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
