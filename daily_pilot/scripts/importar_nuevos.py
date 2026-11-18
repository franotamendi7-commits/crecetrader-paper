#!/usr/bin/env python3
"""Importa los N videos mas nuevos que faltan en E1 (PAPER_ONLY, idempotente).

Por video:
  1. yt-dlp --write-auto-sub (es)  -> data_hist/<id>/<id>.es.vtt
  2. extract_transcript            -> data_hist/<id>/<id>_transcript.json
  3. registro.json
  4. migrate.py --force + extraer_claims.py + analizar_video.py

Uso: python3 daily_pilot/scripts/importar_nuevos.py --n 10
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
PILOT = BASE / 'daily_pilot'
sys.path.insert(0, str(PILOT / 'knowledge'))
sys.path.insert(0, str(BASE / 'scripts'))
import store as S

REG = PILOT / 'registro' / 'registro.json'


def canal_ids() -> list[str]:
    r = subprocess.run(['yt-dlp', '--flat-playlist', '--print', '%(id)s',
                        'https://www.youtube.com/channel/UC4DOPLw9NRRBFW4wYjcWxiA/videos'],
                       capture_output=True, text=True, timeout=1800)
    return [l.strip() for l in r.stdout.splitlines() if l.strip() and not l.startswith('WARNING')]


def faltan() -> list[str]:
    c = S.conectar()
    e1 = set(r[0] for r in c.execute("SELECT video_id FROM videos"))
    c.close()
    return [i for i in canal_ids() if i not in e1]


def transcribir(vid: str) -> Path | None:
    d = BASE / 'data_hist' / vid
    d.mkdir(parents=True, exist_ok=True)
    subprocess.run(['yt-dlp', '--skip-download', '--write-auto-sub', '--sub-langs', 'es',
                    '--sub-format', 'vtt', '-o', str(d / vid),
                    f'https://www.youtube.com/watch?v={vid}'],
                   capture_output=True, text=True, timeout=900)
    from rss_priority_processor import extract_transcript
    return extract_transcript(vid, BASE / 'data_hist')


def uno(vid: str) -> bool:
    try:
        tp = transcribir(vid)
    except Exception as e:
        print(f'  FALLO subtitulos: {e}'); return False
    if not tp:
        print('  sin transcripcion'); return False
    reg = json.loads(REG.read_text()) if REG.exists() else {'videos': {}}
    reg.setdefault('videos', {})[vid] = {
        'video_id': vid, 'title': '', 'published': '',
        'url': f'https://www.youtube.com/watch?v={vid}',
        'detectado': datetime.now(timezone.utc).isoformat(),
        'transcript': str(tp), 'estado': 'transcrito', 'fuente': 'importacion_retroactiva',
    }
    REG.write_text(json.dumps(reg, ensure_ascii=False, indent=2))
    print(f'  OK {tp}')
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, default=10)
    ap.add_argument('--ids', default='')
    a = ap.parse_args()

    ids = a.ids.split(',') if a.ids else faltan()[:a.n]
    print(f'importando {len(ids)} videos')
    ok = []
    for v in ids:
        print(f'[{v}]', flush=True)
        if uno(v):
            ok.append(v)
    print(f'\n{len(ok)}/{len(ids)} transcritos')
    for v in ok:
        subprocess.run([sys.executable, str(PILOT / 'scripts' / 'analizar_video.py'), v],
                       capture_output=True, text=True)
    if ok:
        print('\n-> migrate.py --force && extraer_claims.py')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
