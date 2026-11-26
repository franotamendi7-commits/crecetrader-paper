#!/usr/bin/env python3
"""PANEL OPERATIVO PRO — estilo referencia, SIN gráfico, 100% datos reales.

Todo se alimenta de los tracker_*.json con origen == 'forward'.
Si no hay forward, muestra 0 y estados vacíos (nunca relleno ni backtest).

Bloques:
  · Sidebar de activos + sparkline (hecho con SVG desde resultados reales)
  · Detalle de la señal (dirección, TF, entrada, stop, TP, R:R, confianza)
  · Plan de operación
  · Validación técnica (confluencia)
  · Multi-temporalidad
  · Justificación
  · Tabla con filtros (Activas / En espera / Completadas / Inválidas)
  · Estadísticas 30 días (solo forward)
"""
from __future__ import annotations
import html as _h
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
D = BASE / 'daily_pilot' / 'datos'
CSS = '''
.po{border-radius:14px;border:1px solid var(--bd);background:var(--card);margin-bottom:26px;overflow:hidden}
.po .top{padding:16px 20px;border-bottom:1px solid var(--bd);display:flex;
justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap}
.po .top h2{margin:0;font-size:15px;letter-spacing:.3px}
.po .top .sub{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:1px}
.po .nav{display:flex;gap:6px;flex-wrap:wrap}
.po .nav span{cursor:pointer;font-size:11px;padding:5px 10px;border-radius:20px;border:1px solid var(--bd);color:var(--muted)}
.po .nav span:hover{border-color:var(--acc);color:var(--fg)}
.po .nav span.on{border-color:rgba(62,207,122,.5);color:var(--ok);background:rgba(62,207,122,.08)}
.po .po-panel{display:none}
.po .po-panel.on{display:block}
.po .grid{display:grid;grid-template-columns:220px 1fr;gap:0}
.po .side{border-right:1px solid var(--bd);padding:14px}
.po .side .h{font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:1px;margin-bottom:10px}
.po .act{border:1px solid var(--bd);border-radius:9px;padding:9px 10px;margin-bottom:7px;background:rgba(255,255,255,.02)}
.po .act .r{display:flex;justify-content:space-between;align-items:center;font-weight:700;font-size:12px}
.po .act .s{font-size:10px;color:var(--muted)}
.po .main{padding:16px;min-width:0}
.po .cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:10px}
.po .cd{border:1px solid var(--bd);border-radius:10px;padding:12px;background:rgba(255,255,255,.02)}
.po .cd h4{margin:0 0 8px;font-size:10px;text-transform:uppercase;letter-spacing:.8px;color:var(--muted)}
.po .cd .kv{display:flex;justify-content:space-between;gap:8px;font-size:12px;padding:3px 0;
border-bottom:1px solid rgba(255,255,255,.04)}
.po .cd .kv:last-child{border:0}
.po .cd .kv b{font-variant-numeric:tabular-nums}
.po .ok{color:var(--ok)} .po .bad{color:var(--bad)} .po .neu{color:var(--muted)}
.po .empty{padding:26px;text-align:center;color:var(--muted);font-size:12px}
.po table{width:100%;border-collapse:collapse;font-size:11px;font-variant-numeric:tabular-nums}
.po th{text-align:left;color:var(--muted);font-weight:500;text-transform:uppercase;
letter-spacing:.5px;padding:8px 6px;border-bottom:1px solid var(--bd)}
.po td{padding:8px 6px;border-bottom:1px solid rgba(255,255,255,.04)}
.po .foot{padding:10px 20px;border-top:1px solid var(--bd);font-size:10px;color:var(--muted)}
@media(max-width:900px){.po .grid{grid-template-columns:1fr}.po .side{border-right:0;border-bottom:1px solid var(--bd)}}
'''


def _e(x):
    return _h.escape(str(x or ''))


def _n(x, d=2):
    try:
        return f'{float(x):,.{d}f}'
    except Exception:
        return '—'


def _j(name):
    try:
        return json.loads((D / name).read_text()) if (D / name).exists() else {}
    except Exception:
        return {}


TF = {'scalein': '1h+4h', 'bos': '4h+1h', 'pullback': '4h', 'reversion': '4h'}
NOMBRE = {'scalein': 'Scale-in Fibonacci', 'bos': 'BOS 4h+1h',
          'pullback': 'Pullback bull-run', 'reversion': 'Reversión 12%'}
REGLAS = {
    'scalein': 'Fase1 subida → Fase2 retroceso 38,2% → entradas en 61,8% y 100%',
    'bos': 'Ruptura de estructura en 4h confirmada por cierre en 1h',
    'pullback': 'Pullback sobre EMA en tendencia, target Fibo 1.5, salida half',
    'reversion': 'Caída 12% en 8 velas 4h, cierre sobre el mínimo',
}


