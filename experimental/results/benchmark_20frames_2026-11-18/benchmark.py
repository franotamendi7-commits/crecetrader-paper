#!/usr/bin/env python3
"""Benchmark de lectura de graficos: Qwen3-VL-8B local vs Gemini Flash.

Uso:
  python3 benchmark.py --limit 1                 # smoke test
  python3 benchmark.py                           # 20 frames, ambos modelos
  python3 benchmark.py --models gemini-2.5-flash # solo Gemini
  python3 benchmark.py --frame btc_1d_0prmr_0008 # un frame
"""
import argparse
import base64
import json
import re
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE = Path("/Users/franciscootamendi/YouTubeTradingAgent")
OUT = BASE / "experimental/results/benchmark_20frames_2026-11-18"
KEY_FILE = Path.home() / ".config/crecetrader/gemini_api_key"
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

PROMPT = """Eres un analista tecnico de trading. Mira la imagen y devuelve SOLO un objeto JSON valido, sin markdown, sin explicaciones fuera del JSON.

Esquema obligatorio:
{
  "has_chart": true o false,
  "instrument": "BTCUSD" | "ETHUSD" | "ES1!" | "GC1!" | "VX1!" | "USTECH" | "otro" | "desconocido",
  "timeframe": "1D" | "4H" | "1H" | "1W" | "5m" | "multi" | "desconocido",
  "timeframes": ["..."],
  "current_price": numero o null,
  "levels": [numeros],
  "indicators": ["..."],
  "structure": "alcista" | "bajista" | "lateral" | "desconocido",
  "confidence": 0.0 a 1.0,
  "notes": "texto corto"
}

Reglas:
- Si no hay grafico visible, has_chart=false, current_price=null, levels=[].
- No inventes precios. Usa solo numeros visibles en la imagen.
- El instrumento suele estar en el watermark central o en una esquina: BTCUSD, ETHUSD, ES1!, GC1!, VX1!, USTECH.
- El precio actual es el numero resaltado con fondo de color en el eje derecho.
- "levels" son las lineas horizontales y etiquetas de precio visibles.
- Si hay varios timeframes, timeframe="multi" y lista los visibles en "timeframes".
- Responde solo JSON.
"""


def b64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode("ascii")


def parse_json_text(text: str):
    if not text:
        return None
    t = text.strip()
    if t.startswith("```"):
        t = re.sub(r"^```[a-zA-Z0-9_-]*\s*", "", t)
        t = re.sub(r"\s*```$", "", t)
    try:
        return json.loads(t)
    except Exception:
        pass
    start = t.find("{")
    end = t.rfind("}")
    if start >= 0 and end > start:
        try:
            return json.loads(t[start : end + 1])
        except Exception:
            return None
    return None


def _post(url: str, payload: dict, timeout: int = 900) -> dict:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read())


def call_ollama(model: str, image_path: Path):
    payload = {
        "model": model,
        "prompt": PROMPT,
        "images": [b64(image_path)],
        "stream": False,
        "format": "json",
        "think": False,
        "options": {
            "temperature": 0,
            "num_predict": 500,
            "num_ctx": 4096,
            "top_p": 0.9,
        },
    }
    try:
        data = _post(OLLAMA_URL, payload)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        if e.code == 400 and "think" in body.lower():
            payload.pop("think", None)
            data = _post(OLLAMA_URL, payload)
        else:
            raise RuntimeError(f"HTTP {e.code}: {body[:300]}") from e
    raw = data.get("response", "")
    meta = {
        k: data.get(k)
        for k in (
            "eval_count",
            "prompt_eval_count",
            "total_duration",
            "load_duration",
            "eval_duration",
            "prompt_eval_duration",
        )
    }
    meta["thinking"] = data.get("thinking", "")
    return raw, meta


