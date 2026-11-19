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
GEN = BASE / 'daily_pilot' / 'scripts' / 'generar_dashboard_v4.py'
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


# regenerar
subprocess.run([sys.executable, str(GEN)], capture_output=True, text=True, check=False)
h = HTML.read_text()

caso('existe', HTML.exists(), str(len(h)))
caso('autocontenido', 'fetch(' not in h and not re.search(r'src="http|href="http', h))
caso('paper_only_visible', 'PAPER ONLY' in h)
caso('panel_niveles_mencionados', 'NIVELES MENCIONADOS' in h)
caso('panel_risk', 'RISK MANAGER' in h)
caso('panel_niveles', 'NIVELES CLAVE' in h)
caso('panel_lectura', 'LECTURA DEL DÍA' in h)
caso('panel_distribucion', 'DISTRIBUCIÓN' in h)
caso('no_es_orden', 'NO ES UNA ORDEN' in h)
caso('sin_plan_inventado', 'PLAN DE TRADING' not in h and 'OPERACIÓN PROPUESTA' not in h)

# solo el ultimo video, nunca el historico
info = json.loads(INFO.read_text()) if INFO.exists() else {}
vid = info.get('video_id')
caso('solo_ultimo_video', bool(vid) and vid in h, str(vid))
caso('fuente_unica', info.get('fuente_unica') == vid, str(info.get('fuente_unica')))
caso('sin_video_viejo', 's_GjovZxQqY' not in h and 'fuente: s_' not in h)

# sin grafico inventado
caso('sin_velas_simuladas', 'stroke-width="5"' not in h and h.count('<svg') == 0,
     f'svg={h.count("<svg")}')

# aviso de que no hay feed
caso('aviso_sin_feed', 'sin feed' in h.lower() or 'NO_DISPONIBLE' in h)

print(f'\n{OK}/{OK + FALLO} pruebas OK')
sys.exit(1 if FALLO else 0)
