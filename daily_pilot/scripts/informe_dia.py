#!/usr/bin/env python3
"""Informe del dia — el resumen que Francisco quiere ver.

Toma el ultimo video analizado y produce daily_pilot/datos/informe_hoy.json con:
  que dice el canal y los niveles que menciona. NO aplica C01-C12:
  el metodo lo aplica el trader (ver daily_pilot/datos/informe_hoy.json).
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
    from precios import precios_de_texto
    nums = {}
    for (tt,) in filas:
        for v in precios_de_texto(tt):
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
            'resumen': 'LO QUE DICE EL CANAL (transcripcion). El metodo C01-C12 lo aplica el trader; este panel no ejecuta el motor.',
            'estado': 'PAPER_ONLY',
        },
    }
    # PRECIO: solo si el ULTIMO video lo dice. Si no -> NO_DISPONIBLE (no heredar del historico).
    from precios import precios_de_texto
    ref = None
    tp = BASE / 'data_hist' / vid / f'{vid}_transcript.json'
    if tp.exists():
        _d = json.loads(tp.read_text())
        _cnt = {}
        for _s in _d.get('segments', []):
            for _v in precios_de_texto(_s.get('text', '')):
                _cnt[_v] = _cnt.get(_v, 0) + 1
        if _cnt:
            ref = max(_cnt.items(), key=lambda x: x[1])[0]
    out['precio_referencia'] = ref
    out['precio_procedencia'] = (f'dicho en {vid}' if ref else 'NO_DISPONIBLE: el video no dice el precio; sin feed')

    # MERCADO y ESCENARIOS solo del ULTIMO video (nunca del historico)
    an = PILOT / 'analisis' / f'{vid}_analisis.json'
    if an.exists():
        a = json.loads(an.read_text())
        inst = [k for k, v in (a.get('instrumentos') or {}).items() if v]
        out['instrumentos'] = inst
        out['temporalidades'] = [k for k, v in (a.get('temporalidades') or {}).items() if v]
        out['mercado'] = {'VIDEO': {
            'niveles_originales': [int(float(x['valor'])) for x in (a.get('niveles_explicitos_top') or [])[:8]],
            'nota': 'niveles dichos en el video (no discriminados por instrumento)',
        }}
        _niv = (a.get('niveles_explicitos_top') or [])[:3]
        out['escenarios'] = [
            {'escenario': {'id': f'ESC-{vid}-{i}', 'instrumento': inst[0] if inst else '?',
                           'direccion': None, 'nivel': {'valor': int(float(x['valor']))},  # no se infiere direccion
                           'justificacion': ((x.get('ejemplos') or [{}])[0].get('contexto') or '')[:120],
                           'timestamp_explicacion': ''}}
            for i, x in enumerate(_niv)
        ]
        out['fuente_unica'] = vid

    p = PILOT / 'datos' / 'informe_hoy.json'
    p.write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print(f'{vid} · {len(niv)} niveles · {p}')
    for x in out['niveles_top'][:6]:
        print(f"   {x['precio']:>8} x{x['menciones']}")
    return 0

if __name__ == '__main__':
    sys.exit(main())
