#!/usr/bin/env python3
"""Dashboard SIMPLE del piloto (PAPER_ONLY).

Cuatro bloques, sin ruido:
  1. HOY      — video, niveles, que haria el motor
  2. POR QUE  — 3 razones con cita
  3. MERCADO  — por instrumento (pestania)
  4. SISTEMA  — estado, una linea

Autocontenido (sin fetch) para abrir con file://.
"""
from __future__ import annotations

import html
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
PILOT = BASE / 'daily_pilot'
SALIDA = PILOT / 'dashboard' / 'index.html'


def cargar(*rutas):
    for r in rutas:
        p = Path(r)
        if p.exists():
            try:
                return json.loads(p.read_text())
            except Exception:
                return None
    return None


def esc(s):
    return html.escape(str(s or ''))


def grafiquito(niveles, precio_ref):
    """Mini SVG: niveles como lineas + precio de referencia."""
    if not niveles:
        return ''
    vals = [n['precio'] for n in niveles] + ([precio_ref] if precio_ref else [])
    lo, hi = min(vals), max(vals)
    if hi <= lo:
        hi = lo + 1
    W, H, PAD = 960, 150, 8
    def y(v):
        return H - PAD - (v - lo) / (hi - lo) * (H - 2 * PAD)
    lineas = ''
    for n in niveles:
        yy = y(n['precio'])
        lineas += (f'<line x1="0" y1="{yy:.1f}" x2="{W}" y2="{yy:.1f}" stroke="#30363d" stroke-width="1"/>'
                   f'<text x="{W-4}" y="{yy-3:.1f}" fill="#8b949e" font-size="10" text-anchor="end">'
                   f'{int(n["precio"]):,}'.replace(',', '.') + '</text>')
    if precio_ref:
        yy = y(precio_ref)
        lineas += (f'<line x1="0" y1="{yy:.1f}" x2="{W}" y2="{yy:.1f}" stroke="#f85149" stroke-width="1.5" stroke-dasharray="4 3"/>'
                   f'<text x="4" y="{yy-4:.1f}" fill="#f85149" font-size="10">ref</text>')
    rango = f'{int(lo):,}'.replace(',', '.') + ' – ' + f'{int(hi):,}'.replace(',', '.')
    return (f'<div class="graf"><div class="muted">rango {rango}</div>'
            f'<svg viewBox="0 0 {W} {H}" preserveAspectRatio="none" style="width:100%;height:150px">'
            f'{lineas}</svg></div>')


def tarjeta_hoy(info, estado):
    titulo = esc(info.get('titulo') or (estado.get('video') or {}).get('titulo') or 'sin datos')
    vid = esc(info.get('video_id') or (estado.get('video') or {}).get('video_id') or '-')
    pub = esc((info.get('publicado') or '')[:10])
    niv = info.get('niveles_top') or []
    def fmt(x):
        return f'{int(x):,}'.replace(',', '.')
    # orden: de mayor a menor precio; porcentual: distancia al precio de referencia
    precio_ref = (info.get('precio_referencia') or 0)
    filas = sorted(niv, key=lambda n: -n['precio'])
    niveles = ''
    for n in filas[:6]:
        p = n['precio']
        pct = (f'{(p - precio_ref) / precio_ref * 100:+.1f}%' if precio_ref else '')
        niveles += (f'<div class="nivel"><span class="pill">{fmt(p)}</span>'
                    f'<span class="pct">{pct}</span></div>')
    if not niveles:
        niveles = '<span class="muted">sin niveles</span>'
    situ = esc((estado.get('situacion') or {}).get('frase') or '')
    return f'''
  <section class="card hero">
    <div class="hero-top">
      <div>
        <div class="kicker">HOY · {pub}</div>
        <h1>{titulo}</h1>
        <div class="muted">precio de referencia del video: {fmt(precio_ref) if precio_ref else 'NO_DISPONIBLE'}</div>
      </div>
      <div class="badge">PAPER ONLY<br><span>no ejecuta</span></div>
    </div>
    <div class="niveles-col">{niveles}</div>
    {grafiquito(filas[:8], precio_ref)}
    <div class="situ">{situ}</div>
  </section>'''


def tarjeta_porque(escenarios):
    items = []
    for e in (escenarios or [])[:3]:
        esc_ = e.get('escenario') or {}
        items.append(f'<li><b>{esc(esc_.get("instrumento","?"))}</b> {esc(esc_.get("direccion","?"))} · '
                     f'nivel <b>{esc((esc_.get("nivel") or {}).get("valor"))}</b> '
                     f'<span class="muted">[{esc(esc_.get("timestamp_explicacion",""))}]</span><br>'
                     f'{esc(esc_.get("justificacion") or "")}</li>')
    if not items:
        items.append('<li class="muted">sin escenarios</li>')
    return f'<section class="card"><h2>POR QUÉ</h2><ol class="razones">{"".join(items)}</ol></section>'


