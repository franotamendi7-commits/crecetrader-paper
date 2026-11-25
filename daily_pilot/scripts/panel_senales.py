#!/usr/bin/env python3
"""Panel CARTERA MIXTA para el dashboard v6.

Lee daily_pilot/datos/cartera_mixta.json y muestra la cartera de 6 pares
con las dos estrategias (pullback + reversion), null corregido y
walk-forward. PAPER_ONLY: muestra, no ejecuta.
"""
from __future__ import annotations

import html as _h
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
CARTERA = BASE / 'daily_pilot' / 'datos' / 'cartera_mixta.json'

CSS_EXTRA = '''
.mon{border-radius:14px;padding:18px 20px;border:1px solid var(--bd);
background:var(--card);margin-bottom:26px}
.mon .mt{font-size:11px;text-transform:uppercase;letter-spacing:1px;color:var(--acc);margin-bottom:12px}
.mon .estado{display:inline-block;padding:5px 11px;border-radius:8px;font-size:11px;font-weight:800;
letter-spacing:.4px}
.mon .abierta{background:rgba(62,207,122,.14);border:1px solid rgba(62,207,122,.45);color:var(--ok)}
.mon .cerrada{background:rgba(255,107,99,.10);border:1px solid rgba(255,107,99,.4);color:var(--bad)}
.mon .sin{background:rgba(127,142,163,.10);border:1px solid rgba(127,142,163,.4);color:var(--muted)}
.mon .fila{border:1px solid var(--bd);border-radius:11px;padding:14px 15px;margin-bottom:9px;
background:rgba(255,255,255,.02)}
.mon .fila .top{display:flex;align-items:center;gap:12px;flex-wrap:wrap}
.mon .fila .nom{font-size:16px;font-weight:800}
.mon .fila .precio{margin-left:auto;font-variant-numeric:tabular-nums;font-weight:700}
.mon .kv{display:grid;grid-template-columns:repeat(auto-fit,minmax(115px,1fr));gap:9px;margin-top:12px}
.mon .kv div{background:rgba(255,255,255,.03);border-radius:8px;padding:8px 10px}
.mon .kv span{display:block;color:var(--muted);font-size:10px;text-transform:uppercase;letter-spacing:.5px}
.mon .kv b{font-size:14px;font-variant-numeric:tabular-nums}
.mon .nota{color:var(--muted);font-size:11px;margin-top:10px;line-height:1.5}
.mon .head{color:var(--muted);font-size:11px;margin-bottom:12px}
'''


def _e(s):
    return _h.escape(str(s or ''))


def _n(x, dec=2, signo=False):
    """Numero con coma decimal; negativo con signo menos tipografico."""
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


_ESTADOS = {
    'VALIDADA': ('VALIDADA', 'abierta'),
    'CON RESERVA': ('CON RESERVA', 'sin'),
    'VALIDADA CON RESERVA': ('CON RESERVA', 'sin'),
    'DÉBIL': ('DÉBIL', 'cerrada'),
    'DEBIL': ('DÉBIL', 'cerrada'),
}

_ESTRATEGIAS = {
    'pullback': 'Pullback',
    'reversion': 'Reversión',
}


def _fmt_mejora(txt: str) -> str:
    """Formatea la mejora del JSON: menos tipografico, coma decimal y flechas."""
    t = str(txt or '')
    t = re.sub(r'-(\d+(?:\.\d+)?)', lambda m: '−' + m.group(1).replace('.', ','), t)
    t = t.replace('DD de ', 'DD bajó de ', 1)
    t = t.replace('2018 de ', '2018: ', 1)
    t = t.replace('2025 de ', '2025: ', 1)
    partes = t.split('. ')
    for i in range(1, len(partes)):
        partes[i] = re.sub(r'(\dR) a (−?\d)', r'\1 → \2', partes[i])
    return '. '.join(partes)


def _vacio(msg: str = 'sin datos de la cartera mixta') -> str:
    return ('<div class="mon"><div class="mt">CARTERA MIXTA</div>'
            f'<div class="nota">{_e(msg)}</div></div>')


