#!/usr/bin/env python3
"""Panel ESTRATEGIA VALIDADA para el dashboard v6.

Lee daily_pilot/datos/estrategias_validadas.json y muestra la cartera de
4 pares validada con null sintetico multi-seed y walk-forward 70/30.
PAPER_ONLY: muestra, no ejecuta.
"""
from __future__ import annotations

import html as _h
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
EST = BASE / 'daily_pilot' / 'datos' / 'estrategias_validadas.json'

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
    'VALIDADA CON RESERVA': ('CON RESERVA', 'sin'),
    'DEBIL': ('DÉBIL', 'cerrada'),
}


def html() -> str:
    if not EST.exists():
        return ('<div class="mon"><div class="mt">Estrategia validada</div>'
                '<div class="nota">sin datos</div></div>')
    try:
        d = json.loads(EST.read_text(encoding='utf-8'))
    except Exception:
        return '<div class="mon"><div class="nota">estrategias ilegibles</div></div>'

    regla = d.get('regla') or {}
    cartera = d.get('cartera') or {}
    pares = sorted(d.get('pares') or [],
                   key=lambda p: {'VALIDADA': 0,
                                  'VALIDADA CON RESERVA': 1}.get(p.get('estado'), 2))

    filas = []
    for p in pares:
        label, cls = _ESTADOS.get(p.get('estado'), (p.get('estado') or '—', 'sin'))
        filas.append(
            '<tr>'
            f'<td><b>{_e(p.get("par"))}</b></td>'
            f'<td>{_n(p.get("por_mes"), 1)}</td>'
            f'<td>{_n(p.get("esperanza_R"), 3, True)}</td>'
            f'<td>{_n(p.get("acierto_pct"), 1)}%</td>'
            f'<td>{_n(p.get("dd_R"), 1)}R</td>'
            f'<td>{_n(p.get("pf"), 2)}</td>'
            f'<td>{_n(p.get("null_p"), 3)}</td>'
            f'<td>{_e(p.get("null_seeds"))}</td>'
            f'<td>{_n(p.get("wf_test"), 3, True)}</td>'
            f'<td><span class="estado {cls}">{label}</span></td>'
            '</tr>')

    octu = cartera.get('octubre_2026') or {}

    return (
        '<div class="mon">'
        f'<div class="mt">ESTRATEGIA VALIDADA · {len(pares)} PARES · '
        f'{_n(cartera.get("por_mes"), 1)} señales/mes</div>'
        f'<div class="head">{_e(regla.get("nombre"))} · {_e(regla.get("timeframe"))} · '
        f'{_e(d.get("fuente"))} · actualizado {_e(d.get("generado"))}</div>'
        '<div class="kv">'
        f'<div><span>E</span><b>{_n(cartera.get("esperanza_R"), 3, True)}R</b></div>'
        f'<div><span>Acierto</span><b>{_n(cartera.get("acierto_pct"), 1)}%</b></div>'
        f'<div><span>PF</span><b>{_n(cartera.get("pf"), 2)}</b></div>'
        f'<div><span>DD</span><b>{_n(cartera.get("dd_R"), 1)}R</b></div>'
        '</div>'
        '<div style="overflow-x:auto"><table class="rtab"><tr>'
        '<th>Par</th><th>Señales/mes</th><th>E(R)</th><th>Acierto</th><th>DD</th>'
        '<th>PF</th><th>Null p</th><th>Seeds</th><th>WF test</th><th>Estado</th>'
        '</tr>' + ''.join(filas) + '</table></div>'
        f'<div class="nota">Octubre: cartera {_n(octu.get("cartera_R"), 2)}R vs BTC solo '
        f'{_n(octu.get("btc_solo_R"), 2)}R — la diversificación reduce el mes malo.</div>'
        f'<div class="nota">{_e(d.get("aviso"))}</div>'
        '</div>')
