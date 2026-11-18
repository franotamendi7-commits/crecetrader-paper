#!/usr/bin/env python3
"""Integracion: el Dashboard incrusta la evaluacion del Risk Manager (PAPER_ONLY)."""
import json
import re
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
GEN = BASE / 'daily_pilot' / 'scripts' / 'generar_dashboard.py'
HTML = BASE / 'daily_pilot' / 'dashboard' / 'index.html'
PY = sys.executable   # reproducible fuera de la maquina de Hermes

OK = FALLO = 0


def caso(nombre, cond, detalle=''):
    global OK, FALLO
    if cond:
        OK += 1
        print(f'OK    | {nombre} | {detalle}')
    else:
        FALLO += 1
        print(f'FALLO | {nombre} | {detalle}')


r = subprocess.run([PY, str(GEN)], capture_output=True, text=True, timeout=120)
caso('generador_ok', r.returncode == 0, r.stdout.strip()[:80])

h = HTML.read_text(encoding='utf-8')
m = re.search(r'id="estado-data"[^>]*>(.*?)</script>', h, re.S)
caso('json_incrustado', bool(m))
d = json.loads((m or re.search(r'id="estado-data"[^>]*>(.*?)</script>', h, re.S)).group(1).replace('\\u003c', '<').replace('\\u003e', '>'))
rm = d.get('risk_manager') or {}
caso('rm_decision', rm.get('decision') in ('ACEPTAR', 'RECHAZAR', 'REVISION MANUAL'), str(rm.get('decision')))
caso('rm_paper_only', rm.get('paper_only') is True, str(rm.get('paper_only')))
caso('rm_por_nivel', isinstance(rm.get('por_nivel'), dict) and sum(rm['por_nivel'].values()) > 0, str(rm.get('por_nivel')))
caso('rm_senales', len(rm.get('senales', [])) >= 6, str(len(rm.get('senales', []))))   # P2: robusto
caso('html_risk_card', 'id="risk-card"' in h)
caso('file_limpio', 'fetch(' not in h and not re.search(r'src="http', h))

print(f'\n{OK}/{OK + FALLO} pruebas OK')
sys.exit(1 if FALLO else 0)
