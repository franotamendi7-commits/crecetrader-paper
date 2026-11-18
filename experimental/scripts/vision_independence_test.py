import json, base64, time, requests, os, subprocess

BASE = "/Users/franciscootamendi/YouTubeTradingAgent"
VIDEO_ID = "subONxt5iag"

# Load frame selection (all 69 frames)
SELECTION = json.load(open(f"{BASE}/data_new/{VIDEO_ID}_frame_selection.json"))

# VISION-ONLY prompt (no transcription, no OCR, no prior results)
PROMPT = """You are analyzing a trading chart image. Describe ONLY what you see in the image.

1. Identify the instrument/asset (BTCUSD, ETHUSD, XAUUSD, ES, NQ, AMD, etc.). If unknown: "UNKNOWN".
2. Identify the timeframe (Weekly, Daily, 4H, 1H, 15m, 5m). If unknown: "UNKNOWN".
3. List ONLY price levels CLEARLY VISIBLE. If unreadable: "null".
4. Describe visible structure (trend, range, support, resistance). If unknown: "UNKNOWN".
5. List visible indicators (MA, Fibonacci, Volume, etc.). If none: "none".
6. If NOT a trading chart: "NOT_A_CHART".

Format (no extra text):
INSTRUMENT: ...
TIMEFRAME: ...
PRICES: [...]
STRUCTURE: ...
INDICATORS: ..."""

def run_ocr(image_path):
    try:
        result = subprocess.run(["tesseract", image_path, "stdout", "-l", "spa+eng", "--psm", "6"],
            capture_output=True, text=True, timeout=30)
        return result.stdout.strip()
    except Exception as e:
        return f"OCR_ERROR: {e}"

results = []
raw_outputs = []
results_file = f"{BASE}/experimental/results/vision_validation_69frames.json"
raw_file = f"{BASE}/experimental/results/vision_raw_outputs_69frames.json"

for i, sel in enumerate(SELECTION):
    img_path = sel["frame_path"]
    if not os.path.exists(img_path):
        continue

    print(f"[{i+1}/{len(SELECTION)}] Frame {sel['scene_idx']} ({sel['start']}s): {sel['frame']}...")

    # Step 1: OCR (auxiliary, NOT sent to model)
    ocr_text = run_ocr(img_path)

    # Step 2: Vision-only analysis (NO transcription, NO OCR, NO prior results)
    with open(img_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()

    payload = {"model": "qwen2.5vl:3b", "messages": [
        {"role": "user", "content": PROMPT, "images": [img_b64]}
    ], "stream": False, "options": {"temperature": 0.1}}

    t0 = time.time()
    try:
        resp = requests.post("http://localhost:11434/api/chat", json=payload, timeout=120)
        elapsed = time.time() - t0
        if resp.status_code == 200:
            vision_text = resp.json()["message"]["content"]
            # Save raw output separately
            raw_outputs.append({
                "frame": sel["frame"],
                "timestamp": sel["start"],
                "raw_model_output": vision_text,
                "elapsed_seconds": round(elapsed, 1)
            })
            result = {
                "scene_idx": sel["scene_idx"],
                "start": sel["start"],
                "end": sel["end"],
                "frame": sel["frame"],
                "vision_raw": vision_text,
                "ocr_text": ocr_text,
                "vision_time_seconds": round(elapsed, 1),
                "ocr_time_seconds": 0.2
            }
            print(f"  OK ({elapsed:.1f}s): {vision_text[:80]}...")
        else:
            result = {"scene_idx": sel["scene_idx"], "start": sel["start"], "frame": sel["frame"],
                "error": f"HTTP {resp.status_code}", "ocr_text": ocr_text}
            raw_outputs.append({"frame": sel["frame"], "timestamp": sel["start"], "error": result["error"]})
            print(f"  Error: {resp.status_code}")
    except Exception as e:
        result = {"scene_idx": sel["scene_idx"], "start": sel["start"], "frame": sel["frame"],
            "error": str(e), "ocr_text": ocr_text}
        raw_outputs.append({"frame": sel["frame"], "timestamp": sel["start"], "error": str(e)})
        print(f"  Exception: {e}")

    results.append(result)
    # Save incrementally
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    with open(raw_file, "w") as f:
        json.dump(raw_outputs, f, indent=2, ensure_ascii=False)

    if i < len(SELECTION) - 1:
        time.sleep(2)

print(f"\nCompleted: {len(results)} frames")
ok = sum(1 for r in results if "vision_raw" in r)
err = sum(1 for r in results if "error" in r)
print(f"OK: {ok}, ERR: {err}")
print(f"Total time: {sum(r.get('vision_time_seconds',0) for r in results):.1f}s")