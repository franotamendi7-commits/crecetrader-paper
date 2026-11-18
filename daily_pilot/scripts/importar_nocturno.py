#!/usr/bin/env python3
"""Importa el lote nocturno a E1 (PAPER_ONLY, idempotente, con backup).

Pasos por video (en daily_pilot/nocturno_2026-11-17/<id>/):
  1. copia <id>.es.vtt  ->  data_hist/<id>/<id>.es.vtt
  2. genera <id>_transcript.json (cue-wise, sin red)
  3. registra el video en registro.json (fuente: nocturno, published=fecha_titulo)
Despues hace falta correr: migrate.py --force, extraer_claims.py.
"""
from __future__ import annotations

import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE))
from scripts.rss_priority_processor import extract_transcript   # noqa: E402

PILOT = BASE / 'daily_pilot'
NOCT = PILOT / 'nocturno_2026-11-17'
REG = PILOT / 'registro' / 'registro.json'
PAPER_ONLY = True


def main() -> int:
    reg = json.loads(REG.read_text(encoding='utf-8'))
    ahora = datetime.now(timezone.utc).isoformat()
    copiados = generados = registrados = 0
    for d in sorted(p for p in NOCT.iterdir() if p.is_dir()):
        vid = d.name
        vtt = list(d.glob('*.es.vtt')) or list(d.glob('*.vtt'))
        if not vtt:
            print(f'  {vid}: SIN vtt, omitido')
            continue
        dst = BASE / 'data_hist' / vid
        dst.mkdir(parents=True, exist_ok=True)
        target = dst / f'{vid}.es.vtt'
        if not target.exists():
            shutil.copy2(vtt[0], target)
            copiados += 1
        tp = extract_transcript(vid, BASE / 'data_hist')
        if tp:
            generados += 1
        if vid not in reg['videos']:
            a = {}
            af = d / f'{vid}_analisis.json'
            if af.exists():
                try:
                    a = json.loads(af.read_text(encoding='utf-8'))
                except Exception:
                    a = {}
            reg['videos'][vid] = {
                'video_id': vid, 'titulo': a.get('titulo') or '',
                'published': a.get('fecha_titulo') or None,
                'url': f'https://www.youtube.com/watch?v={vid}',
                'detectado': ahora, 'transcript': str(tp) if tp else None,
                'estado': 'importado_nocturno', 'fuente': 'nocturno_2026-11-17'}
            registrados += 1
        print(f'  {vid}: vtt ok | transcript={"si" if tp else "NO"} | registro={"si" if vid in reg["videos"] else "no"}')
    REG.write_text(json.dumps(reg, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'\ncopiados {copiados} vtt | transcripciones {generados} | registrados {registrados}')
    print(f'registro total: {len(reg["videos"])}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
