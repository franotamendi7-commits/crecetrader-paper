#!/usr/bin/env python3
"""Panel RESUMEN DEL VIDEO para el dashboard v6.

Lee daily_pilot/analisis/resumen_video.json (resumen real del transcript)
y lo renderiza como una seccion autoreferencial del tablero.

Uso:
    from panel_video import CSS_EXTRA, html
PAPER_ONLY: muestra, no ejecuta.
"""
from __future__ import annotations

import html as _h
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
RES = BASE / 'daily_pilot' / 'analisis' / 'resumen_video.json'

CSS_EXTRA = '''
.vid{border-radius:14px;padding:20px 22px;border:1px solid var(--bd);
background:var(--card);margin-bottom:26px}
.vid .tit{font-size:17px;font-weight:800;letter-spacing:-.2px}
.vid .meta{color:var(--muted);font-size:12px;margin-top:4px;line-height:1.6}
.vid .sesgo{display:inline-block;margin-top:10px;padding:6px 12px;border-radius:8px;
background:rgba(224,170,76,.12);border:1px solid rgba(224,170,76,.45);
color:var(--warn);font-size:12px;font-weight:700}
.vid .tesis{margin:14px 0 0;padding:13px 15px;border-left:3px solid var(--acc);
background:rgba(90,162,255,.06);border-radius:0 9px 9px 0;font-size:13px;line-height:1.6}
.vid h3{font-size:11px;text-transform:uppercase;letter-spacing:1px;color:var(--acc);
margin:20px 0 10px}
.vid .niv{display:grid;grid-template-columns:repeat(auto-fill,minmax(215px,1fr));gap:8px}
.vid .n{border:1px solid var(--bd);border-radius:9px;padding:10px 12px;
background:rgba(255,255,255,.025)}
.vid .n .p{font-size:15px;font-weight:800;font-variant-numeric:tabular-nums}
.vid .n .t{font-size:11px;color:var(--warn);font-weight:700;margin:2px 0 4px;text-transform:uppercase}
.vid .n .d{font-size:11px;color:var(--muted);line-height:1.45}
.vid .esc{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:9px}
.vid .e{border:1px solid var(--bd);border-radius:10px;padding:12px 13px;
background:rgba(255,255,255,.03)}
.vid .e b{display:block;font-size:13px;margin-bottom:5px}
.vid .e .prob{font-size:10px;color:var(--warn);font-weight:700;text-transform:uppercase}
.vid .e span{font-size:11px;color:var(--muted);line-height:1.5;display:block;margin-top:4px}
.vid ul{margin:0;padding-left:18px;color:var(--muted);font-size:12px;line-height:1.75}
.vid blockquote{margin:8px 0;padding:9px 13px;border-left:2px solid var(--bd);
color:var(--muted);font-size:12px;font-style:italic;line-height:1.55}
.vid .link{margin-top:16px;padding:12px 14px;border-radius:10px;
border:1px solid rgba(62,207,122,.35);background:rgba(62,207,122,.07);
font-size:12px;line-height:1.6}
.vid .link b{color:var(--ok)}
'''


def _e(s):
    return _h.escape(str(s or ''))


def html() -> str:
    if not RES.exists():
        return ('<div class="vid"><div class="tit">Resumen del video</div>'
                '<div class="meta">sin resumen generado</div></div>')
    import json
    try:
        d = json.loads(RES.read_text(encoding='utf-8'))
    except Exception:
        return '<div class="vid"><div class="meta">resumen ilegible</div></div>'

    sesgo = d.get('sesgo', '')
    meta = (f"{esc(d.get('publicado', '')[:16].replace('T', ' '))} UTC · "
            f"{esc(d.get('duracion_min'))} min · {esc(d.get('fuente'))}")

    niv = d.get('niveles', [])
    # separo: por debajo del precio actual (soporte) y por encima (resistencia/objetivo)
    ref = 59793
    sop = [n for n in niv if float(n['precio']) <= ref]
    res = [n for n in niv if float(n['precio']) > ref]

    def bloque(titulo, arr, color):
        if not arr:
            return ''
        tarjetas = ''.join(
            f'<div class="n"><div class="p">{float(n["precio"]):,.0f}</div>'
            f'<div class="t" style="color:{color}">{_e(n.get("tipo"))}</div>'
            f'<div class="d">{_e(n.get("detalle"))}</div></div>' for n in arr)
        return f'<h3>{titulo}</h3><div class="niv">{tarjetas}</div>'

    esc_html = ''.join(
        f'<div class="e"><b>{_e(e.get("nombre"))}</b>'
        f'<div class="prob">{_e(e.get("probabilidad"))}</div>'
        f'<span>{_e(e.get("detalle"))}</span></div>' for e in d.get('escenarios', []))

    macro = ''.join(f'<li>{_e(x)}</li>' for x in d.get('macro', []))
    citas = ''.join(f'<blockquote>“{_e(x)}”</blockquote>' for x in d.get('frases_clave', []))

    return (f'<div class="vid">'
            f'<div class="tit">▶ {_e(d.get("titulo"))}</div>'
            f'<div class="meta">{meta}</div>'
            f'<div class="sesgo">{_e(sesgo)}</div>'
            f'<div class="tesis">{_e(d.get("tesis"))}</div>'
            f'{bloque("Soporte / zona de compras", sop, "var(--ok)")}'
            f'{bloque("Resistencia / objetivos", res, "var(--bad)")}'
            f'<h3>Escenarios</h3><div class="esc">{esc_html}</div>'
            f'<h3>Contexto macro</h3><ul>{macro}</ul>'
            f'<h3>Frases clave</h3>{citas}'
            f'<div class="link"><b>Conexión con la estrategia:</b> '
            f'{_e(d.get("conexion_estrategia"))}</div>'
            f'</div>'
            f'<div class="meta" style="margin:-16px 0 24px">fuente: {_e(RES.name)} · '
            f'video {_e(d.get("video_id"))}</div>')


# alias para no depender de import de escape en el modulo
def esc(s):
    return _e(s)


if __name__ == '__main__':
    print(html())
