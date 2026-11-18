#!/usr/bin/env python3
"""Extraccion de CLAIMS estructurados desde transcripciones (PAPER_ONLY).

Procedencia: A = DICHO por CreceTrader (texto transcrito). No se infieren B/C/D.
Un claim = un segmento relevante (con numero, negacion o condicion explicita).
Idempotente: usa claim_hash = sha256(video_id|seq|texto).
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path('/Users/franciscootamendi/YouTubeTradingAgent')
sys.path.insert(0, str(BASE / 'daily_pilot'))
sys.path.insert(0, str(BASE / 'daily_pilot' / 'knowledge'))
import store as S
from signal_classifier import clasificar

NUM = re.compile(r'(?<![\d.])(\d{1,3}(?:[.,]\d{3})+(?:[.,]\d+)?)(?![\d])')
MIN_DIGITS = 4


def es_relevante(texto: str) -> bool:
    if NUM.search(texto):
        return True
    if re.search(r'\b(no|sin|tampoco)\b', texto, re.I) and re.search(r'(señal|compra|venta|operacion)', texto, re.I):
        return True
    return bool(re.search(r'\b(si|en caso de|siempre que|cuando|podr\w*|escenario)\b', texto, re.I))


def extraer(video_id: str, cues: list) -> list[dict]:
    out = []
    for c in cues:
        texto = (c.get('text') or '').strip()
        if not texto or not es_relevante(texto):
            continue
        niveles = NUM.findall(texto)
        nivel = niveles[0] if niveles else None
        r = clasificar({'nivel': nivel, 'texto': texto})
        out.append({
            'video_id': video_id, 'seq': c['seq'], 'start': c.get('start'),
            'claim_hash': hashlib.sha256(f"{video_id}|{c['seq']}|{texto}".encode()).hexdigest(),
            'tipo': r['tipo'], 'nivel': nivel, 'procedencia': 'A',
            'confianza': None, 'texto': texto[:500], 'motivo': r['motivo'],
            'extraido_en': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        })
    return out


def cargar_transcripciones() -> list[Path]:
    return sorted((BASE / 'data_hist').glob('*/*_transcript.json'))


def main() -> int:
    conn = S.conectar()
    S.crear_esquema(conn)                     # idempotente: crea claims si falta
    total_nuevos = total = 0
    for tp in cargar_transcripciones():
        d = json.loads(tp.read_text(encoding='utf-8'))
        vid = d.get('video_id') or tp.parent.name
        cues = [{'seq': i, 'start': s.get('start'), 'text': s.get('text', '')}
                for i, s in enumerate(d.get('segments', []), start=1)]
        claims = extraer(vid, cues)
        nuevos = 0
        if conn.execute('SELECT 1 FROM videos WHERE video_id=?', (vid,)).fetchone() is None:
            conn.execute("INSERT OR IGNORE INTO videos(video_id,status) VALUES(?, 'sin_metadatos')",
                         (vid,))
            conn.commit()
            print(f'  (video {vid} ausente en videos: registrado con status=sin_metadatos)')
        for cl in claims:
            cur = conn.execute(
                'INSERT OR IGNORE INTO claims(video_id,seq,start,claim_hash,tipo,nivel,'
                'procedencia,confianza,texto,motivo,extraido_en) '
                'VALUES(?,?,?,?,?,?,?,?,?,?,?)',
                (cl['video_id'], cl['seq'], cl['start'], cl['claim_hash'], cl['tipo'],
                 cl['nivel'], cl['procedencia'], cl['confianza'], cl['texto'],
                 cl['motivo'], cl['extraido_en']))
            if cur.rowcount:
                nuevos += 1
        conn.commit()
        total_nuevos += nuevos
        total += len(claims)
        print(f'{vid}: {len(claims)} candidatos, {nuevos} nuevos')
    n = conn.execute('SELECT COUNT(*) FROM claims').fetchone()[0]
    conn.close()
    print(f'\ntotal claims en store: {n} | candidatos: {total} | nuevos: {total_nuevos}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
