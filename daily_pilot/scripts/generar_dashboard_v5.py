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

# Los pares de crypto de Quantfury (exchange Binance) — NO los de Coinbase.
# Fuente: https://help.quantfury.com/en/articles/5448756-crypto-pairs (2026-11)
PARES_QUANTFURY = [
    'AAVEUSDT', 'ADAUSDT', 'APTUSDT', 'ARBUSDT', 'ATOMUSDT', 'AVAXUSDT', 'BCHUSDT',
    'BTCUSDT', 'DOGEUSDT', 'DOTUSDT', 'ETCUSDT', 'ETHUSDT', 'FILUSDT', 'HBARUSDT',
    'INJUSDT', 'LINKUSDT', 'LTCUSDT', 'MANAUSDT', 'NEARUSDT', 'NEOUSDT', 'ONDOUSDT',
    'OPUSDT', 'POLUSDT', 'RUNEUSDT', 'SANDUSDT', 'SNXUSDT', 'SOLUSDT', 'STXUSDT',
    'THETAUSDT', 'UNIUSDT', 'XRPUSDT',
    # FTM dejo de existir: Binance lo convirtio en Sonic (S) el 2025-01-16 (1:1)
    # y delisto FTM. Quantfury lista S/USDT -> ese es el par correcto.
    'SUSDT',
    # TON existe en Binance pero con status BREAK (trading pausado)
    'TONUSDT',
]
# status de trading segun Binance (BREAK = pausado)
STATUS_ESPERADO = {'SUSDT': 'TRADING', 'TONUSDT': 'BREAK'}
PARES = PARES_QUANTFURY
PLAZOS = (('1w', 'largo', '1S'), ('1d', 'media', '1D'), ('4h', 'corto', '4H'))


def cargar(ruta):
    p = Path(ruta)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text())
    except Exception:
        return None




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
                      'fuente': r['fuente'], 'status': STATUS_ESPERADO.get(par, '')})
    return filas


def ciclo(par='BTCUSDT') -> list:
    """Tramo del ciclo + niveles por TF (C05 + C05-B) para UN par."""
    from velas import velas
    from tramos import tramo_ciclo
    from zonas import zonas
    out = []
    for tf, plazo, etiqueta in PLAZOS:
        r = velas(par, tf, limite=500)
        if 'error' in r:
            out.append({'tf': etiqueta, 'error': r['error']})
            continue
        t = tramo_ciclo(r['velas'])
        if 'error' in t:
            out.append({'tf': etiqueta, 'error': t['error']})
            continue
        z = zonas(t['minimo'], t['maximo'], plazo=plazo, direccion=t['direccion'])
        out.append({'tf': etiqueta, 'min': round(t['minimo'], 2), 'max': round(t['maximo'], 2),
                    'retrocesos': {k: round(v, 2) for k, v in z['zonas_compra'].items()},
                    'extensiones': {k: round(v, 2) for k, v in list(z['extensiones'].items())[:4]},
                    'fuente': r['fuente']})
    return out


# El ciclo (3 TF x 500 velas) es caro: se calcula solo para los primeros
# CICLO_TOP pares. El resto queda en el panel de mercado con su precio real.
CICLO_TOP = 12


def ciclos_pares() -> dict:
    """Ciclo para cada par de la lista corta (los que tienen datos)."""
    return {par: ciclo(par) for par in PARES[:CICLO_TOP]}


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


JS_TABS = '''<script>
(function(){
  var tabs = document.querySelectorAll('.tab');
  var panels = document.querySelectorAll('.tabpanel');
  function mostrar(par){
    for (var i=0;i<tabs.length;i++){ tabs[i].classList.remove('activo'); }
    for (var j=0;j<panels.length;j++){
      panels[j].style.display = (panels[j].getAttribute('data-par') === par) ? 'block' : 'none';
    }
  }
  for (var k=0;k<tabs.length;k++){
    tabs[k].addEventListener('click', function(){ mostrar(this.getAttribute('data-par')); });
  }
  if (panels.length) mostrar(panels[0].getAttribute('data-par'));
})();
</script>
</body></html>'''


