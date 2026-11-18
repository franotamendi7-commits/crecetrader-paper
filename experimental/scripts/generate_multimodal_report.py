import json, os

BASE = "/Users/franciscootamendi/YouTubeTradingAgent"
VA = json.load(open(f"{BASE}/experimental/results/vision_analysis.json"))
TRANSCRIPT = json.load(open(f"{BASE}/data/rTtXDLq2kOQ_transcript.json"))["segments"]

# Build transcript by scene
SCENES = json.load(open(f"{BASE}/data/rTtXDLq2kOQ_scenes.json"))

report_lines = []
report_lines.append("# INFORME MULTIMODAL CORRELACIONADO — Video rTtXDLq2kOQ\n")
report_lines.append("## Bitcoin and Chicago Futures: Where Institutional Money Is Waiting\n")
report_lines.append("### Canal: Bitcoin Hoy / CreceTrader | Duración: ~899s\n\n")

for va in VA:
    idx = va["scene_idx"]
    scene = SCENES[idx] if idx < len(SCENES) else None
    start = va.get("start", 0)
    end = va.get("end", 0)
    
    # Get transcript for this scene
    segs = [s for s in TRANSCRIPT if s["start"] < end and s["end"] > start]
    text = " ".join(s["text"] for s in segs)
    
    report_lines.append(f"## Escena {idx} ({start:.1f}s - {end:.1f}s)\n")
    report_lines.append(f"**Frame:** {va['frame']}\n")
    report_lines.append(f"**Transcripción (audio):** {text[:300]}\n")
    
    if "vision_analysis" in va:
        report_lines.append(f"**Análisis visual (Qwen3.5):** {va['vision_analysis'][:500]}\n")
        report_lines.append(f"**Tiempo de inferencia:** {va['time_seconds']}s\n")
    else:
        report_lines.append(f"**Error:** {va.get('error', 'N/A')}\n")
    
    report_lines.append("\n---\n\n")

# Summary
ok = sum(1 for e in VA if "vision_analysis" in e)
err = sum(1 for e in VA if "error" in e)
report_lines.append(f"## Resumen\n")
report_lines.append(f"- Frames procesados: {len(VA)}\n")
report_lines.append(f"- Éxitos: {ok}\n")
report_lines.append(f"- Timeouts/errores: {err}\n")
report_lines.append(f"- Tiempo total: {sum(e.get('time_seconds', 0) for e in VA):.0f}s\n")

os.makedirs(f"{BASE}/experimental/results", exist_ok=True)
with open(f"{BASE}/experimental/results/multimodal_report.md", "w") as f:
    f.write("\n".join(report_lines))
print(f"Report generated: experimental/results/multimodal_report.md")
print(f"Frames: {len(VA)}, OK: {ok}, Errors: {err}")