def tarjeta_mercado(mercado):
    def fmt(x):
        return f'{int(x):,}'.replace(',', '.')
    tabs, panels = [], []
    for i, (inst, m) in enumerate((mercado or {}).items()):
        activo = ' activo' if i == 0 else ''
        tabs.append(f'<button class="tab{activo}" data-i="{i}">{esc(inst)}</button>')
        pills = ''.join(f'<span class="pill">{fmt(x)}</span>' for x in (m.get('niveles_originales') or [])[:8])
        filas = ''.join(f'<tr><th>{esc(et)}</th><td>{esc(m.get(k))}</td></tr>'
                        for k, et in (('tendencia_weekly', 'Semanal'), ('contexto_diario', 'Diario'),
                                     ('estructura_4h', '4H')) if m.get(k))
        panels.append(f'<div class="panel{activo}" data-i="{i}">{pills}<table class="det">{filas}</table></div>')
    return f'<section class="card"><h2>MERCADO</h2><div class="tabs">{"".join(tabs)}</div>{"".join(panels)}</section>'


def tarjeta_sistema(estado, rm, met):
    est = esc(estado.get('estado') or 'SIN DATOS')
    rev = esc(estado.get('ultima_revision') or '')
    riesgo = rm.get('riesgo_pct_efectivo') if isinstance(rm, dict) else None
    m = f"{float(riesgo)*100:.2f}%" if riesgo is not None else 'NO DISPONIBLE'
    ex = met.get('expectativa_r') if isinstance(met, dict) else None
    met_txt = f"{ex}R" if ex else 'NO DISPONIBLE'
    return f'''<section class="card sys">
    <h2>SISTEMA</h2>
    <div class="sys-grid">
      <div><span class="k">Estado</span><b>{est}</b></div>
      <div><span class="k">Riesgo/operación</span><b>{m}</b></div>
      <div><span class="k">Expectativa</span><b>{met_txt}</b></div>
      <div><span class="k">Última revisión</span><b>{rev[:19].replace("T"," ")}</b></div>
    </div>
    <div class="muted">Expectativa teórica: aún no hay resultados reales.</div>
  </section>'''


CSS = '''
:root{--bg:#0d1117;--card:#161b22;--fg:#e6edf3;--muted:#8b949e;--bd:#30363d}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;padding:20px}
.wrap{max-width:1000px;margin:0 auto;display:grid;gap:14px}
.card{background:var(--card);border:1px solid var(--bd);border-radius:10px;padding:16px 18px}
.card h2{margin:0 0 10px;font-size:12px;letter-spacing:.12em;color:var(--muted);text-transform:uppercase}
.kicker{font-size:12px;letter-spacing:.12em;color:var(--muted);text-transform:uppercase}
h1{margin:4px 0 2px;font-size:21px;line-height:1.25}
.muted{color:var(--muted);font-size:12px}
.hero-top{display:flex;justify-content:space-between;gap:14px;align-items:flex-start}
.badge{background:#1f6feb22;border:1px solid #1f6feb;color:#58a6ff;border-radius:8px;padding:8px 12px;
       text-align:center;font-size:11px;letter-spacing:.06em;white-space:nowrap}
.badge span{color:var(--muted)}
.niveles-col{display:flex;flex-wrap:wrap;gap:6px 14px;margin:12px 0 8px;align-items:center}
.nivel{display:flex;align-items:baseline;gap:6px}
.pct{color:var(--muted);font-size:12px;font-variant-numeric:tabular-nums}
.graf{margin:10px 0 4px}
.pill{background:#21262d;border:1px solid var(--bd);border-radius:20px;padding:3px 10px;
      font-variant-numeric:tabular-nums;font-size:13px}
.situ{font-size:14px;margin-top:6px}
.razones{margin:0;padding-left:20px;display:grid;gap:8px}
.tabs{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:10px}
.tab{background:#21262d;border:1px solid var(--bd);color:var(--fg);border-radius:6px;padding:5px 12px;cursor:pointer;font-size:13px}
.tab.activo{background:#1f6feb;border-color:#1f6feb;color:#fff}
.panel{display:none}.panel.activo{display:block}
table.det{width:100%;border-collapse:collapse;margin-top:10px;font-size:13px}
table.det th{text-align:left;color:var(--muted);font-weight:500;width:90px;vertical-align:top;padding:3px 0}
.sys-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px}
.sys-grid .k{display:block;color:var(--muted);font-size:11px;letter-spacing:.06em;text-transform:uppercase}
.sys-grid b{font-size:15px}
'''

JS = '''document.querySelectorAll('.tab').forEach(function(t){
  t.addEventListener('click',function(){
    var i=t.getAttribute('data-i');
    document.querySelectorAll('.tab,.panel').forEach(function(x){x.classList.remove('activo');});
    t.classList.add('activo');
    document.querySelector('.panel[data-i="'+i+'"]').classList.add('activo');
  });
});'''


def main() -> int:
    info = cargar(PILOT / 'datos' / 'informe_hoy.json') or {}
    estado = cargar(PILOT / 'estado' / 'estado_hoy.json') or {}
    datos = cargar(PILOT / 'datos' / 'dashboard_data.json') or {}
    rm = cargar(PILOT / 'datos' / 'risk_hoy.json') or {}
    met = cargar(PILOT / 'datos' / 'metrics_hoy.json') or {}

    doc = f'''<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>CreceTrader · HOY</title><style>{CSS}</style></head>
<body><div class="wrap">
{tarjeta_hoy(info, estado)}
{tarjeta_porque(datos.get('escenarios'))}
{tarjeta_mercado(datos.get('mercado'))}
{tarjeta_sistema(estado, rm, met)}
</div><script>{JS}</script></body></html>'''

    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(doc)
    print(f'-> {SALIDA} ({len(doc)} B)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
