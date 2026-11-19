#!/usr/bin/env python3
"""Dashboard v4 — cockpit de trading (PAPER_ONLY).

Layout tipo cockpit, con los datos REALES del ultimo video:
  cabecera PAPER ONLY + fila de tickets + chart SVG de niveles
  + plan de trading + niveles clave + risk manager + decision/fundamental.

Autocontenido (sin fetch). Honesto: el precio es el del video, no un feed.
"""
from __future__ import annotations

import html
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
PILOT = BASE / 'daily_pilot'
sys.path.insert(0, str(PILOT / 'core'))
SALIDA = PILOT / 'dashboard' / 'index.html'


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


def fmt(x):
    return f'{int(x):,}'.replace(',', '.')


def tickets(info, estado):
    """PASO 1: solo BTC. Los demas pares no entran (sin feed real)."""
    ref = info.get('precio_referencia') or 0
    val = f'<span class="t-v">{fmt(ref)}</span>' if ref else '<span class="t-v sinfeed">sin precio</span>'
    return (f'<div class="tick activo"><span class="t-k">BTC</span>{val}</div>'
            f'<div class="tick off"><span class="t-k">mas pares</span>'
            f'<span class="t-v sinfeed">sin feed aun</span></div>')


def zonas_panel(info):
    """Zonas calculadas (C05) POR PLAZO, con el rango usado explicito."""
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import zonas_reales as ZR
        r = ZR.calcular('BTC')
        filas = ('<div class="muted">Zonas por plazo: NO DISPONIBLE. Solo el 15,3% de los '
                 'niveles del corpus dice el timeframe (ver LIMITES_CORPUS.md).</div>')
        for plazo in ():
            z = (r['plazos'] or {}).get(plazo) or {}
            if 'error' in z:
                filas += f'<div class="fila"><span>{plazo}</span><b class="rojo">sin datos</b></div>'
                continue
            compra = ' · '.join(f'{k} {v:,.0f}'.replace(',', '.') for k, v in z['zonas_compra'].items())
            ext = ' · '.join(f'{k} {v:,.0f}'.replace(',', '.') for k, v in z['extensiones'].items())
            filas += (f'<div class="zona-bloque"><div class="zona-t"><b>{plazo.upper()}</b> · {z["tf"]} · '
                      f'rango dicho {z["minimo"]:,.0f}–{z["maximo"]:,.0f} ({z["n_videos"]} videos)</div>'
                      f'<div class="zona-l">compra: {compra}</div>'
                      f'<div class="zona-l">extensiones: {ext}</div></div>')
        return (f'<div class="zona-nota">Calculadas (C05) sobre el rango que el canal mencionó. '
                f'Sin feed: el rango es lo DICHO, no el mercado real.</div>{filas}')
    except Exception as e:
        return f'<div class="muted">zonas no disponibles: {e}</div>'

def plan(info):
    e = (info.get('escenarios') or [{}])[0].get('escenario') or {}
    niv = e.get('nivel') or {}
    ref = info.get('precio_referencia') or 0
    ent = niv.get('valor') or 0
    pct = f'{(ent-ref)/ref*100:+.1f}%' if ref and ent else ''
    return f'''<div class="panel">
      <div class="panel-h">NIVELES MENCIONADOS (no es un plan)</div>
      <div class="fila"><span>nivel citado</span><b>{fmt(ent) if ent else "—"}</b><span class="pct">{pct}</span></div>
      <div class="alerta">⚠ NO ES UNA ORDEN — el nivel salio de la transcripcion.
      La decision la toma el trader.</div>
      <div class="nota">{esc(e.get('justificacion') or '')[:150]}</div>
      <div class="nota leyenda">C05 = retrocesos/extensiones fibo · C08 = invalidacion ·
      C02 = 30% oferta / 70% confirmacion. Paper only, sin feed.</div>
    </div>'''


def niveles(info):
    filas = ''
    ref = info.get('precio_referencia') or 0
    for n in sorted(info.get('niveles_top') or [], key=lambda x: -x['precio'])[:8]:
        p = n['precio']
        pct = f'{(p-ref)/ref*100:+.1f}%' if ref else ''
        filas += (f'<div class="fila"><span class="pill">{fmt(p)}</span>'
                  f'<span class="pct">{pct}</span>'
                  f'<span class="muted">x{n["menciones"]}</span></div>')
    return f'<div class="panel"><div class="panel-h">NIVELES CLAVE</div>{filas or "—"}</div>'