def panel_mercado(filas):
    filas_html = ''
    for x in filas:
        if 'error' in x:
            filas_html += f'<tr><td>{esc(x["par"])}</td><td class="num fuente">{esc(x["error"][:22])}</td><td></td></tr>'
            continue
        cls = 'up' if x['cambio'] >= 0 else 'down'
        signo = '+' if x['cambio'] >= 0 else ''
        st = ' <span style="color:var(--bad);font-size:10px">(BREAK)</span>' if x.get('status') == 'BREAK' else ''
        filas_html += (f'<tr><td><b>{esc(x["par"])}</b>{st}</td>'
                       f'<td class="num">{fmt(x["precio"])}</td>'
                       f'<td class="num {cls}">{signo}{x["cambio"]:.2f}%</td>'
                       f'<td class="num fuente">{f(x["high"])} / {f(x["low"])}</td></tr>')
    fuentes = sorted({x.get('fuente', '') for x in filas})
    return (f'<div class="card"><h3>MERCADO REAL · Binance (solo lectura)</h3>'
            f'<table><tr><th>par</th><th style="text-align:right">precio</th>'
            f'<th style="text-align:right">24h</th><th style="text-align:right">max/min</th></tr>'
            f'{filas_html}</table>'
            f'<div class="nota">fuente: {esc(", ".join(x for x in fuentes if x))} · '
            f'<b>no es un feed en vivo</b>: cache de 5 minutos. PAPER ONLY.</div>'
            f'<div class="nota" style="color:var(--warn);font-weight:600">'
            f'NO ES UNA ORDEN — muestra el mercado y los niveles. La decision la toma el trader.</div></div>')


def panel_ciclo(ciclos: dict):
    tabs = ''
    paneles = ''
    for i, (par, ciclo_datos) in enumerate(ciclos.items()):
        activo = ' activo' if i == 0 else ''
        alias = par.replace('USDT', '')
        tabs += f'<button class="tab{activo}" data-par="{esc(par)}">{esc(alias)}</button>'
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
        paneles += f'<div class="tabpanel" data-par="{esc(par)}">{bloques}</div>'
    return (f'<div class="card"><h3>CICLO · tramo y niveles (C05 / C05-B)</h3>'
            f'<div class="tabs">{tabs}</div>{paneles}'
            f'<div class="nota">0 = mínimo, 1 = máximo · retrocesos 0,382/0,5/0,61/0,786 · '
            f'extensiones por encima. Cada TF tiene su swing. '
            f'<a href="#" id="cambiarPar" style="display:none"></a></div></div>')


def panel_cuenta():
    """Cuenta de Binance SOLO LECTURA: capital real y activos con saldo."""
    try:
        import binance_readonly as B
        ak, sk = B._credenciales()
    except Exception as e:
        return ('<div class="card"><h3>CUENTA BINANCE · solo lectura</h3>'
                '<div class="nota">sin clave cargada ('
                '<span class="fuente">~/.hermes/.env</span>): '
                + esc(str(e)[:70]) + '</div></div>')
    try:
        b = B.balance()
        alerta = ('<div class="nota" style="color:var(--bad);font-weight:600">'
                  '⚠️ la cuenta PUEDE OPERAR: la clave deberia ser SOLO LECTURA.</div>'
                  if b.get('canTrade') else
                  '<div class="nota" style="color:var(--ok)">'
                  '✅ solo lectura efectiva (no puede operar)</div>')
        px = B.precios([f"{a['activo']}USDT" for a in b['activos']] or None)
        v = B.valor_usd(b, px)
        filas = ''
        for f in v['filas'][:12]:
            val = f"${f['valor_usdt']:,.2f}" if f['valor_usdt'] is not None else '—'
            filas += (f'<tr><td><b>{esc(f["activo"])}</b></td>'
                      f'<td class="num">{f["total"]:,.6f}</td>'
                      f'<td class="num fuente">{val}</td></tr>')
        return (f'<div class="card"><h3>CUENTA BINANCE · solo lectura</h3>'
                f'<div style="font-size:22px;font-weight:700;margin-bottom:4px">'
                f'${v["total_usdt"]:,.2f} USD</div>'
                f'<div class="fuente">total aproximado · {b["n_activos"]} activos</div>'
                f'<table><tr><th>activo</th><th style="text-align:right">saldo</th>'
                f'<th style="text-align:right">≈USD</th></tr>{filas}</table>'
                f'{alerta}<div class="nota">La clave vive en '
                f'<span class="fuente">~/.hermes/.env</span> (fuera del repo). '
                f'<b>No ejecuta ordenes.</b></div></div>')
    except Exception as e:
        return (f'<div class="card"><h3>CUENTA BINANCE · solo lectura</h3>'
                f'<div class="nota">error al leer: {esc(type(e).__name__)} '
                f'{esc(str(e)[:80])}</div></div>')


