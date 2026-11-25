#!/usr/bin/env python3
"""Panel MONITOR DE SEÑALES para el dashboard v6.

Lee daily_pilot/datos/monitor_senales.json y muestra el estado actual
de la estrategia validada en BTC y ETH.
PAPER_ONLY: muestra, no ejecuta.
"""
from __future__ import annotations

import html as _h
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
MON = BASE / 'daily_pilot' / 'datos' / 'monitor_senales.json'

CSS_EXTRA = '''
.mon{border-radius:14px;padding:18px 20px;border:1px solid var(--bd);
background:linear-gradient(180deg,var(--card),var(--bg2));margin-bottom:26px}
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


def _num(x, dec=2):
    try:
        return f"{float(x):,.{dec}f}"
    except Exception:
        return '—'


def html() -> str:
    if not MON.exists():
        return '<div class="mon"><div class="mt">Monitor de señales</div><div class="nota">sin datos</div></div>'
    try:
        d = json.loads(MON.read_text(encoding='utf-8'))
    except Exception:
        return '<div class="mon"><div class="nota">monitor ilegible</div></div>'

    filas = []
    for p in d.get('pares', []):
        estado = p.get('estado', '—')
        cls = ('abierta' if estado == 'ABIERTA'
               else 'sin' if estado == 'SIN SEÑAL' else 'cerrada')
        if p.get('error'):
            filas.append(f'<div class="fila"><div class="top"><span class="nom">{_e(p.get("par"))}</span>'
                         f'<span class="estado sin">SIN DATOS</span></div></div>')
            continue
        t = p.get('ticket', {})
        kv = ''
        if p.get('senal') or estado == 'ABIERTA':
            kv = (f'<div class="kv">'
                  f'<div><span>Entry</span><b>{_num(p.get("entry"))}</b></div>'
                  f'<div><span>Stop</span><b style="color:var(--bad)">{_num(p.get("stop"))}</b></div>'
                  f'<div><span>Target 3.0</span><b style="color:var(--ok)">{_num(p.get("target"))}</b></div>'
                  f'<div><span>Riesgo/unidad</span><b>{_num(p.get("riesgo_por_unidad"))}</b></div>'
                  f'<div><span>Riesgo</span><b>${_num(t.get("riesgo_usd"))}</b></div>'
                  f'<div><span>Unidades</span><b>{_num(t.get("unidades"), 4)}</b></div>'
                  f'<div><span>Margen 20x</span><b>${_num(t.get("margen_20x"))}</b></div>'
                  f'</div>')
        else:
            kv = (f'<div class="kv">'
                  f'<div><span>Ultima señal</span><b style="font-size:12px">{_e(p.get("fecha_senal", "—"))}</b></div>'
                  f'<div><span>Entry</span><b>{_num(p.get("entry"))}</b></div>'
                  f'<div><span>Stop</span><b style="color:var(--bad)">{_num(p.get("stop"))}</b></div>'
                  f'<div><span>Op. historicas</span><b>{_e(p.get("n_ops_historicas", "—"))}</b></div>'
                  f'</div>')
        filas.append(
            f'<div class="fila"><div class="top">'
            f'<span class="nom">{_e(p.get("par"))}</span>'
            f'<span class="estado {cls}">{_e(estado)}</span>'
            f'<span class="precio">{_num(p.get("precio_actual"))}</span>'
            f'</div>{kv}'
            f'<div class="nota">{_e(p.get("nota"))}</div></div>')

    return (f'<div class="mon"><div class="mt">Monitor de señales · estrategia validada</div>'
            f'<div class="head">{_e(d.get("estrategia"))} · {_e(d.get("validacion"))} · '
            f'actualizado {_e(d.get("generado"))}</div>'
            f'{"".join(filas)}'
            f'<div class="nota">{_e(d.get("aviso"))}</div></div>')
