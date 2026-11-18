#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script para procesar la visión en lotes de 5 frames para LFHkc5dUoLw."""

import json
import sys
from pathlib import Path

sys.path.insert(0, '/Users/franciscootamendi/YouTubeTradingAgent')

from scripts.rss_priority_processor import (
    analyze_frame_vision,
    save_state,
    VISION_PROMPT_TEMPLATE,
    load_state
)

video_id = "LFHkc5dUoLw"
base_dir = Path("/Users/franciscootamendi/YouTubeTradingAgent")
progress_file = base_dir / "experimental" / "results" / "historical_progress.json"
log_file = base_dir / "experimental" / "results" / "run_LFHkc5dUoLw_batched.log"
frames_dir = base_dir / "frames_hist" / video_id
analysis_file = base_dir / "experimental" / "results" / "historical" / (video_id + "_analysis.json")

print("=== Estado actual ===")
state = load_state(progress_file)
entry = state["videos"][video_id]
progress = entry["progress"]
print("Progress:", progress)

if progress.get("vision"):
    print("Vision ya completada. No hay trabajo pendiente.")
    sys.exit(0)

# Obtener lista de frames
frames = sorted(frames_dir.glob("frame_*.jpg"))
print("Total de frames disponibles:", len(frames))

# Cargar análisis existente
if analysis_file.exists():
    with open(analysis_file) as f:
        analysis = json.load(f)
    processed_frames = {item["frame"] for item in analysis.get("frame_results", [])}
    print("Frames ya procesados:", len(processed_frames))
else:
    analysis = {
        "video_id": video_id,
        "title": entry.get("title", ""),
        "published": entry.get("published", ""),
        "frames_processed": 0,
        "frame_results": [],
        "transcript_available": None,
    }
    processed_frames = set()

# Lotes de 5 frames
BATCH_SIZE = 5
frames_to_process = [f for f in frames if f.name not in processed_frames]
print("Frames pendientes de procesar:", len(frames_to_process))

for start_idx in range(0, len(frames_to_process), BATCH_SIZE):
    batch = frames_to_process[start_idx:start_idx + BATCH_SIZE]
    batch_num = start_idx // BATCH_SIZE + 1
    print("=" * 60)
    print("Lote " + str(batch_num) + ": " + str(len(batch)) + " frames")
    print("=" * 60)
    
    for frame in batch:
        print("  Procesando " + frame.name + "...")
        result = analyze_frame_vision(
            frame, "qwen2.5vl:3b", VISION_PROMPT_TEMPLATE,
            "http://localhost:11434", 300
        )
        
        found = False
        for old in analysis.get("frame_results", []):
            if old.get("frame") == frame.name:
                old["vision"] = result
                old["analyzed_at"] = "2026-11-15T22:00:00Z"
                found = True
                break
        if not found:
            analysis.setdefault("frame_results", []).append({
                "frame": frame.name,
                "frame_idx": len(analysis.get("frame_results", [])),
                "vision": result,
                "analyzed_at": "2026-11-15T22:00:00Z",
            })
        
        analysis["frames_processed"] = len(analysis.get("frame_results", []))
        
        analysis_file.parent.mkdir(parents=True, exist_ok=True)
        with open(analysis_file, "w") as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)
        print("    Guardado:", frame.name, "|", result[:80] + "...")
    
    entry["progress"]["vision"] = False
    entry["progress"]["validation"] = False
    save_state(state, progress_file, log_file)
    print("  Estado guardado en", progress_file)
    print("  Total de frames procesados hasta ahora:", analysis["frames_processed"])

entry["progress"]["vision"] = True
entry["progress"]["validation"] = False
save_state(state, progress_file, log_file)

with open(analysis_file) as f:
    final_analysis = json.load(f)
print("=" * 60)
print("=== RESUMEN FINAL ===")
print("Total de frames procesados:", final_analysis["frames_processed"])
print("Frames totales:", len(frames))
print("Análisis guardado en:", analysis_file)
