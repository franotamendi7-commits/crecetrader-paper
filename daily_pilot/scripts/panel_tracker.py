#!/usr/bin/env python3
"""Panel TRACKER PAPER para el dashboard v6.

Lee daily_pilot/datos/tracker_paper.json (lo actualiza tracker_paper.py) y
muestra el seguimiento de la estrategia validada de 4 pares: replay reciente,
forward desde el alta, posiciones abiertas y últimas operaciones cerradas.

Reutiliza las clases .mon / .rtab / .fila / .kv ya existentes: no agrega CSS.
PAPER_ONLY: muestra, no ejecuta.
"""
from __future__ import annotations

import html as _h
import json
from pathlib import Path

from tracker_paper import JOURNAL, RIESGO_USD, metricas_ops

BASE = Path(__file__).resolve().parents[2]
EST = BASE / 'daily_pilot' / 'datos' / 'estrategias_validadas.json'

# Sin CSS nuevo: el panel usa .mon, .rtab, .fila, .kv y .estado del dash.
CSS_EXTRA = ''

_ESTADOS = {
    'VALIDADA': ('VALIDADA', 'abierta'),
    'VALIDADA CON RESERVA': ('CON RESERVA', 'sin'),
    'DEBIL': ('DÉBIL', 'cerrada'),
}
_OP_ESTADOS = {
    'ABIERTA': ('ABIERTA', 'abierta'),
    'EN_BE': ('EN BE', 'abierta'),
    'CERRADA_TARGET': ('TARGET', 'abierta'),
    'CERRADA_BE': ('BE', 'sin'),
    'CERRADA_STOP': ('STOP', 'cerrada'),
    'CERRADA_TIEMPO': ('TIEMPO', 'sin'),
}


def _e(s) -> str:
    return _h.escape(str(s or ''))


def _n(x, dec=2, signo=False) -> str:
    """Numero con coma decimal y menos tipografico."""
    try:
        v = float(x)
    except Exception:
        return '—'
    s = f'{v:.{dec}f}'.replace('.', ',')
    if v < 0:
        return '−' + s.lstrip('-')
    if signo and v > 0:
        return '+' + s
    return s


def _money(x) -> str:
    """USD con separador de miles y coma decimal: $1.234,56."""
    try:
        v = float(x)
    except Exception:
        return '—'
    s = f'{abs(v):,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
    return ('−' if v < 0 else '') + '$' + s


def _p(x) -> str:
    """Precio compacto, igual criterio que el resto del dash."""
    try:
        v = float(x)
    except Exception:
        return '—'
    if v >= 1000:
        return f'{v:,.0f}'
    if v >= 100:
        return f'{v:,.2f}'
    if v >= 1:
        return f'{v:.3f}'
    return f'{v:.5f}'


def _color(x) -> str:
    try:
        return 'var(--ok)' if float(x) > 0 else ('var(--bad)' if float(x) < 0
                                                  else 'var(--muted)')
    except Exception:
        return 'var(--muted)'


def _cargar_meta() -> dict:
    if not EST.exists():
        return {}
    try:
        d = json.loads(EST.read_text(encoding='utf-8'))
        return {p.get('par'): p for p in d.get('pares') or [] if p.get('par')}
    except Exception:
        return {}


def _fecha_corta(iso: str) -> str:
    return (iso or '').replace('T', ' ').replace('Z', '')[:16] or '—'


def _vacio() -> str:
    return ('<div class="mon"><div class="mt">TRACKER PAPER · 4 PARES</div>'
            '<div class="nota">sin journal todavía · se crea al regenerar el dash '
            'o con <b>python3 daily_pilot/scripts/tracker_paper.py</b></div></div>')


