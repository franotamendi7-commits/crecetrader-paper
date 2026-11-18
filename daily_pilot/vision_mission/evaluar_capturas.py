#!/usr/bin/env python3
"""Evaluador de capturas (PREPARADO — NO EJECUTADO sin autorizacion).

Requiere un motor de vision autorizado (Ollama local o endpoint). Por defecto
solo prepara el lote y verifica la muestra. Con --ejecutar y --motor, ejecuta.
"""
import argparse
import base64
import json
import re
import time
import urllib.request
from pathlib import Path

BASE = Path('/Users/franciscootamendi/YouTubeTradingAgent')
OUT = BASE / 'daily_pilot' / 'vision_mission'
MUESTRA = OUT / 'muestra_capturas.json'
URL = re.compile(r'\d{2}[.,]\d{3}')

PROMPT = """Analiza esta captura de un gráfico de TradingView. Devuelve SOLO un JSON con:
instrument, exchange, timeframe, trend_structure, visible_price_labels (solo valores con
etiqueta escrita), horizontal_levels, fibonacci (origen, niveles, objetivo o null),
liquidity_zones, unreadable, confidence, abstentions.
REGLAS: no inventes numeros ni secuencias; si algo no se lee, "UNKNOWN"; maximo 12 precios."""


def preparar():
    reg = json.load(open(MUESTRA))
    print(f'capturas: {len(reg)}')
    for r in reg:
        p = BASE / r['captura']
        print(f"  {r['video_id']} {r['frame']} @{r['pts_time']}s | niveles citados: {URL.findall(r['transcripcion'])}")
    return reg


def preguntar(ruta: Path, motor_url: str, modelo: str):
    b64 = base64.b64encode(ruta.read_bytes()).decode('ascii')
    payload = {'model': modelo, 'messages': [{'role': 'user', 'content': PROMPT, 'images': [b64]}],
               'stream': False, 'options': {'temperature': 0.1}}
    req = urllib.request.Request(motor_url.rstrip('/') + '/api/chat',
                                 data=json.dumps(payload).encode(),
                                 headers={'Content-Type': 'application/json'}, method='POST')
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=600) as r:
        res = json.loads(r.read().decode())
    return res.get('message', {}).get('content', ''), round(time.time() - t0, 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ejecutar', action='store_true')
    ap.add_argument('--motor', default='http://localhost:11434')
    ap.add_argument('--modelo', default='qwen2.5vl:3b')
    ap.add_argument('--out', default=str(OUT / 'resultados_capturas.json'))
    a = ap.parse_args()
    reg = preparar()
    if not a.ejecutar:
        print('\nNO EJECUTADO: falta autorizacion para inferencia audiovisual. '
              'Use --ejecutar solo con motor autorizado.')
        return
    salida = []
    for r in reg:
        try:
            resp, dur = preguntar(BASE / r['captura'], a.motor, a.modelo)
            err = ''
        except Exception as exc:
            resp, dur, err = '', 0.0, str(exc)
        citados = URL.findall(r['transcripcion'])
        leidos = set(x.replace('.', '').replace(',', '') for x in URL.findall(resp))
        salida.append({**r, 'respuesta': resp, 'segundos': dur, 'error': err,
                       'niveles_citados': citados, 'niveles_leidos': sorted(leidos)})
        print(f"  {r['frame']}: {dur}s | error={err}", flush=True)
    Path(a.out).write_text(json.dumps(salida, ensure_ascii=False, indent=2))
    print('resultados:', a.out)


if __name__ == '__main__':
    main()
