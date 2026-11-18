#!/usr/bin/env python3
"""C3/E5 — Escenarios VERSIONADOS por instrumento (PAPER_ONLY).

Construye:
  escenarios/historial.json   — cada mencion es una version (fecha, video, sentido, texto)
  escenarios/vigentes.json    — ultima version por (instrumento, nivel agrupado)

No borra historial. Fuente: tabla claims. Sin vision.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, '/Users/franciscootamendi/YouTubeTradingAgent/daily_pilot/relaciones')
import relaciones as R

OUT = Path(__file__).resolve().parent


def fecha_de(c: dict) -> str:
    """P1-1 FIX: nunca 1970. Si no hay fecha -> SIN_FECHA (excluida de vigentes)."""
    f = (c.get('published') or c.get('detectado') or c.get('extraido_en') or '')[:10]
    return f if f else 'SIN_FECHA'


def main() -> int:
    claims = R.cargar()
    hist = defaultdict(list)
    for c in claims:
        for v, inst, origen in (c.get('nums_inst') or []):
            if inst == 'NO_DETERMINADO' or not R.plausible(inst, v):
                continue
            hist[inst].append({
                'fecha': fecha_de(c), 'video_id': c['video_id'], 'start': c['start'],
                'timeframe': c.get('timeframe') or 'neutro',   # C12: zona distinta por TF
                'nivel': v, 'banda': R.clave_nivel(v), 'sentido': c['sentido'],
                'tipo': c['tipo'], 'procedencia': c['procedencia'],
                'origen_instrumento': origen,
                'texto': (c['texto'] or '')[:200],
            })
    historial = {}
    vigentes = {}
    for inst, items in hist.items():
        items.sort(key=lambda x: (x['fecha'], x['video_id'], x['start'] or ''))
        historial[inst] = items
        ult = {}
        for it in items:
            if it['fecha'] == 'SIN_FECHA':      # P1-1: no puede ser "vigente"
                continue
            # C12 (Francisco): la zona depende del timeframe -> clave compuesta.
            k = (it['banda'], it.get('timeframe') or 'neutro')
            if k not in ult or (it['fecha'], it['start'] or '') >= (ult[k]['fecha'], ult[k]['start'] or ''):
                ult[k] = it
        vigentes[inst] = sorted(ult.values(), key=lambda x: (x['nivel'], x.get('timeframe') or ''))
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'historial.json').write_text(json.dumps(
        {'metodo': 'cada mencion es una version; sin vision; procedencia A',
         'instrumentos': historial}, ensure_ascii=False, indent=2))
    (OUT / 'vigentes.json').write_text(json.dumps(
        {'metodo': 'ultima version por banda de nivel; no es recomendacion', 'vigentes': vigentes},
        ensure_ascii=False, indent=2))
    n_h = sum(len(v) for v in historial.values())
    n_v = sum(len(v) for v in vigentes.values())
    print(f'historial: {n_h} versiones en {len(historial)} instrumentos | vigentes: {n_v}')
    for inst, items in vigentes.items():
        print(f'  {inst}: ' + ', '.join(f"{x['nivel']:.0f}({x['sentido']},{x['fecha']})" for x in items[:6]))
    return 0


if __name__ == '__main__':
    sys.exit(main())
