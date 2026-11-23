#!/usr/bin/env python3
"""ALERTAS DE NIVEL — ¿el precio está cerca de un nivel que importa?

Niveles que importan:
  · los de la CONCORDANCIA (el canal los repitio en varios videos)
  · los retrocesos/extensiones del tramo del ciclo de cada par

Una alerta salta cuando el precio esta a menos de `umbral_pct` del nivel.

    python3 daily_pilot/scripts/alertas_niveles.py
    python3 daily_pilot/scripts/alertas_niveles.py --umbral 1.5

PAPER_ONLY: avisa, no opera.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE / 'daily_pilot' / 'core'))
sys.path.insert(0, str(BASE / 'daily_pilot' / 'scripts'))

PARES = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'XRPUSDT', 'SOLUSDT', 'AVAXUSDT',
         'DOGEUSDT', 'ADAUSDT', 'LINKUSDT', 'LTCUSDT']


def concordancia(n=4) -> dict:
    """Niveles repetidos en los ultimos n videos."""
    import collections
    raiz = BASE / 'daily_pilot' / 'investigacion'
    vids = sorted(raiz.glob('AGENTE_*.json'), key=lambda p: p.stat().st_mtime, reverse=True)[:n]
    ap = collections.defaultdict(set)
    for p in vids:
        try:
            d = json.loads(p.read_text())
        except Exception:
            continue
        vid = d.get('video_id') or p.stem.replace('AGENTE_', '')
        for x in d.get('niveles_dichos', []):
            pr = x.get('precio')
            if pr is not None:
                ap[round(float(pr), 2)].add(vid)   # 2 decimales: DOGE/ADA no colapsan
    return {k: sorted(v) for k, v in ap.items() if len(v) >= 2}


def niveles_par(par: str) -> list:
    """Retrocesos y extensiones del tramo del ciclo de un par."""
    from velas import velas
    from tramos import tramo_ciclo
    from zonas import zonas
    r = velas(par, '1d', limite=500)
    if 'error' in r:
        return []
    t = tramo_ciclo(r['velas'], 3, 60)
    if 'error' in t:
        return []
    z = zonas(t['minimo'], t['maximo'], plazo='media', direccion=t['direccion'])
    out = [{'precio': float(x), 'tipo': f'retroceso {k}', 'par': par}
           for k, x in z['zonas_compra'].items()]
    out += [{'precio': float(x), 'tipo': f'extensión {k}', 'par': par}
            for k, x in z['extensiones'].items()]
    return out


def alertas(precios: dict, niveles: list, umbral_pct: float) -> list:
    """Niveles cuya distancia al precio es menor que el umbral."""
    salidas = []
    for n in niveles:
        px = precios.get(n['par'])
        if not px or not n.get('precio') or n['precio'] <= 0:
            continue
        dist = abs(px - n['precio']) / n['precio'] * 100
        if dist <= umbral_pct:
            salidas.append({**n, 'precio_actual': px,
                            'distancia_pct': round(dist, 2),
                            'direccion': 'encima' if n['precio'] > px else 'debajo'})
    salidas.sort(key=lambda x: x['distancia_pct'])
    return salidas


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--umbral', type=float, default=1.5)
    ap.add_argument('--json', action='store_true')
    a = ap.parse_args()

    from velas import velas
    precios = {}
    for par in PARES:
        r = velas(par, '1d', limite=2)
        if 'error' not in r and r['velas']:
            precios[par] = float(r['velas'][-1]['close'])

    conc = concordancia(4)
    print('AVISO: los niveles del canal no traen par; se asume BTCUSDT')
    niveles = [{'par': 'BTCUSDT', 'precio': float(precio),
                'tipo': f'concordancia ({len(videos)} videos)'}
               for precio, videos in conc.items() if 'BTCUSDT' in precios]
    for par in PARES:
        niveles += niveles_par(par)

    avisos = alertas(precios, niveles, a.umbral)
    if a.json:
        print(json.dumps(avisos, indent=1, ensure_ascii=False))
        return 0
    print(f'ALERTAS DE NIVEL · umbral {a.umbral}% · {len(avisos)} avisos')
    for x in avisos[:25]:
        print(f"  {x['par'].replace('USDT',''):<7} {x['precio']:>12.4f} "
              f"({x['distancia_pct']:>5.2f}% {x['direccion']})  {x['tipo']}")
    if not avisos:
        print('  ningun nivel cerca ahora mismo.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
