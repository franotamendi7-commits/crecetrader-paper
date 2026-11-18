#!/usr/bin/env python3
"""Re-analiza los videos NIVEL POR NIVEL, capturando TF e instrumento del contexto.

Problema que resuelve: el analisis viejo contaba niveles de forma global y mezclaba
ETH/oro/BTC y todos los timeframes. Aqui cada nivel queda con:
    {valor, menciones, tf, instrumento, minuto, contexto}

El TF y el instrumento salen del TEXTO DE LA CUE donde aparece el numero (no se inventan).
Si la cue no dice TF/instrumento -> None (y no se asigna a ninguno).

PAPER_ONLY.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
PILOT = BASE / 'daily_pilot'
OUT = PILOT / 'analisis'
NUM = re.compile(r'(?<![\d.])(\d{1,3}(?:[.,]\d{3})+(?:[.,]\d+)?)(?![\d])')

TF_PAT = {
    'Weekly': r'semanal|weekly',
    'Daily': r'diario|diaria|daily',
    '4H': r'4\s?h|cuatro horas',
    'Intradia': r'intrad[ií]a|una hora|1h|15m',
}
INST_PAT = {
    'BTC': r'\bBTC\b|Bitcoin|bitcoin',
    'ETH': r'\bETH\b|Ethereum|ethereum',
    'SPX': r'\bSPX\b|S&P\s?500',
    'QQQ': r'\bQQQ\b',
    'NQ': r'\bNQ\b|Nasdaq',
    'XAUUSD': r'\boro\b|\bXAU\b|gold',
}


def detectar_tf(txt: str):
    for tf, pat in TF_PAT.items():
        if re.search(pat, txt, re.I):
            return tf
    return None


def detectar_inst(txt: str):
    for inst, pat in INST_PAT.items():
        if re.search(pat, txt, re.I):
            return inst
    return None


def parsear(p: Path) -> list[dict]:
    d = json.loads(p.read_text(encoding='utf-8'))
    return [{'seq': i, 'start': s.get('start'), 'text': s.get('text', '')}
            for i, s in enumerate(d.get('segments', []), start=1)]


def main(video_id: str) -> int:
    tp = BASE / 'data_hist' / video_id / f'{video_id}_transcript.json'
    if not tp.exists():
        print(f'{video_id}: sin transcripcion'); return 1
    cues = parsear(tp)
    # ventana de contexto: la cue actual + la anterior y la siguiente
    agreg = defaultdict(lambda: {'menciones': 0, 'tf': Counter(), 'inst': Counter(), 'donde': []})
    for i, c in enumerate(cues):
        ctx = ' '.join(x['text'] for x in cues[max(0, i - 1): i + 2])
        tf = detectar_tf(ctx)
        inst = detectar_inst(ctx)
        for m in NUM.finditer(c['text']):
            s = m.group(1)
            try:
                v = float(s.replace('.', '').replace(',', '')) if s.count('.') > 1 or ',' in s \
                    else float(s.replace(',', '.'))
            except ValueError:
                continue
            if v <= 1000:
                continue
            k = int(v)
            a = agreg[k]
            a['menciones'] += 1
            if tf:
                a['tf'][tf] += 1
            if inst:
                a['inst'][inst] += 1
            if len(a['donde']) < 3:
                a['donde'].append({'minuto': c['start'], 'contexto': c['text'][:120]})

    niveles = []
    for k, a in sorted(agreg.items(), key=lambda x: -x[1]['menciones']):
        tf = a['tf'].most_common(1)[0][0] if a['tf'] else None
        inst = a['inst'].most_common(1)[0][0] if a['inst'] else None
        niveles.append({'valor': str(k), 'menciones': a['menciones'], 'tf': tf,
                        'instrumento': inst, 'ejemplos': a['donde']})

    OUT.mkdir(parents=True, exist_ok=True)
    p = OUT / f'{video_id}_analisis.json'
    prev = json.loads(p.read_text()) if p.exists() else {}
    prev['niveles_con_tf'] = niveles[:60]
    prev['tf_counter'] = dict(Counter(n['tf'] for n in niveles if n['tf']))
    prev['inst_counter'] = dict(Counter(n['instrumento'] for n in niveles if n['instrumento']))
    prev['reanalizado_tf'] = datetime.now(timezone.utc).isoformat()
    p.write_text(json.dumps(prev, ensure_ascii=False, indent=2))
    c_tf = sum(1 for n in niveles if n['tf'])
    c_in = sum(1 for n in niveles if n['instrumento'])
    print(f'{video_id}: {len(niveles)} niveles · con TF {c_tf} · con instrumento {c_in}')
    return 0


if __name__ == '__main__':
    vid = sys.argv[1] if len(sys.argv) > 1 else None
    if vid:
        sys.exit(main(vid))
    # sin argumento: TODOS los que tienen transcripcion
    ids = sorted(p.name for p in (BASE / 'data_hist').glob('*') if p.is_dir())
    print(f're-analizando {len(ids)} videos')
    for v in ids:
        main(v)