def panel_risk():
    """Risk manager visible: C01 (jerarquia) + C02 (30/70) + C11 (riesgo)."""
    try:
        sys.path.insert(0, str(PILOT))
        from risk_manager.risk_manager import Config, Signal, RiskManager
        cfg = Config()
        rm = RiskManager(cfg)
        capital = getattr(cfg, 'capital_operable', None) or getattr(cfg, 'account_balance', 0) or 0
        try:
            from risk_manager.risk_manager import notional_de_riesgo
            n5 = notional_de_riesgo(capital, 0.05)
            n25 = notional_de_riesgo(capital, 0.025)
            _20x = (
                f'<div class="ciclo-l"><b>Quantfury 20x</b> · tendencia 5% = '
                f'riesgo ${f(n5["riesgo_dinero"])} · notional <b>${f(n5["notional"])}</b> · '
                f'margen ${f(n5["margen"])} · <span style="color:var(--bad)">liquida con '
                f'{n5["movimiento_contrario_liquida_pct"]}% en contra</span></div>'
                f'<div class="ciclo-l">correccion 2,5% = riesgo ${f(n25["riesgo_dinero"])} · '
                f'notional ${f(n25["notional"])} · margen ${f(n25["margen"])}</div>')
        except Exception:
            _20x = ''
        lineas = (f'<div class="ciclo-l">capital: <b>${f(capital)}</b> · '
                  f'riesgo long tope: <b>{float(getattr(cfg, "riesgo_long_pct", 0.05)) * 100:.0f}%</b> · '
                  f'correccion: <b>2%</b></div>'
                  f'<div class="ciclo-l">C01: el semanal manda; diario y 4h confirman '
                  f'(<span class="fuente">core/jerarquia.py</span>)</div>'
                  f'<div class="ciclo-l">C02: 30% oferta + 70% confirmacion (2x35%)</div>'
                  f'<div class="ciclo-l">C11: riesgo = confianza x tope · por defecto 0,50 = '
                  f'<b>2,5%</b> sin confianza explicita</div>{_20x}')
    except Exception as e:
        lineas = f'<div class="ciclo-l">risk manager no disponible: {esc(str(e)[:60])}</div>'
    return (f'<div class="card"><h3>RISK MANAGER · C01 / C02 / C11</h3>{lineas}'
            f'<div class="nota">PAPER ONLY: calcula, no ejecuta. Capital y topes de '
            f'<span class="fuente">risk_manager/risk_manager.py</span>.</div></div>')


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


