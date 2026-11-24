#!/usr/bin/env python3
"""HIPOTESIS DE MEJORA — se puede subir la taza de respeto sin sobreajustar?

Mide la misma ventana con walk-forward y la compara entre:

    baseline        : linea exacta del nivel (low <= n <= high)
    H1 confluencia  : el nivel tambien aparece en OTRO timeframe (<=0,5%)
    H2 zona         : banda de ATR x k alrededor del nivel
    H5 primer toque : solo el primer toque de la zona (vs los siguientes)

Uso:
    python3 daily_pilot/scripts/hipotesis_estrategia.py
    python3 daily_pilot/scripts/hipotesis_estrategia.py --par ETHUSDT --tf 1d

PAPER_ONLY: mide, no opera. No cambia el metodo.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE / 'daily_pilot' / 'core'))

PLAZO = {'1w': 'largo', '1d': 'media', '4h': 'corto'}
TFs = ('1w', '1d', '4h')


def _velas(par: str, tf: str):
    from velas import velas
    r = velas(par, tf, limite=500)
    return None if 'error' in r else r['velas']


def atr(velas: list, n: int = 14) -> float:
    """Average True Range."""
    trs = []
    for i in range(1, len(velas)):
        trs.append(max(velas[i]['high'] - velas[i]['low'],
                       abs(velas[i]['high'] - velas[i - 1]['close']),
                       abs(velas[i]['low'] - velas[i - 1]['close'])))
    if not trs:
        return velas[-1]['close'] * 0.01
    return sum(trs[-n:]) / min(n, len(trs))


def ancho_zona(nivel: float, a: float, k: float) -> float:
    return max(a * k, abs(nivel) * 0.001)


def en_zona(x: dict, nivel: float, ancho: float) -> bool:
    lo, hi = nivel - ancho / 2, nivel + ancho / 2
    return x['low'] <= hi and x['high'] >= lo


def toca_linea(x: dict, nivel: float) -> bool:
    return x['low'] <= nivel <= x['high']


def niveles_por_tf(par: str) -> dict:
    """{tf: [(tipo, precio), ...]} con el tramo de cada TF."""
    from tramos import tramo_ciclo
    from zonas import zonas
    out = {}
    for tf in TFs:
        v = _velas(par, tf)
        if not v:
            continue
        t = tramo_ciclo(v, 3, 60)
        if 'error' in t:
            continue
        z = zonas(t['minimo'], t['maximo'], plazo=PLAZO.get(tf, 'media'),
                  direccion=t['direccion'])
        out[tf] = ([('retro', float(x)) for x in z['zonas_compra'].values()] +
                   [('ext', float(x)) for x in z['extensiones'].values()])
    return out


def confluye(precio: float, tf_propio: str, por_tf: dict, tol_pct: float = 0.5) -> bool:
    """True si el nivel aparece en otro TF dentro de tol_pct."""
    for tf, lista in por_tf.items():
        if tf == tf_propio:
            continue
        for _, p in lista:
            if p > 0 and abs(p - precio) / p * 100 <= tol_pct:
                return True
    return False


def evaluar(par: str, tf: str = '1d', detalle: int = 90, k_atr: float = 0.5,
            min_muestra: int = 5) -> dict:
    from tramos import tramo_ciclo
    from zonas import zonas

    v = _velas(par, tf)
    if not v or len(v) < 30:
        return {'error': 'sin velas'}
    inicio = max(20, len(v) - detalle)
    t = tramo_ciclo(v[:inicio], 3, 60)
    if 'error' in t:
        return {'error': t['error']}
    z = zonas(t['minimo'], t['maximo'], plazo=PLAZO.get(tf, 'media'),
              direccion=t['direccion'])
    datos = v[inicio:]
    por_tf = niveles_por_tf(par)
    a = atr(v[:inicio])

    def midas(nivel: float, filtro) -> tuple:
        hold = n = 0
        for i in range(len(datos) - 1):
            x, sg = datos[i], datos[i + 1]
            if not toca_linea(x, nivel):
                continue
            prev_arriba = datos[i - 1]['close'] >= nivel if i > 0 else x['open'] >= nivel
            cruzo = prev_arriba != (x['close'] >= nivel)
            h = (not cruzo) and ((x['close'] >= nivel) == (sg['close'] >= nivel))
            if filtro and not filtro(i):
                continue
            n += 1
            hold += int(h)
        return hold, n

    def midas_zona(nivel: float, ancho: float, filtro=None) -> tuple:
        hold = n = 0
        for i in range(len(datos) - 1):
            x, sg = datos[i], datos[i + 1]
            if not en_zona(x, nivel, ancho):
                continue
            lo, hi = nivel - ancho / 2, nivel + ancho / 2
            rechaza = (x['close'] >= hi and sg['close'] >= hi) or \
                      (x['close'] <= lo and sg['close'] <= lo)
            if filtro and not filtro(i):
                continue
            n += 1
            hold += int(rechaza)
        return hold, n

    filas = []
    for tipo, valores in (('retroceso', z['zonas_compra'].items()),
                          ('extension', z['extensiones'].items())):
        for k, nivel in valores:
            fl = float(nivel)
            if fl <= 0:
                continue
            ancho = ancho_zona(fl, a, k_atr)
            b_h, b_n = midas(fl, None)
            c_h, c_n = midas(fl, lambda i, _p=fl: confluye(_p, tf, por_tf))
            p_h, p_n = midas(fl, lambda i, _p=fl: orden_toque(datos, i, _p, ancho) == 0)
            r_h, r_n = midas(fl, lambda i, _p=fl: orden_toque(datos, i, _p, ancho) > 0)
            z_h, z_n = midas_zona(fl, ancho)
            filas.append({'etiqueta': f'{tipo[:4]} {k}', 'nivel': round(fl, 2),
                          'ancho': round(ancho, 2),
                          'base': (b_h, b_n), 'confluencia': (c_h, c_n),
                          'primer_toque': (p_h, p_n), 'resto': (r_h, r_n),
                          'zona': (z_h, z_n)})
    return {'par': par, 'tf': tf, 'detalle': detalle, 'k_atr': k_atr,
            'tramo': {'min': round(t['minimo'], 2), 'max': round(t['maximo'], 2),
                      'direccion': t['direccion']},
            'niveles': filas, 'min_muestra': min_muestra}


def orden_toque(datos: list, i: int, nivel: float, ancho: float) -> int:
    """Cuantas veces toco la zona antes del indice i."""
    return sum(1 for j in range(i) if en_zona(datos[j], nivel, ancho))


def _tasa(t: tuple) -> str:
    h, n = t
    return f'{h}/{n} ({h / n * 100:.0f}%)' if n else '0/0'


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--par', default='BTCUSDT')
    ap.add_argument('--tf', default='1d')
    ap.add_argument('--detalle', type=int, default=90)
    ap.add_argument('--k-atr', type=float, default=0.5)
    a = ap.parse_args()
    r = evaluar(a.par.upper(), a.tf, a.detalle, a.k_atr)
    if 'error' in r:
        print('ERROR:', r['error'])
        return 1
    print(f"HIPOTESIS {r['par']} {r['tf']} · tramo ({r['tramo']['direccion']}) "
          f"{r['tramo']['min']} -> {r['tramo']['max']} · {r['detalle']} velas")
    print(f"  {'nivel':<12}{'base':>14}{'confluencia':>16}{'1er toque':>14}"
          f"{'resto':>14}{'zona':>14}")
    for f in sorted(r['niveles'], key=lambda x: -(x['base'][1])):
        print(f"  {f['etiqueta']:<12}{_tasa(f['base']):>14}{_tasa(f['confluencia']):>16}"
              f"{_tasa(f['primer_toque']):>14}{_tasa(f['resto']):>14}"
              f"{_tasa(f['zona']):>14}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
