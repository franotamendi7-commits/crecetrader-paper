#!/usr/bin/env python3
"""Dashboard v5 — panel con MERCADO REAL (Binance read-only) + el ultimo video.

Cambios vs v4:
  · precio REAL de varios pares (klines publicas de Binance, cache 5 min)
  · grafico de VELAS REALES (nada inventado)
  · tramo del ciclo y niveles calculados por TF (C05, C05-B)
  · el ultimo video analizado con sus niveles dichos

Autocontenido (sin fetch). PAPER_ONLY: muestra, no ejecuta.
"""
from __future__ import annotations

import html
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
PILOT = BASE / 'daily_pilot'
sys.path.insert(0, str(PILOT / 'core'))
SALIDA = PILOT / 'dashboard' / 'index.html'

PARES = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'XRPUSDT', 'SOLUSDT', 'ADAUSDT']
PLAZOS = (('1w', 'largo', '1S'), ('1d', 'media', '1D'), ('4h', 'corto', '4H'))


def cargar(ruta):
    p = Path(ruta)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text())
    except Exception:
        return None


def esc(s):
    return html.escape(str(s or ''))


def decimales(precio) -> int:
    """Decimales seguan la magnitud: que se lea bien en todos los pares."""
    p = abs(float(precio))
    if p >= 1000:
        return 0
    if p >= 100:
        return 2
    if p >= 1:
        return 2
    if p >= 0.1:
        return 4
    return 5


def fmt(x, dec=None):
    try:
        v = float(x)
        d = dec if dec is not None else decimales(v)
        return f'{v:,.{d}f}'.replace(',', '.')
    except Exception:
        return str(x)


def f(v):
    """Formato corto (max/min), con los decimales que correspondan."""
    return fmt(v)


# ---------------------------------------------------------------- datos reales
def mercado() -> list:
    """Precio real y cambio 24h de cada par. Cache de 5 min en velas.py."""
    from velas import velas
    filas = []
    for par in PARES:
        r = velas(par, '1d', limite=3)
        if 'error' in r or len(r['velas']) < 2:
            filas.append({'par': par.replace('USDT', ''), 'error': r.get('error', 'sin datos')})
            continue
        v = r['velas'][-1]
        prev = r['velas'][-2]
        cambio = (v['close'] - prev['close']) / prev['close'] * 100 if prev['close'] else 0.0
        filas.append({'par': par.replace('USDT', ''), 'precio': v['close'],
                      'cambio': round(cambio, 2), 'high': v['high'], 'low': v['low'],
                      'fuente': r['fuente']})
    return filas


def ciclo() -> list:
    """Tramo del ciclo + niveles por TF (C05 + C05-B)."""
    from velas import velas
    from tramos import tramo_ciclo
    from zonas import zonas
    out = []
    for tf, plazo, etiqueta in PLAZOS:
        r = velas('BTCUSDT', tf, limite=500)
        if 'error' in r:
            out.append({'tf': etiqueta, 'error': r['error']})
            continue
        t = tramo_ciclo(r['velas'])
        if 'error' in t:
            out.append({'tf': etiqueta, 'error': t['error']})
            continue
        z = zonas(t['minimo'], t['maximo'], plazo=plazo)
        out.append({'tf': etiqueta, 'min': round(t['minimo'], 2), 'max': round(t['maximo'], 2),
                    'retrocesos': {k: round(v, 2) for k, v in z['zonas_compra'].items()},
                    'extensiones': {k: round(v, 2) for k, v in z['extensiones'].items()},
                    'fuente': r['fuente']})
    return out


def grafico_velas(par='BTCUSDT', tf='1d', n=60) -> dict:
    """Velas reales para el grafico (nada inventado)."""
    from velas import velas
    r = velas(par, tf, limite=n)
    if 'error' in r:
        return {'error': r['error']}
    v = r['velas'][-n:]
    return {'par': par, 'tf': tf, 'velas': [
        {'o': x['open'], 'h': x['high'], 'l': x['low'], 'c': x['close']} for x in v],
        'fuente': r['fuente']}


