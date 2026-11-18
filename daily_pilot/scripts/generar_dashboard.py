#!/usr/bin/env python3
"""Genera daily_pilot/dashboard/index.html (autocontenido, file://).

Fuentes (solo lectura):
  - RSS del canal (si hay red) + daily_pilot/registro/registro.json
  - daily_pilot/estado/estado_hoy.json
  - daily_pilot/datos/dashboard_data.json
  - daily_pilot/analisis/<id>_analisis.json (evidencia de analisis real, si existe)

NO modifica E1, la skill, el scheduler ni los registros.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
PILOT = BASE / 'daily_pilot'
ESTADO = PILOT / 'estado' / 'estado_hoy.json'
REG = PILOT / 'registro' / 'registro.json'
DATOS = PILOT / 'datos' / 'dashboard_data.json'
ANALISIS_DIR = PILOT / 'analisis'
SALIDA = PILOT / 'dashboard' / 'index.html'
RSS = 'https://www.youtube.com/feeds/videos.xml?channel_id=UC4DOPLw9NRRBFW4wYjcWxiA'

ESTADOS = ['SIN VIDEO NUEVO', 'VIDEO NUEVO ENCONTRADO', 'ANALISIS PENDIENTE',
           'VIDEO NUEVO ANALIZADO', 'ERROR DE ANALISIS']
LITERALES = {
    'SIN VIDEO NUEVO': 'SIN VIDEO NUEVO',
    'VIDEO NUEVO ENCONTRADO': 'VIDEO NUEVO ENCONTRADO',
    'ANALISIS PENDIENTE': 'ANÁLISIS PENDIENTE',
    'VIDEO NUEVO ANALIZADO': 'VIDEO NUEVO ANALIZADO',
    'ERROR DE ANALISIS': 'ERROR DE ANÁLISIS',
}


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def hoy_utc() -> str:
    """Frontera de 'hoy' en UTC. detectado/analizado se guardan en UTC:
    comparar contra hora local (-03) invertía el estado a medianoche."""
    return datetime.now(timezone.utc).strftime('%Y-%m-%d')


def sha(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def leer_json(p: Path, default):
    try:
        return json.loads(Path(p).read_text(encoding='utf-8'))
    except Exception:
        return default


def json_seguro(obj) -> str:
    """JSON incrustable en <script type="application/json"> sin romper el HTML."""
    return json.dumps(obj, ensure_ascii=False).replace('<', '\\u003c').replace('>', '\\u003e')


def rss_ids() -> tuple[list[dict], str]:
    try:
        x = urllib.request.urlopen(RSS, timeout=20).read().decode('utf-8', 'replace')
    except Exception as exc:
        return [], f'no disponible: {exc}'
    out = []
    for e in re.findall(r'<entry>(.*?)</entry>', x, re.S):
        vid = re.search(r'<yt:videoId>([^<]+)</yt:videoId>', e)
        ti = re.search(r'<title>(.*?)</title>', e, re.S)
        pub = re.search(r'<published>([^<]+)</published>', e)
        if vid:
            out.append({'video_id': vid.group(1),
                        'titulo': re.sub(r'<[^>]+>', '', ti.group(1)) if ti else '',
                        'publicado': pub.group(1) if pub else ''})
    return out, 'ok'


def evidencia_analisis(video_id: str) -> dict | None:
    """Evidencia de analisis REAL (no basta la transcripcion)."""
    p = ANALISIS_DIR / f'{video_id}_analisis.json'
    if not p.exists():
        return None
    d = leer_json(p, None)
    if not isinstance(d, dict) or not d.get('analizado_at'):
        return None
    return {'archivo': str(p), 'analizado_at': d.get('analizado_at'),
            'n_cues': d.get('n_cues'), 'sha256': sha(p)}


def derivar_estado(no_rss: bool = False) -> dict:
    rss, red = ([], True) if no_rss else rss_ids()
    reg = leer_json(REG, {'videos': {}})['videos']
    base = leer_json(ESTADO, {})
    errores = list(base.get('errores') or [])
    ultimo = rss[0] if rss else None
    # P0-5: el "ultimo analizado" es el ULTIMO ANALISIS REAL, no el video nuevo.
    ua = base.get('ultimo_analisis_completo') or base.get('ultimo_analizado')

    comun = {'red': red, 'rss': rss, 'ultimo_analizado': ua,
             'ultimo_analisis_completo': base.get('ultimo_analisis_completo'),
             'errores': errores, 'paper_only': True,
             'situacion': base.get('situacion'), 'escenarios_estado': base.get('escenarios'),
             'macro': base.get('macro')}

    if not rss:
        return {**comun, 'estado': base.get('estado') or 'NO DISPONIBLE',
                'fuente_estado': 'estado_hoy.json (RSS no disponible)',
                'ultimo_video': base.get('video'),
                'deteccion_at': base.get('deteccion_at'), 'analisis_at': base.get('analisis_at')}

    vid = ultimo['video_id']
    if vid not in reg:
        # no esta registrado: el flujo todavia no lo detecto
        return {**comun, 'estado': 'VIDEO NUEVO ENCONTRADO',
                'fuente_estado': 'RSS + registro.json', 'ultimo_video': ultimo,
                'deteccion_at': base.get('deteccion_at'), 'analisis_at': None}

    entrada = reg[vid]
    ev = evidencia_analisis(vid)
    est_reg = (entrada.get('estado') or '').strip()
    detectado = (entrada.get('detectado') or '').strip()
    if est_reg.lower().startswith('error'):
        estado = 'ERROR DE ANALISIS'
        errores.append(f'{vid}: {est_reg}')
    elif not ev:
        estado = 'ANALISIS PENDIENTE'
    elif detectado[:10] == hoy_utc():
        estado = 'VIDEO NUEVO ANALIZADO'
    else:
        estado = 'SIN VIDEO NUEVO'

    return {**comun, 'estado': estado, 'fuente_estado': 'RSS + registro.json + evidencia',
            'ultimo_video': ultimo,
            'ultimo_analizado': (ua if ua else
                                 ({'video_id': vid, 'analizado_at': ev['analizado_at']} if ev else None)),
            'deteccion_at': detectado or None,
            'analisis_at': ev['analizado_at'] if ev else None,
            'evidencia_analisis': ev}


def estimacion_escenarios(datos: dict) -> dict:
    """Estimacion del sistema (NO calibrada con backtest).

    Formula documentada y transparente:
      por cada escenario se suman puntos:
        +2 si declara condicion de activacion
        +2 si declara entrada
        +2 si declara objetivos
        +1 por cada nivel con procedencia A (max 3)
        +1 si el veredicto del Manager no es FALTA_INFORMACION
      se agrupa por direccion (alcista / bajista / lateral) y se normaliza a 100%.
    Si el total es 0 o no hay escenarios -> NO DISPONIBLE.
    """
    escenarios = datos.get('escenarios') or []
    if not escenarios:
        return {'disponible': False, 'motivo': 'sin escenarios'}
    puntos = {'alcista': 0.0, 'bajista': 0.0, 'lateral': 0.0}
    detalle = []
    for e in escenarios:
        s = e.get('escenario') or {}
        ev = e.get('evaluacion') or {}
        dirn = (s.get('direccion') or '').lower()
        grupo = dirn if dirn in puntos else 'lateral'
        p = 0.0
        p += 2 if (s.get('condicion_activacion') or {}).get('valor') else 0
        p += 2 if (s.get('entrada') or {}).get('valor') is not None else 0
        p += 2 if s.get('objetivos') else 0
        niveles_a = [n for n in ([s.get('nivel')] + list(s.get('objetivos') or []))
                     if isinstance(n, dict) and n.get('procedencia') == 'A']
        p += min(len(niveles_a), 3)
        p += 1 if (ev.get('veredicto') or s.get('veredicto')) not in (None, 'FALTA_INFORMACION') else 0
        puntos[grupo] += p
        detalle.append({'id': s.get('id'), 'direccion': grupo, 'puntos': p})
    total = sum(puntos.values())
    if total <= 0:
        return {'disponible': False, 'motivo': 'puntuacion total 0'}
    return {
        'disponible': True,
        'metodo': 'puntuacion por evidencia declarada (condicion+2, entrada+2, objetivos+2, niveles A +1 c/u max 3, veredicto no FALTA_INFORMACION +1), normalizado a 100%',
        'advertencia': 'Estimación del sistema, no certeza. Sin calibrar con backtest.',
        'porcentajes': {k: round(v / total * 100) for k, v in puntos.items()},
        'puntos': puntos, 'detalle': detalle,
    }


def evaluacion_risk_manager() -> dict:
    """Ejecuta el Risk Manager (aislado, PAPER_ONLY) sobre el piloto real."""
    import subprocess
    rm_py = PILOT / 'risk_manager' / 'risk_manager.py'
    senales = PILOT / 'risk_manager' / 'senales_piloto_s_GjovZxQqY.json'
    if not rm_py.exists() or not senales.exists():
        return {'disponible': False, 'motivo': 'risk_manager o senales no encontrados'}
    code = ("import sys,json; sys.path.insert(0,%r); "
            "from risk_manager import evaluar_json; print(json.dumps(evaluar_json(%r),ensure_ascii=False))"
            % (str(rm_py.parent), str(senales)))
    try:
        out = subprocess.run([sys.executable, '-c', code], capture_output=True, text=True, timeout=60)
    except Exception as exc:
        return {'disponible': False, 'motivo': f'error: {exc}'}
    if out.returncode != 0:
        return {'disponible': False, 'motivo': (out.stderr or out.stdout)[:300]}
    try:
        return json.loads(out.stdout)
    except Exception as exc:
        return {'disponible': False, 'motivo': f'json invalido: {exc}'}


def metricas_piloto() -> dict:
    """Ejecuta metrics.py (PAPER_ONLY) y devuelve el calculo."""
    import subprocess
    mp = PILOT / 'metrics' / 'metrics.py'
    if not mp.exists():
        return {'disponible': False, 'motivo': 'metrics.py no encontrado'}
    try:
        out = subprocess.run([sys.executable, str(mp)], capture_output=True, text=True, timeout=60)
    except Exception as exc:
        return {'disponible': False, 'motivo': f'error: {exc}'}
    if out.returncode != 0:
        return {'disponible': False, 'motivo': (out.stderr or out.stdout)[:300]}
    try:
        return json.loads(out.stdout)
    except Exception as exc:
        return {'disponible': False, 'motivo': f'json invalido: {exc}'}


def resumen_claims() -> dict:
    """Resumen de la tabla claims del Knowledge Store (procedencia A)."""
    import sqlite3
    db = PILOT / 'knowledge' / 'store.db'
    if not db.exists():
        return {'disponible': False, 'motivo': 'store.db no encontrado'}
    try:
        c = sqlite3.connect(f'file:{db}?mode=ro', uri=True)
        por_tipo = dict(c.execute('SELECT tipo, COUNT(*) FROM claims GROUP BY tipo ORDER BY 2 DESC').fetchall())
        n = c.execute('SELECT COUNT(*) FROM claims').fetchone()[0]
        videos = c.execute('SELECT COUNT(DISTINCT video_id) FROM claims').fetchone()[0]
        proc = dict(c.execute('SELECT procedencia, COUNT(*) FROM claims GROUP BY procedencia').fetchall())
        integ = c.execute('PRAGMA integrity_check').fetchone()[0]
        c.close()
    except Exception as exc:
        return {'disponible': False, 'motivo': f'error: {exc}'}
    return {'disponible': True, 'n_claims': n, 'n_videos': videos, 'por_tipo': por_tipo,
            'procedencia': proc, 'integrity': integ}


def resumen_extra() -> dict:
    """Resumenes de C2/C3/E5/E6/seguimiento para el tablero."""
    import sqlite3
    out = {}
    rel = PILOT / 'relaciones' / 'relaciones.json'
    if rel.exists():
        d = json.loads(rel.read_text(encoding='utf-8'))
        out['relaciones'] = {'niveles_repetidos': d.get('niveles_repetidos', []),
                             'contradicciones': d.get('contradicciones', []),
                             'niveles_sin_instrumento': d.get('niveles_sin_instrumento', {}),
                             'niveles_descartados': d.get('niveles_descartados')}
    vig = PILOT / 'escenarios' / 'vigentes.json'
    if vig.exists():
        d = json.loads(vig.read_text(encoding='utf-8'))
        out['escenarios_vigentes'] = d.get('vigentes', {})
    db = PILOT / 'knowledge' / 'store.db'
    if db.exists():
        try:
            c = sqlite3.connect(f'file:{db}?mode=ro', uri=True)
            out['temporalidad'] = dict(c.execute(
                'SELECT temporalidad, COUNT(*) FROM claims GROUP BY temporalidad').fetchall())
            c.close()
        except Exception:
            pass
    seg = PILOT / 'seguimiento' / 'estados.jsonl'
    if seg.exists():
        reg = [json.loads(l) for l in seg.read_text(encoding='utf-8').splitlines() if l.strip()]
        ult = {}
        for e in reg:
            ult[e['escenario_id']] = e['estado']
        out['seguimiento'] = {'n_registros': len(reg), 'estado_actual': ult}
    return out


def datos_ultimo_analisis(video_id: str) -> dict | None:
    """Construye el detalle (mercado + escenarios) desde el ULTIMO ANALISIS real.
    Fuente primaria: daily_pilot/analisis/<video_id>_analisis.json (procedencia A)."""
    p = PILOT / 'analisis' / f'{video_id}_analisis.json'
    if not p.exists():
        return None
    try:
        d = json.loads(p.read_text(encoding='utf-8'))
    except Exception:
        return None
    insts = d.get('instrumentos') or {}
    mercado = {}
    for inst, menciones in insts.items():
        niveles = [n for n in (d.get('niveles_explicitos_top') or [])][:6]
        mercado[inst] = {
            'menciones': menciones,
            'niveles_citados': [{'valor': n.get('valor'), 'minuto': (n.get('ejemplos') or [{}])[0].get('minuto')}
                                for n in niveles],
            'procedencia': 'A',
            'fuente': f'analisis/{video_id}_analisis.json',
        }
    escenarios = []
    for n in (d.get('niveles_explicitos_top') or [])[:8]:
        ej = (n.get('ejemplos') or [{}])[0]
        escenarios.append({'nivel': n.get('valor'), 'minuto': ej.get('minuto'),
                           'contexto': ej.get('contexto'), 'procedencia': 'A',
                           'tipo': 'NIVEL_MENCIONADO'})
    return {'fuente': f'analisis/{video_id}_analisis.json', 'video_id': video_id,
            'published': None, 'generado_el': d.get('analizado_at'),
            'mercado': mercado, 'escenarios': escenarios,
            'limitaciones': d.get('limitaciones') or [],
            'procedencia_niveles': d.get('procedencia_niveles') or 'A'}


def plan_asignacion() -> dict:
    """Plan de asignacion por instrumento (C02, Francisco)."""
    sys.path.insert(0, str(PILOT / 'core'))
    import allocacion as AL
    capital = 10000.0
    out = {}
    for inst in sorted(AL.OFERTA_UNIVERSE):
        out[inst] = AL.plan(inst, capital, en_oferta=True)
    return {'capital_referencia': capital, 'planes': out, 'paper_only': AL.PAPER_ONLY}


TEMPLATE = r'''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>YouTube Analyst — Dashboard</title>
<style>
:root{--bg:#121417;--panel:#1b1f24;--panel2:#22272e;--border:#2d333b;--fg:#e6e9ee;--muted:#9aa4b0;
--blue:#4da3ff;--green:#3ecf8e;--amber:#f0b429;--red:#ff5c5c}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
.wrap{max-width:1080px;margin:0 auto;padding:22px 18px 60px}
header.top{display:flex;flex-wrap:wrap;gap:12px;align-items:center;justify-content:space-between;
background:var(--panel);border:1px solid var(--border);border-radius:14px;padding:16px 18px;margin-bottom:14px}
h1{font-size:19px;margin:0}
.aviso{font-size:12px;letter-spacing:.06em;color:var(--amber);border:1px solid var(--amber);
border-radius:8px;padding:3px 8px;text-transform:uppercase}
.estado{display:flex;align-items:center;gap:10px;margin-top:10px;font-weight:600;flex-wrap:wrap}
.badge{border-radius:10px;padding:6px 12px;font-size:13px;border:1px solid var(--border)}
.b-VERDE{color:var(--green);border-color:var(--green)} .b-AZUL{color:var(--blue);border-color:var(--blue)}
.b-AMBAR{color:var(--amber);border-color:var(--amber)} .b-ROJO{color:var(--red);border-color:var(--red)}
.b-GRIS{color:var(--muted);border-color:var(--border)}
nav.tabs{display:flex;gap:6px;flex-wrap:wrap;margin:14px 0}
.tab{background:var(--panel);border:1px solid var(--border);color:var(--fg);border-radius:10px;
padding:9px 14px;cursor:pointer;font-size:14px}
.tab.active{border-color:var(--blue);color:var(--blue)}
section{display:none}
section.active{display:block}
.card{background:var(--panel);border:1px solid var(--border);border-radius:14px;padding:16px;margin:12px 0}
.card h2{font-size:16px;margin:0 0 10px}
.row{display:flex;flex-wrap:wrap;gap:10px}
.kv{flex:1 1 200px;background:var(--panel2);border:1px solid var(--border);border-radius:10px;padding:10px 12px}
.kv label{display:block;color:var(--muted);font-size:12px}
.kv b{font-size:14px}
.pill{display:inline-block;border:1px solid var(--border);border-radius:999px;padding:1px 8px;font-size:11px;margin:1px 3px 1px 0}
.p-A{color:var(--green);border-color:var(--green)} .p-B{color:var(--blue);border-color:var(--blue)}
.p-C{color:var(--amber);border-color:var(--amber)} .p-D{color:#c792ea;border-color:#c792ea}
.p-none{color:var(--muted);border-color:var(--border)}
.missing{color:var(--muted);font-style:italic}
.btn{background:var(--panel2);border:1px solid var(--border);color:var(--fg);border-radius:9px;
padding:7px 11px;cursor:pointer;font-size:13px;margin:4px 6px 4px 0}
.btn:hover{border-color:var(--blue)}
.btn.amber:hover{border-color:var(--amber)} .btn.red:hover{border-color:var(--red)}
.foot{color:var(--muted);font-size:12px;margin-top:18px;border-top:1px solid var(--border);padding-top:10px}
.estado-item{border-left:3px solid var(--border);padding:8px 10px;margin:8px 0;background:var(--panel2);border-radius:8px}
</style>
</head>
<body>
<div class="wrap">
  <header class="top">
    <div>
      <h1>YouTube Analyst — Dashboard</h1>
      <div id="h-ultima" style="color:var(--muted);font-size:13px"></div>
    </div>
    <div style="text-align:right">
      <span class="aviso">PAPER ONLY · no ejecuta órdenes</span>
      <div id="h-hash" style="color:var(--muted);font-size:11px;margin-top:6px"></div>
    </div>
  </header>

  <div class="card" id="estado-card">
    <h2>Estado diario del YouTube Analyst</h2>
    <div class="estado"><span id="estado-badge" class="badge b-GRIS">—</span>
      <span id="estado-text" style="color:var(--muted);font-size:13px"></span></div>
    <div class="row" style="margin-top:12px" id="estado-kv"></div>
  </div>
  <div id="estimacion-card"></div>
  <div id="risk-card"></div>
  <div id="metrics-card"></div>
  <div id="alloc-card"></div>
  <div id="claims-card"></div>
  <div id="relaciones-card"></div>
  <div id="escenarios-card"></div>
  <div id="temporalidad-card"></div>
  <div id="seguimiento-card"></div>

  <nav class="tabs">
    <button class="tab active" data-tab="mercado">MERCADO</button>
    <button class="tab" data-tab="planes">PLANES</button>
    <button class="tab" data-tab="manager">MANAGER</button>
    <button class="tab" data-tab="seguimiento">SEGUIMIENTO</button>
    <button class="tab" data-tab="decision">DECISIÓN</button>
  </nav>

  <section id="mercado" class="active"></section>
  <section id="planes"></section>
  <section id="manager"></section>
  <section id="seguimiento"></section>
  <section id="decision"></section>

  <div class="foot" id="pie"></div>
</div>

<script type="application/json" id="estado-data">__ESTADO__</script>
<script type="application/json" id="detalle-data">__DATOS__</script>
<script>
var ESTADO = JSON.parse(document.getElementById('estado-data').textContent);
var DATOS  = JSON.parse(document.getElementById('detalle-data').textContent);
var ND = 'NO DISPONIBLE';
function esc(s){return (s==null?'':String(s)).replace(/[&<>]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;'}[c];});}
function prov(p){ if(!p) return '<span class="pill p-none">SIN PROCEDENCIA</span>';
  var m={A:'p-A',B:'p-B',C:'p-C',D:'p-D'}; return '<span class="pill '+(m[p]||'p-none')+'">'+esc(p)+'</span>'; }
function lista(arr){ if(!arr||!arr.length) return '<span class="missing">'+ND+'</span>';
  return arr.map(esc).join(' · '); }
function kv(k,v,raw){ if(v==null||v===''){return '<div class="kv"><label>'+esc(k)+'</label><b><span class="missing">'+ND+'</span></b></div>';}
  return '<div class="kv"><label>'+esc(k)+'</label><b>'+(raw?v:esc(v))+'</b></div>'; }
var LIT={'SIN VIDEO NUEVO':'SIN VIDEO NUEVO','VIDEO NUEVO ENCONTRADO':'VIDEO NUEVO ENCONTRADO',
 'ANALISIS PENDIENTE':'ANÁLISIS PENDIENTE','VIDEO NUEVO ANALIZADO':'VIDEO NUEVO ANALIZADO',
 'ERROR DE ANALISIS':'ERROR DE ANÁLISIS'};
function badge(estado){
  var c={'SIN VIDEO NUEVO':'b-AZUL','VIDEO NUEVO ENCONTRADO':'b-AMBAR','ANALISIS PENDIENTE':'b-AMBAR',
         'VIDEO NUEVO ANALIZADO':'b-VERDE','ERROR DE ANALISIS':'b-ROJO'}[estado]||'b-GRIS';
  return '<span class="badge '+c+'">'+esc(LIT[estado]||estado)+'</span>';
}
function decs(){ try{return JSON.parse(localStorage.getItem('ytra_dashboard_decisions_v2'))||{};}catch(e){return {};} }
function estadoEsc(id){
  var d=(decs()[id]||{});
  if(d.resultado==='objetivo_alcanzado') return 'OBJETIVO_ALCANZADO';
  if(d.resultado==='invalidado') return 'INVALIDADO';
  if(d.resultado==='expirado') return 'EXPIRADO';
  if(d.decision==='operar_manual') return 'ACTIVADO';
  if(d.decision==='seguimiento') return 'EN_SEGUIMIENTO';
  if(d.decision==='esperar') return 'ESPERANDO_ACTIVACION';
  return 'EN_OBSERVACION';
}

(function(){
  document.getElementById('h-ultima').textContent = 'Última revisión: '+(ESTADO.ultima_revision||ND);
  document.getElementById('h-hash').textContent = 'estado '+(ESTADO.hash_estado||'—')+' · datos '+(ESTADO.hash_datos||'—');
  document.getElementById('estado-badge').outerHTML = badge(ESTADO.estado);
  document.getElementById('estado-text').textContent = 'Fuente: '+(ESTADO.fuente_estado||ND)+
    (ESTADO.red&&ESTADO.red!=='ok'?' · red: '+ESTADO.red:'');
  var v=ESTADO.ultimo_video||{};
  var h = kv('Estado', LIT[ESTADO.estado]||ESTADO.estado) +
    kv('ID', v.video_id) + kv('Título', v.titulo) + kv('Publicado', v.publicado) +
    kv('Última revisión', ESTADO.ultima_revision) +
    kv('Detección', ESTADO.deteccion_at) + kv('Análisis', ESTADO.analisis_at) +
    kv('Enlace', v.url?('<a href="'+esc(v.url)+'" target="_blank" style="color:var(--blue)">ver video</a>'):null, true);
  if (ESTADO.errores && ESTADO.errores.length) h += kv('Errores', ESTADO.errores.join(' · '));
  if (ESTADO.evidencia_analisis) h += kv('Evidencia de análisis', ESTADO.evidencia_analisis.archivo);
  document.getElementById('estado-kv').innerHTML = h;
})();

(function(){
  var e=ESTADO.estimacion||{};
  var out='<div class="card"><h2>Escenarios comparados — estimación del sistema</h2>';
  if(!e.disponible){ out+='<span class="missing">NO DISPONIBLE'+(e.motivo?' · '+esc(e.motivo):'')+'</span>'; }
  else{
    var col={alcista:'var(--green)',bajista:'var(--red)',lateral:'var(--amber)'};
    ['alcista','bajista','lateral'].forEach(function(k){
      out+='<div style="margin-top:10px"><div style="display:flex;justify-content:space-between">'+
        '<b style="color:'+col[k]+'">'+k.charAt(0).toUpperCase()+k.slice(1)+'</b>'+
        '<b>'+esc(e.porcentajes[k])+'%</b></div>'+
        '<div style="background:var(--panel2);border:1px solid var(--border);border-radius:8px;height:10px;margin-top:4px">'+
        '<div style="width:'+esc(e.porcentajes[k])+'%;background:'+col[k]+';height:10px;border-radius:8px"></div></div></div>';
    });
    out+='<div style="color:var(--amber);font-size:12px;margin-top:8px">'+esc(e.advertencia)+'</div>'+
         '<div style="color:var(--muted);font-size:12px;margin-top:4px">Método: '+esc(e.metodo)+'</div>'+
         '<div style="color:var(--muted);font-size:12px;margin-top:4px">Puntos: '+esc(JSON.stringify(e.puntos))+'</div>';
  }
  out+='</div>'; document.getElementById('estimacion-card').innerHTML=out;
})();

(function(){
  var r=ESTADO.risk_manager||{};
  var out='<div class="card"><h2>Risk Manager <span class="badge blue">PAPER ONLY · no ejecuta órdenes</span></h2>';
  if(!r.disponible && r.paper_only===undefined && !r.decision){
    out+='<span class="missing">NO DISPONIBLE'+(r.motivo?' · '+esc(r.motivo):'')+'</span></div>';
    document.getElementById('risk-card').innerHTML=out; return;
  }
  var col={'ACEPTAR':'var(--green)','RECHAZAR':'var(--red)','REVISION MANUAL':'var(--amber)','NO_EVALUABLE':'var(--muted)'};
  out+='<div style="display:flex;gap:18px;flex-wrap:wrap;margin-top:8px">'+
    '<div><span class="muted">Decisión</span><br><b style="color:'+(col[r.decision]||'var(--muted)')+'">'+esc(r.decision)+'</b></div>'+
    '<div><span class="muted">Exposición total</span><br><b>'+esc(r.exposicion_total!=null?('$'+r.exposicion_total):'NO DISPONIBLE')+'</b></div>'+
    '<div><span class="muted">Por nivel</span><br><b>'+esc(JSON.stringify(r.por_nivel||{}))+'</b></div></div>';
  out+='<div style="color:var(--muted);font-size:12px;margin-top:6px">Niveles: nivel informativo (mencionado) · escenario (zona/condicional) · candidata (señal explícita) · no operable. El Manager cuantifica escenarios y candidatas; no activa operaciones.</div>';
  if((r.razones||[]).length){ out+='<div style="margin-top:8px">'; (r.razones||[]).forEach(function(x){out+='<div style="color:var(--amber);font-size:13px">'+esc(x)+'</div>';}); out+='</div>'; }
  out+='<div style="margin-top:10px">';
  (r.senales||[]).forEach(function(s){
    out+='<div style="border-top:1px solid var(--border);padding:8px 0">'+
      '<div style="display:flex;justify-content:space-between;flex-wrap:wrap"><b>'+esc(s.id)+'</b>'+
      '<span style="color:'+(col[s.decision]||'var(--muted)')+'">'+esc(s.decision)+'</span></div>'+
      '<div style="color:var(--muted);font-size:12px">'+esc(s.instrument||'')+' · '+esc(s.direction||'')+' · nivel '+esc(s.nivel||'')+
      (s.tipo?' · '+esc(s.tipo):'')+'</div>';
    if(s.razones && s.razones.length){ s.razones.forEach(function(x){ out+='<div style="color:var(--amber);font-size:12px">· '+esc(x)+'</div>'; }); }
    if(s.risk && s.risk.perdida_potencial!=null){
      out+='<div style="color:var(--muted);font-size:12px;margin-top:2px">Riesgo/unidad '+esc(s.risk.risk_per_unit)+' · tamaño '+esc(s.risk.position_size)+
        ' · pérdida potencial '+esc(s.risk.perdida_potencial)+' · R múltiplos '+esc(JSON.stringify(s.risk.r_multiples||[]))+'</div>';
    }
    out+='</div>';
  });
  out+='</div></div>';
  document.getElementById('risk-card').innerHTML=out;
})();

(function(){
  var m=ESTADO.metricas||{};
  var out='<div class="card"><h2>Métricas del piloto <span class="badge blue">PAPER ONLY · sin backtest</span></h2>';
  if(!m.paper_only && m.decision===undefined && !m.n_senales){
    out+='<span class="missing">NO DISPONIBLE'+(m.motivo?' · '+esc(m.motivo):'')+'</span></div>';
    document.getElementById('metrics-card').innerHTML=out; return;
  }
  var kv=[['Señales registradas',m.n_senales],['Resultados reales',m.n_resultados],
          ['Tasa de acierto',m.tasa_acierto!=null?m.tasa_acierto:'NO DISPONIBLE'],
          ['R medio',m.r_medio!=null?m.r_medio:'NO DISPONIBLE'],
          ['Expectativa',m.expectativa!=null?m.expectativa:'NO DISPONIBLE'],
          ['Drawdown máx',m.drawdown_max!=null?m.drawdown_max:'NO DISPONIBLE']];
  out+='<div style="display:flex;gap:18px;flex-wrap:wrap;margin-top:8px">';
  kv.forEach(function(x){ out+='<div><span class="muted">'+x[0]+'</span><br><b>'+esc(String(x[1]))+'</b></div>'; });
  out+='</div>';
  if(m.expectativa_teorica_r!=null){
    out+='<div style="color:var(--amber);font-size:13px;margin-top:8px">Expectativa TEÓRICA (R múltiplos declarados): '+
      esc(String(m.expectativa_teorica_r))+'</div>';
  }
  out+='<div style="color:var(--muted);font-size:12px;margin-top:6px">'+esc(m.advertencia||m.motivo||'')+'</div></div>';
  document.getElementById('metrics-card').innerHTML=out;
})();

(function(){
  var a=ESTADO.asignacion||{}; var planes=a.planes||{};
  var out='<div class="card"><h2>Asignación por instrumento <span class="badge blue">C02 · 30% oferta / 70% confirmación</span></h2>';
  out+='<div style="color:var(--muted);font-size:12px">Capital de referencia $'+esc(String(a.capital_referencia))+
    ' · PAPER ONLY · no ejecuta órdenes · topes por activo según C02</div><div style="margin-top:8px">';
  Object.keys(planes).forEach(function(k){
    var p=planes[k];
    var tramos=(p.tramos||[]).map(function(t){return esc(String(Math.round(t.porcentaje*100))+'% $'+t.monto+' ('+t.zona+')');}).join(' · ');
    out+='<div style="display:flex;justify-content:space-between;border-top:1px solid var(--border);padding:5px 0;gap:10px">'+
      '<span><b>'+esc(k)+'</b> <span style="color:var(--muted)">'+esc(p.tipo)+'</span></span>'+
      '<span style="color:var(--muted)">máx '+esc(String(Math.round(p.allocacion_maxima*100)))+'% · '+tramos+'</span></div>';
  });
  out+='</div><div style="color:var(--muted);font-size:12px;margin-top:6px">Las 5 del proyecto (BTCUSD, ETHUSD, SPX, QQQ, XAUUSD) se compran en oferta. Cualquier otro activo: solo en tendencia. ADA y otros fuera del universo.</div></div>';
  document.getElementById('alloc-card').innerHTML=out;
})();

(function(){
  var c=ESTADO.claims||{};
  var out='<div class="card"><h2>Claims extraídos del Knowledge Store</h2>';
  if(!c.disponible){
    out+='<span class="missing">NO DISPONIBLE'+(c.motivo?' · '+esc(c.motivo):'')+'</span></div>';
    document.getElementById('claims-card').innerHTML=out; return;
  }
  out+='<div style="display:flex;gap:18px;flex-wrap:wrap;margin-top:8px">'+
    '<div><span class="muted">Claims</span><br><b>'+esc(String(c.n_claims))+'</b></div>'+
    '<div><span class="muted">Vídeos</span><br><b>'+esc(String(c.n_videos))+'</b></div>'+
    '<div><span class="muted">Procedencia</span><br><b>'+esc(JSON.stringify(c.procedencia||{}))+'</b></div>'+
    '<div><span class="muted">Integrity</span><br><b>'+esc(String(c.integrity))+'</b></div></div>';
  out+='<div style="margin-top:10px"><span class="muted">Por tipo</span><div style="margin-top:6px">';
  Object.keys(c.por_tipo||{}).forEach(function(k){
    out+='<div style="display:flex;justify-content:space-between;border-top:1px solid var(--border);padding:5px 0">'+
      '<span>'+esc(k)+'</span><b>'+esc(String(c.por_tipo[k]))+'</b></div>';
  });
  out+='</div></div>';
  out+='<div style="color:var(--muted);font-size:12px;margin-top:8px">Procedencia A = DICHO por CreceTrader (transcripción). No incluye B (observado), C (calculado) ni D (Manager): el extractor no los infiere.</div></div>';
  document.getElementById('claims-card').innerHTML=out;
})();

(function(){
  var x=ESTADO.extra||{};
  /* --- relaciones --- */
  var r=x.relaciones||{};
  var out='<div class="card"><h2>Niveles repetidos entre vídeos</h2>';
    out+='<div style="color:var(--muted);font-size:12px">Descartados por filtro de plausibilidad: '+
    esc(String(r.niveles_descartados!=null?r.niveles_descartados:'NO DISPONIBLE'))+'</div><div style="margin-top:8px">';
  var si=r.niveles_sin_instrumento||{};
  var nsi=Object.keys(si).reduce(function(a,k){return a+si[k];},0);
  if(nsi>0){
    out+='<div style="color:var(--amber);font-size:12px;margin-bottom:6px">'+esc(String(nsi))+
      ' niveles SIN instrumento (no se asignan a ciegas) — por video: '+
      esc(JSON.stringify(si))+'</div>';
  }
  (r.niveles_repetidos||[]).forEach(function(n){
    out+='<div style="display:flex;justify-content:space-between;border-top:1px solid var(--border);padding:5px 0">'+
      '<span>'+esc(n.instrumento)+' <b>'+esc(String(n.nivel_aproximado))+'</b></span>'+
      '<span style="color:var(--muted)">'+esc(String(n.n_videos))+' vídeos</span></div>';
  });
  if(!(r.niveles_repetidos||[]).length){ out+='<span class="missing">NO DISPONIBLE</span>'; }
  out+='</div>';
  var cc=(r.contradicciones||[]).length;
  out+='<div style="margin-top:8px;color:'+(cc?'var(--red)':'var(--muted)')+'">Contradicciones: '+esc(String(cc))+'</div></div>';
  document.getElementById('relaciones-card').innerHTML=out;
  /* --- escenarios vigentes --- */
  var v=x.escenarios_vigentes||{};
  var out2='<div class="card"><h2>Escenarios vigentes por instrumento (última versión)</h2>';
  var keys=Object.keys(v);
  if(!keys.length){ out2+='<span class="missing">NO DISPONIBLE</span>'; }
  keys.forEach(function(inst){
    out2+='<div style="margin-top:10px"><b>'+esc(inst)+'</b><div style="margin-top:4px">';
    (v[inst]||[]).forEach(function(e){
      var col=e.sentido==='alcista'?'var(--green)':(e.sentido==='bajista'?'var(--red)':'var(--muted)');
      out2+='<div style="display:flex;justify-content:space-between;border-top:1px solid var(--border);padding:4px 0">'+
        '<span>'+esc(String(e.nivel))+' <span style="color:'+col+'">'+esc(e.sentido)+'</span></span>'+
        '<span style="color:var(--muted)">'+esc(e.fecha)+' · '+esc(e.video_id)+'</span></div>';
    });
    out2+='</div></div>';
  });
  out2+='<div style="color:var(--muted);font-size:12px;margin-top:8px">No es recomendación. Historial completo en daily_pilot/escenarios/historial.json</div></div>';
  document.getElementById('escenarios-card').innerHTML=out2;
  /* --- temporalidad --- */
  var t=x.temporalidad||{};
  var out3='<div class="card"><h2>Temporalidad declarada en los claims</h2><div style="display:flex;gap:16px;flex-wrap:wrap;margin-top:8px">';
  Object.keys(t).forEach(function(k){ out3+='<div><span class="muted">'+esc(k)+'</span><br><b>'+esc(String(t[k]))+'</b></div>'; });
  out3+='</div><div style="color:var(--muted);font-size:12px;margin-top:8px">Clasificación por declaración explícita en el texto; "neutro" = no declara temporalidad.</div></div>';
  document.getElementById('temporalidad-card').innerHTML=out3;
  /* --- seguimiento --- */
  var s=x.seguimiento||{};
  var out4='<div class="card"><h2>Seguimiento de escenarios <span class="badge blue">PAPER ONLY</span></h2>';
  out4+='<div style="color:var(--muted);font-size:13px">Registros: '+esc(String(s.n_registros!=null?s.n_registros:0))+'</div>';
  var ea=s.estado_actual||{};
  var ks=Object.keys(ea);
  if(!ks.length){ out4+='<span class="missing">SIN REGISTROS — los estados se cargan al confirmar seguimiento (no automático)</span>'; }
  ks.forEach(function(k){
    out4+='<div style="display:flex;justify-content:space-between;border-top:1px solid var(--border);padding:5px 0">'+
      '<span>'+esc(k)+'</span><b>'+esc(ea[k])+'</b></div>';
  });
  out4+='</div>';
  document.getElementById('seguimiento-card').innerHTML=out4;
})();

(function(){
  var d=ESTADO.detalle||{};
  var banner='';
  if(d.tipo==='fallback'){
    banner='<div style="background:var(--red);color:#fff;padding:8px 12px;border-radius:8px;font-size:13px;margin-bottom:10px">'
      +esc(d.banner||'DETALLE DE OTRO VIDEO')+'</div>';
  } else if(d.tipo==='analisis'){
    banner='<div style="background:var(--panel2);border:1px solid var(--border);padding:6px 12px;border-radius:8px;font-size:12px;margin-bottom:10px;color:var(--muted)">'
      +'Detalle del análisis: '+esc(String(d.video_id||'NO DISPONIBLE'))+' · generado '+esc(String(d.generado_el||'NO DISPONIBLE'))+'</div>';
  }
  var m = DATOS.mercado||{}; var orden=['BTCUSD','ETHUSD','SPX','QQQ','XAUUSD'];
  var out=banner+'<div class="card"><h2>Mercado</h2><div style="color:var(--muted);font-size:13px;margin-bottom:10px">Fuente: '+
    esc(DATOS.fuente||ND)+' · '+esc(DATOS.aviso||'')+'</div>';
  orden.forEach(function(k){ var x=m[k]; if(!x) return;
    out+='<div class="card"><h2>'+esc(k)+'</h2><div class="row">'+
      kv('Precio de referencia', (x.precio_referencia&&x.precio_referencia.valor!=null)?x.precio_referencia.valor:null)+
      kv('Procedencia', prov(x.precio_referencia&&x.precio_referencia.procedencia), true)+
      kv('Actualización', x.actualizacion)+
      '</div><div class="row" style="margin-top:10px">'+
      kv('Weekly', x.tendencia_weekly)+kv('Daily', x.contexto_diario)+kv('4H', x.estructura_4h)+'</div>'+
      '<div style="margin-top:10px">Niveles originales: '+lista(x.niveles_originales)+'<br>'+
      'Niveles calculados: '+lista(x.niveles_calculados)+'<br>Zonas de liquidez: '+lista(x.zonas_liquidez)+'<br>'+
      'Escenario alcista: '+esc(x.escenario_alcista||ND)+'<br>Escenario bajista: '+esc(x.escenario_bajista||ND)+
      (x.precio_referencia&&x.precio_referencia.nota?'<div style="color:var(--muted);font-size:12px;margin-top:6px">'+esc(x.precio_referencia.nota)+'</div>':'')+
      '</div></div>';
  });
  out+='</div>';
  if (ESTADO.situacion) {
    var s=ESTADO.situacion;
    out+='<div class="card"><h2>Situación y contexto (estado diario)</h2><div class="row">'+
      kv('Frase', s.frase)+kv('Instrumento', s.instrumento)+kv('Temporalidad', s.temporalidad)+
      kv('Escenario principal', s.escenario_principal)+kv('Próximo control', s.proximo_control)+
      kv('Invalidación', s.invalidacion)+kv('Evidencia (video·min)', s.evidencia_video_min)+'</div></div>';
  }
  if (ESTADO.macro) {
    var mc=ESTADO.macro;
    out+='<div class="card"><h2>Contexto macro y fundamental</h2>'+
      '<div style="margin-top:6px"><b>Mencionado por CreceTrader</b><br>'+lista(mc.mencionado_por_crecetrader)+'</div>'+
      '<div style="margin-top:6px"><b>Hechos externos documentados</b><br>'+lista(mc.hechos_externos)+'</div>'+
      '<div style="margin-top:6px"><b>No determinado</b><br>'+lista(mc.no_determinado)+'</div></div>';
  }
  document.getElementById('mercado').innerHTML=out;
})();

(function(){
  var out='<div class="card"><h2>Planes — escenarios del YouTube Analyst</h2>'+
    '<div style="color:var(--muted);font-size:13px">Original del Analyst, separado del Manager.</div></div>';
  (DATOS.escenarios||[]).forEach(function(e){
    var s=e.escenario||{};
    out+='<div class="card"><div class="row">'+
      kv('ID', s.id)+kv('Instrumento', s.instrumento)+kv('Dirección', s.direccion)+
      kv('Temporalidades', (s.temporalidades||[]).join(', '))+kv('Clasificación', s.clasificacion)+'</div>'+
      '<div class="row" style="margin-top:10px">'+
      kv('Nivel', (s.nivel&&s.nivel.valor!=null)?s.nivel.valor:null)+prov(s.nivel&&s.nivel.procedencia)+
      kv('Entrada', (s.entrada&&s.entrada.valor!=null)?s.entrada.valor:null)+prov(s.entrada&&s.entrada.procedencia)+
      kv('Stop/Invalidación (Analyst)', (s.stop&&s.stop.valor!=null)?s.stop.valor:'no declarado')+'</div>'+
      '<div style="margin-top:10px">Justificación: '+esc(s.justificacion||ND)+'<br>'+
      'Evidencia del video: '+lista(s.evidencia)+'<br>'+
      'Condición de activación: '+esc((s.condicion_activacion&&s.condicion_activacion.valor)||ND)+'<br>'+
      'Objetivos: '+lista((s.objetivos||[]).map(function(o){return o.valor;}))+'<br>'+
      'Método de cálculo: '+esc(s.metodo_calculo||ND)+'<br>'+
      'Video de origen: '+esc(s.video_id||ND)+' · '+esc(s.timestamp_explicacion||ND)+'<br>'+
      'Información faltante: '+lista(s.info_faltante)+'</div></div>';
  });
  document.getElementById('planes').innerHTML=out;
})();

(function(){
  var out='<div class="card"><h2>Manager — evaluación independiente</h2>'+
    '<div style="color:var(--muted);font-size:13px">Propuestas del Manager, no decisiones ejecutadas.</div></div>';
  (DATOS.escenarios||[]).forEach(function(e){
    var s=e.escenario||{}; var ev=e.evaluacion||{}; var d=ev.dimensiones||{}; var ry=d.riesgo_y_capital||{};
    out+='<div class="card"><div class="row">'+kv('Escenario', ev.escenario_id||s.id)+kv('Veredicto', ev.veredicto||s.veredicto)+'</div>'+
      '<div class="row" style="margin-top:10px">'+
      kv('Calidad del análisis', d.calidad_analisis)+kv('Completitud', d.completitud_plan)+
      kv('Viabilidad técnica', d.viabilidad_tecnica)+kv('Riesgo y capital', ry.veredicto)+'</div>'+
      '<div style="margin-top:10px">Motivos: '+lista(ev.motivos)+'<br>Condiciones faltantes: '+lista(ev.condiciones_faltantes)+
      '<br>Qué necesita: '+esc(ev.que_se_necesita||ND)+'<br>'+
      'Propuesta de stop: '+(ev.propuesta_stop?esc(ev.propuesta_stop.valor)+' ('+esc(ev.propuesta_stop.metodo)+')':ND)+
      '<br>Riesgo/beneficio: '+esc(ev.risk_reward||ND)+'<br>Capital: '+esc(ev.capital?JSON.stringify(ev.capital):null)+
      '<br>Decisión del usuario: '+esc(ev.decision_usuario||'pendiente')+'</div></div>';
  });
  document.getElementById('manager').innerHTML=out;
})();

function renderSeguimiento(){
  var out='<div class="card"><h2>Seguimiento por escenario</h2>'+
    '<div style="color:var(--muted);font-size:13px">Tocar un nivel NO activa la operación. La activación depende de la condición del escenario.</div>';
  (DATOS.escenarios||[]).forEach(function(e){
    var s=e.escenario||{}; var ev=e.evaluacion||{};
    var st=estadoEsc(s.id);
    var inval=(s.stop&&s.stop.valor!=null)?esc(s.stop.valor):'sin stop declarado por el Analyst'+
      (ev.propuesta_stop?' · propuesta Manager: '+esc(ev.propuesta_stop.valor)+' ('+prov(ev.propuesta_stop.procedencia)+')':'');
    out+='<div class="estado-item"><b>'+esc(s.id||'')+'</b> · '+esc(s.instrumento||'')+' · '+esc(s.direccion||'')+
      '<div style="color:var(--muted);font-size:12px;margin-top:4px">Condición: '+
      esc((s.condicion_activacion&&s.condicion_activacion.valor)||ND)+'</div>'+
      '<div style="color:var(--muted);font-size:12px;margin-top:4px">Invalidación: '+inval+'</div>'+
      '<div class="pill pill-estado" style="margin-top:6px">'+esc(st)+'</div></div>';
  });
  out+='</div>'; document.getElementById('seguimiento').innerHTML=out;
}

function renderDecision(){
  var LS='ytra_dashboard_decisions_v2';
  function load(){ try{return JSON.parse(localStorage.getItem(LS))||{};}catch(e){return {};} }
  function save(d){ try{localStorage.setItem(LS,JSON.stringify(d));}catch(e){} }
  function pinta(id){ var d=load()[id]||{}; var el=document.getElementById('dec-'+id); if(!el) return;
    el.textContent='Actual: '+(d.decision||'sin decisión')+(d.resultado?' · '+d.resultado:''); }
  var out='<div class="card"><h2>Decisión del usuario (local)</h2>'+
    '<div style="color:var(--muted);font-size:13px">Manual y local. No ejecuta operaciones.</div>';
  (DATOS.escenarios||[]).forEach(function(e){
    var id=(e.escenario||{}).id;
    out+='<div class="card"><b>'+esc(id)+'</b><div style="margin-top:8px">'+
      '<button class="btn" onclick="decAct(\''+esc(id)+'\',\'seguimiento\')">Aceptar seguimiento</button>'+
      '<button class="btn amber" onclick="decAct(\''+esc(id)+'\',\'esperar\')">Esperar</button>'+
      '<button class="btn" onclick="decAct(\''+esc(id)+'\',\'operar_manual\')">Operar manualmente</button>'+
      '<button class="btn red" onclick="decAct(\''+esc(id)+'\',\'descartar\')">Descartar</button></div>'+
      '<div style="margin-top:8px">'+
      '<button class="btn" onclick="decRes(\''+esc(id)+'\',\'objetivo_alcanzado\')">Objetivo alcanzado</button>'+
      '<button class="btn red" onclick="decRes(\''+esc(id)+'\',\'invalidado\')">Invalidado</button>'+
      '<button class="btn" onclick="decRes(\''+esc(id)+'\',\'expirado\')">Expirado</button></div>'+
      '<div id="dec-'+esc(id)+'" style="color:var(--muted);font-size:12px;margin-top:6px">Actual: sin decisión</div></div>';
  });
  out+='</div>'; document.getElementById('decision').innerHTML=out;
  (DATOS.escenarios||[]).forEach(function(e){ pinta((e.escenario||{}).id); });
  window._decLoad=load; window._decSave=save; window._decPinta=pinta;
}
window.decAct=function(id,accion){ var d=window._decLoad(); d[id]=d[id]||{}; d[id].decision=accion; d[id].ts=new Date().toISOString(); window._decSave(d);
  renderDecision(); renderSeguimiento(); };
window.decRes=function(id,res){ var d=window._decLoad(); d[id]=d[id]||{}; d[id].resultado=res; d[id].ts=new Date().toISOString(); window._decSave(d);
  renderDecision(); renderSeguimiento(); };
renderDecision();
renderSeguimiento();

document.querySelectorAll('.tab').forEach(function(t){
  t.addEventListener('click',function(){
    document.querySelectorAll('.tab').forEach(function(x){x.classList.remove('active');});
    document.querySelectorAll('section').forEach(function(x){x.classList.remove('active');});
    t.classList.add('active'); document.getElementById(t.dataset.tab).classList.add('active');
  });
});

document.getElementById('pie').innerHTML =
  'PAPER ONLY · no ejecuta órdenes · sin servidor (file://) · datos: dashboard_data.json + estado_hoy.json · '+
  'generado '+esc(ESTADO.generado_el||'')+' · hash estado '+esc(ESTADO.hash_estado||'—')+' · hash datos '+esc(ESTADO.hash_datos||'—');
</script>
</body>
</html>
'''


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--no-rss', action='store_true',
                    help='no usa red: estado derivado de estado_hoy.json/registro (auditable offline)')
    ap.add_argument('--check', action='store_true',
                    help='NO escribe el HTML: solo deriva y reporta (auditoria read-only)')
    args = ap.parse_args()
    estado = derivar_estado(no_rss=args.no_rss)
    estado['ultima_revision'] = now_iso()
    estado['generado_el'] = now_iso()
    estado['hash_estado'] = sha(ESTADO)[:16] if ESTADO.exists() else '—'
    estado['hash_datos'] = sha(DATOS)[:16] if DATOS.exists() else '—'
    if estado['estado'] not in ESTADOS:
        estado['estado'] = 'NO DISPONIBLE'
    datos = leer_json(DATOS, {'mercado': {}, 'escenarios': []})
    # CONTRATO: el detalle debe poder leerse por separado del estado.
    ua = estado.get('ultimo_analisis_completo') or {}
    # H-01/H-05 FIX: el detalle sale del ULTIMO ANALISIS; dashboard_data.json es solo fallback.
    da = datos_ultimo_analisis(ua.get('video_id')) if ua.get('video_id') else None
    if da:
        datos = da
        detalle = {'tipo': 'analisis', 'video_id': da.get('video_id'),
                   'fuente': da.get('fuente'), 'published': da.get('published'),
                   'generado_el': da.get('generado_el')}
    else:
        _fuente = str(datos.get('fuente') or '')
        _vid_detalle = _fuente.split()[0] if _fuente else None
        _datos = dict(datos)
        _datos.setdefault('video_id', _vid_detalle)
        if not _datos.get('published'):
            _datos['published'] = _fuente.split('(')[-1].rstrip(')') if '(' in _fuente else None
        datos_ok = bool(_datos.get('mercado')) and bool(_datos.get('escenarios'))
        if datos_ok:
            _pub = _datos.get('published') or 'fecha no declarada'
            detalle = {'tipo': 'fallback', 'video_id': _datos.get('video_id'),
                       'fuente': _datos.get('fuente'), 'published': _datos.get('published'),
                       'generado_el': _datos.get('generado_el') or _datos.get('actualizacion'),
                       'banner': f"DETALLE DE OTRO VIDEO · {_datos.get('video_id')} · {_pub}"}
        else:
            detalle = {'tipo': 'no_disponible', 'video_id': None, 'fuente': None,
                       'published': None, 'generado_el': None}
    estado['detalle'] = detalle
    estado['estimacion'] = estimacion_escenarios(datos)
    estado['risk_manager'] = evaluacion_risk_manager()
    estado['metricas'] = metricas_piloto()
    estado['claims'] = resumen_claims()
    estado['extra'] = resumen_extra()
    estado['asignacion'] = plan_asignacion()

    if args.check:
        print('=== MODO CHECK (no escribe) ===')
        print(f'estado      : {estado.get("estado")}')
        print(f'detalle     : {json.dumps(estado.get("detalle"), ensure_ascii=False)}')
        print(f'instrumentos: {sorted((datos.get("mercado") or {}).keys())}')
        print(f'escenarios  : {len(datos.get("escenarios") or [])}')
        print(f'claims      : {(estado.get("claims") or {}).get("n_claims")}')
        return 0

    html = TEMPLATE.replace('__ESTADO__', json_seguro(estado)).replace('__DATOS__', json_seguro(datos))
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(html, encoding='utf-8')
    print(f'estado: {estado["estado"]} | video: {(estado.get("ultimo_video") or {}).get("video_id")}')
    print(f'salido: {SALIDA} ({SALIDA.stat().st_size} bytes)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
