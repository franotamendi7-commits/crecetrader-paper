#!/usr/bin/env python3
"""Dashboard v6 — tablero limpio.

Dos bloques separados:
    1 · MERCADO QUANTFURY  : precios reales de las 33 criptos operables.
    2 · ANÁLISIS CRECETRADER: lo que dijo el canal hoy (simple).

Sin paneles de estrategia: no hay backtest, ni ticket, ni paper, ni alertas.

Uso:
    python3 daily_pilot/scripts/generar_dashboard_v6.py
    open daily_pilot/dashboard/index.html

PAPER_ONLY: muestra, no ejecuta.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
PILOT = BASE / 'daily_pilot'
sys.path.insert(0, str(PILOT / 'core'))
sys.path.insert(0, str(PILOT / 'scripts'))

PARES_QUANTFURY = [
    'AAVEUSDT', 'ADAUSDT', 'APTUSDT', 'ARBUSDT', 'ATOMUSDT', 'AVAXUSDT', 'BCHUSDT',
    'BTCUSDT', 'DOGEUSDT', 'DOTUSDT', 'ETCUSDT', 'ETHUSDT', 'FILUSDT', 'HBARUSDT',
    'INJUSDT', 'LINKUSDT', 'LTCUSDT', 'MANAUSDT', 'NEARUSDT', 'NEOUSDT', 'ONDOUSDT',
    'OPUSDT', 'POLUSDT', 'RUNEUSDT', 'SANDUSDT', 'SNXUSDT', 'SOLUSDT', 'STXUSDT',
    'THETAUSDT', 'UNIUSDT', 'XRPUSDT', 'SUSDT', 'TONUSDT',
]
STATUS_ESPERADO = {'SUSDT': 'TRADING', 'TONUSDT': 'BREAK'}


def esc(s):
    import html
    return html.escape(str(s or ''))


def cargar(p, default=None):
    q = Path(p)
    if not q.exists():
        return default
    try:
        return json.loads(q.read_text())
    except Exception:
        return default


def fmt_precio(x) -> str:
    if x is None:
        return '—'
    if x >= 1000:
        return f'{x:,.0f}'
    if x >= 100:
        return f'{x:,.2f}'
    if x >= 1:
        return f'{x:.3f}'
    return f'{x:.5f}'


# ------------------------------------------------------------------ datos
def mercado() -> list:
    """Precio real + cambio 24h de cada par de Quantfury."""
    from velas import velas
    out = []
    for par in PARES_QUANTFURY:
        r = velas(par, '1d', limite=3)
        if 'error' in r or len(r['velas']) < 2:
            out.append({'par': par.replace('USDT', ''), 'precio': None,
                        'cambio': None, 'fuente': r.get('error', 'sin datos'),
                        'status': STATUS_ESPERADO.get(par, '')})
            continue
        v, prev = r['velas'][-1], r['velas'][-2]
        out.append({
            'par': par.replace('USDT', ''),
            'precio': float(v['close']),
            'cambio': round((v['close'] - prev['close']) / prev['close'] * 100, 2)
            if prev['close'] else 0.0,
            'fuente': r['fuente'],
            'status': STATUS_ESPERADO.get(par, ''),
        })
    return out


def lectura_agente(info: dict, niveles: list) -> dict:
    """Reparto alcista/bajista a partir de lo dicho por el canal.

    Es una lectura del texto, NO una prediccion. La suma es 100.
    """
    if not info or not niveles:
        return {'alcista': None, 'bajista': None, 'lateral': None, 'evidencia': []}
    ref = float(niveles[0].get('precio') or 0)
    arriba = sum(1 for n in niveles if ref and float(n.get('precio') or 0) > ref)
    abajo = sum(1 for n in niveles if ref and float(n.get('precio') or 0) < ref)
    tot = max(1, arriba + abajo)
    # si hay muchos niveles arriba, sesgo alcista; muchos abajo, bajista
    pct_ar = round(arriba / tot * 100)
    pct_ab = round(abajo / tot * 100)
    lateral = max(0, 100 - abs(pct_ar - pct_ab))
    alcista = pct_ar
    bajista = pct_ab
    return {'alcista': pct_ar, 'bajista': round(100 - pct_ar, 2), 'lateral': None,
            'evidencia': ['Basado en los niveles dichos en el video']}


# ------------------------------------------------------------------ HTML
from panel_resultados import CSS_EXTRA, html as html_resultados
from panel_video import CSS_EXTRA as CSS_VIDEO, html as html_video
from panel_senales import CSS_EXTRA as CSS_SENALES, html as html_senales

CSS = CSS_EXTRA + CSS_VIDEO + CSS_SENALES + '''
:root{--bg:#080c12;--bg2:#0d1420;--card:#131b28;--card2:#182233;--bd:#232f42;--fg:#eaf1f9;
--muted:#7f8ea3;--acc:#5aa2ff;--ok:#3ecf7a;--bad:#ff6b63;--warn:#e0aa4c}
*{box-sizing:border-box}
body{margin:0;background:
radial-gradient(1200px 500px at 80% -10%,rgba(90,162,255,.10),transparent),
linear-gradient(180deg,#0a1018,#070a0f);color:var(--fg);
font-family:-apple-system,BlinkMacSystemFont,"SF Pro Text","Segoe UI",Roboto,sans-serif;font-size:14px;
-webkit-font-smoothing:antialiased}
.wrap{max-width:1240px;margin:0 auto;padding:26px 22px 48px}

header{display:flex;align-items:center;gap:14px;margin-bottom:6px}
.dot{width:42px;height:42px;border-radius:12px;
background:linear-gradient(135deg,#f7931a 0%,#ffb84d 100%);
box-shadow:0 6px 20px rgba(247,147,26,.35);
display:flex;align-items:center;justify-content:center;font-weight:800;color:#fff;font-size:20px}
h1{font-size:23px;margin:0;font-weight:700;letter-spacing:-.3px}
.sub{color:var(--muted);font-size:13px;margin-top:4px}
.pill{margin-left:auto;display:flex;align-items:center;gap:7px;color:var(--ok);
border:1px solid rgba(62,207,122,.45);background:rgba(62,207,122,.10);
border-radius:20px;padding:7px 15px;font-size:12px;font-weight:700;letter-spacing:.5px}
.pill .p{width:7px;height:7px;border-radius:50%;background:var(--ok);
box-shadow:0 0 0 3px rgba(62,207,122,.22)}

.hoy{display:flex;gap:14px;align-items:center;background:linear-gradient(180deg,var(--card),var(--bg2));
border:1px solid var(--bd);border-radius:14px;padding:13px 18px;margin:18px 0 24px;
font-size:13px;flex-wrap:wrap}
.lbl{color:var(--muted);font-weight:600;text-transform:uppercase;font-size:11px;letter-spacing:.8px}
.badge{background:rgba(62,207,122,.14);border:1px solid rgba(62,207,122,.45);color:var(--ok);
border-radius:9px;padding:6px 12px;font-weight:700;font-size:12px}
.badge.no{background:rgba(255,107,99,.12);border-color:rgba(255,107,99,.45);color:var(--bad)}
.sep{color:var(--bd)}

section{margin-bottom:30px}
.shead{display:flex;align-items:baseline;gap:12px;margin-bottom:14px;padding-bottom:10px;
border-bottom:1px solid var(--bd)}
h2{font-size:12px;text-transform:uppercase;letter-spacing:1.2px;color:var(--acc);
margin:0;font-weight:700;white-space:nowrap}
.shead .n{color:var(--muted);font-size:12px;font-variant-numeric:tabular-nums}
.shead .hint{margin-left:auto;color:var(--muted);font-size:11px}

.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(152px,1fr));gap:10px}
.mcard{background:linear-gradient(180deg,var(--card),var(--bg2));
border:1px solid var(--bd);border-radius:11px;padding:13px 14px;
transition:border-color .15s,transform .15s}
.mcard:hover{border-color:var(--acc);transform:translateY(-1px)}
.mcard .par{font-weight:700;font-size:14px;letter-spacing:.2px}
.mcard .precio{font-size:19px;font-weight:700;margin:6px 0 3px;
font-variant-numeric:tabular-nums;letter-spacing:-.2px}
.mcard .chg{font-size:13px;font-weight:600;font-variant-numeric:tabular-nums}
.up{color:var(--ok)} .down{color:var(--bad)} .flat{color:var(--muted)}
.brk{color:var(--bad);font-size:10px;font-weight:700;letter-spacing:.4px}

.leer{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px}
.lcard{border-radius:13px;padding:17px 18px;border:1px solid;position:relative;overflow:hidden}
.lcard::before{content:"";position:absolute;left:0;top:0;bottom:0;width:4px}
.lcard.a{background:linear-gradient(180deg,rgba(62,207,122,.10),rgba(62,207,122,.03));
border-color:rgba(62,207,122,.35)} .lcard.a::before{background:var(--ok)}
.lcard.b{background:linear-gradient(180deg,rgba(255,107,99,.10),rgba(255,107,99,.03));
border-color:rgba(255,107,99,.35)} .lcard.b::before{background:var(--bad)}
.lcard.c{background:linear-gradient(180deg,rgba(224,170,76,.10),rgba(224,170,76,.03));
border-color:rgba(224,170,76,.35)} .lcard.c::before{background:var(--warn)}
.lcard .t{font-size:14px;font-weight:700;display:flex;justify-content:space-between;
align-items:center}
.lcard .p{font-size:31px;font-weight:800;font-variant-numeric:tabular-nums;letter-spacing:-.5px}
.chips{display:flex;flex-wrap:wrap;gap:7px;margin-top:13px}
.chip{background:rgba(255,255,255,.055);border:1px solid rgba(255,255,255,.07);
border-radius:20px;padding:5px 12px;font-size:12px;color:var(--muted)}
.nivel{background:linear-gradient(180deg,var(--card),var(--bg2));border:1px solid var(--bd);
border-radius:11px;padding:13px 15px;display:flex;justify-content:space-between;
align-items:center;gap:14px}
.nivel b{font-variant-numeric:tabular-nums;font-size:15px;font-weight:700}
.nivel .men{color:var(--muted);font-size:12px}
.nivel .cita{color:var(--muted);font-size:11px;max-width:380px;
overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
footer{color:var(--muted);font-size:12px;margin-top:30px;line-height:1.7;
border-top:1px solid var(--bd);padding-top:16px}
.warn{color:var(--warn);font-weight:600}
.kpi{display:flex;gap:26px;margin-top:10px;flex-wrap:wrap}
.kpi div{font-size:12px;color:var(--muted)}
.kpi b{display:block;font-size:17px;color:var(--fg);font-variant-numeric:tabular-nums;
margin-top:3px}
'''


def mcard(x) -> str:
    par = esc(x['par'])
    st = ' <span class="brk">BREAK</span>' if x.get('status') == 'BREAK' else ''
    if x['precio'] is None:
        return f'<div class="mcard"><div class="par">{par}{st}</div><div class="precio flat">—</div><div class="chg flat">sin datos</div></div>'
    cls = 'up' if x['cambio'] >= 0 else 'down'
    flecha = '▲' if x['cambio'] > 0.05 else ('▼' if x['cambio'] < -0.05 else '·')
    return (f'<div class="mcard"><div class="par">{par}{st}</div>'
            f'<div class="precio">{fmt_precio(x["precio"])}</div>'
            f'<div class="chg {cls}">{flecha} {x["cambio"]:+.2f}%</div></div>')


def lcard(clase, titulo, pct, color_var) -> str:
    if pct is None:
        return f'<div class="lcard {clase}"><div class="t"><span>{titulo}</span></div><div class="p" style="color:var(--muted)">—</div></div>'
    return (f'<div class="lcard {clase}"><div class="t"><span>{titulo}</span>'
            f'<span class="p" style="color:{color_var}">{pct}%</span></div></div>')


def main() -> int:
    info = cargar(PILOT / 'datos' / 'informe_hoy.json') or {}
    vid = info.get('video_id') or ''
    ag = PILOT / 'investigacion' / f'AGENTE_{vid}.json'
    datos_ag = cargar(ag) or {}
    niveles = datos_ag.get('niveles_dichos') or []
    mer = mercado()
    lec = lectura_agente(info, niveles)

    fuen = sorted({x.get('fuente', '') for x in mer if x.get('fuente')})
    cards = ''.join(mcard(x) for x in mer)

    ev = ''.join(f'<span class="chip">{esc(e)}</span>' for e in lec['evidencia'])
    top = [n for n in sorted(niveles, key=lambda z: -(z.get('menciones') or 0))[:8]]
    niv_html = ''.join(
        f'<div class="nivel"><b>{fmt_precio(float(n["precio"]))}</b>'
        f'<span class="men">x{n.get("menciones")} menciones</span>'
        f'<span class="men">{esc(str(n.get("cita") or "")[:70])}</span></div>'
        for n in top) or '<div class="nota">sin niveles hoy</div>'

    hay_video = 'SÍ' if vid else 'NO'
    badge_cls = 'badge no' if not vid else 'badge'
    revisado = info.get('publicado', '')[:16].replace('T', ' ') or '—'
    gen = cargar(PILOT / 'datos' / 'monitor_senales.json') or {}
    tablero = (gen.get('generado') or '')[:16].replace('T', ' ').replace('Z', '') or '—'
    titulo = f'Análisis de {info.get("par") or "Mercado"}'

    doc = f'''<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>YouTubeTradingAgent · tablero</title><style>{CSS}</style></head>
<body><div class="wrap">

<header>
  <div class="dot">₿</div>
  <div><h1>{esc(titulo)}</h1><div class="sub">Tablero de decisión · datos reales de Binance</div></div>
  <div class="pill">● PAPER ONLY</div>
</header>

<div class="hoy">
  <span class="lbl">Hoy</span>
  <span class="{badge_cls}">▶ Video nuevo: {hay_video}</span>
  <span class="lbl">·</span>
  <span>Video: {esc(revisado)}</span>
  <span class="sep">·</span>
  <span>Tablero: {esc(tablero)}</span>
</div>

<section>
  <div class="shead"><h2>Mercado Quantfury</h2><span class="n">{len(mer)} criptos operables</span><span class="hint">precio y cambio 24h</span></div>
  <div class="grid">{cards}</div>
</section>

<section>
  <div class="shead"><h2>Análisis CreceTrader</h2><span class="n">lo que dice el canal</span><span class="hint">lectura de niveles, no predicción</span></div>
  <div class="leer">
    {lcard('a', 'Alcista', lec['alcista'], 'var(--ok)')}
    {lcard('b', 'Bajista', lec['bajista'], 'var(--bad)')}
  </div>
  <div class="chips" style="margin-top:12px">{ev}</div>
  <div class="chips" style="margin-top:16px;flex-direction:column;align-items:stretch;gap:8px">
    <div style="font-size:12px;color:var(--muted);text-transform:uppercase;letter-spacing:.6px;margin-bottom:2px">Niveles clave que mencionó</div>
    {niv_html}
  </div>
</section>

{html_senales()}

{html_video()}

{html_resultados()}
<footer>
  · Los precios son <b>reales</b> (Binance, solo lectura), caché de 5 minutos — no es un feed en vivo.<br>
  · El reparto Alcista/Bajista se calcula de los <b>niveles dichos en el video</b>: es una lectura del texto, no una predicción.<br>
  · Fuente: {esc(", ".join(f for f in fuen if f))} · video {esc(vid)}<br>
  · <span class="warn">PAPER ONLY</span> — no ejecuta órdenes. La decisión la toma el trader.
</footer>

</div></body></html>'''

    out = PILOT / 'dashboard' / 'index.html'
    out.write_text(doc, encoding='utf-8')
    print(f'-> {out} ({len(doc)} B)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
