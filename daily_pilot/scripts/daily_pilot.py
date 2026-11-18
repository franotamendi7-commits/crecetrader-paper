#!/usr/bin/env python3
"""YouTube Analyst — piloto diario (aislado).

Detecta videos nuevos del canal por RSS, evita reprocesar, transcribe con
timestamps y registra. NO ejecuta inferencia audiovisual (el Mac no es maquina
de inferencia). El informe lo genera el agente con la transcripcion.
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, '/Users/franciscootamendi/YouTubeTradingAgent')
BASE = Path(__file__).resolve().parents[2]
PILOT = BASE / 'daily_pilot'
REG = PILOT / 'registro' / 'registro.json'
RSS = 'https://www.youtube.com/feeds/videos.xml?channel_id=UC4DOPLw9NRRBFW4wYjcWxiA'


def fetch_rss():
    with urllib.request.urlopen(RSS, timeout=20) as r:
        x = r.read().decode('utf-8', 'replace')
    out = []
    for e in re.findall(r'<entry>(.*?)</entry>', x, re.S):
        vid = re.search(r'<yt:videoId>([^<]+)</yt:videoId>', e)
        ti = re.search(r'<title>(.*?)</title>', e, re.S)
        pub = re.search(r'<published>([^<]+)</published>', e)
        if vid:
            out.append({'video_id': vid.group(1),
                        'title': re.sub(r'<[^>]+>', '', ti.group(1)) if ti else '',
                        'published': pub.group(1) if pub else ''})
    return out


def cargar_registro():
    if REG.exists():
        return json.load(open(REG))
    return {'videos': {}}


def guardar_registro(reg):
    REG.parent.mkdir(parents=True, exist_ok=True)
    REG.write_text(json.dumps(reg, ensure_ascii=False, indent=2))


def transcribir(video_id):
    d = BASE / 'data_hist' / video_id
    d.mkdir(parents=True, exist_ok=True)
    subprocess.run(['yt-dlp', '--skip-download', '--write-auto-sub', '--sub-langs', 'es',
                    '--sub-format', 'vtt', '-o', str(d / video_id),
                    f'https://www.youtube.com/watch?v={video_id}'],
                   capture_output=True, text=True)
    from scripts.rss_priority_processor import extract_transcript
    return extract_transcript(video_id, BASE / 'data_hist')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check-only', action='store_true')
    a = ap.parse_args()
    reg = cargar_registro()
    rss = fetch_rss()
    nuevos = []
    for v in rss:
        vid = v['video_id']
        if vid in reg['videos']:
            continue
        if a.check_only:
            nuevos.append(v)
            continue
        try:
            tp = transcribir(vid)
            estado = 'transcrito' if tp else 'sin_transcripcion'
        except Exception as exc:
            tp, estado = None, f'error: {exc}'
        reg['videos'][vid] = {
            'video_id': vid, 'title': v['title'], 'published': v['published'],
            'url': f'https://www.youtube.com/watch?v={vid}',
            'detectado': datetime.now(timezone.utc).isoformat(),
            'transcript': str(tp) if tp else None, 'estado': estado,
        }
        nuevos.append(v)
        print(f"{vid} | {estado} | {v['title'][:60]}", flush=True)
    guardar_registro(reg)
    if not nuevos:
        print('Sin publicaciones nuevas.', flush=True)
    print(f"registro: {len(reg['videos'])} videos", flush=True)


if __name__ == '__main__':
    main()