def panel_alertas() -> str:
    """Niveles que el precio tiene cerca (concordancia + ciclo)."""
    try:
        sys.path.insert(0, str(PILOT / 'scripts'))
        from alertas_niveles import concordancia, niveles_par, alertas, PARES
        from velas import velas
        precios = {}
        for par in PARES[:6]:
            r = velas(par, '1d', limite=2)
            if 'error' not in r and r['velas']:
                precios[par] = float(r['velas'][-1]['close'])
        conc = concordancia(4)
        niveles = []
        for precio, videos in list(conc.items())[:8]:
            if 'BTCUSDT' in precios:
                niveles.append({'par': 'BTCUSDT', 'precio': float(precio),
                                'tipo': f'concordancia ({len(videos)} videos)'})
        # tambien los niveles del ciclo de cada par (C05)
        for par in PARES[:6]:
            for x in niveles_par(par):
                niveles.append(dict(x, tipo=f"{x['tipo']} · {par.replace('USDT','')}"))
        avisos = alertas(precios, niveles, 1.5)
        filas = ''.join(
            f'<tr><td>{x["par"].replace("USDT","")}</td>'
            f'<td class="num">{x["precio"]:.4f}</td>'
            f'<td class="num">{x["distancia_pct"]:.2f}%</td>'
            f'<td class="dim">{x["tipo"]}</td></tr>'
            for x in avisos[:8]) or '<tr><td colspan="4" class="dim">ninguno ahora</td></tr>'
        return ('<div class="card"><h3>ALERTAS DE NIVEL</h3>'
                f'<div class="nota">{len(avisos)} avisos · umbral 1,5%</div>'
                f'<table><thead><tr><th>par</th><th>nivel</th><th>dist</th><th>que</th></tr></thead>'
                f'<tbody>{filas}</tbody></table></div>')
    except Exception as e:
        return f'<div class="card"><h3>ALERTAS DE NIVEL</h3><div class="nota">sin datos ({e})</div></div>'


def panel_backtest(par: str) -> str:
    """Cuanto respeta el precio los niveles del metodo."""
    try:
        from backtest_niveles import backtest
        r = backtest(par, '1d')
        if 'error' in r:
            raise RuntimeError(r['error'])
        top = sorted([f for f in r['niveles'] if f['toques']],
                     key=lambda x: -x['toques'])
        filas = ''.join(
            f'<tr><td class="dim">{f["etiqueta"]}</td>'
            f'<td class="num">{f["nivel"]:.2f}</td>'
            f'<td class="num">{f["toques"]}</td>'
            f'<td class="num">{f["hold"]}</td>'
            f'<td class="num">{f["tasa_hold"]:.0f}%</td></tr>' for f in top)
        return ('<div class="card"><h3>BACKTEST DE NIVELES</h3>'
                f'<div class="nota">{par.replace("USDT","")} 1D · tramo '
                f'{r["tramo"]["min"]:.0f} → {r["tramo"]["max"]:.0f} '
                f'({r["tramo"]["direccion"]}) · respetados con n≥'
                f'{r["min_muestra"]}: {r["promedio_hold"]}%</div>'
                f'<table><thead><tr><th>nivel</th><th>precio</th><th>toques</th>'
                f'<th>hold</th><th>respeta</th></tr></thead>'
                f'<tbody>{filas}</tbody></table></div>')
    except Exception as e:
        return f'<div class="card"><h3>BACKTEST DE NIVELES</h3><div class="nota">sin datos ({e})</div></div>'


def panel_ticket(par: str = 'BTCUSDT', tf: str = '4h') -> str:
    """El ticket del metodo: regimen, direccion, tramo y niveles."""
    try:
        from agente_ticket import analizar
        r = analizar(par, tf)
        if 'error' in r:
            raise RuntimeError(r['error'])
        ret = sorted(r['retrocesos'].items(), key=lambda kv: float(kv[0]))
        filas = ''.join(
            f'<tr><td class="dim">{k}</td><td class="num">{v:.2f}</td></tr>'
            for k, v in ret[:5])
        pos = r.get('posicion_en_tramo_pct')
        return ('<div class="card"><h3>TICKET</h3>'
                f'<div class="nota">{par.replace("USDT","")} {tf} · '
                f'{r["regimen"].get("1w")} / {r["regimen"].get("1d")} / '
                f'{r["regimen"].get("4h")}</div>'
                f'<div style="font-size:20px;font-weight:700;margin:6px 0">'
                f'{_etiq(r["direccion"])}</div>'
                f'<div class="fuente" style="margin-bottom:6px">{esc(r["motivo"])}</div>'
                f'<div class="fuente">tramo {r["tramo"]["min"]:.2f} → '
                f'{r["tramo"]["max"]:.2f} · precio {r["precio_actual"]:.2f}'
                + (f' ({pos}% del tramo)' if pos is not None else '')
                + '</div><table><thead><tr><th>retroceso</th><th>nivel</th></tr></thead>'
                f'<tbody>{filas}</tbody></table>'
                f'<div class="nota">Analisis del metodo, <b>no una orden</b>.</div></div>')
    except Exception as e:
        return f'<div class="card"><h3>TICKET</h3><div class="nota">sin datos ({e})</div></div>'


