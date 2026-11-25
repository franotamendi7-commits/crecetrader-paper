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

import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
INF = BASE / 'daily_pilot' / 'investigacion' / 'ESTRATEGIA_GANADORA.md'
EST = BASE / 'daily_pilot' / 'datos' / 'estrategias_validadas.json'

CSS_EXTRA = '''
.res{border-radius:14px;padding:18px 20px;border:1px solid var(--bd);
background:var(--card);margin-bottom:26px}
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
    """Saca el veredicto de la seccion 'VEREDICTO FINAL' del markdown.

    El encabezado '## 6. VEREDICTO FINAL' no debe romperse por el prefijo '## '.
    Devuelve (veredicto_final, existe): ej. ('PASA', True) o ('NO EXISTE', False).
    """
    seccion = []
    en = False
    for linea in txt.splitlines():
        s = linea.strip()
        if s.upper().startswith('## '):
            en = 'VEREDICTO' in s.upper()
            if en:
                seccion = []
            continue
        if en:
            seccion.append(linea.strip().strip('*').strip())
    u_all = '\n'.join(seccion).upper()
    if 'NO EXISTE' in u_all or 'NO HAY' in u_all or 'INCONCLUSO' in u_all:
        return 'NO EXISTE', False
    if 'EXISTE' in u_all:
        vered = 'PASA' if 'PASA' in u_all else ('RUIDO' if 'RUIDO' in u_all else 'EXISTE')
        return (vered, True)
    return 'NO EXISTE', False


def _bloques(txt: str) -> list[list[list[str]]]:
    """Separa el markdown en bloques de tabla markdown (filas de celdas)."""
    bloques: list[list[list[str]]] = []
    actual: list[list[str]] = []
    for linea in txt.splitlines():
        l = linea.strip()
        if l.startswith('|'):
            actual.append([c.strip() for c in l.strip('|').split('|')])
        elif actual:
            bloques.append(actual)
            actual = []
    if actual:
        bloques.append(actual)
    return bloques


def _filas(txt: str, limite: int = 8) -> list[list[str]]:
    """Devuelve el bloque de variantes: [header, fila1, fila2, ...].

    Es el bloque que contiene filas con veredicto (PASA / RUIDO). Evita mezclar
    la tabla de cobertura de mercado (Par/TF/Velas) con la de variantes.
    """
    for b in _bloques(txt):
        if len(b) < 2:
            continue
        datos = [r for r in b[1:] if not all(set(c) <= set('-: ') for c in r)]
        if any('PASA' in ' '.join(r).upper() or 'RUIDO' in ' '.join(r).upper() for r in datos):
            return [b[0]] + datos
    return []


def html() -> str:
    if not INF.exists():
        return (
            '<div class="res"><div class="verdict" style="color:var(--acc)">BÚSQUEDA EN CURSO</div>'
            '<div class="meta">Todavía no hay veredicto. Se mostrará aquí '
            'apenas termine el análisis.</div></div>')

    txt = INF.read_text(encoding='utf-8', errors='replace')
    veredicto, gana = _veredicto(txt)
    filas = _filas(txt)

    vered_real = veredicto
    if len(filas) > 1:
        for f in filas[1:]:
            if 'PASA' in f[-1].upper() or 'RUIDO' in f[-1].upper():
                vered_real = f[-1]
                break

    titulo = f'ESTRATEGIA GANADORA · {vered_real}'

    cuerpo = ''
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

    linea_est = ''
    if EST.exists():
        try:
            ed = json.loads(EST.read_text(encoding='utf-8'))
            desc = ed.get('descartados') or {}
            tot = desc.get('total_pares_quantfury')
            pos = desc.get('con_expectativa_positiva')
            validos = [p for p in ed.get('pares') or [] if p.get('estado') == 'VALIDADA']
            val = (validos[0].get('par') or '').replace('USDT', '') if validos else '—'
            if tot and pos is not None:
                linea_est = (f'<div class="meta" style="margin-top:8px">{pos} de {tot} pares con '
                             f'E&gt;0 · solo {_esc(val)} valida estrictamente.</div>')
        except Exception:
            linea_est = ''

    return (f'<div class="res"><div class="verdict {"si" if gana else "no"}">{_esc(vered_real)}</div>'
            f'{cuerpo}'
            f'{linea_est}'
            f'<div class="meta" style="margin-top:12px">fuente: {_esc(INF.name)} · veredicto: {_esc(veredicto)}</div></div>')


def _esc(s) -> str:
    import html as _h
    return _h.escape(str(s or ''))


if __name__ == '__main__':
    print(html())
