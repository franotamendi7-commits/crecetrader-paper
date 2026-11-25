#!/usr/bin/env python3
"""Panel SEÑALES — activas a la izquierda, historial a la derecha.

Lee tracker_scalein.json y tracker_paper.json. Clasifica:
  · ACTIVAS  → estado ABIERTA / EN_BE / señal muy reciente (<= 48h)
  · CERRADAS → CERRADA_* con su resultado

PAPER_ONLY: muestra, no ejecuta.
"""
from __future__ import annotations
import html as _h
import datetime
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
D = BASE / 'daily_pilot' / 'datos'
CSS = '''
.sg{border-radius:14px;padding:18px 20px;border:1px solid var(--bd);
background:var(--card);margin-bottom:26px}
.sg .mt{font-size:11px;text-transform:uppercase;letter-spacing:1px;color:var(--warn);margin-bottom:12px}
.sg .cols{display:grid;grid-template-columns:1fr 1fr;gap:14px}
@media(max-width:800px){.sg .cols{grid-template-columns:1fr}}
.sg .col h3{font-size:11px;text-transform:uppercase;letter-spacing:.8px;
color:var(--muted);margin:0 0 10px;padding-bottom:8px;border-bottom:1px solid var(--bd)}
.sg .op{border:1px solid var(--bd);border-radius:9px;padding:10px 12px;margin-bottom:7px;
background:rgba(255,255,255,.02);font-size:12px}
.sg .op.activa{border-color:rgba(62,207,122,.45);background:rgba(62,207,122,.06)}
.sg .op .h{display:flex;justify-content:space-between;gap:8px;font-weight:700;margin-bottom:5px}
.sg .op .d{color:var(--muted);font-variant-numeric:tabular-nums;line-height:1.55}
.sg .op .r{font-weight:700}
.sg .ok{color:var(--ok)} .sg .bad{color:var(--bad)} .sg .neu{color:var(--muted)}
.sg .vacio{color:var(--muted);font-size:12px;padding:10px 0}
'''


def _e(x):
    return _h.escape(str(x or ''))


def _j(n):
    try:
        return json.loads((D / n).read_text()) if (D / n).exists() else {}
    except Exception:
        return {}


def _nums(x, d=2):
    try:
        return f'{float(x):,.{d}f}'
    except Exception:
        return '—'


def _clasificar():
    activas, cerradas = [], []
    for nombre, etiqueta in (('tracker_scalein.json', 'SCALE-IN'),
                             ('tracker_paper.json', 'PULLBACK')):
        j = _j(nombre)
        for o in j.get('operaciones') or []:
            estado = str(o.get('estado') or '')
            r = o.get('resultado_R')
            usd = o.get('resultado_usd')
            if usd is None and r is not None and o.get('riesgo_usd'):
                usd = float(r) * float(o['riesgo_usd'])
            item = {'par': (o.get('par') or '').replace('USDT', ''),
                    'estrategia': o.get('estrategia') or etiqueta.lower(),
                    'fecha': o.get('senal_fecha') or '',
                    'entrada': o.get('entrada') or o.get('stop_inicial'),
                    'stop': o.get('stop') or o.get('stop_inicial'),
                    'target': o.get('target'),
                    'estado': estado, 'R': r, 'usd': usd,
                    'origen': o.get('origen') or 'replay'}
            if estado.startswith('CERRADA'):
                item['cierre'] = o.get('cierre_fecha') or ''
                cerradas.append(item)
            else:
                activas.append(item)
    activas.sort(key=lambda x: x['fecha'], reverse=True)
    cerradas.sort(key=lambda x: x['fecha'], reverse=True)
    return activas, cerradas


def html() -> str:
    activas, cerradas = _clasificar()
    a = ''.join(
        f'<div class="op activa"><div class="h"><span>{_e(x["par"])} · {_e(x["estrategia"])}</span>'
        f'<span class="neu">{_e(x["estado"] or "ABIERTA")}</span></div>'
        f'<div class="d">{_e(x["fecha"])} · entry {_nums(x["entrada"])} · '
        f'stop {_nums(x["stop"])} · target {_nums(x["target"])}</div></div>'
        for x in activas[:12]) or '<div class="vacio">sin señales activas</div>'
    c = ''.join(
        f'<div class="op"><div class="h"><span>{_e(x["par"])} · {_e(x["estrategia"])}</span>'
        f'<span class="r {"ok" if (x["usd"] or 0)>0 else "bad"}">'
        f'{"+" if (x["usd"] or 0)>0 else ""}${_nums(x["usd"])}</span></div>'
        f'<div class="d">{_e(x["fecha"])} → {_e(x["cierre"])} · '
        f'R {_nums(x["R"], 3)} · {_e(x["estado"])}</div></div>'
        for x in cerradas[:12]) or '<div class="vacio">sin historial</div>'
    return (f'<div class="sg"><div class="mt">Señales · paper trading</div>'
            f'<div class="cols">'
            f'<div class="col"><h3>ACTIVAS ({len(activas)})</h3>{a}</div>'
            f'<div class="col"><h3>CERRADAS ({len(cerradas)})</h3>{c}</div>'
            f'</div></div>')