def risk(info):
    try:
        import allocacion as A
        p = A.plan('BTCUSD', 1000.0, en_oferta=True)
        tramos = ' · '.join(f"{int(t['porcentaje']*100)}%" for t in p['tramos'])
        return f'''<div class="panel"><div class="panel-h">RISK MANAGER</div>
      <div class="fila"><span>capital operable</span><b>${p['capital_operable']:.0f}</b></div>
      <div class="fila"><span>tope activo</span><b>${p['allocacion_maxima_monto']:.0f} ({int(p['allocacion_maxima']*100)}%)</b></div>
      <div class="fila"><span>tramos</span><b>{tramos}</b></div>
      <div class="nota">C02: 30% oferta + 70% confirmacion (2x35%). Paper only.</div>
    </div>'''
    except Exception as e:
        return f'<div class="panel"><div class="panel-h">RISK MANAGER</div><div class="muted">no disponible</div></div>'


def decision(info, estado):
    esc_ = (info.get('escenarios') or [{}])[0].get('escenario') or {}
    return f'''<div class="panel"><div class="panel-h">LECTURA DEL DÍA</div>
      <div class="verdict">LO QUE DICE EL CANAL</div>
      <div class="nota">{esc(esc_.get('justificacion') or '')[:130]}</div>
      <div class="nota">El metodo (C01-C12) y la decision son del trader. Paper only.</div>
    </div>'''


def fundamental(info):
    return '''<div class="panel"><div class="panel-h">FUNDAMENTAL</div>
      <div class="nota">NO DISPONIBLE: el corpus no tiene feed fundamental.
      Lo que el canal diga aparece en la transcripción.</div></div>'''


def sentimiento(info):
    return '''<div class="panel"><div class="panel-h">SENTIMIENTO</div>
      <div class="nota">NO DISPONIBLE: sin feed de Fear&Greed / VIX.
      No se inventa.</div></div>'''


def distribucion(info, capital=1000.0):
    """C02: capital operable + topes por activo (barras), SIN inventar asignacion."""
    try:
        import allocacion as A
        filas = ''
        for inst in ('BTCUSD', 'ETHUSD', 'QQQ', 'XAUUSD'):
            plan = A.plan(inst, capital, en_oferta=True)
            tope = plan['allocacion_maxima']
            operable = min(capital, plan['allocacion_maxima_monto'])
            ancho = int(tope * 100)
            filas += (f'<div class="barra-fila"><div class="barra-label"><span>{inst}</span>'
                      f'<b>{ancho}% · ${operable:.0f}</b></div>'
                      f'<div class="barra"><i style="width:{ancho}%"></i></div></div>')
        return (f'<div class="panel"><div class="panel-h">DISTRIBUCIÓN (C02)</div>{filas}'
                f'<div class="nota">Tope por activo sobre ${capital:.0f}. No es una orden: '
                f'es el máximo permitido. BTC 45%, ETH 20%, QQQ/XAU 10%.</div></div>')
    except Exception as e:
        return (f'<div class="panel"><div class="panel-h">DISTRIBUCIÓN</div>'
                f'<div class="muted">no disponible</div></div>')