# --------------------------------------------------------------------- HTML
CSS = '''
:root{--bg:#0d1117;--card:#161b22;--bd:#30363d;--fg:#e6edf3;--muted:#8b949e;--acc:#58a6ff;--ok:#3fb950;--warn:#d29922;--bad:#f85149}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:14px/1.45 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}
.wrap{max-width:1180px;margin:0 auto;padding:18px}
header{display:flex;justify-content:space-between;align-items:center;margin-bottom:14px}
h1{font-size:19px;margin:0}
.sub{color:var(--muted);font-size:12px}
.pill-only{color:var(--ok);border:1px solid var(--ok);border-radius:20px;padding:4px 12px;font-size:12px;font-weight:600}
.feed{color:var(--muted);font-size:11px;margin-top:3px}
.grid{display:grid;gap:12px}
.g2{grid-template-columns:repeat(auto-fit,minmax(340px,1fr))}
.g3{grid-template-columns:repeat(auto-fit,minmax(250px,1fr))}
.card{background:var(--card);border:1px solid var(--bd);border-radius:10px;padding:13px}
.card h3{margin:0 0 10px;font-size:13px;color:var(--muted);font-weight:600;letter-spacing:.3px}
table{width:100%;border-collapse:collapse;font-variant-numeric:tabular-nums}
th,td{text-align:left;padding:4px 6px;font-size:13px;border-bottom:1px solid #ffffff0d}
th{color:var(--muted);font-weight:500;font-size:11px}
td.num{text-align:right}
.up{color:var(--ok)} .down{color:var(--bad)}
.ciclo-bloque{border-bottom:1px solid #ffffff10;padding:8px 0}
.ciclo-t{font-weight:600;font-size:13px;margin-bottom:4px}
.ciclo-l{font-size:12px;color:var(--muted);font-variant-numeric:tabular-nums}
.ciclo-l b{color:var(--fg);font-weight:600}
.nota{color:var(--muted);font-size:11px;margin-top:6px}
.fuente{color:var(--muted);font-size:11px}
.pill{display:inline-block;background:#21262d;border:1px solid var(--bd);border-radius:12px;padding:1px 8px;font-size:12px;font-variant-numeric:tabular-nums}
'''


def panel_mercado(filas):
    filas_html = ''
    for x in filas:
        if 'error' in x:
            filas_html += f'<tr><td>{esc(x["par"])}</td><td class="num fuente">{esc(x["error"][:22])}</td><td></td></tr>'
            continue
        cls = 'up' if x['cambio'] >= 0 else 'down'
        signo = '+' if x['cambio'] >= 0 else ''
        filas_html += (f'<tr><td><b>{esc(x["par"])}</b></td>'
                       f'<td class="num">{fmt(x["precio"])}</td>'
                       f'<td class="num {cls}">{signo}{x["cambio"]:.2f}%</td>'
                       f'<td class="num fuente">{f(x["high"])} / {f(x["low"])}</td></tr>')
    fuentes = sorted({x.get('fuente', '') for x in filas})
    return (f'<div class="card"><h3>MERCADO REAL · Binance (solo lectura)</h3>'
            f'<table><tr><th>par</th><th style="text-align:right">precio</th>'
            f'<th style="text-align:right">24h</th><th style="text-align:right">max/min</th></tr>'
            f'{filas_html}</table>'
            f'<div class="nota">fuente: {esc(", ".join(x for x in fuentes if x))} · '
            f'<b>no es un feed en vivo</b>: cache de 5 minutos. PAPER ONLY.</div></div>')


def panel_ciclo(ciclo_datos):
    bloques = ''
    for c in ciclo_datos:
        if 'error' in c:
            bloques += f'<div class="ciclo-bloque"><div class="ciclo-t">{esc(c["tf"])}</div><div class="ciclo-l">sin datos</div></div>'
            continue
        retro = ' · '.join(f'{k}: <b>{fmt(v)}</b>' for k, v in c['retrocesos'].items())
        ext = ' · '.join(f'{k}: <b>{fmt(v)}</b>' for k, v in list(c['extensiones'].items())[:4])
        bloques += (f'<div class="ciclo-bloque"><div class="ciclo-t">{esc(c["tf"])}</div>'
                    f'<div class="ciclo-l">tramo <b>{fmt(c["min"])}</b> → <b>{fmt(c["max"])}</b> · {esc(c["fuente"])}</div>'
                    f'<div class="ciclo-l">{retro}</div>'
                    f'<div class="ciclo-l">ext {ext}</div></div>')
    return (f'<div class="card"><h3>CICLO BTC · tramo y niveles (C05 / C05-B)</h3>{bloques}'
            f'<div class="nota">0 = mínimo, 1 = máximo · retrocesos 0,382/0,5/0,61/0,786 · '
            f'extensiones por encima. Cada TF tiene su swing.</div></div>')


