#!/usr/bin/env python3
"""B3 (complemento): deduplicacion de transcripciones SIN modificar originales."""
import json
from pathlib import Path

BASE = Path('/Users/franciscootamendi/YouTubeTradingAgent')
OUT = BASE / 'benchmark_vision_b1' / 'temporal'
VIDEOS = ['EJoLhxbwYxo', 'LFHkc5dUoLw', 'LzPTdClLo_w', 'XLgPycsN0ls',
          'dPHvRw1wzYQ', 'jeOFS1TZYQA', 's3KxjqkzwKM', 'scJ-ai2FRiE']

resumen = {}
for vid in VIDEOS:
    src = BASE / 'data_hist' / vid / f'{vid}_transcript.json'
    if not src.exists():
        resumen[vid] = {'error': 'sin transcripcion'}
        continue
    d = json.load(open(src))
    segs = d.get('segments', [])
    dedup = []
    for s in segs:
        t = s.get('text', '').strip()
        if dedup and t == dedup[-1]['text']:
            continue
        dedup.append(s)
    out = dict(d)
    out['segments'] = dedup
    out['cue_count_original'] = len(segs)
    out['cue_count_dedup'] = len(dedup)
    out['cue_count_eliminados'] = len(segs) - len(dedup)
    out['dedup_method'] = 'texto consecutivo identico'
    dst = OUT / f'{vid}_transcript_dedup.json'
    dst.write_text(json.dumps(out, ensure_ascii=False, indent=2))
    resumen[vid] = {'original': len(segs), 'dedup': len(dedup),
                    'eliminados': len(segs) - len(dedup),
                    'salida': str(dst.relative_to(BASE))}

(OUT / 'vtt_dedup_resumen.json').write_text(json.dumps(resumen, ensure_ascii=False, indent=2))
print(json.dumps(resumen, ensure_ascii=False, indent=2))
