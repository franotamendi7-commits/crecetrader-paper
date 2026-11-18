import json, os

BASE = "/Users/franciscootamendi/YouTubeTradingAgent"
VA = json.load(open(f"{BASE}/experimental/results/vision_analysis.json"))
SCENES = json.load(open(f"{BASE}/data/rTtXDLq2kOQ_scenes.json"))

# Build canonical registry with all 19 frames
canonical = {}
for e in VA:
    canonical[e["scene_idx"]] = e

# Add missing frames as errors
for idx in [6, 12, 16]:
    if idx not in canonical:
        scene = SCENES[idx]
        canonical[idx] = {
            "scene_idx": idx,
            "start": scene["start"],
            "end": scene["end"],
            "frame": f"scene_{idx:03d}_{scene['start']:.1f}s.jpg",
            "transcript": "",
            "error": "HTTPConnectionPool: Read timed out (600s) - 3 attempts failed",
            "time_seconds": 0,
            "status": "ERROR_TIMEOUT"
        }

# Sort by scene_idx
canonical_list = [canonical[i] for i in sorted(canonical.keys())]

# Save canonical registry
os.makedirs(f"{BASE}/experimental/results", exist_ok=True)
with open(f"{BASE}/experimental/results/vision_analysis_canonical.json", "w") as f:
    json.dump(canonical_list, f, indent=2, ensure_ascii=False)

# Also update vision_analysis.json with canonical data
with open(f"{BASE}/experimental/results/vision_analysis.json", "w") as f:
    json.dump(canonical_list, f, indent=2, ensure_ascii=False)

# Summary
ok = sum(1 for e in canonical_list if "vision_analysis" in e)
err = sum(1 for e in canonical_list if "error" in e)
print(f"Canonical registry: {len(canonical_list)} frames")
print(f"OK: {ok}, ERR: {err}")
for e in canonical_list:
    status = "OK" if "vision_analysis" in e else "ERR"
    print(f"  [{e['scene_idx']:2d}] {status:3s} t={e.get('time_seconds',0):6.1f}s  {e['frame']}")