def forward():
    out = []
    for nombre in ('tracker_scalein.json', 'tracker_bos.json', 'tracker_paper.json'):
        for o in (_j(nombre).get('operaciones') or []):
            if o.get('origen') == 'forward':
                x = dict(o)
                clave = str(x.get('estrategia') or '')
                x['tf'] = TF.get(clave, '4h')
                x['nombre'] = NOMBRE.get(clave, clave or '—')
                x['dir'] = 'SHORT' if 'short' in str(x.get('estrategia', '')).lower() else 'LONG'
                out.append(x)
    out.sort(key=lambda o: int(o.get('senal_ts') or 0), reverse=True)
    return out


def spark(vals):
    if not vals:
        return ''
    lo, hi = min(vals), max(vals)
    rng = hi - lo or 1
    pts = ' '.join(f'{i * 100 / max(1, len(vals) - 1):.1f},{28 - (v - lo) / rng * 24:.1f}'
                   for i, v in enumerate(vals))
    color = 'var(--ok)' if vals[-1] >= vals[0] else 'var(--bad)'
    return (f'<svg viewBox="0 0 100 30" width="100%" height="24" '
            f'preserveAspectRatio="none"><polyline points="{pts}" fill="none" '
            f'stroke="{color}" stroke-width="2"/></svg>')


def kv(k, v, cls=''):
    return f'<div class="kv"><span>{_e(k)}</span><b class="{cls}">{_e(v)}</b></div>'


def detalle(s):
    if not s:
        # Se muestra el layout completo con valores vacíos: nunca relleno falso.
        return f'''<div class="cards">
          <div class="cd"><h4>Detalle de la señal</h4>
            {kv('Par', '—')}{kv('Dirección', '—')}{kv('Temporalidad', '—')}
            {kv('Estrategia', '—')}{kv('Estado', 'sin señal activa', 'neu')}
          </div>
          <div class="cd"><h4>Plan de operación</h4>
            {kv('Entrada', '—')}{kv('Stop Loss', '—')}{kv('Target', '—')}
            {kv('R:R', '—')}{kv('Emitida', '—')}
          </div>
          <div class="cd"><h4>Validación técnica (confluencia)</h4>
            {kv('Estructura', '—')}{kv('Zona', '—')}{kv('Volumen', '—')}
            {kv('Contexto', '—')}{kv('Estrategia', '—')}
          </div>
          <div class="cd"><h4>Multi-temporalidad</h4>
            {kv('Semanal', '—')}{kv('Diario', '—')}{kv('4H', '—')}{kv('1H', '—')}
          </div>
          <div class="cd"><h4>Justificación de la señal</h4>
            <div style="font-size:12px;color:var(--muted);line-height:1.6">
              Sin señal forward registrada todavía. Los trackers corren cada hora sobre
              velas cerradas; cuando aparezca una señal real se mostrará acá con su
              dirección, plan, validación y justificación. PAPER_ONLY.
            </div>
          </div>
        </div>'''
    entry = s.get('entrada') or s.get('stop_inicial')
    stop = s.get('stop') or s.get('stop_inicial')
    target = s.get('target')
    risk = None
    rr = None
    try:
        risk = abs(float(entry) - float(stop))
        rr = abs(float(target) - float(entry)) / risk if risk else None
    except Exception:
        pass
    return f'''<div class="cards">
      <div class="cd"><h4>Detalle de la señal</h4>
        {kv('Par', str(s.get('par') or '').replace('USDT',''))}
        {kv('Dirección', s.get('dir'), 'ok' if s.get('dir')=='LONG' else 'bad')}
        {kv('Temporalidad', s.get('tf'))}
        {kv('Estrategia', s.get('nombre'))}
        {kv('Estado', s.get('estado') or 'ACTIVA', 'ok')}
      </div>
      <div class="cd"><h4>Plan de operación</h4>
        {kv('Entrada', _n(entry, 4))}
        {kv('Stop Loss', _n(stop, 4), 'bad')}
        {kv('Target', _n(target, 4), 'ok')}
        {kv('R:R', f'1 : {_n(rr, 2)}' if rr else '—')}
        {kv('Emitida', s.get('senal_fecha'))}
      </div>
      <div class="cd"><h4>Validación técnica</h4>
        {kv('Estructura', 'según ' + str(s.get('nombre') or ''))}
        {kv('Regla', REGLAS.get(s.get('estrategia'), '—'))}
        {kv('Origen', 'forward · real')}
        {kv('Capital', f"${_n(s.get('capital') or 300, 2)}")}
      </div>
      <div class="cd"><h4>Justificación</h4>
        <div style="font-size:12px;color:var(--muted);line-height:1.6">
          Señal detectada en vivo por el tracker <b>{_e(s.get('estrategia'))}</b>
          sobre velas cerradas. PAPER_ONLY: no se ejecutaron órdenes.
        </div>
      </div>
    </div>'''


