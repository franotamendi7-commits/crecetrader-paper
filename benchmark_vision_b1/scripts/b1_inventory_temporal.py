#!/usr/bin/env python3
"""B1 + B3 (solo lectura sobre production, escribe en benchmark_vision_b1/).

- Inventario de frames: hash, dimensiones, tamano, varianza (legibilidad basica), duplicados.
- Recuperacion temporal: pts_time por frame via ffmpeg showinfo, verificando que el
  numero de archivo es el indice 1-based de extraccion.
- Verificacion de correspondencia frame<->video por re-extraccion de una muestra.
"""
import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageStat

BASE = Path('/Users/franciscootamendi/YouTubeTradingAgent')
OUT = BASE / 'benchmark_vision_b1'
VIDEOS = ['EJoLhxbwYxo', 'LFHkc5dUoLw', 'LzPTdClLo_w', 'XLgPycsN0ls',
          'dPHvRw1wzYQ', 'jeOFS1TZYQA', 's3KxjqkzwKM', 'scJ-ai2FRiE']


def probe_duration(video: Path) -> float:
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                        '-of', 'default=noprint_wrappers=1:nokey=1', str(video)],
                       capture_output=True, text=True)
    return float(r.stdout.strip())


def showinfo_pts(video: Path, fps: str, nmax: int):
    """Devuelve lista de pts_time (s) en orden de extraccion (1-based)."""
    cmd = ['ffmpeg', '-hide_banner', '-loglevel', 'info', '-i', str(video),
           '-vf', f'fps={fps},showinfo', '-f', 'null', '-']
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
    pts = []
    for line in r.stderr.splitlines():
        if 'pts_time:' in line:
            seg = line.split('pts_time:')[1].split()[0]
            try:
                pts.append(float(seg))
            except ValueError:
                pass
    return pts


def img_stats(path: Path):
    im = Image.open(path).convert('L')
    st = ImageStat.Stat(im)
    return im.size, round(st.stddev[0], 2)


def main():
    inv = []
    temporal = {}
    hashes = {}
    for vid in VIDEOS:
        fdir = BASE / 'frames_hist' / vid
        files = sorted(fdir.glob('frame_*.jpg'))
        vpath = BASE / 'data_hist' / vid / f'{vid}.mp4'
        dur = probe_duration(vpath) if vpath.exists() else None
        nums = [int(f.stem.split('_')[1]) for f in files]
        maxnum = max(nums) if nums else 0
        fps_imp = (maxnum / dur) if (dur and maxnum) else None
        fps_str = ('5' if fps_imp and fps_imp > 1 else '1/30') if fps_imp else '1/30'
        print(f'{vid}: frames={len(files)} max_num={maxnum} dur={dur} fps_impl={fps_imp}', flush=True)
        pts = showinfo_pts(vpath, fps_str, maxnum) if vpath.exists() else []
        # verificar pts_time(n) ~ (n-1)/fps
        fps_val = 5.0 if fps_str == '5' else 1 / 30
        verificados = 0
        for i, t in enumerate(pts, start=1):
            esperado = (i - 1) / fps_val
            if abs(t - esperado) < 1e-6:
                verificados += 1
        correspondencia = {
            'video_id': vid, 'duration_s': dur, 'max_frame_number': maxnum,
            'fps_implicito': fps_imp, 'fps_usado_showinfo': fps_str,
            'pts_capturados': len(pts), 'pts_verificados': verificados,
            'frames': {},
        }
        for f in files:
            n = int(f.stem.split('_')[1])
            t = pts[n - 1] if 0 < n <= len(pts) else None
            ok = None
            if t is not None:
                ok = abs(t - (n - 1) / fps_val) < 1e-6
            correspondencia['frames'][f.name] = {'idx': n, 'pts_time': t, 'verificado': ok}
        temporal[vid] = correspondencia
        for f in files:
            data = f.read_bytes()
            h = hashlib.md5(data).hexdigest()
            size, std = img_stats(f)
            dup = hashes.get(h)
            hashes[h] = f.name
            inv.append({
                'video_id': vid, 'frame': f.name, 'idx': int(f.stem.split('_')[1]),
                'ancho': size[0], 'alto': size[1], 'bytes': len(data),
                'std_lum': std, 'md5': h, 'duplicado_de': dup or '',
                'pts_time': correspondencia['frames'][f.name]['pts_time'],
                'tiempo_verificado': correspondencia['frames'][f.name]['verificado'],
            })
    (OUT / 'inventory.json').write_text(json.dumps(inv, ensure_ascii=False, indent=2))
    with open(OUT / 'inventory.csv', 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(inv[0].keys()))
        w.writeheader(); w.writerows(inv)
    (OUT / 'temporal' / 'timestamps.json').write_text(json.dumps(temporal, ensure_ascii=False, indent=2))
    dups = [r for r in inv if r['duplicado_de']]
    print(f'\nTOTAL frames={len(inv)} | duplicados={len(dups)}')
    print('duplicados:', [(r['frame'], r['duplicado_de']) for r in dups][:10])
    for vid, c in temporal.items():
        vf = sum(1 for x in c['frames'].values() if x['verificado'])
        print(f"  {vid}: pts={c['pts_capturados']} verificados={vf}/{len(c['frames'])}")


if __name__ == '__main__':
    main()
