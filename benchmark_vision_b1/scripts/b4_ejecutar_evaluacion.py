#!/usr/bin/env python3
"""B4 (NO EJECUTAR sin referencia humana validada): envia los 20 frames
individuales al modelo local y guarda respuestas crudas + metadatos."""
import argparse
import base64
import json
import time
import urllib.request
from pathlib import Path

PROMPT = """You are analyzing ONE screenshot of a TradingView chart. Answer ONLY with a single JSON object with exactly these keys:

{
  "instrument": "BTCUSD, ETHUSD, ES, NQ, XAUUSD, AMD, MDT, SPX, or UNKNOWN",
  "exchange": "exchange or source if visible, otherwise UNKNOWN",
  "timeframe": "Weekly, Daily, 4H, 1H, 15m, 5m, or UNKNOWN",
  "visible_price_labels": [
    {"value": "number as written", "location": "approximate position in image",
     "legibility": "clear|partial|illegible", "confidence": 1-5,
     "justification": "what in the image shows this value"}
  ],
  "horizontal_levels": [{"level": "...", "role": "support|resistance|UNKNOWN", "label_visible": true|false}],
  "trendlines": [{"direction": "ascending|descending|horizontal|UNKNOWN", "description": "..."}],
  "market_structure": "trend|range|support|resistance|UNKNOWN",
  "liquidity_zones": [{"zone": "...", "evidence": "..."}],
  "indicators": ["MA", "Fibonacci", "Volume"],
  "visible_candlestick_information": "legible OHLC/body/wick detail, or UNKNOWN",
  "unreadable_information": ["list of elements you could not read"],
  "confidence": 1-5,
  "abstentions": ["fields you could not determine"]
}

RULES (mandatory):
- Transcribe ONLY values that are actually written in the image.
- Do NOT invent, complete, or deduce numbers. If a digit is uncertain, mark it illegible.
- Do NOT produce enumerations, sequences, or lists of numbers that are not printed on the chart.
- Maximum 12 price labels.
- If a field cannot be read, use "UNKNOWN" (or empty list where applicable).
- Do NOT guess the function of a line if it could have several interpretations; describe it.
- If the chart is not legible enough, abstain."""

URL = 'http://localhost:11434'
MODEL = 'qwen2.5vl:3b'


def ask(img: Path):
    b64 = base64.b64encode(img.read_bytes()).decode('ascii')
    payload = {'model': MODEL,
               'messages': [{'role': 'user', 'content': PROMPT, 'images': [b64]}],
               'stream': False,
               'options': {'temperature': 0.1}}
    req = urllib.request.Request(URL + '/api/chat',
                                 data=json.dumps(payload).encode(),
                                 headers={'Content-Type': 'application/json'},
                                 method='POST')
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=600) as r:
        res = json.loads(r.read().decode())
    return res.get('message', {}).get('content', ''), round(time.time() - t0, 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--frames', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--ejecutar', action='store_true', help='requerido para correr')
    a = ap.parse_args()
    if not a.ejecutar:
        print('B4 NO EJECUTADO: falta referencia humana validada. Use --ejecutar solo cuando exista.')
        return
    out = []
    for img in sorted(Path(a.frames).glob('frame_*.jpg')):
        try:
            resp, dur = ask(img)
            err = ''
        except Exception as exc:
            resp, dur, err = '', 0.0, str(exc)
        out.append({'frame': img.name, 'modelo': MODEL, 'prompt': PROMPT,
                    'temperatura': 0.1, 'duracion_s': dur, 'error': err,
                    'respuesta_cruda': resp})
        print(img.name, dur, 's', flush=True)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