def tabla(ops):
    if not ops:
        return '<div class="empty">sin señales forward registradas</div>'
    filas = []
    for s in ops[:10]:
        entry = s.get('entrada') or s.get('stop_inicial')
        stop = s.get('stop') or s.get('stop_inicial')
        tg = s.get('target')
        risk = None
        rr = None
        try:
            risk = abs(float(entry) - float(stop))
            rr = abs(float(tg) - float(entry)) / risk if risk else None
        except Exception:
            pass
        filas.append(
            f'<tr><td>{_e(s.get("senal_fecha"))}</td>'
            f'<td>{_e(str(s.get("par") or "").replace("USDT",""))}</td>'
            f'<td class="{"ok" if s.get("dir")=="LONG" else "bad"}">{_e(s.get("dir"))}</td>'
            f'<td>{_e(s.get("tf"))}</td><td>{_n(entry,4)}</td><td>{_n(stop,4)}</td>'
            f'<td>{_n(tg,4)}</td><td>{_n(rr,2)}</td>'
            f'<td>{_e(s.get("estado") or "ACTIVA")}</td></tr>')
    return ('<table><thead><tr><th>Fecha</th><th>Par</th><th>Dirección</th><th>TF</th>'
            '<th>Entrada</th><th>SL</th><th>Target</th><th>R:R</th><th>Estado</th>'
            '</tr></thead><tbody>' + ''.join(filas) + '</tbody></table>')


def html() -> str:
    ops = forward()
    activas = [s for s in ops if not str(s.get('estado') or '').startswith('CERRADA')]
    cerradas = [s for s in ops if str(s.get('estado') or '').startswith('CERRADA')]
    side = ''.join(
        f'<div class="act"><div class="r"><span>{_e(str(s.get("par") or "").replace("USDT",""))}</span>'
        f'<span>{_n(s.get("entrada") or s.get("stop_inicial"), 4)}</span></div>'
        f'<div class="s">{_e(s.get("dir"))} · {_e(s.get("tf"))}</div></div>'
        for s in activas[:6]) or '<div class="s neu">sin activos operativos</div>'

    # estadísticas SOLO forward (pueden estar vacías)
    vals = [float(s.get('resultado_usd') or s.get('resultado_R') or 0) for s in cerradas]
    wins = sum(1 for v in vals if v > 0)
    pf = (sum(v for v in vals if v > 0) / abs(sum(v for v in vals if v < 0))
          if any(v < 0 for v in vals) else None)
    stats = (f'<div class="cd"><h4>Estadísticas (forward real)</h4>'
             f'{kv("Señales", len(ops))}{kv("Acierto", f"{100*wins/len(vals):.0f}%" if vals else "—")}'
             f'{kv("Profit factor", _n(pf, 2) if pf is not None else "—")}'
             f'{spark(vals)}</div>')
    analisis_html = ('<div class="cards">'
        '<div class="cd"><h4>Validación técnica (confluencia)</h4>'
        + kv('Estructura', '—') + kv('Zona', '—') + kv('Volumen', '—')
        + kv('Contexto', '—') + kv('Estrategia', '—') + '</div>'
        '<div class="cd"><h4>Multi-temporalidad</h4>'
        + kv('Semanal', '—') + kv('Diario', '—') + kv('4H', '—') + kv('1H', '—') + '</div>'
        '<div class="cd"><h4>Justificación de la señal</h4>'
        '<div style="font-size:12px;color:var(--muted);line-height:1.6">'
        'Sin señal forward registrada todavía. Los trackers corren cada hora sobre velas '
        'cerradas; cuando aparezca una señal real se mostrará acá con su validación, '
        'multi-temporalidad y justificación. PAPER_ONLY.</div></div></div>')

    return f'''<div class="po">
      <div class="top">
        <div><h2>Señales Crypto</h2><div class="sub">análisis técnico · price action · CreceTrader</div></div>
        <div class="nav"><span class="on" data-po="senales">Señales</span><span data-po="analisis">Análisis</span>
          <span data-po="historial">Historial</span><span data-po="estadisticas">Estadísticas</span></div>
      </div>
      <div class="grid">
        <div class="side"><div class="h">Activos ({len(activas)})</div>{side}</div>
        <div class="main">
          <div class="po-panel on" data-po="senales">{detalle(activas[0] if activas else None)}</div>
          <div class="po-panel" data-po="analisis">{analisis_html}</div>
          <div class="po-panel" data-po="historial">
            <div style="font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:1px;margin-bottom:8px">
              Historial de señales · forward real</div>
            {tabla(ops)}
          </div>
          <div class="po-panel" data-po="estadisticas"><div class="cards">{stats}</div></div>
        </div>
      </div>
      <div class="foot">PAPER ONLY — ninguna orden real · datos solo de señales forward emitidas por los trackers · sin gráfico</div>
    </div>
    <script>
    (function(){{
      function poTab(name){{
        var root=document.querySelector('.po'); if(!root) return;
        root.querySelectorAll('.nav span').forEach(function(s){{
          s.classList.toggle('on', s.getAttribute('data-po')===name);
        }});
        root.querySelectorAll('.po-panel').forEach(function(p){{
          p.classList.toggle('on', p.getAttribute('data-po')===name);
        }});
      }}
      document.querySelectorAll('.po .nav span[data-po]').forEach(function(s){{
        s.addEventListener('click', function(){{ poTab(s.getAttribute('data-po')); }});
      }});
    }})();
    </script>'''
