import json, base64, time, requests, os, subprocess

BASE = "/Users/franciscootamendi/YouTubeTradingAgent"
SELECTION = json.load(open(f"{BASE}/experimental/results/frame_selection.json"))

# Load existing canonical results (do NOT overwrite)
existing_results = {}
results_file = f"{BASE}/experimental/results/vision_analysis_canonical.json"
if os.path.exists(results_file):
    try:
        existing_list = json.load(open(results_file))
        for e in existing_list:
            existing_results[e.get("scene_idx")] = e
    except:
        pass

# NEW structured prompt
PROMPT = """You are analyzing a trading chart image. Follow these rules strictly:

1. ONLY describe what you ACTUALLY SEE in the image. Do NOT infer from audio or transcription.
2. Identify the instrument visible in the chart (e.g., BTCUSD, XAUUSD, ETHUSD). If you cannot identify it, respond "UNKNOWN".
3. Identify the timeframe ONLY if visible (e.g., Weekly, Daily, 4H, 1H, 15m). If not visible, respond "UNKNOWN".
4. List ONLY price levels that are CLEARLY VISIBLE in the chart. If you cannot read a price, respond "null".
5. Do NOT invent dates, events, indicator values, or price levels.
6. If the image is NOT a trading chart (desktop, webpage, person, slide), respond "NOT_A_CHART".
7. Distinguish between what the chart shows vs what a speaker might say.

Respond in this EXACT format (no extra text):
A_VISUAL: instrument=..., timeframe=..., prices=[...], indicators=[...], structure=...
B_AUDIO: [summarize what the transcription says about this moment in 1 sentence]
C_INTERPRET: [your analysis based ONLY on visual evidence, 1-2 sentences]
D_UNCERTAIN: [what you cannot determine from the image]"""

def run_ocr(image_path):
    """Run Tesseract OCR on image, return text."""
    try:
        result = subprocess.run(
            ["tesseract", image_path, "stdout", "-l", "spa+eng", "--psm", "6"],
            capture_output=True, text=True, timeout=30
        )
        return result.stdout.strip()
    except Exception as e:
        return f"OCR_ERROR: {e}"

# Frames to process (10 selected for comparison)
test_frames = [4, 10, 1, 2, 6, 12, 16, 13, 15, 17]
test_scenes = [s for s in SELECTION if s["scene_idx"] in test_frames]

# Results for new pipeline (separate file)
new_results = []
new_results_file = f"{BASE}/experimental/results/vision_analysis_v2.json"

for i, sel in enumerate(test_scenes):
    img_path = sel["frame_path"]
    if not os.path.exists(img_path):
        print(f"SKIP: {img_path} not found")
        continue

    print(f"\n[{i+1}/{len(test_scenes)}] Processing frame {sel['scene_idx']}: {sel['frame']}...")

    # Step 1: OCR
    t0_ocr = time.time()
    ocr_text = run_ocr(img_path)
    ocr_time = time.time() - t0_ocr
    print(f"  OCR ({ocr_time:.1f}s): {ocr_text[:80]}...")

    # Step 2: Vision analysis
    with open(img_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()

    payload = {
        "model": "qwen3.5:9b-mlx",
        "messages": [{"role": "user", "content": PROMPT, "images": [img_b64]}],
        "stream": False
    }

    t0_vision = time.time()
    try:
        resp = requests.post("http://localhost:11434/api/chat", json=payload, timeout=600)
        vision_time = time.time() - t0_vision

        if resp.status_code == 200:
            answer = resp.json().get("message", {}).get("content", "")
            result = {
                "scene_idx": sel["scene_idx"],
                "start": sel["start"],
                "end": sel["end"],
                "frame": sel["frame"],
                "transcript": sel["transcript_text"],
                "ocr_text": ocr_text,
                "ocr_time_seconds": round(ocr_time, 1),
                "vision_analysis": answer,
                "vision_time_seconds": round(vision_time, 1),
                "total_time_seconds": round(ocr_time + vision_time, 1),
                "pipeline": "v2_structured",
                "prompt_version": "structured_v1"
            }
            print(f"  Vision ({vision_time:.1f}s): {answer[:100]}...")
        else:
            result = {
                "scene_idx": sel["scene_idx"],
                "frame": sel["frame"],
                "error": f"HTTP {resp.status_code}",
                "ocr_text": ocr_text,
                "ocr_time_seconds": round(ocr_time, 1),
                "vision_time_seconds": round(vision_time, 1),
                "pipeline": "v2_structured"
            }
            print(f"  Error: {resp.status_code}")
    except Exception as e:
        vision_time = time.time() - t0_vision
        result = {
            "scene_idx": sel["scene_idx"],
            "frame": sel["frame"],
            "error": str(e),
            "ocr_text": ocr_text,
            "ocr_time_seconds": round(ocr_time, 1),
            "vision_time_seconds": round(vision_time, 1),
            "pipeline": "v2_structured"
        }
        print(f"  Exception: {e}")

    new_results.append(result)

    # Save incrementally
    with open(new_results_file, "w") as f:
        json.dump(new_results, f, indent=2, ensure_ascii=False)

print(f"\n\nCompleted: {len(new_results)} frames processed")
print(f"Saved to {new_results_file}")

# Summary
ok = sum(1 for r in new_results if "vision_analysis" in r)
err = sum(1 for r in new_results if "error" in r)
ocr_ok = sum(1 for r in new_results if r.get("ocr_text") and not r.get("ocr_text","").startswith("OCR_ERROR"))
print(f"OK: {ok}, ERR: {err}")
print(f"OCR successful: {ocr_ok}/{len(new_results)}")