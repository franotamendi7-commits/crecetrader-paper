#!/usr/bin/env python3
"""Dashboard v6 — tablero limpio.

Dos bloques separados:
    1 · MERCADO QUANTFURY  : precios reales de las 33 criptos operables.
    2 · ANÁLISIS CRECETRADER: lo que dijo el canal hoy (simple).

Sin paneles de estrategia: no hay backtest, ni ticket, ni paper, ni alertas.

Uso:
    python3 daily_pilot/scripts/generar_dashboard_v6.py
    open daily_pilot/dashboard/index.html
    # o via servidor local:
    python3 -m http.server 8765 --directory daily_pilot/dashboard

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
    'ARBUSDT', 'AVAXUSDT', 'BTCUSDT', 'DOGEUSDT', 'DOTUSDT', 'ETCUSDT', 'FILUSDT', 'HBARUSDT', 'INJUSDT', 'LINKUSDT', 'NEARUSDT', 'THETAUSDT', 'XRPUSDT',
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
from panel_operativo import CSS as CSS_OPERATIVO, html as html_operativo
from panel_pro import CSS as CSS_PRO, html as html_pro
from tracker_paper import actualizar as actualizar_tracker

CSS = CSS_OPERATIVO + CSS_PRO + '''
:root{--bg:#080c12;--bg2:#0d1420;--card:#131b28;--card2:#182233;--bd:#232f42;--fg:#eaf1f9;
--muted:#7f8ea3;--acc:#5aa2ff;--ok:#3ecf7a;--bad:#ff6b63;--warn:#e0aa4c}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);
font-family:-apple-system,BlinkMacSystemFont,"SF Pro Text","Segoe UI",Roboto,"Inter",sans-serif;font-size:14px;
 font-variant-numeric:tabular-nums;
-webkit-font-smoothing:antialiased}
.wrap{max-width:1240px;margin:0 auto;padding:26px 22px 48px}

header{display:flex;align-items:center;gap:14px;margin-bottom:6px}
.dot{width:42px;height:42px;border-radius:12px;
background:#f7931a;
box-shadow:0 6px 20px rgba(247,147,26,.35);
display:flex;align-items:center;justify-content:center;font-weight:800;color:#fff;font-size:20px}
h1{font-size:23px;margin:0;font-weight:700;letter-spacing:-.3px}
.sub{color:var(--muted);font-size:13px;margin-top:4px}
.pill{margin-left:auto;display:flex;align-items:center;gap:7px;color:var(--ok);
border:1px solid rgba(62,207,122,.45);background:rgba(62,207,122,.10);
border-radius:20px;padding:7px 15px;font-size:12px;font-weight:700;letter-spacing:.5px}
.pill .p{width:7px;height:7px;border-radius:50%;background:var(--ok);
box-shadow:0 0 0 3px rgba(62,207,122,.22)}

.hoy{display:flex;gap:14px;align-items:center;background:var(--card);
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
.mcard{background:var(--card);
border:1px solid var(--bd);border-radius:11px;padding:13px 14px;
transition:border-color .15s,transform .15s}
.mcard:hover{border-color:var(--acc);transform:translateY(-1px)}
.mcard-link{display:block;text-decoration:none;color:inherit}
.mcard .par{font-weight:700;font-size:14px;letter-spacing:.2px}
.mcard .precio{font-size:19px;font-weight:700;margin:6px 0 3px;
font-variant-numeric:tabular-nums;letter-spacing:-.2px}
.mcard .chg{font-size:13px;font-weight:600;font-variant-numeric:tabular-nums}
.up{color:var(--ok)} .down{color:var(--bad)} .flat{color:var(--muted)}
.brk{color:var(--bad);font-size:10px;font-weight:700;letter-spacing:.4px}

.leer{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px}
.lcard{border-radius:13px;padding:17px 18px;border:1px solid;position:relative;overflow:hidden}
.lcard::before{content:"";position:absolute;left:0;top:0;bottom:0;width:4px}
.lcard.a{background:rgba(62,207,122,.08);border-color:rgba(62,207,122,.35)} .lcard.a::before{background:var(--ok)}
.lcard.b{background:rgba(255,107,99,.08);border-color:rgba(255,107,99,.35)} .lcard.b::before{background:var(--bad)}
.lcard.c{background:rgba(224,170,76,.08);border-color:rgba(224,170,76,.35)} .lcard.c::before{background:var(--warn)}
.lcard .t{font-size:14px;font-weight:700;display:flex;justify-content:space-between;
align-items:center}
.lcard .p{font-size:31px;font-weight:800;font-variant-numeric:tabular-nums;letter-spacing:-.5px}
.chips{display:flex;flex-wrap:wrap;gap:7px;margin-top:13px}
.chip{background:rgba(255,255,255,.055);border:1px solid rgba(255,255,255,.07);
border-radius:20px;padding:5px 12px;font-size:12px;color:var(--muted)}
.nivel{background:var(--card);border:1px solid var(--bd);
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
.graf{width:100%;height:150px;background:rgba(255,255,255,.02);border:1px solid var(--bd);border-radius:10px}
.sin-datos{color:var(--muted);font-size:12px;padding:14px}
.pdetail{display:none}
.dom-a{border-left:3px solid rgba(62,207,122,.55)}
.dom-b{border-left:3px solid rgba(224,170,74,.55)}
.dom-c{border-left:3px solid rgba(224,170,74,.55)}
@media (max-width:1024px){
 body{padding:18px 16px 40px}
 .grid{grid-template-columns:repeat(auto-fill,minmax(140px,1fr))}
 .leer{grid-template-columns:repeat(auto-fit,minmax(240px,1fr))}
}
@media (max-width:640px){
 body{padding:14px 12px 32px}
 .grid{grid-template-columns:repeat(auto-fill,minmax(130px,1fr));gap:8px}
 h1{font-size:19px}
 .kpi{gap:14px}
}
#modal-overlay{display:none;position:fixed;inset:0;z-index:60;background:rgba(3,6,10,.72);align-items:center;justify-content:center;padding:18px}
#modal-overlay.open{display:flex}
#modal-overlay .modal{background:var(--bg2);border:1px solid var(--bd);border-radius:16px;max-width:780px;width:100%;max-height:84vh;overflow-y:auto;padding:24px;position:relative;box-shadow:0 24px 70px rgba(0,0,0,.55)}
#modal-overlay .modal h2{font-size:15px;text-transform:uppercase;letter-spacing:1.2px;color:var(--acc);margin:0 0 4px}
#modal-overlay .modal h3{font-size:11px;text-transform:uppercase;letter-spacing:1px;color:var(--acc);margin:18px 0 8px}
#modal-overlay .modal .meta{color:var(--muted);font-size:12px;line-height:1.7}
#modal-overlay .modal .kpi{display:flex;gap:26px;margin-top:10px;flex-wrap:wrap}
#modal-overlay .modal .kpi div{font-size:12px;color:var(--muted)}
#modal-overlay .modal .kpi b{display:block;font-size:17px;color:var(--fg);font-variant-numeric:tabular-nums;margin-top:3px}
#modal-overlay .modal .nivel{background:var(--card);border:1px solid var(--bd);border-radius:11px;padding:13px 15px;display:flex;justify-content:space-between;align-items:center;gap:14px;margin-bottom:8px}
#modal-overlay .modal .graf{width:100%;height:150px;background:rgba(255,255,255,.02);border:1px solid var(--bd);border-radius:10px}
#modal-overlay .modal .sin-datos{color:var(--muted);font-size:12px;padding:14px}
#modal-overlay .modal .res{border-radius:14px;padding:18px 20px;border:1px solid var(--bd);background:var(--card);margin-bottom:0}
#modal-x{position:absolute;top:12px;right:14px;background:none;border:1px solid var(--bd);color:var(--muted);width:30px;height:30px;border-radius:8px;cursor:pointer;font-size:16px;line-height:1}
#modal-x:hover{color:var(--fg);border-color:var(--acc)}
.sg-c{border-radius:14px;padding:18px 20px;border:1px solid var(--bd);
 background:var(--card);margin-bottom:26px}
.sg-c .mt{font-size:11px;text-transform:uppercase;letter-spacing:1px;color:var(--acc);margin-bottom:12px}
.sg-c .op{border:1px solid var(--bd);border-radius:9px;padding:10px 12px;margin-bottom:7px;
 background:rgba(255,255,255,.02);font-size:12px}
.sg-c .op .h{display:flex;justify-content:space-between;gap:8px;font-weight:700;margin-bottom:5px}
.sg-c .op .d{color:var(--muted);font-variant-numeric:tabular-nums;line-height:1.55}
.sg-c .vacio{color:var(--muted);font-size:12px;padding:10px 0}
.sg-c .kpi{display:flex;gap:18px;flex-wrap:wrap;margin-top:10px}
.sg-c .kpi div{font-size:12px;color:var(--muted)}
.sg-c .kpi b{display:block;font-size:16px;color:var(--fg);font-variant-numeric:tabular-nums;margin-top:2px}
'''


def mcard(x) -> str:
    par = esc(x['par'])
    st = ' <span class="brk">BREAK</span>' if x.get('status') == 'BREAK' else ''
    if x['precio'] is None:
        return (f'<a class="mcard-link" href="#par-{par}" onclick="abrirModal(this)"><div class="mcard"><div class="par">{par}{st}</div>'
                f'<div class="precio flat">—</div><div class="chg flat">sin datos</div></div></a>')
    cls = 'up' if x['cambio'] >= 0 else 'down'
    flecha = '▲' if x['cambio'] > 0.05 else ('▼' if x['cambio'] < -0.05 else '·')
    return (f'<a class="mcard-link" href="#par-{par}" onclick="abrirModal(this)"><div class="mcard"><div class="par">{par}{st}</div>'
            f'<div class="precio">{fmt_precio(x["precio"])}</div>'
            f'<div class="chg {cls}">{flecha} {x["cambio"]:+.2f}%</div></div></a>')


def lcard(clase, titulo, pct, color_var) -> str:
    if pct is None:
        return f'<div class="lcard {clase}"><div class="t"><span>{titulo}</span></div><div class="p" style="color:var(--muted)">—</div></div>'
    return (f'<div class="lcard {clase}"><div class="t"><span>{titulo}</span>'
            f'<span class="p" style="color:{color_var}">{pct}%</span></div></div>')


def _es_num(x, dec=2, signo=False) -> str:
    """Numero con coma decimal; negativo con signo menos tipografico."""
    try:
        v = float(x)
    except Exception:
        return '—'
    s = f'{v:.{dec}f}'.replace('.', ',')
    if v < 0:
        return '−' + s.lstrip('-')
    if signo and v > 0:
        return '+' + s
    return s


def _pdetalles(mer: list, niveles: list, est: dict) -> str:
    """Vista por par: datos reales del mercado + estrategia validada cuando existe."""
    m = {x['par']: x for x in mer}
    pares_est = {p.get('par'): p for p in (est or {}).get('pares') or []}
    estrategias = {e.get('clave'): e for e in (est or {}).get('estrategias') or []}
    cartera = (est or {}).get('cartera') or {}
    capital = _es_num(cartera.get('capital'), 0)
    riesgo_pct = _es_num(cartera.get('riesgo_por_operacion_pct'), 2)
    riesgo_usd = _es_num(cartera.get('riesgo_usd'), 2)
    pie = (f'capital ${capital} · riesgo {riesgo_pct}% = ${riesgo_usd} · '
           '20x · PAPER ONLY')
    bloques = []
    for par in PARES_QUANTFURY:
        disp = par.replace('USDT', '')
        x = m.get(disp) or {}
        precio_s = fmt_precio(x.get('precio')) if x.get('precio') is not None else '—'
        chg_s = f'{x["cambio"]:+.2f}%' if x.get('cambio') is not None else '—'
        niv = '<div class="meta">sin niveles configurados</div>'
        if par == 'BTCUSDT' and niveles:
            top = sorted(niveles, key=lambda z: -(z.get('menciones') or 0))[:8]
            niv = ''.join(
                f'<div class="niv"><b>{fmt_precio(float(n.get("precio")))}</b>'
                f'<span class="men">x{n.get("menciones")} menciones</span></div>' for n in top)
        e = pares_est.get(par)
        if e:
            label = {'VALIDADA': 'VALIDADA', 'CON RESERVA': 'CON RESERVA',
                     'VALIDADA CON RESERVA': 'CON RESERVA', 'DÉBIL': 'DÉBIL',
                     'DEBIL': 'DÉBIL'}.get(e.get('estado'), e.get('estado') or '—')
            ed = estrategias.get(e.get('estrategia')) or {}
            nombre_est = ed.get('nombre') or e.get('estrategia') or '—'
            regla = ed.get('regla') or '—'
            if e.get('null_p') is not None:
                null_txt = (f'Null p {_es_num(e.get("null_p"), 3)} · '
                            f'seeds {e.get("seeds") or "—"}')
            else:
                null_txt = f'Null seeds {e.get("null_seeds") or "—"}'
            if e.get('wf_train') is not None:
                wf_txt = (f'WF train → test {_es_num(e.get("wf_train"), 3, True)} → '
                          f'{_es_num(e.get("wf_test"), 3, True)}')
            else:
                wf_txt = f'WF test {_es_num(e.get("wf_test"), 3, True)}'
            nota = (f'<div class="meta">{esc(e.get("nota"))}</div>'
                    if e.get('nota') else '')
            ar = (f'<div class="kpi">'
                  f'<div><span>Estado</span><b>{esc(label)}</b></div>'
                  f'<div><span>Señales/mes</span><b>{_es_num(e.get("por_mes"), 1)}</b></div>'
                  f'<div><span>E(R)</span><b>{_es_num(e.get("E_R"), 3, True)}R</b></div>'
                  f'<div><span>Acierto</span><b>{_es_num(e.get("acierto_pct"), 1)}%</b></div>'
                  f'<div><span>DD</span><b>{_es_num(e.get("dd_R"), 1)}R</b></div>'
                  f'<div><span>PF</span><b>{_es_num(e.get("pf"), 2)}</b></div>'
                  f'</div>'
                  f'<div class="meta">estrategia: {esc(nombre_est)}</div>'
                  f'<div class="meta">regla: {esc(regla)}</div>'
                  f'<div class="meta">{esc(null_txt)}</div>'
                  f'<div class="meta">{esc(wf_txt)}</div>'
                  f'{nota}')
        else:
            ar = '<div class="meta">sin estrategia validada</div>'
        bloques.append(
            f'<section class="pdetail" id="par-{esc(disp)}">'
            f'<div class="res">'
            f'<div class="shead"><h2>{esc(par)}</h2><span class="n">{esc(disp)}</span>'
            f'<span class="hint">detalle operativo</span></div>'
            f'<div class="kpi">'
            f'<div><span>Activo</span><b>{esc(disp)}</b></div>'
            f'<div><span>Precio</span><b>{esc(precio_s)}</b></div>'
            f'<div><span>Cambio 24h</span><b>{esc(chg_s)}</b></div>'
            f'<div><span>Estado</span><b>{esc(x.get("status") or "—")}</b></div>'
            f'</div>'
            f'<h3>Niveles</h3>{niv}'
            f'<h3>Estrategia validada</h3>{ar}'
            f'<div class="meta">{esc(pie)}</div>'
            f'</div></section>')
    return ''.join(bloques)


def html_senales_unificado() -> str:
    """Panel de señales unificado — SOLO operaciones con origen == 'forward'."""
    ops_fwd = []
    for nombre in ('tracker_scalein.json', 'tracker_bos.json', 'tracker_paper.json'):
        j = cargar(PILOT / 'datos' / nombre) or {}
        for o in (j.get('operaciones') or []):
            if o.get('origen') == 'forward':
                ops_fwd.append(o)
    ops_fwd.sort(key=lambda o: int(o.get('senal_ts') or 0))
    hist = ops_fwd[-10:]
    n_fwd = len(ops_fwd)
    n_act = len([o for o in hist if not str(o.get('estado') or '').startswith('CERRADA')])
    if not hist:
        items = ('<div class="vacio">Sin señales forward nuevas hoy. '
                 'El panel se carga con cada nueva señal emitida por los trackers.</div>')
    else:
        items = ''
        for o in hist:
            par = _e((o.get('par') or '').replace('USDT', ''))
            d = _e(o.get('senal_fecha') or '')
            ent = _e(o.get('entrada') or o.get('stop_inicial') or '—')
            sto = _e(o.get('stop') or o.get('stop_inicial') or '—')
            tgt = _e(o.get('target') or '—')
            ec = _e(o.get('estado') or 'ABIERTA')
            tag = 'ok' if not str(o.get('estado') or '').startswith('CERRADA') else 'muted'
            items += (f'<div class="op"><div class="h"><span>{par} · {_e(o.get("estrategia") or "")}</span>'
                       f'<span class="{tag}">{ec}</span></div>'
                       f'<div class="d">{d} · entrada {ent} · stop {sto} · tp {tgt}</div></div>')
    return (f'<div class="sg-c"><div class="mt">Señales · paper trading · FORWARD</div>'
            f'<div class="kpi"><div><span>Señales forward</span><b>{n_fwd}</b></div>'
            f'<div><span>Activas</span><b>{n_act}</b></div>'
            f'<div><span>Historial (últimas 10)</span><b>{len(hist)}</b></div></div>'
            f'{items}</div>')


def main() -> int:
    info = cargar(PILOT / 'datos' / 'informe_hoy.json') or {}
    # El resumen simple del video debe venir SIEMPRE de resumen_video.json
    # (analisis vigente), no del AGENTE_<video viejo>.json.
    rv = cargar(PILOT / 'analisis' / 'resumen_video.json') or {}
    vid = rv.get('video_id') or info.get('video_id') or ''
    niveles = rv.get('niveles') or []
    mer = mercado()
    actualizar_tracker()          # journal paper de la estrategia validada
    lec = lectura_agente(info, niveles)

    fuen = sorted({x.get('fuente', '') for x in mer if x.get('fuente')})
    cards = ''.join(mcard(x) for x in mer)
    secciones_pdetalles = _pdetalles(mer, niveles, cargar(PILOT / 'datos' / 'cartera_mixta.json'))

    ev = ''.join(f'<span class="chip">{esc(e)}</span>' for e in lec['evidencia'])
    top = [n for n in niveles[:6]]
    niv_html = ''.join(
        f'<div class="nivel"><b>{fmt_precio(float(n["precio"]))}</b>'
        f'<span>{esc(str(n.get("tipo") or ""))}</span></div>'
        for n in top) or '<div class="nota">sin niveles hoy</div>'
    ent_html = ''.join(
        f'<div class="chip">{esc(str(e.get("nombre") or ""))}: '
        f'{esc(str(e.get("detalle") or "")[:110])}</div>'
        for e in (rv.get('escenarios') or [])[:3]) or '<div class="nota">sin entradas definidas</div>'
    sesgo = esc(str(rv.get('sesgo') or '—'))

    hay_video = 'SÍ' if vid else 'NO'
    badge_cls = 'badge no' if not vid else 'badge'
    revisado = info.get('publicado', '')[:16].replace('T', ' ') or '—'
    gen = cargar(PILOT / 'datos' / 'monitor_senales.json') or {}
    tablero = (gen.get('generado') or '')[:16].replace('T', ' ').replace('Z', '') or '—'
    titulo = f'Análisis de {info.get("par") or "Mercado"}'

    modal_html = '''
<div id="modal-overlay" onclick="cerrarModal()">
  <div class="modal" onclick="event.stopPropagation()">
    <button class="modal-x" onclick="cerrarModal()" aria-label="Cerrar">×</button>
    <div id="modal-body"></div>
  </div>
</div>
<script>
document.addEventListener('click', function(ev) {
  var a = ev.target && ev.target.closest ? ev.target.closest('a.mcard-link') : null;
  if (a) { ev.preventDefault(); abrirModal(a.getAttribute('href').slice(1)); }
});
function cerrarModal() {
  var m = document.getElementById('modal-overlay');
  if (m) { m.classList.remove('open'); document.body.style.overflow = ''; }
}
function abrirModal(id) {
  var el = document.getElementById(id);
  var b = document.getElementById('modal-body');
  if (!el || !b) { return; }
  b.innerHTML = el.innerHTML;
  var m = document.getElementById('modal-overlay');
  if (m) { m.classList.add('open'); document.body.style.overflow = 'hidden'; }
}
document.addEventListener('keydown', function(ev) { if (ev.key === 'Escape') { cerrarModal(); } });
</script>
'''

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

<section class="dom-a">
  <div class="shead"><h2>Mercado Quantfury</h2><span class="n">{len(mer)} criptos operables</span><span class="hint">precio y cambio 24h</span></div>
  <div class="grid">{cards}</div>
</section>

{secciones_pdetalles}

{html_operativo()}

{html_pro()}
{html_senales_unificado()}

<section class="dom-c">
  <div class="shead"><h2>Resumen CreceTrader</h2><span class="n">lo que dice el canal</span><span class="hint">resumen diario simple</span></div>
  <div class="leer">
    {lcard('a', 'Alcista', lec['alcista'], 'var(--ok)')}
    {lcard('b', 'Bajista', lec['bajista'], 'var(--bad)')}
  </div>
  <div class="chips" style="margin-top:12px">{ev}</div>
  <div class="chips" style="margin-top:16px;flex-direction:column;align-items:stretch;gap:8px">
    <div style="font-size:12px;color:var(--muted);text-transform:uppercase;letter-spacing:.6px;margin-bottom:2px">Niveles clave</div>
    {niv_html}
  </div>
  <div class="kpi" style="margin-top:14px">
    <div><span>Sesgo</span><b>{sesgo}</b></div>
  </div>
  <div class="chips" style="margin-top:12px;flex-direction:column;align-items:stretch;gap:8px">
    <div style="font-size:12px;color:var(--muted);text-transform:uppercase;letter-spacing:.6px;margin-bottom:2px">Posibles entradas según CreceTrader</div>
    {ent_html}
  </div>
</section>

<footer>
  · Los precios son <b>reales</b> (Binance, solo lectura), caché de 5 minutos — no es un feed en vivo.<br>
  · El reparto Alcista/Bajista se calcula de los <b>niveles dichos en el video</b>: es una lectura del texto, no una predicción.<br>
  · Fuente: {esc(", ".join(f for f in fuen if f))} · video {esc(vid)}<br>
  · <span class="warn">PAPER ONLY</span> — no ejecuta órdenes. La decisión la toma el trader.
</footer>

{modal_html}

</div></body></html>'''

    out = PILOT / 'dashboard' / 'index.html'
    out.write_text(doc, encoding='utf-8')
    print(f'-> {out} ({len(doc)} B)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
