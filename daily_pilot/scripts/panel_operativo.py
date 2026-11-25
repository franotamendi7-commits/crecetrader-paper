#!/usr/bin/env python3
"""Panel OPERATIVO: entradas activas y último estado de los trackers."""
from __future__ import annotations
import html as _h
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
D = BASE / 'daily_pilot' / 'datos'
CSS = '''
.op{border-radius:14px;padding:18px 20px;border:1px solid var(--bd);
background:var(--card);margin-bottom:26px}
.op .mt{font-size:11px;text-transform:uppercase;letter-spacing:1px;color:var(--ok);margin-bottom:12px}
.op .row{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:9px}
.op .c{border:1px solid var(--bd);border-radius:9px;padding:10px 12px;background:rgba(255,255,255,.02)}
.op .c span{display:block;color:var(--muted);font-size:10px;text-transform:uppercase;letter-spacing:.5px}
.op .c b{font-size:15px;font-variant-numeric:tabular-nums}
.op .live{margin-top:12px;font-size:12px;color:var(--muted);line-height:1.6}
.op .live b{color:var(--ok)}
'''


def _e(x):
    return _h.escape(str(x or ''))


def _j(name):
    p = D / name
    try:
        return json.loads(p.read_text()) if p.exists() else {}
    except Exception:
        return {}


def html() -> str:
    si = _j('tracker_scalein.json')
    pp = _j('tracker_paper.json')
    rs = si.get('resumen') or {}
    rp = pp.get('resumen') or {}
    cs = si.get('config') or {}
    pares = cs.get('pares') or []
    return (
        f'<div class="op"><div class="mt">Panel operativo · PAPER TRADING</div>'
        f'<div class="row">'
        f'<div class="c"><span>Scale-in · pares</span><b>{len(pares)}</b></div>'
        f'<div class="c"><span>Scale-in · señales</span><b>{_e(rs.get("n", 0))}</b></div>'
        f'<div class="c"><span>Scale-in · acierto</span><b>{_e(rs.get("win", 0))}%</b></div>'
        f'<div class="c"><span>Scale-in · resultado</span><b>${_e(rs.get("total_usd", 0))}</b></div>'
        f'<div class="c"><span>Scale-in · DD</span><b>${_e(rs.get("dd_usd", 0))}</b></div>'
        f'<div class="c"><span>Riesgo</span><b>{_e(cs.get("riesgo_pct", 2))}%</b></div>'
        f'<div class="c"><span>Forward scale-in</span><b>{_e(rs.get("forward_n", 0))}</b></div>'
        f'<div class="c"><span>Forward pullback</span><b>{_e(rp.get("forward_n", 0))}</b></div>'
        f'</div>'
        f'<div class="live">Entradas: <b>{_e(", ".join(p.replace("USDT","") for p in pares))}</b>'
        f' · stop fijo + scale-in en Fibo 0.5/0.618 · filtro R≥4% · riesgo {_e(cs.get("riesgo_pct",2))}%'
        f'<br>FORWARD EN CURSO — los trackers corren cada 4h y registran señales nuevas. '
        f'Las señales de hoy se ven en el detalle de cada par.</div></div>')
