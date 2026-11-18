#!/usr/bin/env python3
"""B1: seleccion estratificada de frames para anotacion humana.

Estratifica por video y por tramo temporal (temprano/medio/tardio) usando el
timestamp verificado. NO usa las identificaciones del modelo.
"""
import csv
import json
from pathlib import Path

BASE = Path('/Users/franciscootamendi/YouTubeTradingAgent')
OUT = BASE / 'benchmark_vision_b1'
inv = json.load(open(OUT / 'inventory.json'))
VIDEOS = ['EJoLhxbwYxo', 'LFHkc5dUoLw', 'LzPTdClLo_w', 'XLgPycsN0ls',
          'dPHvRw1wzYQ', 'jeOFS1TZYQA', 's3KxjqkzwKM', 'scJ-ai2FRiE']
POR_VIDEO = 6
TRAMOS = ['temprano', 'medio', 'tardio']

sel = []
for vid in VIDEOS:
    frames = sorted([r for r in inv if r['video_id'] == vid], key=lambda r: r['idx'])
    if not frames:
        continue
    tmin, tmax = frames[0]['pts_time'], frames[-1]['pts_time']
    span = (tmax - tmin) or 1.0
    buckets = {t: [] for t in TRAMOS}
    for r in frames:
        frac = (r['pts_time'] - tmin) / span
        buckets['temprano' if frac < 1/3 else ('medio' if frac < 2/3 else 'tardio')].append(r)
    for t in TRAMOS:
        b = buckets[t]
        if not b:
            continue
        b = sorted(b, key=lambda r: r['idx'])
        n = max(1, round(POR_VIDEO / 3))
        for i in range(n):
            r = b[round(i * (len(b) - 1) / max(1, n - 1))] if n > 1 else b[0]
            item = dict(r)
            item['tramo'] = t
            item['frame_id'] = f"{vid}__{Path(r['frame']).stem}"
            sel.append(item)

# dedup por frame_id (la interpolacion puede repetir)
seen = set()
uniq = []
for s in sel:
    if s['frame_id'] in seen:
        continue
    seen.add(s['frame_id'])
    uniq.append(s)
sel = uniq

campos = ['frame_id', 'video_id', 'frame', 'idx', 'pts_time', 'tramo',
          'instrument', 'timeframe', 'price_levels', 'indicators', 'structure',
          'legible_instrument', 'legible_timeframe', 'legible_prices',
          'legible_indicators', 'legible_structure', 'abstencion', 'certainty_1_5',
          'timestamp_source', 'notes']
with open(OUT / 'annotations' / 'template_anotacion.csv', 'w', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=campos)
    w.writeheader()
    for s in sel:
        w.writerow({k: s.get(k, '') for k in campos})

(OUT / 'annotations' / 'seleccion_estratificada.json').write_text(
    json.dumps(sel, ensure_ascii=False, indent=2))
print(f'seleccionados: {len(sel)} frames de {len(VIDEOS)} videos')
for vid in VIDEOS:
    n = sum(1 for s in sel if s['video_id'] == vid)
    print(f'  {vid}: {n}')
