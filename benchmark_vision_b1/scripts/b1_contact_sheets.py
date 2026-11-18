#!/usr/bin/env python3
"""B1: contact sheets por video con identificador unico (video + idx)."""
import json
from pathlib import Path
from PIL import Image, ImageDraw

BASE = Path('/Users/franciscootamendi/YouTubeTradingAgent')
OUT = BASE / 'benchmark_vision_b1' / 'contact_sheets'
VIDEOS = ['EJoLhxbwYxo', 'LFHkc5dUoLw', 'LzPTdClLo_w', 'XLgPycsN0ls',
          'dPHvRw1wzYQ', 'jeOFS1TZYQA', 's3KxjqkzwKM', 'scJ-ai2FRiE']
COLS, ROWS = 4, 5
CELL_W, CELL_H = 640, 352
LABEL_H = 26


def sheet(vid, files, dst):
    rows = (len(files) + COLS - 1) // COLS
    canvas = Image.new('RGB', (COLS * CELL_W, rows * (CELL_H + LABEL_H)), (20, 20, 20))
    draw = ImageDraw.Draw(canvas)
    for i, f in enumerate(files):
        im = Image.open(f).convert('RGB')
        im.thumbnail((CELL_W, CELL_H))
        x = (i % COLS) * CELL_W
        y = (i // COLS) * (CELL_H + LABEL_H)
        canvas.paste(im, (x, y + LABEL_H))
        label = f"{vid} | {f.stem} | idx {int(f.stem.split('_')[1]):04d}"
        draw.text((x + 4, y + 6), label, fill=(255, 220, 0))
    canvas.save(dst, quality=85)
    return dst


registro = {}
for vid in VIDEOS:
    files = sorted((BASE / 'frames_hist' / vid).glob('frame_*.jpg'))
    dst = OUT / f'{vid}_contact_sheet.jpg'
    sheet(vid, files, dst)
    registro[vid] = {'frames': len(files), 'contact_sheet': str(dst.relative_to(BASE)),
                     'ids': [f'{vid}__{f.stem}' for f in files]}
    print(f'{vid}: {len(files)} -> {dst.name}')

(OUT / 'contact_sheets_index.json').write_text(json.dumps(registro, ensure_ascii=False, indent=2))
print('OK')