def html() -> str:
    if not CARTERA.exists():
        return _vacio()
    try:
        d = json.loads(CARTERA.read_text(encoding='utf-8'))
    except Exception:
        return _vacio('cartera mixta ilegible')

    cartera = d.get('cartera') or {}
    pares = d.get('pares') or []
    estrategias = {e.get('clave'): e for e in d.get('estrategias') or []}

    filas = []
    for p in pares:
        label, cls = _ESTADOS.get(p.get('estado'), (p.get('estado') or '—', 'sin'))
        est = _ESTRATEGIAS.get(p.get('estrategia'), p.get('estrategia') or '—')
        if p.get('null_p') is not None:
            null_txt = f'p {_n(p.get("null_p"), 3)} · {_e(p.get("seeds"))}'
        else:
            null_txt = f'{_e(p.get("null_seeds"))} seeds'
        if p.get('wf_train') is not None:
            wf_txt = (f'{_n(p.get("wf_train"), 3, True)} → '
                      f'{_n(p.get("wf_test"), 3, True)}')
        else:
            wf_txt = _n(p.get('wf_test'), 3, True)
        filas.append(
            '<tr>'
            f'<td><b>{_e(p.get("par"))}</b></td>'
            f'<td>{_e(est)}</td>'
            f'<td>{_n(p.get("por_mes"), 1)}</td>'
            f'<td>{_n(p.get("E_R"), 3, True)}R</td>'
            f'<td>{_n(p.get("acierto_pct"), 1)}%</td>'
            f'<td>{_n(p.get("dd_R"), 1)}R</td>'
            f'<td>{_n(p.get("pf"), 2)}</td>'
            f'<td>{null_txt}</td>'
            f'<td>{wf_txt}</td>'
            f'<td><span class="estado {cls}">{_e(label)}</span></td>'
            '</tr>')

    reversion = [p for p in pares if p.get('estrategia') == 'reversion'
                 and p.get('wf_train') is not None and p.get('wf_test') is not None]
    nota_wf = ''
    if reversion:
        det = ' y '.join(
            f'{_n(p.get("wf_train"), 3, True)} → {_n(p.get("wf_test"), 3, True)}'
            for p in reversion)
        nombres = ' y '.join(_e((p.get('par') or '').replace('USDT', '')) for p in reversion)
        nota_wf = (f'<div class="nota">{nombres} · walk-forward mejora: '
                   f'{det}.</div>')

    nombre_ests = ' + '.join(_e(e.get('nombre')) for e in estrategias.values()
                             if e.get('nombre'))
    capital = _n(cartera.get('capital'), 0)
    riesgo_pct = _n(cartera.get('riesgo_por_operacion_pct'), 2)
    riesgo_usd = _n(cartera.get('riesgo_usd'), 2)

    return (
        '<div class="mon">'
        f'<div class="mt">CARTERA MIXTA · {len(pares)} PARES · '
        f'{_n(cartera.get("senales_por_mes"), 1)} señales/mes</div>'
        f'<div class="head">{nombre_ests} · actualizado {_e(d.get("generado"))} · '
        f'{_e(d.get("aviso"))}</div>'
        '<div class="kv">'
        f'<div><span>E</span><b>{_n(cartera.get("esperanza_R"), 3, True)}R</b></div>'
        f'<div><span>Acierto</span><b>{_n(cartera.get("acierto_pct"), 1)}%</b></div>'
        f'<div><span>PF</span><b>{_n(cartera.get("pf"), 2)}</b></div>'
        f'<div><span>DD</span><b>{_n(cartera.get("dd_R"), 1)}R</b></div>'
        '</div>'
        f'<div class="nota">Riesgo {riesgo_pct}% de ${capital} = ${riesgo_usd} '
        'por operación.</div>'
        f'<div class="nota">{_e(_fmt_mejora(cartera.get("mejora")))}</div>'
        '<div style="overflow-x:auto"><table class="rtab"><tr>'
        '<th>Par</th><th>Estrategia</th><th>Señales/mes</th><th>E(R)</th>'
        '<th>Acierto</th><th>DD</th><th>PF</th><th>Null</th><th>WF</th>'
        '<th>Estado</th>'
        '</tr>' + ''.join(filas) + '</table></div>'
        f'{nota_wf}'
        '<div class="nota">PAPER ONLY: cartera de investigación; no ejecuta órdenes.</div>'
        '</div>')
