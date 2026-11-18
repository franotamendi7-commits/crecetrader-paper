#!/usr/bin/env python3
"""Mision de validacion visual — prepara la muestra (sin procesar videos).

Reutiliza frames y transcripciones existentes. Selecciona 5-8 capturas por video
en momentos con niveles citados y en tramos temporales distintos.
"""
import json
import re
import shutil
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
OUT = BASE / 'daily_pilot' / 'vision_mission'
CAP = OUT / 'capturas'
CAP.mkdir(parents=True, exist_ok=True)
VIDEOS = ['dPHvRw1wzYQ', 'XLgPycsN0ls', 's3KxjqkzwKM']
POR_VIDEO = 6


def s2(ts):
    h, m, sec = ts.split(':')
    return int(h) * 3600 + int(m) * 60 + float(sec)


def main():
    registro = []
    for vid in VIDEOS:
        d = json.load(open(BASE / 'data_hist' / vid / f'{vid}_transcript.json'))
        frames = sorted((BASE / 'frames_hist' / vid).glob('frame_*.jpg'))
        ts = json.load(open(BASE / 'benchmark_vision_b1' / 'temporal' / 'timestamps.json'))[vid]['frames']
        pts = {name: data['pts_time'] for name, data in ts.items()}

        # momentos con niveles citados
        momentos = []
        last = None
        for s in d['segments']:
            t = s['text'].strip()
            if t == last:
                continue
            last = t
            if re.search(r'\d{2}[.,]\d{3}', t):
                momentos.append((s2(s['start']), t))
        momentos = sorted(set(momentos))
        # elige hasta 4 momentos distintos, separados
        elegidos = []
        for t, txt in momentos:
            if all(abs(t - e) > 60 for e, _ in elegidos):
                elegidos.append((t, txt))
            if len(elegidos) >= 4:
                break

        # para cada momento, el frame mas cercano
        usados = set()
        for t, txt in elegidos:
            cercano = min(frames, key=lambda f: abs(pts[f.name] - t))
            if cercano.name in usados:
                continue
            usados.add(cercano.name)
            registro.append({'video_id': vid, 'frame': cercano.name,
                             'pts_time': pts[cercano.name], 'momento': f'{int(t//60):02d}:{int(t%60):02d}',
                             'transcripcion': txt[:160]})

        # completar con tramos equidistantes si faltan
        if len([r for r in registro if r['video_id'] == vid]) < POR_VIDEO:
            n = len([r for r in registro if r['video_id'] == vid])
            for i in range(POR_VIDEO - n):
                idx = round(i * (len(frames) - 1) / max(1, POR_VIDEO - n - 1))
                f = frames[idx]
                if f.name in usados:
                    continue
                usados.add(f.name)
                registro.append({'video_id': vid, 'frame': f.name,
                                 'pts_time': pts[f.name], 'momento': 'tramo',
                                 'transcripcion': 'muestreo de tramo (sin nivel citado_exacto)'})

        for r in registro:
            if r['video_id'] != vid:
                continue
            src = BASE / 'frames_hist' / vid / r['frame']
            dst = CAP / f"{vid}__{r['frame']}"
            if not dst.exists():
                shutil.copy2(src, dst)
            r['captura'] = str(dst.relative_to(BASE))

    (OUT / 'muestra_capturas.json').write_text(json.dumps(registro, ensure_ascii=False, indent=2))
    print(f'capturas: {len(registro)} en {CAP}')
    for r in registro:
        print(f"  {r['video_id']} {r['frame']} @{r['pts_time']}s | {r['momento']} | {r['transcripcion'][:70]}")


if __name__ == '__main__':
    main()