def call_gemini(model: str, image_path: Path, key: str, retries: int = 6):
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": PROMPT},
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": b64(image_path),
                        }
                    },
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0,
            "maxOutputTokens": 1200,
            "responseMimeType": "application/json",
            "thinkingConfig": {"thinkingBudget": 0},
        },
    }
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{urllib.parse.quote(model)}:generateContent?key={urllib.parse.quote(key)}"
    )
    delay = 20
    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=900) as resp:
                data = json.loads(resp.read())
            break
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < retries - 1:
                print(f"    429 rate limit, espero {delay}s (intento {attempt + 1}/{retries})")
                time.sleep(delay)
                delay = min(delay * 2, 90)
                continue
            raise
    if "error" in data:
        raise RuntimeError(data["error"].get("message", str(data["error"])))
    candidates = data.get("candidates") or []
    if not candidates:
        raise RuntimeError(f"sin candidates: {json.dumps(data)[:300]}")
    parts = (candidates[0].get("content") or {}).get("parts") or []
    raw = "".join(p.get("text", "") for p in parts)
    return raw, data.get("usageMetadata", {})


def get_rss_mb() -> float:
    try:
        out = subprocess.run(
            ["ps", "-Ao", "rss,command"], capture_output=True, text=True, check=False
        ).stdout
        total_kb = 0
        for line in out.splitlines():
            low = line.lower()
            if ("llama-server" in low or "ollama" in low) and "grep" not in low:
                try:
                    total_kb += int(line.split(None, 1)[0])
                except Exception:
                    pass
        return round(total_kb / 1024.0, 1)
    except Exception:
        return 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default="qwen3-vl:8b-instruct,gemini-2.5-flash")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--frame", default=None)
    ap.add_argument("--out", default=str(OUT / "results.jsonl"))
    args = ap.parse_args()

    manifest = json.loads((OUT / "manifest.json").read_text())
    frames = manifest["frames"]
    if args.frame:
        frames = [f for f in frames if f["id"] == args.frame]
    if args.limit:
        frames = frames[: args.limit]
    models = [m.strip() for m in args.models.split(",") if m.strip()]

    key = KEY_FILE.read_text().strip() if KEY_FILE.exists() else ""
    outpath = Path(args.out)
    done = set()
    if outpath.exists():
        for line in outpath.read_text().splitlines():
            try:
                rec = json.loads(line)
                if rec.get("error"):
                    continue
                done.add((rec["model"], rec["frame_id"]))
            except Exception:
                pass

    print(f"frames={len(frames)} models={models} out={outpath}")
    with outpath.open("a", encoding="utf-8") as f:
        for model in models:
            for fr in frames:
                if (model, fr["id"]) in done:
                    continue
                image_path = BASE / fr["path"]
                t0 = time.time()
                try:
                    if model.startswith("gemini"):
                        if not key:
                            raise RuntimeError("falta la API key en ~/.config/crecetrader/gemini_api_key")
                        raw, usage = call_gemini(model, image_path, key)
                    else:
                        raw, usage = call_ollama(model, image_path)
                    parsed = parse_json_text(raw)
                    rec = {
                        "model": model,
                        "frame_id": fr["id"],
                        "path": str(image_path),
                        "latency_s": round(time.time() - t0, 2),
                        "raw": raw,
                        "parsed": parsed,
                        "usage": usage,
                        "rss_mb": get_rss_mb(),
                        "error": None,
                    }
                    status = "ok" if parsed else "JSON_INVALIDO"
                    print(f"{model:22s} {fr['id']:30s} {rec['latency_s']:7.2f}s {status}")
                except Exception as e:
                    rec = {
                        "model": model,
                        "frame_id": fr["id"],
                        "path": str(image_path),
                        "latency_s": round(time.time() - t0, 2),
                        "raw": "",
                        "parsed": None,
                        "usage": {},
                        "rss_mb": get_rss_mb(),
                        "error": repr(e),
                    }
                    print(f"{model:22s} {fr['id']:30s} ERROR {e}")
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                f.flush()


if __name__ == "__main__":
    main()
