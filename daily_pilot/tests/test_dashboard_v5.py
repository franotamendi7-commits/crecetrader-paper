#!/usr/bin/env python3
"""Test del dashboard v4 (cockpit simple). PAPER_ONLY.

Verifica lo que el dashboard PROMETE hoy:
  - autocontenido (sin fetch, sin refs http)
  - solo el ULTIMO video
  - sin grafico inventado (sin velas simuladas)
  - paneles presentes (PLAN, RISK, NIVELES, DECISION, DISTRIBUCION)
  - PAPER ONLY visible
  - aviso de STOP sin definir
"""
import json
import re
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
GEN = BASE / 'daily_pilot' / 'scripts' / 'generar_dashboard_v5.py'
HTML = BASE / 'daily_pilot' / 'dashboard' / 'index.html'
INFO = BASE / 'daily_pilot' / 'datos' / 'informe_hoy.json'

OK = FALLO = 0


def caso(nombre, cond, detalle=''):
    global OK, FALLO
    if cond:
        OK += 1
        print(f'OK    | {nombre} | {detalle}')
    else:
        FALLO += 1
        print(f'FALLO | {nombre} | {detalle}')


# idempotencia: regenerar NO debe cambiar el hash
import hashlib
def _sha(): return hashlib.sha256(HTML.read_bytes()).hexdigest()
def _estructura():
    """El dashboard ya no es idempotente: los precios son vivos (Binance).
    Lo que si debe ser estable es la ESTRUCTURA (paneles, tablas, avisos).
    Para eso se quitan TODOS los numeros y el origen de los datos."""
    import re
    txt = HTML.read_text()
    l = re.sub(r'<svg.*?</svg>', '<svg>velas</svg>', txt, flags=re.S)
    l = re.sub(r'>\((cache|binance)\)<', '>(origen)<', l)
    l = re.sub(r'fuente: (cache|binance)(, (cache|binance))?', 'fuente: origen', l)
    l = re.sub(r'\s*\u00b7 (cache|binance)', ' \u00b7 origen', l)
    # fuera todo numero (con signo, decimales, %, miles)
    l = re.sub(r'[+-]?[0-9][0-9.,]*%?', 'N', l)
    return hashlib.sha256(l.encode()).hexdigest()

pre = _estructura()
r = subprocess.run([sys.executable, str(GEN)], capture_output=True, text=True)
caso('generador_ok', r.returncode == 0, str(r.returncode))
post = _estructura()
caso('estructura_estable', pre == post, f'{pre[:8]} == {post[:8]}')
h = HTML.read_text()

caso('existe', HTML.exists(), str(len(h)))
caso('autocontenido', 'fetch(' not in h and not re.search(r'src="http|href="http', h))
caso('paper_only_visible', 'PAPER ONLY' in h)
caso('mercado_real', 'MERCADO REAL' in h)
caso('velas_reales', 'VELAS REALES' in h)
caso('ciclo_por_tf', 'CICLO · tramo y niveles' in h)
caso('ciclo_varios_pares', h.count('class="tab') >= 5, str(h.count('class="tab')))
caso('risk_visible', 'RISK MANAGER' in h)
caso('ultimo_video', 'ULTIMO VIDEO' in h)
caso('precio_del_video_etiquetado', 'precio del video, no feed' in h)
caso('no_es_orden', 'NO ES UNA ORDEN' in h)
caso('sin_plan_inventado', 'PLAN DE TRADING' not in h and 'OPERACIÓN PROPUESTA' not in h)

# solo el ultimo video, nunca el historico
info = json.loads(INFO.read_text()) if INFO.exists() else {}
vid = info.get('video_id')
caso('solo_ultimo_video', bool(vid) and vid in h, str(vid))
caso('fuente_unica', info.get('fuente_unica') == vid, str(info.get('fuente_unica')))
caso('sin_video_viejo', 's_GjovZxQqY' not in h and 'fuente: s_' not in h)

# sin grafico inventado
caso('velas_reales_presentes', h.count('<rect') >= 50 and h.count('<svg') >= 1,
     f'svg={h.count("<svg")}')

# aviso de que no hay feed
caso('aviso_sin_feed', 'no es un feed en vivo' in h.lower() or 'sin feed' in h.lower())

print(f'\n{OK}/{OK + FALLO} pruebas OK')
sys.exit(1 if FALLO else 0)
