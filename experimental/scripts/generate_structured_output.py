import json, os

BASE = "/Users/franciscootamendi/YouTubeTradingAgent"
VA = json.load(open(f"{BASE}/experimental/results/vision_analysis.json"))
TRANSCRIPT = json.load(open(f"{BASE}/data/rTtXDLq2kOQ_transcript.json"))["segments"]
SCENES = json.load(open(f"{BASE}/data/rTtXDLq2kOQ_scenes.json"))

# Build structured output per scene
structured = []
for va in VA:
    idx = va["scene_idx"]
    scene = SCENES[idx] if idx < len(SCENES) else None
    start = va.get("start", scene["start"] if scene else 0)
    end = va.get("end", scene["end"] if scene else 0)
    
    # Get transcript for this scene
    segs = [s for s in TRANSCRIPT if s["start"] < end and s["end"] > start]
    text = " ".join(s["text"] for s in segs)
    
    # Determine content type
    vision = va.get("vision_analysis", "")
    if "no financial chart" in vision.lower() or "not a trading chart" in vision.lower() or "no chart" in vision.lower():
        content_type = "NO_CHART"
    elif "webpage" in vision.lower() or "landing page" in vision.lower() or "advertisement" in vision.lower():
        content_type = "WEBPAGE"
    elif "desktop" in vision.lower() and "wallpaper" in vision.lower():
        content_type = "DESKTOP"
    else:
        content_type = "CHART"
    
    entry = {
        "scene_id": idx,
        "start_time": round(start, 1),
        "end_time": round(end, 1),
        "duration": round(end - start, 1),
        "frame": va["frame"],
        "content_type": content_type,
        "transcript_audio": text[:500],
        "vision_analysis": vision[:1000] if vision else None,
        "error": va.get("error"),
        "time_seconds": va.get("time_seconds", 0),
        "status": "OK" if "vision_analysis" in va else "ERROR"
    }
    structured.append(entry)

# Save structured output
os.makedirs(f"{BASE}/experimental/results", exist_ok=True)
with open(f"{BASE}/experimental/results/structured_scenes.json", "w") as f:
    json.dump(structured, f, indent=2, ensure_ascii=False)

# Summary
ok = sum(1 for e in structured if e["status"] == "OK")
err = sum(1 for e in structured if e["status"] == "ERROR")
charts = sum(1 for e in structured if e["content_type"] == "CHART")
no_chart = sum(1 for e in structured if e["content_type"] in ("NO_CHART", "WEBPAGE", "DESKTOP"))

print(f"Total: {len(structured)}")
print(f"OK: {ok}, Errors: {err}")
print(f"Charts: {charts}, Non-charts: {no_chart}")
print(f"Saved to experimental/results/structured_scenes.json")