def panel_paper() -> str:
    """Operaciones simuladas registradas. PAPER_ONLY."""
    try:
        p = PILOT / 'datos' / 'paper_trades.json'
        if not p.exists():
            return ('<div class="card"><h3>PAPER TRADING</h3><div class="nota">'
                    'sin operaciones registradas. Papel de $1.000 · '
                    '<b>no manda ordenes</b>.</div></div>')
        d = cargar(p) or {}
        ops = d.get('operaciones', [])
        cerradas = [o for o in ops if not o.get('abierta')]
        abiertas = [o for o in ops if o.get('abierta')]
        tot = sum(o.get('resultado_usd') or 0 for o in cerradas)
        g = sum(1 for o in cerradas if (o.get('resultado_usd') or 0) > 0)
        filas = ''.join(
            f'<tr><td>#{o["id"]}</td><td>{o["lado"].upper()}</td>'
            f'<td>{o["par"].replace("USDT","")}</td>'
            f'<td class="num">{o["entrada"]:.2f}</td>'
            f'<td class="num">{o.get("resultado_usd", "—")}</td></tr>'
            for o in ops[-6:])
        return ('<div class="card"><h3>PAPER TRADING</h3>'
                f'<div class="nota">papel ${d.get("papel_inicial", 1000):,.0f} · '
                f'{len(cerradas)} cerradas · ganadoras {g} · '
                f'acumulado <b>${tot:+.2f}</b></div>'
                f'<table><thead><tr><th>#</th><th>lado</th><th>par</th>'
                f'<th>entrada</th><th>USD</th></tr></thead>'
                f'<tbody>{filas}</tbody></table>'
                f'<div class="nota">{len(abiertas)} abierta(s). '
                f'<b>No ejecuta ordenes reales.</b></div></div>')
    except Exception as e:
        return f'<div class="card"><h3>PAPER TRADING</h3><div class="nota">sin datos ({e})</div></div>'


def main() -> int:
    info = cargar(PILOT / 'datos' / 'informe_hoy.json') or {}
    mer = mercado()
    ciclos = ciclos_pares()
    esc_datos = escenario_pares()
    _ag = PILOT / 'investigacion' / f'AGENTE_{info.get("video_id")}.json'
    niveles = (cargar(_ag) or {}).get('niveles_dichos')
    conc = concordancia(4)
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
  {panel_risk()}
</div>

<div class="grid" style="margin-top:12px">
  {panel_cuenta()}
</div>

<div class="grid" style="margin-top:12px">
  {panel_ciclo(ciclos)}
</div>

<div class="grid g2" style="margin-top:12px">
  {panel_alertas()}
  {panel_backtest('BTCUSDT')}
</div>

<div class="grid g2" style="margin-top:12px">
  {panel_ticket('BTCUSDT', '4h')}
  {panel_paper()}
</div>

<div class="grid" style="margin-top:12px">
  {panel_escenarios(esc_datos)}
</div>

<div class="grid" style="margin-top:12px">
  {panel_estrategia(info, niveles)}
</div>

