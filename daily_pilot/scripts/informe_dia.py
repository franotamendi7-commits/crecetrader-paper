#!/usr/bin/env python3
"""Informe del dia — el resumen que Francisco quiere ver.

Toma el ultimo video analizado y produce daily_pilot/datos/informe_hoy.json con:
  que dice el canal, niveles, que propone el motor (C01-C12) y por que.
PAPER_ONLY: propone, no ejecuta.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
PILOT = BASE / 'daily_pilot'
sys.path.insert(0, str(PILOT / 'knowledge'))
sys.path.insert(0, str(PILOT / 'core'))
import store as S

def cargar_ultimo():
    c = S.conectar()
    v = c.execute("SELECT video_id,title,published,source FROM videos ORDER BY published DESC LIMIT 1").fetchone()
    c.close()
    return v

def niveles_del_video(video_id: str):
    c = S.conectar()
    filas = c.execute("SELECT texto FROM claims WHERE video_id=?", (video_id,)).fetchall()
    c.close()
    import re
    nums = {}
    for (t,) in filas:
        for m in re.finditer(r'(?<![\d.])(\d{1,3}(?:[.,]\d{3})+(?:[.,]\d+)?)(?![\d])', t or ''):
            s = m.group(1)
            try:
                v = float(s.replace('.', '').replace(',', '')) if s.count('.') > 1 or ',' in s else float(s.replace(',', '.'))
            except ValueError:
                continue
            if v > 1000:
                nums[v] = nums.get(v, 0) + 1
    return sorted(nums.items(), key=lambda x: -x[1])[:12]

def main() -> int:
    v = cargar_ultimo()
    if not v:
        print('sin videos'); return 1
    vid, titulo, pub, fuente = v
    niv = niveles_del_video(vid)
    out = {
        'video_id': vid, 'titulo': titulo, 'publicado': pub, 'fuente': fuente,
        'papel_only': True,
        'niveles_top': [{'precio': int(p), 'menciones': n} for p, n in niv],
        'propuesta': {
            'resumen': 'El motor aplica C01-C12 sobre la transcripcion. Sin validar contra el grafico.',
            'estado': 'PAPER_ONLY',
        },
    }
    # precio de referencia (del mercado que ya conocio el video)
    dd = json.loads((PILOT / 'datos' / 'dashboard_data.json').read_text()) if (PILOT / 'datos' / 'dashboard_data.json').exists() else {}
    ref = None
    for m in (dd.get('mercado') or {}).values():
        v = (m.get('precio_referencia') or {}).get('valor')
        if v:
            ref = v; break
    out['precio_referencia'] = ref
    p = PILOT / 'datos' / 'informe_hoy.json'
    p.write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print(f'{vid} · {len(niv)} niveles · {p}')
    for x in out['niveles_top'][:6]:
        print(f"   {x['precio']:>8} x{x['menciones']}")
    return 0

if __name__ == '__main__':
    sys.exit(main())
