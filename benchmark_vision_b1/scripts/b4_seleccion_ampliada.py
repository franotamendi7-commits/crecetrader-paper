#!/usr/bin/env python3
"""Fase 1 — Muestra experimental ampliada y menos redundante (B4).

LFHkc5dUoLw: 3994, 4006, 4013 (fijos por orden).
Resto: seleccion maximin (3 por video) por distancia visual, para evitar escenas casi identicas.
NO modifica la seleccion historica de B1.
"""
import csv
import itertools
import json
from pathlib import Path
from PIL import Image, ImageChops, ImageStat

BASE = Path('/Users/franciscootamendi/YouTubeTradingAgent')
B4 = BASE / 'benchmark_vision_b1'
OUT = B4 / 'B4_muestra_ampliada'
OUT.mkdir(parents=True, exist_ok=True)
TS = json.load(open(B4 / 'temporal' / 'timestamps.json'))
VIDEOS = ['LzPTdClLo_w', 'jeOFS1TZYQA', 'scJ-ai2FRiE', 's3KxjqkzwKM']


def dist(a, b):
    d = ImageChops.difference(a, b)
    return sum(ImageStat.Stat(d).mean) / 3


def maximin(files, k):
    ims = {f: Image.open(f).convert('RGB').resize((320, 176)) for f in files}
    elegidos = [max(files, key=lambda f: ImageStat.Stat(ims[f]).stddev[0])]
    while len(elegidos) < k:
        resto = [f for f in files if f not in elegidos]
        nuevo = max(resto, key=lambda f: min(dist(ims[f], ims[e]) for e in elegidos))
        elegidos.append(nuevo)
    return elegidos


filas = []
for f in sorted((BASE / 'frames_hist' / 'LFHkc5dUoLw').glob('frame_*.jpg')):
    if int(f.stem.split('_')[1]) in (3994, 4006, 4013):
        filas.append({'video_id': 'LFHkc5dUoLw', 'frame': f.name,
                      'idx': int(f.stem.split('_')[1]),
                      'pts_time': TS['LFHkc5dUoLw']['frames'][f.name]['pts_time'],
                      'escena': 'cierre / rechazo en 81.446 (unica escena)',
                      'motivo': 'seleccion fija por orden; representantes de la unica escena disponible'})
for vid in VIDEOS:
    files = sorted((BASE / 'frames_hist' / vid).glob('frame_*.jpg'))
    elegidos = maximin(files, 3)
    for f in elegidos:
        t = TS[vid]['frames'][f.name]['pts_time']
        filas.append({'video_id': vid, 'frame': f.name, 'idx': int(f.stem.split('_')[1]),
                      'pts_time': t, 'escena': f'tramo {t:.0f}s',
                      'motivo': 'maximin: maxima distancia visual respecto de los ya elegidos'})

with open(OUT / 'manifest_muestra_ampliada.csv', 'w', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=list(filas[0].keys()))
    w.writeheader(); w.writerows(filas)
(OUT / 'manifest_muestra_ampliada.json').write_text(json.dumps(filas, ensure_ascii=False, indent=2))
print('seleccion ampliada:', len(filas), 'frames')
for vid in ['LFHkc5dUoLw'] + VIDEOS:
    print(' ', vid, [r['frame'] for r in filas if r['video_id'] == vid])
