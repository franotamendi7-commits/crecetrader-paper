#!/usr/bin/env python3
"""Evidencia de analisis REAL para un video (textual, asistido, sin vision).

Genera daily_pilot/analisis/<video_id>_analisis.json con:
  analizado_at, n_cues, sha256_transcript, niveles explicitos (minuto+contexto),
  instrumentos, temporalidades, conceptos, procedencias y limitaciones.
NO ejecuta vision ni inventa niveles: solo transcribe lo dicho.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

BASE = Path('/Users/franciscootamendi/YouTubeTradingAgent')
PILOT = BASE / 'daily_pilot'
OUT = PILOT / 'analisis'
TS = re.compile(r'^(\d+):(\d{2}):(\d{2})\.(\d{3})$')
NUM = re.compile(r'(?<![\d.])(\d{1,3}(?:[.,]\d{3})+(?:[.,]\d+)?)(?![\d])')

INSTRUMENTOS = {'BTC': r'\bBTC\b|Bitcoin', 'ETH': r'\bETH\b|Ethereum', 'SPX': r'\bSPX\b|S&P\s?500',
                'QQQ': r'\bQQQ\b', 'NQ': r'\bNQ\b|Nasdaq', 'XAUUSD': r'\boro\b|XAU|gold'}
TEMPORALIDADES = {'Weekly': r'semanal|weekly', 'Daily': r'diario|diaria|daily',
                  '4H': r'4\s?h|cuatro horas', 'Intradia': r'intrad[ií]a|rango'}
CONCEPTOS = {'fibonacci': r'fibonacci|fibo', 'liquidez': r'liquidez', 'acumulacion': r'acumulaci[oó]n',
             'distribucion': r'distribuci[oó]n', 'fomo': r'fomo', 'holders': r'holders|institucion',
             'estructura': r'estructura|m[aá]ximos y m[ií]nimos', 'tendencia': r'tendencia|alcista|bajista',
             'rango': r'rango|lateralidad', 'soporte': r'soporte', 'resistencia': r'resistencia|techo',
             'invalidacion': r'invalidaci[oó]n', 'stop': r'\bstop\b|p[eé]rdida',
             'objetivo': r'objectivo|proyecci[oó]n|proyecta', 'entrada': r'entrada|comprar|compro',
             'volumen': r'volumen', 'reversal': r'reversi[oó]n', 'divergencia': r'divergencia'}


def parse_transcript(p: Path) -> list[dict]:
    d = json.loads(p.read_text(encoding='utf-8'))
    out = []
    for i, s in enumerate(d.get('segments', []), start=1):
        out.append({'seq': i, 'start': s.get('start'), 'end': s.get('end'), 'text': s.get('text', '')})
    return out


def hhmm(ts: str) -> str:
    m = TS.match(ts or '')
    return f'{int(m.group(1)):02d}:{m.group(2)}' if m else ''


def main(video_id: str) -> int:
    tp = BASE / 'data_hist' / video_id / f'{video_id}_transcript.json'
    if not tp.exists():
        print(f'FAIL: no transcripcion para {video_id}')
        return 2
    cues = parse_transcript(tp)
    niveles = [{'valor': m.group(1), 'minuto': hhmm(c['start']), 'contexto': c['text'][:150]}
               for c in cues for m in NUM.finditer(c['text'])]
    inst = Counter()
    for c in cues:
        for k, pat in INSTRUMENTOS.items():
            if re.search(pat, c['text'], re.I):
                inst[k] += 1
    tmp = Counter()
    for c in cues:
        for k, pat in TEMPORALIDADES.items():
            if re.search(pat, c['text'], re.I):
                tmp[k] += 1
    conc = {}
    for k, pat in CONCEPTOS.items():
        hits = [hhmm(c['start']) for c in cues if re.search(pat, c['text'], re.I)]
        if hits:
            conc[k] = {'menciones': len(hits), 'primeros': hits[:6]}
    top = Counter()
    donde = defaultdict(list)
    for n in niveles:
        key = n['valor'].replace('.', '').replace(',', '')
        if len(key) >= 4:
            top[key] += 1
            if len(donde[key]) < 3:
                donde[key].append({'minuto': n['minuto'], 'contexto': n['contexto']})
    evid = {
        'video_id': video_id,
        'analizado_at': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'metodo': 'extraccion textual asistida sobre la transcripcion (sin vision)',
        'n_cues': len(cues),
        'sha256_transcript': hashlib.sha256(tp.read_bytes()).hexdigest(),
        'transcript_path': str(tp),
        'instrumentos': dict(inst),
        'temporalidades': dict(tmp),
        'conceptos': conc,
        'niveles_explicitos_top': [{'valor': k, 'menciones': v, 'ejemplos': donde[k]}
                                   for k, v in top.most_common(20)],
        'procedencia_niveles': 'A (dicho por CreceTrader segun la transcripcion)',
        'limitaciones': [
            'Analisis TEXTUAL: sin verificacion visual de graficos (vision no autorizada).',
            'Los numeros provienen de la transcripcion; no contrastados con feed.',
            'No se infirieron niveles: solo se transcribio lo dicho.',
        ],
    }
    OUT.mkdir(parents=True, exist_ok=True)
    p = OUT / f'{video_id}_analisis.json'
    p.write_text(json.dumps(evid, ensure_ascii=False, indent=2))
    print(f'OK {p} | cues={len(cues)} niveles={len(niveles)} instrumentos={dict(inst)}')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else 'i0qXzL0eSYs'))
