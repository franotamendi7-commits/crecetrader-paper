import json, os, re

hist_dir = "/Users/franciscootamendi/YouTubeTradingAgent/experimental/results/historical"
videos = {}
for f in os.listdir(hist_dir):
    if f.endswith("_analysis.json"):
        d = json.load(open(os.path.join(hist_dir, f)))
        videos[d["video_id"]] = d

for vid, d in videos.items():
    print(f"=== {vid} ===")
    for fr in d["frame_results"]:
        if isinstance(fr, str):
            v = fr
        else:
            v = fr.get("vision", "")
        if isinstance(v, str) and v.strip():
            lines = v.strip().split("\n")
            inst = lines[0].replace("INSTRUMENT:", "").strip() if "INSTRUMENT:" in lines[0] else "UNKNOWN"
            tf = lines[1].replace("TIMEFRAME:", "").strip() if len(lines) > 1 and "TIMEFRAME:" in lines[1] else "UNKNOWN"
            prices = []
            if "PRICES:" in v:
                p_str = v.split("PRICES:")[1].split("\n")[0]
                p_str = p_str.strip("[]")
                prices = [p.strip() for p in p_str.split(",") if p.strip()]
            structure = ""
            if "STRUCTURE:" in v:
                structure = v.split("STRUCTURE:")[1].split("\n")[0].strip()
            frame_num = fr.get("frame_idx", "?") if isinstance(fr, dict) else "?"
            print(f"  [{frame_num}] {fr.get('frame','?')} {inst} {tf} | prices=[{', '.join(prices[:4])}{'...' if len(prices)>4 else ''}] | {structure}")
    print()
