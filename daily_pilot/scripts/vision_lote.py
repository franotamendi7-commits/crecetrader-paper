#!/usr/bin/env python3
"""Vision en lote: descarga video -> frames -> VLM local. Read-only sobre el repo (escribe en daily_pilot/frames y tmp/).

Uso: python3 -B vision_lote.py <vid1,vid2,...>
"""
import subprocess, sys, time, json
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
PILOT = BASE / 'daily_pilot'
FRAMES = PILOT / 'frames'
TMP = PILOT / 'tmp'
FPS = 1 / 30.0          # 1 frame cada 30 s
MAXH = 720


def log(*a):
    print(*a, flush=True)


def descargar(vid: str) -> Path | None:
    outdir = BASE / 'data_hist' / vid
    outdir.mkdir(parents=True, exist_ok=True)
    if list(outdir.glob('*.mp4')):
        return list(outdir.glob('*.mp4'))[0]
    log(f'  [{vid}] descargando (video, <=720p)...')
    r = subprocess.run(['yt-dlp', '-f', f'bv*[height<={MAXH}]/b[height<={MAXH}]/b',
                        '--no-playlist', '--no-write-subs',
                        '-o', str(outdir / '%(id)s.%(ext)s'),
                        f'https://www.youtube.com/watch?v={vid}'],
                       capture_output=True, text=True, timeout=900)
    f = list(outdir.glob('*.mp4')) + list(outdir.glob('*.webm')) + list(outdir.glob('*.mkv'))
    if r.returncode != 0 or not f:
        log(f'  [{vid}] FALLO descarga: {r.stderr[-200:]}')
        return None
    log(f'  [{vid}] OK {f[0].name} ({f[0].stat().st_size/1e6:.0f} MB)')
    return f[0]


def frames(vid: str, fuente: Path) -> Path:
    d = FRAMES / vid
    d.mkdir(parents=True, exist_ok=True)
    if len(list(d.glob('*.jpg'))) >= 3:
        log(f'  [{vid}] frames ya existen: {len(list(d.glob("*.jpg")))}')
        return d
    log(f'  [{vid}] extrayendo frames (1/{int(1/FPS)}s)...')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(fuente),
                    '-vf', f'fps={FPS},scale=1280:-2', '-q:v', '3', str(d / '%05d.jpg')],
                   capture_output=True, timeout=900)
    n = len(list(d.glob('*.jpg')))
    log(f'  [{vid}] {n} frames')
    return d


def vlm(vid: str, d: Path) -> dict | None:
    out = TMP / f'vision_{vid}.json'
    if out.exists() and out.stat().st_size > 100:
        log(f'  [{vid}] VLM ya corrida')
        return json.loads(out.read_text())
    log(f'  [{vid}] corriendo VLM local...')
    t0 = time.time()
    r = subprocess.run([sys.executable, str(PILOT / 'scripts' / 'leer_grafico.py'),
                        '--frames-dir', str(d), '--out', str(out)],
                       capture_output=True, text=True, timeout=7200)
    if r.returncode != 0:
        log(f'  [{vid}] FALLO VLM: {r.stderr[-300:]}')
        return None
    vis = json.loads(out.read_text()) if out.exists() else None
    n = vis.get('n_frames', 0) if vis else 0
    g = sum(1 for x in (vis or {}).get('frames', []) if x['data'].get('es_grafico'))
    log(f'  [{vid}] VLM: {g}/{n} graficos · {time.time()-t0:.0f}s')
    return vis


def main() -> int:
    ids = [x for x in (sys.argv[1] if len(sys.argv) > 1 else '').split(',') if x]
    if not ids:
        print('uso: vision_lote.py <vid1,vid2,...>'); return 2
    resumen = []
    for vid in ids:
        log(f'\n=== {vid} ===')
        t0 = time.time()
        f = descargar(vid)
        if not f:
            resumen.append((vid, 'FALLA descarga', 0)); continue
        d = frames(vid, f)
        vis = vlm(vid, d)
        n = len(list(d.glob('*.jpg')))
        g = sum(1 for x in (vis or {}).get('frames', []) if x['data'].get('es_grafico')) if vis else 0
        resumen.append((vid, f'{g}/{n} graficos', round(time.time() - t0)))
        log(f'  [{vid}] total {time.time()-t0:.0f}s')
    log('\n==== RESUMEN ====')
    for vid, q, s in resumen:
        log(f'  {vid:14s} {q:16s} {s}s')
    return 0


if __name__ == '__main__':
    sys.exit(main())
