#!/usr/bin/env python3
"""Deriva el registro de senales desde el Risk Manager (idempotente, PAPER_ONLY)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, '/Users/franciscootamendi/YouTubeTradingAgent/daily_pilot/metrics')
import metrics as M

BASE = Path(__file__).resolve().parents[2]
RM_DIR = BASE / 'daily_pilot' / 'risk_manager'

if __name__ == '__main__':
    sys.path.insert(0, str(RM_DIR))
    from risk_manager import evaluar_json
    ev = evaluar_json(str(RM_DIR / 'senales_piloto_s_GjovZxQqY.json'))
    previas = {s.get('id') for s in M._read(M.SENALES)}
    n = 0
    for s in ev.get('senales', []):
        if s.get('id') in previas:
            continue
        M.registrar_senal(s, video_id='s_GjovZxQqY', fecha='2026-11-16')
        n += 1
    print(f'registradas {n} senales nuevas | total {len(M._read(M.SENALES))}')
    print(json.dumps(M.calcular(), ensure_ascii=False, indent=2))
