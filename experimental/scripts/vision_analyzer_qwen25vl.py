import json, base64, time, requests, os, subprocess

BASE = "/Users/franciscootamendi/YouTubeTradingAgent"
VIDEO_ID = "subONxt5iag"

SELECTION = json.load(open(f"{BASE}/data_new/{VIDEO_ID}_frame_selection.json"))

# Use only every 4th frame (1 per 60s) to reduce requests: ~18 frames
# But for now, use all 69 frames
# Actually, let's select 15 key frames (every ~60s)
key_frames = [s for s in SELECTION if s["start"] % 60 == 0 or s["start"] == 0]
if len(key_frames) < 15:
    # Add more frames
    step = len(SELECTION) // 15
    key_frames = [SELECTION[i] for i in range(0, len(SELECTION), step)]
print(f"Selected {len(key_frames)} key frames from {len(SELECTION)} total")

PROMPT = """You are analyzing a trading chart image. Follow these rules strictly:

1. ONLY describe what you ACTUALLY SEE in the image.
2. Identify the instrument (BTCUSD, ETHUSD, XAUUSD, ES, NQ, etc.). If unknown: "UNKNOWN".
3. Identify the timeframe (Weekly, Daily, 4H, 1H, 15m, 5m). If unknown: "UNKNOWN".
4. List ONLY price levels CLEARLY VISIBLE. If unreadable: "null".
5. Do NOT invent dates, events, or values.
6. If NOT a trading chart (desktop, web, person, slide): "NOT_A_CHART".
7. Distinguish what chart shows vs what speaker says.

Format:
A_VISUAL: instrument=..., timeframe=..., prices=[...], indicators=[...], structure=...
B_AUDIO: [1 sentence summary of transcription]
C_INTERPRET: [analysis based ONLY on visual, 1-2 sentences]
D_UNCERTAIN: [what cannot be determined]"""

def run_ocr(image_path):
    try:
        result = subprocess.run(["tesseract", image_path, "stdout", "-l", "spa+eng", "--psm", "6"],
            capture_output=True, text=True, timeout=30)
        return result.stdout.strip()
    except Exception as e:
        return f"OCR_ERROR: {e}"

def analyze_frame(image_path, transcript):
    with open(image_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
    payload = {"model": "qwen2.5vl:3b", "messages": [
        {"role": "user", "content": PROMPT + "\n\nTranscription: " + transcript[:300], "images": [img_b64]}
    ], "stream": False, "options": {"temperature": 0.1}}
    t0 = time.time()
    try:
        resp = requests.post("http://localhost:11434/api/chat", json=payload, timeout=120)
        elapsed = time.time() - t0
        if resp.status_code == 200:
            return resp.json()["message"]["content"], round(elapsed, 1), None
        else:
            return None, round(elapsed, 1), f"HTTP {resp.status_code}: {resp.text[:100]}"
    except Exception as e:
        return None, round(time.time()-t0, 1), str(e)

results = []
results_file = f"{BASE}/experimental/results/vision_analysis_qwen25vl.json"

for i, sel in enumerate(key_frames):
    img_path = sel["frame_path"]
    if not os.path.exists(img_path):
        continue

    print(f"[{i+1}/{len(key_frames)}] Frame {sel['scene_idx']} ({sel['start']}s): {sel['frame']}...")

    ocr_text = run_ocr(img_path)
    ocr_time = 0.2

    vision_text, vision_time, error = analyze_frame(img_path, sel["transcript_text"])

    if error:
        result = {"scene_idx": sel["scene_idx"], "start": sel["start"], "frame": sel["frame"],
            "error": error, "ocr_text": ocr_text, "pipeline": "qwen2.5vl:3b"}
        print(f"  Error: {error}")
    else:
        result = {"scene_idx": sel["scene_idx"], "start": sel["start"], "end": sel["end"],
            "frame": sel["frame"], "transcript": sel["transcript_text"],
            "ocr_text": ocr_text, "ocr_time_seconds": ocr_time,
            "vision_analysis": vision_text, "vision_time_seconds": vision_time,
            "total_time_seconds": round(ocr_time + vision_time, 1),
            "pipeline": "qwen2.5vl:3b", "model": "qwen2.5vl:3b"}
        print(f"  OK ({vision_time}s): {vision_text[:80]}...")

    results.append(result)
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

print(f"\nCompleted: {len(results)} frames")
ok = sum(1 for r in results if "vision_analysis" in r)
err = sum(1 for r in results if "error" in r)
print(f"OK: {ok}, ERR: {err}")
print(f"Total time: {sum(r.get('total_time_seconds', r.get('vision_time_seconds',0)) for r in results):.1f}s")
print(f"Avg: {sum(r.get('total_time_seconds', r.get('vision_time_seconds',0)) for r in results)/len(results):.1f}s")