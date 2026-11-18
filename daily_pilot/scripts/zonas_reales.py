#!/usr/bin/env python3
"""Zonas calculadas REAL (C05) para un activo, por plazo.

A diferencia del dash anterior (que solo listaba lo dicho), esto CALCULA:
    retrocesos 50 / 61 / 78   (zonas de compra)
    extensiones 50/100/150/200 (ruptura del maximo)
sobre el rango [minimo, maximo] que el canal menciono.

Plazos (C05):
    corto  -> 4H    : niveles del ultimo video
    media  -> diario : niveles de los ultimos 5 videos
    largo  -> semanal: niveles de los ultimos 20 videos

HONESTIDAD: los extremos salen de los niveles DICHOS por el canal, no de un
feed de mercado. Sin feed no hay precios en tiempo real.
PAPER_ONLY.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
PILOT = BASE / 'daily_pilot'
sys.path.insert(0, str(PILOT / 'core'))
import zonas as Z

PLAZO_VIDEOS = {'corto': 1, 'media': 5, 'largo': 20}
TF = {'corto': '4H', 'media': 'diario', 'largo': 'semanal'}

# Rangos tipicos por activo, para NO mezclar niveles entre instrumentos.
# Sin esto, los 1.065 de ETH y los 165.000 de BTC se mezclan y el calculo es basura.
RANGO = {
    'BTC': (10000, 300000),
    'ETH': (500, 20000),
    'SPX': (3000, 20000),
    'QQQ': (200, 20000),
    'XAUUSD': (500, 20000),
}


def niveles_de(ids: list[str], activo: str) -> list[float]:
    """Niveles dichos en esos videos, FILTRADOS al rango del activo."""
    lo, hi = RANGO.get(activo, (0, 10 ** 9))
    out = []
    for v in ids:
        p = PILOT / 'analisis' / f'{v}_analisis.json'
        if not p.exists():
            continue
        a = json.loads(p.read_text())
        for x in (a.get('niveles_explicitos_top') or []):
            try:
                n = float(str(x['valor']).replace('.', '').replace(',', ''))
            except Exception:
                continue
            if lo <= n <= hi:
                out.append(n)
    return sorted(set(out))


def videos_recientes(n: int) -> list[str]:
    import sqlite3
    sys.path.insert(0, str(PILOT / 'knowledge'))
    import store as S
    c = sqlite3.connect('file:' + str(S.STORE_PATH) + '?mode=ro', uri=True)
    ids = [r[0] for r in c.execute("SELECT video_id FROM videos ORDER BY published DESC LIMIT ?", (n,))]
    c.close()
    return ids


def calcular(activo: str = 'BTC') -> dict:
    """Zonas calculadas por plazo, sobre los niveles dichos por el canal."""
    res = {'activo': activo, 'paper_only': True, 'fuente': 'niveles dichos por CreceTrader',
           'sin_feed': True, 'plazos': {}}
    for plazo, n in PLAZO_VIDEOS.items():
        ids = videos_recientes(n)
        niv = niveles_de(ids, activo)
        if len(niv) < 2:
            res['plazos'][plazo] = {'error': 'faltan niveles'}
            continue
        mn, mx = niv[0], niv[-1]
        z = Z.zonas(mn, mx, plazo='corto' if plazo == 'corto' else 'media')
        z['tf'] = TF[plazo]
        z['n_videos'] = len(ids)
        z['n_niveles'] = len(niv)
        z['rango_dicho'] = {'minimo': mn, 'maximo': mx, 'n_niveles': len(niv)}
        res['plazos'][plazo] = z
    return res


if __name__ == '__main__':
    r = calcular('BTC')
    for plazo, z in r['plazos'].items():
        if 'error' in z:
            print(f'{plazo:7s} {z["error"]}')
            continue
        print(f'{plazo:7s} TF={z["tf"]:8s} rango {z["minimo"]:,.0f}-{z["maximo"]:,.0f} '
              f'({z["n_niveles"]} niveles, {z["n_videos"]} videos)')
        print(f'         compra: ' + ' · '.join(f'{k}={v:,.0f}' for k, v in z['zonas_compra'].items()))
        print(f'         ext   : ' + ' · '.join(f'{k}={v:,.0f}' for k, v in z['extensiones'].items()))
