import json, base64, time, requests, os

BASE = "/Users/franciscootamendi/YouTubeTradingAgent"
SELECTION = json.load(open(f"{BASE}/experimental/results/frame_selection.json"))

# Only process failed frames
failed = [4, 6, 10, 12, 16]  # Wait, these are scene indices not positions
# Actually the failed ones are scene_idx: 1, 2, 6, 12, 16
failed_indices = [1, 2, 6, 12, 16]
failed_scenes = [s for s in SELECTION if s["scene_idx"] in failed_indices]

PROMPT = "What instrument and timeframe? List visible price levels. Be very brief."

# Load existing
existing = {}
results_file = f"{BASE}/experimental/results/vision_analysis.json"
if os.path.exists(results_file):
    try:
        existing_list = json.load(open(results_file))
        for e in existing_list:
            existing[e.get("scene_idx")] = e
    except:
        pass

results = [e for e in existing.values() if e.get("scene_idx") not in failed_indices]

for sel in failed_scenes:
    img_path = sel["frame_path"]
    if not os.path.exists(img_path):
        print(f"SKIP: {img_path} not found")
        continue
    
    with open(img_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
    
    payload = {
        "model": "qwen3.5:9b-mlx",
        "messages": [{"role": "user", "content": PROMPT, "images": [img_b64]}],
        "stream": False
    }
    
    print(f"Retrying frame {sel['scene_idx']}: {sel['frame']}...")
    t0 = time.time()
    try:
        resp = requests.post("http://localhost:11434/api/chat", json=payload, timeout=600)
        elapsed = time.time() - t0
        if resp.status_code == 200:
            answer = resp.json().get("message", {}).get("content", "")
            results.append({
                "scene_idx": sel["scene_idx"],
                "start": sel["start"],
                "end": sel["end"],
                "frame": sel["frame"],
                "transcript": sel["transcript_text"],
                "vision_analysis": answer,
                "time_seconds": round(elapsed, 1),
                "retry": True
            })
            print(f"  Done in {elapsed:.1f}s")
        else:
            print(f"  Error: {resp.status_code}")
            results.append({"scene_idx": sel["scene_idx"], "frame": sel["frame"], "error": resp.text, "time_seconds": round(elapsed,1)})
    except Exception as e:
        print(f"  Exception: {e}")
        results.append({"scene_idx": sel["scene_idx"], "frame": sel["frame"], "error": str(e)})

    with open(results_file, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

print(f"\nCompleted: {len(results)} frames analyzed")
print(f"Saved to {results_file}")