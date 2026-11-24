#!/usr/bin/env python3
"""Panel de RESULTADOS de la búsqueda de estrategia para el dashboard v6.

Lee daily_pilot/investigacion/ESTRATEGIA_GANADORA.md si existe y muestra
el veredicto + la tabla de las mejores variantes. Si el archivo no existe,
muestra un cartel neutro de «en curso».

Uso:
    from panel_resultados import html
    html()   -> cadena HTML lista para insertar

PAPER_ONLY: muestra, no ejecuta.
"""
from __future__ import annotations

import re
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
INF = BASE / 'daily_pilot' / 'investigacion' / 'ESTRATEGIA_GANADORA.md'

CSS_EXTRA = '''
.res{border-radius:14px;padding:18px 20px;border:1px solid var(--bd);
background:linear-gradient(180deg,var(--card),var(--bg2));margin-bottom:26px}
.verdict{font-size:20px;font-weight:800;letter-spacing:-.3px;margin-bottom:6px}
.verdict.si{color:var(--ok)} .verdict.no{color:var(--warn)}
.res .meta{color:var(--muted);font-size:12px;line-height:1.7}
.rtab{width:100%;border-collapse:collapse;margin-top:14px;font-size:13px}
.rtab th{text-align:left;color:var(--muted);font-size:11px;text-transform:uppercase;
letter-spacing:.6px;padding:0 8px 8px;border-bottom:1px solid var(--bd)}
.rtab td{padding:9px 8px;border-bottom:1px solid rgba(255,255,255,.05);
font-variant-numeric:tabular-nums}
.rtab tr:hover{background:rgba(255,255,255,.03)}
.pill-ok{color:var(--ok);font-weight:700}
.pill-no{color:var(--muted);font-weight:600}
'''


def _veredicto(txt: str) -> tuple[str, bool]:
    """Saca el veredicto del markdown: busca lineas que arranquen con VEREDICTO."""
    for linea in txt.splitlines():
        l = linea.strip().strip('*').strip()
        if not l.upper().startswith('VEREDICTO'):
            continue
        seg = l.upper()
        if 'NO EXISTE' in seg or 'NO HAY' in seg or 'INCONCLUSO' in seg:
            return 'NO EXISTE', False
        if 'EXISTE' in seg:
            return 'EXISTE', True
    return '', False


def _filas(txt: str, limite: int = 8) -> list[list[str]]:
    """Parsea la primera tabla markdown en filas de celdas."""
    out = []
    for linea in txt.splitlines():
        l = linea.strip()
        if not l.startswith('|'):
            continue
        celdas = [c.strip() for c in l.strip('|').split('|')]
        if all(set(c) <= set('-: ') for c in celdas):   # separador
            continue
        if celdas and celdas[0].lower() in ('tf', 'regla', 'variante', 'par', 'par/tf'):
            continue                                       # encabezado
        out.append(celdas)
        if len(out) >= limite:
            break
    return out


def html() -> str:
    if not INF.exists():
        return (
            '<div class="res"><div class="verdict" style="color:var(--acc)">BÚSQUEDA EN CURSO</div>'
            '<div class="meta">Todavía no hay veredicto. Se mostrará aquí '
            'apenas termine el análisis.</div></div>')

    txt = INF.read_text(encoding='utf-8', errors='replace')
    veredicto, gana = _veredicto(txt)

    titulo = 'ESTRATEGIA GANADORA · EXISTE' if gana else \
             'ESTRATEGIA GANADORA · NO EXISTE' if veredicto == 'NO EXISTE' else 'RESULTADO DE LA BÚSQUEDA'

    cuerpo = ''
    filas = _filas(txt)
    if filas:
        cab = ''.join(f'<th>{c}</th>' for c in filas[0]) if len(filas[0]) > 1 else ''
        cuerpo += f'<table class="rtab"><tr>{cab}</tr>'
        for f in filas[1:]:
            tds = ''.join(f'<td>{c}</td>' for c in f)
            cuerpo += f'<tr>{tds}</tr>'
        cuerpo += '</table>'
    else:
        # resumen de primeras lineas con datos
        lineas = [l.strip() for l in txt.splitlines()
                  if l.strip() and not l.strip().startswith('#')][:12]
        cuerpo = '<div class="meta">' + '<br>'.join(_esc(l) for l in lineas) + '</div>'

    return (f'<div class="res"><div class="verdict {"si" if gana else "no"}">{_esc(titulo)}</div>'
            f'{cuerpo}'
            f'<div class="meta" style="margin-top:12px">fuente: {_esc(INF.name)}</div></div>')


def _esc(s) -> str:
    import html as _h
    return _h.escape(str(s or ''))


if __name__ == '__main__':
    print(html())