<div class="grid" style="margin-top:12px">
  {panel_concordancia(conc)}
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
</div>
{JS_TABS}'''

    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(doc)
    print(f'-> {SALIDA} ({len(doc)} B)')
    return 0




# --------------------------------------------------------------- escenario
def escenario_pares() -> list:
    """Por cada par: regimen por TF + direccion (C01) + confianza (C10).

    La probabilidad NO se inventa: es la confianza que sale de la jerarquia
    W > D > 4H (core/jerarquia.py). Si el semanal esta en rango, no se opera.
    """
    from velas import velas
    from tramos import regimen_de
    from jerarquia import determinar, sin_semanal
    out = []
    for par in PARES:
        regs = {}
        for tf in ('1w', '1d', '4h'):
            r = velas(par, tf, limite=500)
            regs[tf] = regimen_de(r['velas'])['regimen'] if 'error' not in r else 'no_determinado'
        j = determinar(regs['1w'], regs['1d'], regs['4h'])
        ref = sin_semanal(regs['1d'], regs['4h'])
        out.append({'par': par.replace('USDT', ''), 'w': regs['1w'], 'd': regs['1d'],
                    'h': regs['4h'], 'direccion': j['direccion'],
                    'confianza': j['confianza'], 'motivo': j['motivo'],
                    'ref_direccion': ref['direccion'], 'ref_confianza': ref['confianza'],
                    'ref_motivo': ref['motivo']})
    return out


def _barra(pct, direccion):
    largo = max(2, int(pct * 2.4))
    color = 'var(--ok)' if direccion in ('long', 'short') else 'var(--warn)'
    return (f'<div style="display:flex;align-items:center;gap:8px">'
            f'<div style="width:150px;height:10px;background:#21262d;border-radius:5px;overflow:hidden">'
            f'<i style="display:block;height:100%;width:{largo}px;background:{color}"></i></div>'
            f'<b style="font-variant-numeric:tabular-nums">{pct}%</b></div>')


def _etiq(d):
    return {'long': 'LONG', 'short': 'SHORT', 'correccion': 'CORRECCION',
            'no_operar': 'NO OPERAR'}.get(d, d)


# C10 (playbook:215): confianza por marcos confluentes. La asigna el trader.
CONFIANZA_POR_MARCOS = {3: 1.00, 2: 0.75, 1: 0.50}


def panel_escenarios(datos):
    # ordenado por la probabilidad de la REGLA (C01): los operables primero
    operables = sorted([x for x in datos if x['direccion'] != 'no_operar'],
                       key=lambda x: -float(x['confianza']))
    no_opera = sorted([x for x in datos if x['direccion'] == 'no_operar'],
                      key=lambda x: -float(x.get('ref_confianza', 0)))
    def fila(x):
        # C10: la confianza la asigna el trader (FIRMA). Se muestra la tabla del
        # playbook por marcos confluentes, no un 85% inventado.
        marcos = sum(1 for r in (x.get('w'), x.get('d'), x.get('h'))
                     if r in ('alcista', 'bajista'))
        conf = CONFIANZA_POR_MARCOS.get(marcos, 0.0)
        pct = int(round(conf * 100))
        ref_pct = int(round(float(x.get('ref_confianza', 0)) * 100))
        return (f'<tr><td><b>{esc(x["par"])}</b></td>'
                f'<td>{_barra(pct, x["direccion"])}</td>'
                f'<td><b>{_etiq(x["direccion"])}</b><div class="fuente">{esc(x["motivo"])}</div></td>'
                f'<td class="fuente">{_barra(ref_pct, x.get("ref_direccion"))} '
                f'<b>{_etiq(x.get("ref_direccion"))}</b>'
                f'<div class="fuente">{esc(x.get("ref_motivo"))}</div></td>'
                f'<td class="fuente">{esc(x["w"])} / {esc(x["d"])} / {esc(x["h"])}</td></tr>')
    filas = ''.join(fila(x) for x in operables + no_opera)
    sep = ('<tr><td colspan="5" style="border-bottom:2px solid var(--bd);padding:2px">'
           '<span class="fuente">— sin tendencia macro: NO SE OPERA (C01) —</span></td></tr>')
    if operables and no_opera:
        cuerpo = ''.join(fila(x) for x in operables) + sep + ''.join(fila(x) for x in no_opera)
    elif no_opera:
        cuerpo = sep + ''.join(fila(x) for x in no_opera)
    else:
        cuerpo = filas
    return (f'<div class="card"><h3>CONFIANZA POR PAR · ¿TOMAMOS POSICIONES? (heuristica)</h3>'
            f'<table><tr><th>par</th><th>CON SEMANAL (C01)</th><th>direccion</th>'
            f'<th>SIN SEMANAL (referencia)</th><th>W / D / 4H</th></tr>{cuerpo}</table>'
            f'<div class="nota"><b>CON SEMANAL</b> es la regla C01: si el semanal esta en '
            f'<b>rango</b>, no se opera. <b>SIN SEMANAL</b> es solo una referencia de '
            f'que pasaria con diario y 4h — <b>no es la regla</b>. '
            f'La confianza la asigna el trader (FIRMA C10); el numero es heuristico, '
            f'<b>no una probabilidad</b> ni una senal de compra.</div></div>')


def panel_estrategia(info, niveles):
    """La estrategia VISIBLE: lo que el canal dice, con cita."""
    filas = ''
    for n in (niveles or [])[:8]:
        cit = esc(n.get('cita', ''))[:150]
        pistas = ', '.join(n.get('pistas', []))
        filas += (f'<tr><td><span class="pill">{esc(n.get("precio"))}</span></td>'
                  f'<td class="fuente">x{esc(n.get("menciones"))}</td>'
                  f'<td class="fuente">{esc(pistas)}</td>'
                  f'<td class="fuente">{cit}</td></tr>')
    if not filas:
        filas = '<tr><td colspan="4" class="fuente">sin niveles en el ultimo video</td></tr>'
    return (f'<div class="card"><h3>ESTRATEGIA VISIBLE · lo que dice CreceTrader</h3>'
            f'<table><tr><th>nivel</th><th>menciones</th><th>tipo</th><th>cita</th></tr>{filas}</table>'
            f'<div class="nota">Salen de la transcripcion del ultimo video. '
            f'<b>NO ES UNA ORDEN</b>: el metodo lo aplica el trader.</div></div>')


def esc(s):
    return html.escape(str(s or ''))


def concordancia(n=4) -> list:
    """Niveles que se REPITEN en los ultimos n videos (confluencia temporal).

    Fuente: los AGENTE_<video>.json del agente de estrategia. No se inventa.
    """
    import collections
    raiz = PILOT / 'investigacion'
    vids = sorted(raiz.glob('AGENTE_*.json'), key=lambda p: p.stat().st_mtime, reverse=True)[:n]
    ap = collections.defaultdict(set)
    for p in vids:
        try:
            d = json.loads(p.read_text())
        except Exception:
            continue
        vid = d.get('video_id') or p.stem.replace('AGENTE_', '')
        for x in d.get('niveles_dichos', []):
            pr = x.get('precio')
            if pr is None:
                continue
            ap[round(float(pr), 0)].add(vid)
    out = [{'precio': k, 'n_videos': len(v), 'videos': sorted(v)}
           for k, v in ap.items() if len(v) >= 2]
    out.sort(key=lambda x: -x['n_videos'])
    return out


def panel_concordancia(datos):
    filas = ''
    for x in datos[:10]:
        filas += (f'<tr><td><span class="pill">{esc(x["precio"])}</span></td>'
                  f'<td class="num"><b>{x["n_videos"]}</b></td>'
                  f'<td class="fuente">{esc(", ".join(x["videos"]))}</td></tr>')
    if not filas:
        filas = '<tr><td colspan="3" class="fuente">sin niveles repetidos</td></tr>'
    return (f'<div class="card"><h3>CONCORDANCIA · niveles repetidos en los ultimos videos</h3>'
            f'<table><tr><th>nivel</th><th style="text-align:right">videos</th><th>cuales</th></tr>{filas}</table>'
            f'<div class="nota">Un nivel que el canal repite en varios videos es mas '
            f'forte que uno que dice una vez. No es una orden: es la confluencia '
            f'<b>temporal</b> (la espacial es el tramo del ciclo).</div></div>')


if __name__ == '__main__':
    raise SystemExit(main())
