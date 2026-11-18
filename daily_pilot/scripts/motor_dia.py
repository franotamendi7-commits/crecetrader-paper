#!/usr/bin/env python3
"""Motor del dia — pipeline completo para un video (PAPER_ONLY).

  1. extrae frames (ffmpeg, 1 frame cada 30 s) si no existen
  2. corre el VLM local (qwen3-vl:8b-instruct) sobre los frames
  3. guarda daily_pilot/datos/vision_hoy.json
  4. regenera el informe del dia y el dashboard

Uso:
  python3 daily_pilot/scripts/motor_dia.py --video cH2KY5vnsVQ
  python3 daily_pilot/scripts/motor_dia.py            # ultimo video de E1

Sin VLM si --sin-vision. PAPER_ONLY: propone, no ejecuta.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
PILOT = BASE / 'daily_pilot'
sys.path.insert(0, str(PILOT / 'knowledge'))
sys.path.insert(0, str(PILOT / 'scripts'))
import store as S

FPS = '1/30'


def ultimo_video() -> str | None:
    c = S.conectar()
    r = c.execute("SELECT video_id FROM videos ORDER BY published DESC LIMIT 1").fetchone()
    c.close()
    return r[0] if r else None


def extraer_frames(video_id: str) -> Path:
    d = PILOT / 'frames' / video_id
    if d.exists() and list(d.glob('*.jpg')):
        return d
    d.mkdir(parents=True, exist_ok=True)
    # fuente: transcripcion json no sirve para ffmpeg; se usa el video si existe
    fuentes = list((BASE / 'data_hist' / video_id).glob('*.mp4')) + \
              list((BASE / 'data_hist' / video_id).glob('*.webm'))
    if not fuentes:
        print(f'  {video_id}: sin video en data_hist -> no se pueden extraer frames')
        return d
    cmd = ['ffmpeg', '-y', '-i', str(fuentes[0]), '-vf', f'fps={FPS}',
           str(d / 'scene_%03d.jpg'), '-loglevel', 'error']
    subprocess.run(cmd, check=True, timeout=900)
    print(f'  frames: {len(list(d.glob("*.jpg")))} -> {d}')
    return d


def vision(d: Path) -> dict | None:
    jpgs = sorted(d.glob('*.jpg'))
    if not jpgs:
        return None
    out = PILOT / 'datos' / 'vision_hoy.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    r = subprocess.run([sys.executable, str(PILOT / 'scripts' / 'leer_grafico.py'),
                        '--frames-dir', str(d), '--out', str(out)],
                       capture_output=True, text=True, timeout=3600)
    print(r.stdout.strip()[-400:])
    return json.loads(out.read_text()) if out.exists() else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--video', default=None)
    ap.add_argument('--sin-vision', action='store_true')
    a = ap.parse_args()

    vid = a.video or ultimo_video()
    if not vid:
        print('sin videos'); return 1
    print(f'video: {vid}')

    t0 = time.time()
    frames = None if a.sin_vision else extraer_frames(vid)
    vis = None
    if frames:
        vis = vision(frames)

    # regenerar informe + dashboard
    subprocess.run([sys.executable, str(PILOT / 'scripts' / 'informe_dia.py')], check=False)
    subprocess.run([sys.executable, str(PILOT / 'scripts' / 'generar_dashboard.py')], check=False)

    n = vis.get('n_frames') if vis else 0
    g = sum(1 for r in (vis or {}).get('frames', []) if r['data'].get('es_grafico'))
    print(f'\nVLM: {g}/{n} frames con grafico · {time.time()-t0:.0f}s')
    print('dashboard regenerado.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
