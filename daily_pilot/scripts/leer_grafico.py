#!/usr/bin/env python3
"""Sensor visual del piloto — lee los fotogramas de un video con un VLM local.

Modelo: qwen3-vl:8b-instruct (Ollama, LOCAL, sin servicios externos ni cuota).
Salida: JSON estructurado por frame + consolidado.

Uso:
  python3 daily_pilot/scripts/leer_grafico.py --frames-dir frames --out /tmp/vision_19.json
  python3 daily_pilot/scripts/leer_grafico.py --frames-dir frames --limite 3   # smoke test

PAPER_ONLY: solo LEE. No opera.
"""
from __future__ import annotations

import argparse
import base64
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

OLLAMA = 'http://localhost:11434/api/chat'
MODELO = 'qwen3-vl:8b-instruct'
PAPER_ONLY = True

PROMPT = """Sos analista de price action. Mirá SOLO este fotograma y respondé con un ÚNICO objeto JSON valido, sin texto fuera:
{
  "instrumento": "BTCUSD | ETHUSD | SPX | QQQ | XAUUSD | NO_VISIBLE",
  "tf_aparente": "4H | diario | semanal | 1H | NO_VISIBLE",
  "estructura": "maximos_crecientes | minimos_decrecientes | rango | ruptura | NO_VISIBLE",
  "niveles_visibles": [{"precio": 0.0, "tipo": "soporte|resistencia|calculado|NO_VISIBLE"}],
  "vela_actual": "verde | roja | indecision | NO_VISIBLE",
  "observacion": "una frase corta"
}
Reglas: si un eje usa punto como separador de miles, el precio es el numero entero (75.471 = 75471).
Si algo no se ve, poné NO_VISIBLE. No inventes."""

LIMPIO = re.compile(r'^```(json)?|```$')

def parsear(txt: str) -> dict | None:
    s = txt.strip()
    s = LIMPIO.sub('', s).strip()
    try:
        return json.loads(s)
    except Exception:
        m = re.search(r'\{.*\}', s, re.S)
        if m:
            try:
                return json.loads(m.group(0))
            except Exception:
                return None
    return None

def leer_frame(ruta: Path) -> dict:
    b64 = base64.b64encode(ruta.read_bytes()).decode()
    payload = {'model': MODELO,
               'messages': [{'role': 'user', 'content': PROMPT, 'images': [b64]}],
               'stream': False,
               'options': {'temperature': 0.1, 'num_predict': 512}}
    req = urllib.request.Request(OLLAMA, data=json.dumps(payload).encode(),
                                 headers={'Content-Type': 'application/json'})
    t0 = time.time()
    r = json.load(urllib.request.urlopen(req, timeout=900))
    txt = r['message']['content']
    obj = parsear(txt)
    return {'frame': ruta.name, 'segundos': round(time.time() - t0, 1),
            'json_valido': obj is not None, 'data': obj if obj else {'crudo': txt[:300]}}

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--frames-dir', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--limite', type=int, default=0)
    a = ap.parse_args()

    frames = sorted(Path(a.frames_dir).glob('*.jpg'))[:a.limite or None]
    print(f'frames: {len(frames)} · modelo: {MODELO}', flush=True)
    res = []
    for i, f in enumerate(frames, 1):
        r = leer_frame(f)
        res.append(r)
        ins = (r['data'] or {}).get('instrumento', '?')
        niv = len((r['data'] or {}).get('niveles_visibles', []))
        print(f"  [{i:2d}/{len(frames)}] {f.name:26s} {r['segundos']:5.1f}s json={r['json_valido']} {ins} niveles={niv}", flush=True)

    ok = sum(1 for r in res if r['json_valido'])
    consolidado = {}
    for r in res:
        for n in (r['data'] or {}).get('niveles_visibles', []):
            p = n.get('precio')
            if isinstance(p, (int, float)) and p > 0:
                consolidado[p] = consolidado.get(p, 0) + 1

    out = {'modelo': MODELO, 'paper_only': PAPER_ONLY, 'n_frames': len(res),
           'json_validos': ok, 'tasa_json': round(ok / len(res), 3) if res else 0,
           'niveles_consolidados': dict(sorted(consolidado.items(), key=lambda x: -x[1])),
           'frames': res}
    Path(a.out).write_text(json.dumps(out, indent=2, ensure_ascii=False))
    print(f"\n{ok}/{len(res)} JSON validos · {len(consolidado)} niveles distintos")
    print(f"-> {a.out}")
    return 0 if ok == len(res) else 1

if __name__ == '__main__':
    sys.exit(main())
