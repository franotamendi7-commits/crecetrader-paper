#!/usr/bin/env python3
"""TERCERA VUELTA — abanico intradia, liquidez institucional y regimen confirmado.

Mide si esas partes del metodo (que el backtest de retrocesos no cubre) respetan
mas el precio. Walk-forward: los niveles se calculan con velas anteriores al test.

    python3 daily_pilot/scripts/hipotesis_tres.py --par BTCUSDT

PAPER_ONLY: mide, no opera. No cambia el metodo.
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE / 'daily_pilot' / 'core'))

PLAZO = {'1w': 'largo', '1d': 'media', '4h': 'corto'}
FIBO_ABANICO = (0.236, 0.382, 0.618, 0.929, 1.238)   # C04 firmado


def _velas(par: str, tf: str):
    from velas import velas
    r = velas(par, tf, limite=500)
    return None if 'error' in r else r['velas']


# ---------------------------------------------------------------- A · abanico
def cierre_21h(velas_1h: list, fecha) -> float | None:
    for v in velas_1h:
        f = datetime.fromtimestamp(v['ts'] / 1000, tz=timezone.utc)
        if f.date() == fecha and f.hour == 21:
            return v['close']
    return None


def niveles_abanico(cierre_21: float) -> list:
    """9 niveles: cierre ± fibo x 1000 (C04)."""
    if cierre_21 is None:
        return []
    out = []
    for r in FIBO_ABANICO:
        out.append(round(cierre_21 + r * 1000, 2))
        out.append(round(cierre_21 - r * 1000, 2))
    return out


def medir_abanico(par: str, detalle: int = 90) -> dict:
    from velas import velas
    v = _velas(par, '1d')
    v1 = _velas(par, '1h')
    if not v or not v1:
        return {'sin_dato': 'falta cache 1h o 1d'}
    datos = v[-detalle:]
    toques = hold = 0
    toques_ny = hold_ny = 0
    for i, x in enumerate(datos[:-1]):
        f = datetime.fromtimestamp(x['ts'] / 1000, tz=timezone.utc).date()
        c21 = cierre_21h(v1, f)
        nivs = niveles_abanico(c21) if c21 else []
        hit = next((nv for nv in nivs
                    if x['low'] <= nv <= x['high']
                    or abs(x['close'] - nv) <= max(1.0, nv * 0.001)), None)
        if hit is None:
            continue
        sg = datos[i + 1]
        prev_arriba = datos[i - 1]['close'] >= hit if i > 0 else x['open'] >= hit
        cruzo = prev_arriba != (x['close'] >= hit)
        h = (not cruzo) and ((x['close'] >= hit) == (sg['close'] >= hit))
        toques += 1
        hold += int(h)
        hora = datetime.fromtimestamp(x['ts'] / 1000, tz=timezone.utc).hour \
            + datetime.fromtimestamp(x['ts'] / 1000, tz=timezone.utc).minute / 60
        if 13.5 <= hora <= 20.0:
            toques_ny += 1
            hold_ny += int(h)
    return {'toques': toques, 'hold': hold,
            'tasa': round(hold / toques * 100, 1) if toques else None,
            'ny': {'toques': toques_ny, 'hold': hold_ny}}


# ---------------------------------------------------------------- B · liquidez
def medir_liquidez(par: str, tf: str = '1d', detalle: int = 150,
                   tol_pct: float = 0.5) -> dict:
    from tramos import tramo_ciclo, nivel_anual
    from zonas import zonas
    from liquidez import calcular

    v = _velas(par, tf)
    if not v:
        return {'error': 'sin velas'}
    inicio = max(20, len(v) - detalle)
    t = tramo_ciclo(v[:inicio], 3, 60)
    if 'error' in t:
        return {'error': t['error']}
    z = zonas(t['minimo'], t['maximo'], plazo=PLAZO.get(tf, 'media'),
              direccion=t['direccion'])
    liq = calcular(
        zonas_fibo=z['zonas_compra'],
        precios_comienzo_ano=[nivel_anual(par)['precio']]
        if 'precio' in nivel_anual(par) else [],
        pools_volumen=[x['close'] for x in
                       sorted(v[:inicio], key=lambda q: q.get('volume', 0),
                              reverse=True)[:5] if 'volume' in x],
        timeframe=tf,
    )
    niveles_liq = liq.get('liquidez_institucional') or []
    datos = v[inicio:]
    con_h = con_n = sin_h = sin_n = 0
    for i in range(len(datos) - 1):
        x, sg = datos[i], datos[i + 1]
        # hold solo contra el nivel de liquidez cuando el precio esta cerca
        if not any(nv > 0 and abs(x['close'] - nv) / nv * 100 <= tol_pct
                   for nv in niveles_liq):
            continue
        objetivo = min(niveles_liq, key=lambda nv: abs(nv - x['close']))
        prev = datos[i - 1]['close'] if i > 0 else x['open']
        cruzo = (prev >= objetivo) != (x['close'] >= objetivo)
        h = (not cruzo) and ((x['close'] >= objetivo) == (sg['close'] >= objetivo))
        con_n += 1; con_h += int(h)
    def tasa(h, n):
        return round(h / n * 100, 1) if n else None
    return {'niveles_liq': [round(x, 2) for x in niveles_liq][:6],
            'con_liq': {'hold': con_h, 'n': con_n, 'tasa': tasa(con_h, con_n)},
            'sin_liq': {'hold': sin_h, 'n': sin_n, 'tasa': tasa(sin_h, sin_n)}}


# ---------------------------------------------------------------- D · regimen
def medir_regimen(par: str, tf: str = '1d', detalle: int = 150) -> dict:
    from tramos import tramo_ciclo, regimen_de
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
    niveles = [float(x) for x in z['zonas_compra'].values()] + \
              [float(x) for x in z['extensiones'].values()]
    datos = v[inicio:]
    conf_h = conf_n = nc_h = nc_n = 0
    for i in range(len(datos) - 1):
        x, sg = datos[i], datos[i + 1]
        for fl in niveles:
            if not (x['low'] <= fl <= x['high']):
                continue
            r = regimen_de(v[:inicio + i])
            confirmado = str(r['regimen']).lower() in ('tendencia_alcista', 'tendencia_bajista')
            prev = datos[i - 1]['close'] if i > 0 else x['open']
            cruzo = (prev >= fl) != (x['close'] >= fl)
            h = (not cruzo) and ((x['close'] >= fl) == (sg['close'] >= fl))
            if confirmado:
                conf_n += 1; conf_h += int(h)
            else:
                nc_n += 1; nc_h += int(h)
    def tasa(h, n):
        return round(h / n * 100, 1) if n else None
    return {'confirmado': {'hold': conf_h, 'n': conf_n, 'tasa': tasa(conf_h, conf_n)},
            'no_confirmado': {'hold': nc_h, 'n': nc_n, 'tasa': tasa(nc_h, nc_n)}}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--par', default='BTCUSDT')
    ap.add_argument('--tf', default='1d')
    ap.add_argument('--detalle', type=int, default=150)
    a = ap.parse_args()
    par, tf, d = a.par.upper(), a.tf, a.detalle
    print(f'TERCERA VUELTA · {par} {tf} · {d} velas')

    print('\nA · ABANICO INTRADIA (C04, ±0,25/0,50/0,75/1,00/1,25 del cierre 21:00)')
    r = medir_abanico(par, min(d, 90))
    print('  ', r if 'sin_dato' in r else
          f"toques {r['toques']} · hold {r['hold']} ({r['tasa']}%) · "
          f"en sesion NY: {r['ny']['hold']}/{r['ny']['toques']}")

    print('\nB · LIQUIDEZ INSTITUCIONAL (fibo + 1 ene + pools)')
    b = medir_liquidez(par, tf, d)
    print('  ', b)

    print('\nD · REGIMEN CONFIRMADO (supera_y_consolida)')
    g = medir_regimen(par, tf, d)
    print('  ', g)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
