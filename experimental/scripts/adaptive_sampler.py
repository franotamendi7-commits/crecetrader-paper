import json, os, re

BASE = "/Users/franciscootamendi/YouTubeTradingAgent"
SCENES = json.load(open(f"{BASE}/data/rTtXDLq2kOQ_scenes.json"))
TRANSCRIPT = json.load(open(f"{BASE}/data/rTtXDLq2kOQ_transcript.json"))["segments"]
FRAMES_DIR = f"{BASE}/frames"

price_re = re.compile(r'\$?\s*\d[\d.,]*\s*(mil|k|dólares|dollars)?', re.IGNORECASE)

selected = []
for i, scene in enumerate(SCENES):
    start = scene["start"]
    end = scene["end"]
    duration = scene["duration"]

    segs = [s for s in TRANSCRIPT if s["start"] < end and s["end"] > start]
    text = " ".join(s["text"] for s in segs)

    has_price = bool(price_re.search(text))
    has_btc = "bitcoin" in text.lower() or "btc" in text.lower()
    has_eth = "ethereum" in text.lower() or "eth" in text.lower()

    frame_name = f"scene_{i:03d}_{start:.1f}s.jpg"
    frame_path = os.path.join(FRAMES_DIR, frame_name)

    if os.path.exists(frame_path):
        selected.append({
            "scene_idx": i,
            "start": start,
            "end": end,
            "duration": duration,
            "frame": frame_name,
            "frame_path": frame_path,
            "transcript_text": text[:500],
            "has_price": has_price,
            "has_btc": has_btc,
            "has_eth": has_eth,
            "priority": "high" if (has_price or duration > 30) else "normal"
        })

    if duration > 60:
        mid = start + duration / 2
        selected[-1]["needs_mid_frame"] = True
        selected[-1]["mid_time"] = mid

print(f"Selected {len(selected)} frames from {len(SCENES)} scenes")
high = sum(1 for s in selected if s["priority"] == "high")
print(f"High priority: {high}, Normal: {len(selected)-high}")

os.makedirs(f"{BASE}/experimental/results", exist_ok=True)
with open(f"{BASE}/experimental/results/frame_selection.json", "w") as f:
    json.dump(selected, f, indent=2, ensure_ascii=False)
print("Saved to experimental/results/frame_selection.json")