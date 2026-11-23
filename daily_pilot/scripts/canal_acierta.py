#!/usr/bin/env python3
"""¿EL CANAL ACIERTA? — las predicciones de CreceTrader contra lo que paso.

Para cada video (de los mas viejos a los mas nuevos):
  · se toman los niveles que el canal menciono
  · se mira si, en los dias siguientes, el precio los toco

    python3 daily_pilot/scripts/canal_acierta.py

PAPER_ONLY: evalua, no opera.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE / 'daily_pilot' / 'core'))

RAIZ = BASE / 'daily_pilot' / 'investigacion'


def _fecha_video(vid: str):
    p = RAIZ / f'AGENTE_{vid}.json'
    if not p.exists():
        return None
    try:
        d = json.loads(p.read_text())
    except Exception:
        return None
    return d.get('publicado') or d.get('fecha')


def evaluar(dias: int = 10) -> list:
    """Para cada video, si el precio posterior toco los niveles dichos."""
    from velas import velas
    v = velas('BTCUSDT', '1d', limite=500)['velas']
    # indice por fecha
    por_fecha = {}
    for i, x in enumerate(v):
        f = datetime.fromtimestamp(x['ts'] / 1000, tz=timezone.utc).date()
        por_fecha[f] = i

    filas = []
    for p in sorted(RAIZ.glob('AGENTE_*.json'),
                    key=lambda q: q.stat().st_mtime):
        try:
            d = json.loads(p.read_text())
        except Exception:
            continue
        vid = d.get('video_id') or p.stem.replace('AGENTE_', '')
        # sin fecha de publicacion en el JSON: se usa el momento en que el
        # agente proceso el video (st_mtime) como referencia
        try:
            f_pub = datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc).date()
        except Exception:
            continue
        # primer dia con datos >= publicacion
        i0 = next((i for f, i in sorted(por_fecha.items()) if f >= f_pub), None)
        if i0 is None or i0 + 1 >= len(v):
            continue
        ventana = v[i0:i0 + dias + 1]
        if not ventana:
            continue
        mins = min(x['low'] for x in ventana)
        maxs = max(x['high'] for x in ventana)
        niveles = [float(n['precio']) for n in (d.get('niveles_dichos') or [])][:6]
        tocados = sum(1 for nv in niveles if mins <= nv <= maxs)
        filas.append({'video': vid, 'pub': str(f_pub),
                      'niveles': len(niveles), 'tocados': tocados,
                      'tasa': round(tocados / len(niveles) * 100, 1) if niveles else None})
    return filas


def main() -> int:
    filas = [f for f in evaluar() if f['niveles']]
    if not filas:
        print('sin datos suficientes')
        return 0
    with_tasa = [f for f in filas if f['tasa'] is not None]
    prom = round(sum(f['tasa'] for f in with_tasa) / len(with_tasa), 1)
    print(f"¿EL CANAL ACIERTA? · {len(filas)} videos · tasa media {prom}%")
    for f in filas[-12:]:
        print(f"  {f['pub']} {f['video']:<12} niveles {f['niveles']:>2} "
              f"tocados {f['tocados']:>2} ({f['tasa']}%)")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