def html() -> str:
    if not JOURNAL.exists():
        return _vacio()
    try:
        j = json.loads(JOURNAL.read_text(encoding='utf-8'))
    except Exception:
        return '<div class="mon"><div class="nota">tracker ilegible</div></div>'

    ops = j.get('operaciones') or []
    if not isinstance(ops, list):
        return _vacio()
    meta = _cargar_meta()
    pares = list(j.get('estrategia', {}).get('pares') or meta)
    pares.sort(key=lambda p: {'VALIDADA': 0, 'VALIDADA CON RESERVA': 1}
               .get((meta.get(p) or {}).get('estado'), 2))

    g = metricas_ops(ops)
    desde = _fecha_corta(j.get('desde'))
    generado = _fecha_corta(j.get('generado'))
    regla = j.get('estrategia', {}).get('nombre') or 'pullback EMA13 · stop swing · Fib 1.5'

    kpis = [
        ('Ops', str(g['n'])),
        ('Cerradas', str(g['cerradas'])),
        ('Abiertas', str(g['abiertas'])),
        ('E replay', f"{_n(g['E'], 3, True)}R" if g['E'] is not None else '—'),
        ('Acierto', f"{_n(g['acierto'], 1)}%" if g['acierto'] is not None else '—'),
        ('PF', _n(g['pf'], 2)),
        ('DD', f"{_n(g['dd'], 1)}R" if g['cerradas'] else '—'),
        ('Total', f"{_n(g['total'], 1, True)}R"),
        ('USD 0,35%', _money(g['usd'])),
        ('Forward', str(g['forward_n'])),
    ]
    kv_html = ''.join(f'<div><span>{k}</span><b>{v}</b></div>' for k, v in kpis)

    # tabla por par -----------------------------------------------------
    filas = []
    for par in pares:
        po = [o for o in ops if o.get('par') == par]
        m = metricas_ops(po)
        est = meta.get(par) or {}
        label, cls = _ESTADOS.get(est.get('estado'), (est.get('estado') or '—', 'sin'))
        bt = est.get('esperanza_R')
        if m['forward_n']:
            fwd = str(m['forward_n'])
            if m['forward_E'] is not None:
                fwd += f" · {_n(m['forward_E'], 3, True)}R"
        else:
            fwd = '—'
        filas.append(
            '<tr>'
            f'<td><b>{_e(par)}</b></td>'
            f'<td><span class="estado {cls}">{label}</span></td>'
            f'<td>{m["n"]}</td>'
            f'<td>{m["abiertas"]}</td>'
            f'<td style="color:{_color(m["E"])}">'
            f'{_n(m["E"], 3, True) + "R" if m["E"] is not None else "—"}</td>'
            f'<td>{_n(m["acierto"], 1) + "%" if m["acierto"] is not None else "—"}</td>'
            f'<td>{_n(m["pf"], 2)}</td>'
            f'<td>{_n(m["dd"], 1) + "R" if m["cerradas"] else "—"}</td>'
            f'<td style="color:{_color(bt)}">'
            f'{_n(bt, 3, True) + "R" if bt is not None else "—"}</td>'
            f'<td>{fwd}</td>'
            '</tr>')
    tabla = ('<div style="overflow-x:auto"><table class="rtab"><tr>'
             '<th>Par</th><th>Estado</th><th>Ops</th><th>Abiertas</th>'
             '<th>E replay</th><th>Acierto</th><th>PF</th><th>DD</th>'
             '<th>E backtest</th><th>Forward</th>'
             '</tr>' + ''.join(filas) + '</table></div>')

    # posiciones abiertas ----------------------------------------------
    abiertas = sorted([o for o in ops
                       if not str(o.get('estado') or '').startswith('CERRADA')],
                      key=lambda o: -(o.get('R_actual') or 0))
    abiertas_html = ''
    for o in abiertas:
        label, cls = _OP_ESTADOS.get(o.get('estado'), (o.get('estado') or '—', 'sin'))
        abiertas_html += (
            '<div class="fila"><div class="top">'
            f'<span class="nom">{_e(o.get("par"))}</span>'
            f'<span class="estado {cls}">{label}</span>'
            f'<span class="precio" style="color:{_color(o.get("R_actual"))}">'
            f'R actual {_n(o.get("R_actual"), 2, True)}R</span></div>'
            '<div class="kv">'
            f'<div><span>Entrada</span><b>{_p(o.get("entrada"))}</b></div>'
            f'<div><span>Stop actual</span><b>{_p(o.get("stop_actual"))}</b></div>'
            f'<div><span>Target</span><b>{_p(o.get("target"))}</b></div>'
            f'<div><span>Riesgo</span><b>{_money(RIESGO_USD)}</b></div>'
            f'<div><span>Barras</span><b>{o.get("barras") or 0}</b></div>'
            f'<div><span>Señal</span><b>{_e(o.get("senal_fecha"))}</b></div>'
            '</div></div>')
    if not abiertas_html:
        abiertas_html = ('<div class="nota">sin posiciones abiertas: la regla no '
                         'tiene señal viva en este momento.</div>')
    else:
        abiertas_html = ('<div class="head" style="margin-top:14px">Posiciones abiertas</div>'
                         + abiertas_html)

    # ultimas cerradas --------------------------------------------------
    cerradas = sorted([o for o in ops
                       if str(o.get('estado') or '').startswith('CERRADA')],
                      key=lambda o: o.get('cierre_ts') or 0, reverse=True)[:8]
    cerradas_html = ''
    if cerradas:
        filas_c = []
        for o in cerradas:
            label, _ = _OP_ESTADOS.get(o.get('estado'), (o.get('estado') or '—', 'sin'))
            r = o.get('resultado_R')
            filas_c.append(
                '<tr>'
                f'<td>{_e(o.get("cierre_fecha"))}</td>'
                f'<td><b>{_e(o.get("par"))}</b></td>'
                f'<td>{_p(o.get("entrada"))}</td>'
                f'<td>{_p(o.get("stop_inicial"))}</td>'
                f'<td>{_p(o.get("target"))}</td>'
                f'<td style="color:{_color(r)}">{_n(r, 2, True)}R</td>'
                f'<td>{label}</td>'
                f'<td>{_e(o.get("origen"))}</td>'
                '</tr>')
        cerradas_html = (
            '<div class="head" style="margin-top:16px">Últimas operaciones cerradas</div>'
            '<div style="overflow-x:auto"><table class="rtab"><tr>'
            '<th>Cierre</th><th>Par</th><th>Entrada</th><th>Stop</th><th>Target</th>'
            '<th>Resultado</th><th>Salida</th><th>Origen</th>'
            '</tr>' + ''.join(filas_c) + '</table></div>')

    errores = j.get('errores') or []
    err_html = ''
    if errores:
        det = ' · '.join(f'{_e(x.get("par"))}: {_e(x.get("error"))}' for x in errores)
        err_html = f'<div class="nota">sin datos de {det}</div>'

    nota_fwd = (f'Forward: {g["forward_n"]} operación(es) nueva(s) desde el alta '
                f'({desde}) · replay: señales de las últimas 1000 velas 4h.')
    if g['forward_n'] == 0:
        nota_fwd = (f'Forward: todavía no hay señales nuevas desde el alta ({desde}) · '
                    'el replay son las señales de las últimas 1000 velas 4h.')

    return (
        '<div class="mon">'
        f'<div class="mt">TRACKER PAPER · {len(pares)} PARES · {g["n"]} OPERACIONES</div>'
        f'<div class="head">{_e(regla)} · 4h · actualizado {generado} · PAPER ONLY</div>'
        f'<div class="kv">{kv_html}</div>'
        f'{tabla}'
        f'{abiertas_html}'
        f'{cerradas_html}'
        f'<div class="nota" style="margin-top:12px">{nota_fwd}</div>'
        f'<div class="nota">Riesgo 0,35% de $300 = {_money(RIESGO_USD)} por operación '
        '· 1R = $1,05 · sizing con stop fijo.</div>'
        f'{err_html}'
        '<div class="nota">PAPER ONLY: el tracker registra y compara contra el '
        'backtest; no ejecuta órdenes.</div>'
        '</div>')


if __name__ == '__main__':
    print(html())
