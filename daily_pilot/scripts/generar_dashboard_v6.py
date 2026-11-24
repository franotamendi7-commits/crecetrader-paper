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
    """Reparto alcista/bajista/lateral a partir de lo dicho por el canal.

    Es una lectura del texto, NO una prediccion.
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
    return {'alcista': alcista, 'bajista': bajista, 'lateral': lateral,
            'evidencia': ['Basado en los niveles dichos en el video']}


# ------------------------------------------------------------------ HTML
CSS = '''
:root{--bg:#0b0f14;--card:#141b24;--bd:#263141;--fg:#e8eef5;--muted:#8a97a6;
--acc:#4f9dff;--ok:#35c26a;--bad:#e5534b;--warn:#d9a441}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);
font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;font-size:14px}
.wrap{max-width:1200px;margin:0 auto;padding:20px 20px 40px}
header{display:flex;align-items:center;gap:14px;margin-bottom:18px}
.dot{width:38px;height:38px;border-radius:10px;background:linear-gradient(135deg,#f7931a,#ffb84d);
display:flex;align-items:center;justify-content:center;font-weight:800;color:#fff;font-size:19px}
h1{font-size:22px;margin:0;font-weight:700}
.sub{color:var(--muted);font-size:13px;margin-top:3px}
.pill{margin-left:auto;color:var(--ok);border:1px solid var(--ok);border-radius:20px;
padding:5px 14px;font-size:12px;font-weight:700;letter-spacing:.4px}
.hoy{display:flex;gap:10px;align-items:center;background:var(--card);
border:1px solid var(--bd);border-radius:12px;padding:12px 16px;margin-bottom:20px;font-size:13px}
.hoy .lbl{color:var(--muted);font-weight:600;text-transform:uppercase;font-size:11px;letter-spacing:.5px}
.badge{background:rgba(53,194,106,.14);border:1px solid rgba(53,194,106,.5);color:var(--ok);
border-radius:8px;padding:6px 12px;font-weight:700}
.badge.no{background:rgba(229,83,75,.12);border-color:rgba(229,83,75,.5);color:var(--bad)}
section{margin-bottom:26px}
h2{font-size:12px;text-transform:uppercase;letter-spacing:1px;color:var(--acc);
margin:0 0 12px;padding-bottom:8px;border-bottom:2px solid var(--bd);font-weight:700}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:10px}
.mcard{background:var(--card);border:1px solid var(--bd);border-radius:10px;padding:12px}
.mcard .par{font-weight:700;font-size:14px}
.mcard .precio{font-size:19px;font-weight:700;margin:5px 0 2px;
font-variant-numeric:tabular-nums}
.mcard .chg{font-size:13px;font-weight:600}
.up{color:var(--ok)} .down{color:var(--bad)} .flat{color:var(--muted)}
.leer{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}
.lcard{border-radius:12px;padding:16px;border:1px solid}
.lcard.a{background:rgba(53,194,106,.08);border-color:rgba(53,194,106,.35)}
.lcard.b{background:rgba(229,83,75,.08);border-color:rgba(229,83,75,.35)}
.lcard.c{background:rgba(217,164,65,.08);border-color:rgba(217,164,65,.35)}
.lcard .t{font-size:15px;font-weight:700;display:flex;justify-content:space-between}
.lcard .p{font-size:30px;font-weight:800;font-variant-numeric:tabular-nums}
.chips{display:flex;flex-wrap:wrap;gap:6px;margin-top:10px}
.chip{background:rgba(255,255,255,.06);border-radius:20px;padding:5px 11px;font-size:12px;color:var(--muted)}
.nivel{background:var(--card);border:1px solid var(--bd);border-radius:10px;padding:12px;
display:flex;justify-content:space-between;align-items:center;gap:12px}
.nivel b{font-variant-numeric:tabular-nums;font-size:15px}
.nivel .men{color:var(--muted);font-size:12px}
footer{color:var(--muted);font-size:12px;margin-top:26px;line-height:1.6}
.warn{color:var(--warn);font-weight:600}
'''


def mcard(x) -> str:
    par = esc(x['par'])
    st = ' <span style="color:var(--bad);font-size:10px">(BREAK)</span>' if x.get('status') == 'BREAK' else ''
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
    badge_cls = '' if vid else 'no'
    revisado = info.get('publicado', '')[:16].replace('T', ' ') or '—'
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
  <span class="badge {badge_cls}">▶ Video nuevo: {hay_video}</span>
  <span class="lbl">·</span>
  <span>Última revisión: {esc(revisado)}</span>
</div>

<section>
  <h2>Mercado Quantfury · {len(mer)} criptos operables</h2>
  <div class="grid">{cards}</div>
</section>

<section>
  <h2>Análisis CreceTrader · lo que dice el canal</h2>
  <div class="leer">
    {lcard('a', 'Alcista', lec['alcista'], 'var(--ok)')}
    {lcard('b', 'Bajista', lec['bajista'], 'var(--bad)')}
    {lcard('c', 'Lateral', lec['lateral'], 'var(--warn)')}
  </div>
  <div class="chips" style="margin-top:12px">{ev}</div>
  <div class="chips" style="margin-top:16px;flex-direction:column;align-items:stretch;gap:8px">
    <div style="font-size:12px;color:var(--muted);text-transform:uppercase;letter-spacing:.6px;margin-bottom:2px">Niveles clave que mencionó</div>
    {niv_html}
  </div>
</section>

<footer>
  · Los precios son <b>reales</b> (Binance, solo lectura), caché de 5 minutos — no es un feed en vivo.<br>
  · El reparto Alcista/Bajista/Lateral se calcula de los <b>niveles dichos en el video</b>: es una lectura del texto, no una predicción.<br>
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