CSS = '''
:root{--bg:#0b0f14;--card:#151b23;--fg:#e6edf3;--muted:#8b949e;--bd:#262d36;--acc:#8b5cf6;--ok:#3fb950;--rojo:#f85149;--ambar:#d29922}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:14px/1.45 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;padding:16px}
.wrap{max-width:1180px;margin:0 auto;display:grid;gap:12px}
header{display:flex;justify-content:space-between;align-items:center}
h1{font-size:18px;margin:0}
.sub{color:var(--muted);font-size:12px}
.pill-only{background:#0c2b16;border:1px solid var(--ok);color:var(--ok);border-radius:20px;padding:4px 12px;font-size:11px;letter-spacing:.06em}
.ticks{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px}
.tick{background:var(--card);border:1px solid var(--bd);border-radius:10px;padding:10px 12px;text-align:left;color:var(--fg);cursor:pointer}
.tick.activo{border-color:var(--acc)}
.t-k{display:block;color:var(--muted);font-size:11px;letter-spacing:.06em}
.t-v{display:block;font-size:17px;font-weight:600;margin-top:2px;font-variant-numeric:tabular-nums}
.grid-main{display:grid;grid-template-columns:1.7fr 1fr;gap:12px}
.grid-2{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.grid-4{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}
.card{background:var(--card);border:1px solid var(--bd);border-radius:10px;padding:12px 14px}
.panel{background:var(--card);border:1px solid var(--bd);border-radius:10px;padding:12px 14px}
.panel-h{font-size:11px;letter-spacing:.12em;color:var(--muted);text-transform:uppercase;margin-bottom:8px}
.tag{background:var(--acc);color:#fff;border-radius:4px;padding:2px 7px;font-size:10px;letter-spacing:.08em}
.fila{display:flex;gap:8px;align-items:baseline;padding:3px 0;border-bottom:1px solid #ffffff08;font-size:13px}
.fila span:first-child{color:var(--muted);min-width:96px}
.pill{background:#21262d;border:1px solid var(--bd);border-radius:14px;padding:2px 9px;font-variant-numeric:tabular-nums;font-size:12px}
.pct{color:var(--muted);font-size:12px}
.muted{color:var(--muted);font-size:11px}
.nota{color:var(--muted);font-size:12px;margin-top:8px}
.rojo{color:var(--rojo)}
.sinfeed{color:var(--muted);font-size:13px;font-weight:400}
.alerta{background:#2d1b0e;border:1px solid var(--ambar);color:var(--ambar);border-radius:6px;padding:6px 9px;font-size:12px;margin-top:8px}
.leyenda{border-top:1px solid #ffffff10;padding-top:6px;margin-top:10px}
.barra-fila{margin:6px 0}
.barra-label{display:flex;justify-content:space-between;font-size:12px;color:var(--muted);margin-bottom:3px}
.barra{height:7px;background:#21262d;border-radius:4px;overflow:hidden}
.barra i{display:block;height:100%;background:var(--acc);border-radius:4px}
.zona-bloque{border-bottom:1px solid #ffffff10;padding:8px 0}
.zona-t{font-size:13px;margin-bottom:3px}
.zona-l{font-size:12px;color:var(--muted);font-variant-numeric:tabular-nums}
.zona-nota{font-size:11px;color:var(--ambar);margin-bottom:8px}
.verdict{font-weight:600;padding:6px 10px;border-radius:6px;background:#0c2b16;color:var(--ok);display:inline-block}
.chart-head{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:6px}
'''


def main() -> int:
    info = cargar(PILOT / 'datos' / 'informe_hoy.json') or {}
    estado = cargar(PILOT / 'estado' / 'estado_hoy.json') or {}
    titulo = esc(info.get('titulo') or (estado.get('video') or {}).get('titulo') or 'sin datos')
    vid = esc(info.get('video_id') or '—')
    pub = esc((info.get('publicado') or '')[:10])
    ts = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%MZ')

    doc = f'''<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>YouTubeTradingAgent · {titulo[:40]}</title><style>{CSS}</style></head>
<body><div class="wrap">
<header>
  <div><h1>YouTubeTradingAgent</h1><div class="sub">Análisis · Señales · Gestión de Capital</div></div>
  <div class="pill-only">● PAPER ONLY</div>
</header>

<div class="ticks">{tickets(info, estado)}</div>

<div class="grid-main">
  <div class="card">
    <div class="chart-head"><b>ZONAS CALCULADAS · {vid}</b><span class="muted">video {pub} · {ts}</span></div>
    {zonas_panel(info)}
  </div>
  <div style="display:grid;gap:12px;align-content:start">
    {plan(info)}
    {risk(info)}
  </div>
</div>

<div class="grid-2">
  {niveles(info)}
  {decision(info, estado)}
</div>

<div class="grid-4">
  {fundamental(info)}
  {sentimiento(info)}
  {distribucion(info)}
  <div class="panel"><div class="panel-h">FUENTE</div>
    <div class="nota">video: {vid}<br>transcripción + claims + playbook C01–C12.<br>
    Sin feed en tiempo real.</div></div>
</div>
</div></body></html>'''

    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(doc)
    print(f'-> {SALIDA} ({len(doc)} B)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