def panel_video(info):
    if not info:
        return '<div class="card"><h3>ULTIMO VIDEO</h3><div class="nota">sin datos</div></div>'
    vid = esc(info.get('video_id') or '—')
    pub = esc(str(info.get('publicado') or '')[:10])
    titulo = esc(info.get('titulo') or '')
    proc = esc(info.get('precio_procedencia') or '')
    ref = info.get('precio_referencia')
    niveles = info.get('niveles') or info.get('niveles_clave') or []
    lista = ''
    for n in niveles[:8]:
        lista += f'<div><span class="pill">{esc(n.get("precio", n))}</span> <span class="fuente">{esc(n.get("veces", ""))}</span></div>'
    sin_niveles = '<span class="fuente">sin niveles</span>'
    return (f'<div class="card"><h3>ULTIMO VIDEO · {vid}</h3>'
            f'<div style="font-size:13px;margin-bottom:6px">{titulo}</div>'
            f'<div class="fuente">{pub}</div>'
            f'<div class="ciclo-l" style="margin-top:8px">precio citado: <b>{f(ref) if ref else "—"}</b> '
            f'<span class="fuente">({proc}) · precio del video, no feed</span></div>'
            f'<div style="margin-top:8px">{lista or sin_niveles}</div></div>')


def panel_grafico(datos):
    if 'error' in datos:
        return f'<div class="card"><h3>VELAS REALES</h3><div class="nota">sin datos: {esc(datos["error"])}</div></div>'
    v = datos['velas']
    mn = min(x['l'] for x in v)
    mx = max(x['h'] for x in v)
    span = (mx - mn) or 1
    W, Hh = 900, 190
    paso = W / len(v)
    cuerpo = ''
    for i, x in enumerate(v):
        o, c = x['o'], x['c']
        y_o = Hh - (o - mn) / span * Hh
        y_c = Hh - (c - mn) / span * Hh
        color = '#3fb950' if c >= o else '#f85149'
        x0 = i * paso + paso * 0.15
        ancho = max(1.5, paso * 0.7)
        cuerpo += f'<line x1="{x0 + ancho/2:.1f}" y1="{Hh - (x["h"] - mn)/span*Hh:.1f}" x2="{x0 + ancho/2:.1f}" y2="{Hh - (x["l"] - mn)/span*Hh:.1f}" stroke="{color}" stroke-width="1"/>'
        cuerpo += f'<rect x="{x0:.1f}" y="{min(y_o, y_c):.1f}" width="{ancho:.1f}" height="{max(1, abs(y_c - y_o)):.1f}" fill="{color}"/>'
    return (f'<div class="card"><h3>VELAS REALES · {esc(datos["par"])} {esc(datos["tf"])} '
            f'<span class="fuente">({esc(datos["fuente"])})</span></h3>'
            f'<svg viewBox="0 0 {W} {Hh}" style="width:100%;height:auto" '
            f'preserveAspectRatio="none">{cuerpo}</svg>'
            f'<div class="nota">{len(v)} velas reales de Binance · mínimo {fmt(mn)} · máximo {fmt(mx)} · '
            f'<b>no es una simulación</b></div></div>')


def main() -> int:
    info = cargar(PILOT / 'datos' / 'informe_hoy.json') or {}
    mer = mercado()
    cic = ciclo()
    graf = grafico_velas()

    doc = f'''<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>YouTubeTradingAgent · mercado real</title><style>{CSS}</style></head>
<body><div class="wrap">
<header>
  <div><h1>YouTubeTradingAgent</h1><div class="sub">Mercado real · ciclo · último video</div></div>
  <div class="pill-only">● PAPER ONLY</div>
</header>

<div class="grid g2">
  {panel_mercado(mer)}
  {panel_ciclo(cic)}
</div>

<div class="grid" style="margin-top:12px">
  {panel_grafico(graf)}
</div>

<div class="grid g2" style="margin-top:12px">
  {panel_video(info)}
  <div class="card"><h3>QUE ES ESTO</h3>
    <div class="nota" style="font-size:12px;line-height:1.6">
    · Los precios y las velas son <b>reales</b> (Binance, solo lectura).<br>
    · Los niveles salen del <b>tramo del ciclo</b> de cada TF (C05/C05-B).<br>
    · El precio citado en el video está <b>etiquetado como del video</b>.<br>
    · <b>PAPER ONLY</b>: nada de esto ejecuta órdenes.<br>
    · El método C01–C12 está firmado en <span class="fuente">metodo/FIRMA_C01_C12.md</span>.
    </div></div>
</div>
</div></body></html>'''

    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(doc)
    print(f'-> {SALIDA} ({len(doc)} B)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
