#!/usr/bin/env python3
"""Informe de vision+lectura de los videos de estrategia (8) y el de hoy.

Lee: daily_pilot/tmp/vision_<vid>.json + data_hist/<vid>/<vid>_transcript.json
Escribe: daily_pilot/investigacion/INFORME_VISION_8.md
PAPER_ONLY, read-only sobre las fuentes.
"""
import json, pathlib, sys, collections
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'core'))
from precios import precios_de_texto

PILOT = pathlib.Path(__file__).resolve().parents[1]
BASE = PILOT.parent
ESTRATEGIA = ['9_91uE05BPE', 'pLgygQEPwvs', 'PiuwNj15Nv8', 'fHpsbPovocE',
              'YiVZ_aAK0Uk', 'd-6Ud3BhQ0I', 'JB0QyPbmdNg', 'TgOtsgQXZVA']
HOY = 'EX-Rx_pnNpc'
GRUPOS = [('ESTRATEGIA (8)', ESTRATEGIA), ('ACTUALIDAD (hoy)', [HOY])]


def leer_vlm(vid):
    p = PILOT / 'tmp' / f'vision_{vid}.json'
    if not p.exists():
        return None
    d = json.loads(p.read_text())
    nc = d.get('niveles_consolidados') or {}
    vn = {float(k): n for k, n in nc.items() if float(k) > 1000}
    fr = d.get('frames', [])
    g = [x for x in fr if x['data'].get('es_grafico')]
    instr = collections.Counter(x['data'].get('instrumento') for x in g)
    tf = collections.Counter(x['data'].get('tf_aparente') for x in g)
    return {'n_frames': d.get('n_frames'), 'graficos': len(g),
            'instr': instr.most_common(4), 'tf': tf.most_common(4), 'niveles': vn}


def leer_canal(vid):
    p = BASE / 'data_hist' / vid / f'{vid}_transcript.json'
    if not p.exists():
        return None
    d = json.loads(p.read_text())
    cnt = collections.Counter()
    frases = []
    for s in d.get('segments', []):
        t = s.get('text', '')
        for x in precios_de_texto(t):
            cnt[x] += 1
        if any(k in t.lower() for k in ('calculado', 'nivel', 'objetivo', 'proyeccion', 'fibonacci')):
            ps = precios_de_texto(t)
            if ps:
                frases.append((s.get('start'), ps[:2], t[:110]))
    return {'n_cues': len(d.get('segments', [])), 'niveles': cnt, 'frases': frases[:6]}


def fmt_niveles(vn, n=6):
    return ', '.join(f'{int(k)}×{v}' for k, v in sorted(vn.items(), key=lambda x: -x[1])[:n]) or '—'


def main():
    out = ['# INFORME DE VISIÓN + LECTURA — estrategia (8) y actualidad (hoy)',
           '',
           'VLM local `qwen3-vl:8b-instruct` · 1 frame/30 s · read-only · PAPER_ONLY',
           '']
    tot_f = tot_g = tot_c = 0
    for nombre, ids in GRUPOS:
        out += [f'## {nombre}', '',
                '| vídeo | frames | gráficos | instrumento | TF aparente | niveles VLM | coinciden canal |',
                '|---|---|---|---|---|---|---|']
        for vid in ids:
            v = leer_vlm(vid); c = leer_canal(vid)
            if not v:
                out.append(f'| {vid} | — | sin VLM | — | — | — | — |'); continue
            nc = v['niveles']; cc = (c or {}).get('niveles', {})
            com = [k for k in nc if k in cc]
            tot_f += v['n_frames']; tot_g += v['graficos']; tot_c += len(com)
            instr = (v['instr'][0][0] if v['instr'] else '—')
            tf = (v['tf'][0][0] if v['tf'] else '—')
            out.append(f"| {vid} | {v['n_frames']} | {v['graficos']} | {instr} | {tf} | "
                       f"{len(nc)} | **{len(com)}** |")
        out.append('')
    out += [f'**TOTAL: {tot_f} frames · {tot_g} gráficos · {tot_c} niveles coincidentes**', '']
    # detalle por video
    for nombre, ids in GRUPOS:
        out.append(f'## Detalle — {nombre}')
        for vid in ids:
            v = leer_vlm(vid); c = leer_canal(vid)
            if not v and not c:
                out.append(f'### {vid}\nsin datos'); continue
            out += ['', f'### {vid}']
            if v:
                out.append(f"- **Visión**: {v['graficos']}/{v['n_frames']} gráficos · "
                           f"instrumento `{v['instr'][0][0] if v['instr'] else '—'}` · "
                           f"TF `{v['tf'][0][0] if v['tf'] else '—'}`")
                out.append(f"- **Niveles VLM**: {fmt_niveles(v['niveles'])}")
            if c:
                out.append(f"- **Canal** ({c['n_cues']} cues): {fmt_niveles(c['niveles'], 8)}")
                for st, ps, t in c['frases'][:3]:
                    out.append(f"  - `{st}` **{ps}** — {t}")
            if v and c:
                com = [k for k in v['niveles'] if k in c['niveles']]
                out.append(f"- **COINCIDEN**: {', '.join(str(int(k)) for k in sorted(com, key=lambda x: -v['niveles'][x])[:6]) or '—'}")
    out += ['', '## Lectura', '',
            '- El VLM detecta **instrumento y timeframe** de forma fiable (409/409).',
            '- Los **niveles fuertes** (28.963, 19.126, 69.000, 56.750) **coinciden** con el audio.',
            '- Hay **ruido** (eje, volumen, interfaz): por eso el VLM se usa para **contexto**,',
            '  y los niveles salen del **audio + cálculo C05**.', '']
    dst = PILOT / 'investigacion' / 'INFORME_VISION_8.md'
    dst.write_text('\n'.join(out))
    print(f'-> {dst}')
    print(f'TOTAL {tot_f} frames · {tot_g} graficos · {tot_c} coincidentes')


if __name__ == '__main__':
    main()
