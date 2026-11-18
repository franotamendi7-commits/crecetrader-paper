import json, os

BASE = "/Users/franciscootamendi/YouTubeTradingAgent"
VIDEO_ID = "subONxt5iag"

# Parse subtitles
data = json.load(open(f"{BASE}/data_new/{VIDEO_ID}.es.json3"))
events = data.get("events", [])

# Build transcript segments with timestamps
segments = []
for e in events:
    text = "".join(s.get("utf8", "") for s in e.get("segs", [])).strip()
    if not text:
        continue
    start = e.get("tStartMs", 0) / 1000.0
    dur = e.get("dDurationMs", 0) / 1000.0
    segments.append({"start": round(start, 1), "end": round(start + dur, 1), "text": text})

# Save transcript
transcript = {"video_id": VIDEO_ID, "segments": segments}
with open(f"{BASE}/data_new/{VIDEO_ID}_transcript.json", "w") as f:
    json.dump(transcript, f, indent=2, ensure_ascii=False)
print(f"Transcript: {len(segments)} segments, {segments[-1]['end']:.1f}s total")

# Create frame selection (1 frame per 15s)
frames_dir = f"{BASE}/frames_new"
frame_files = sorted(os.listdir(frames_dir))
print(f"Frames: {len(frame_files)}")

# Map frame index to timestamp (frame_0001.jpg = 0s, frame_0002.jpg = 15s, etc.)
selected = []
for i, fname in enumerate(frame_files):
    ts = i * 15.0
    # Get transcript text for this time window (±15s)
    segs = [s for s in segments if s["start"] < ts + 15 and s["end"] > ts - 15]
    text = " ".join(s["text"] for s in segs)
    
    selected.append({
        "scene_idx": i,
        "start": ts,
        "end": ts + 15,
        "frame": fname,
        "frame_path": os.path.join(frames_dir, fname),
        "transcript_text": text[:500]
    })

with open(f"{BASE}/data_new/{VIDEO_ID}_frame_selection.json", "w") as f:
    json.dump(selected, f, indent=2, ensure_ascii=False)
print(f"Frame selection: {len(selected)} frames saved")