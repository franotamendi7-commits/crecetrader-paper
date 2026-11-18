#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Procesa el análisis visual de un video, reanudando desde el checkpoint.
"""
import json, os, time, requests, base64, subprocess, sys

BASE = "/Users/franciscootamendi/YouTubeTradingAgent"
VIDEO_ID = sys.argv[1] if len(sys.argv) > 1 else "mv2VdVtXvDw"

DATA = json.load(open(f"{BASE}/experimental/results/historical_progress.json"))
entry = DATA["videos"][VIDEO_ID]
progress = entry["progress"]

# Verificar que los pasos anteriores están completos
if not progress["download"]:
    print("ERROR: descarga pendiente")
    sys.exit(1)
if not progress["frames"]:
    print("ERROR: frames pendientes")
    sys.exit(1)
if not progress["transcript"]:
    print("ERROR: transcripción pendiente")
    sys.exit(1)

# Cargar el estado actual
VIDEO = {VIDEO_ID: entry}
state = VIDEO

frames_dir = f"{BASE}/frames_hist/{VIDEO_ID}"
frames = sorted([f for f in os.listdir(frames_dir) if f.endswith('.jpg')])
print(f"Frames disponibles: {len(frames)}")

# Cargar el análisis existente
analysis_file = f"{BASE}/experimental/results/historical/{VIDEO_ID}_analysis.json"
results = []
if os.path.exists(analysis_file):
    results = json.load(open(analysis_file))
    print(f"Análisis existente: {results.get('frames_processed', 0)} frames")

# Modelo a usar
model = "qwen2.5vl:3b"

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

def analyze_frame(image_path, transcript):
    with open(image_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
    payload = {"model": model, "messages": [
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

# Procesar las frames restantes
frames_to_process = frames[results.get("frames_processed", 0):]
print(f"Frames pendientes: {len(frames_to_process)}")

completed = results.get("frames_processed", 0)
for frame_name in frames_to_process:
    frame_path = os.path.join(frames_dir, frame_name)
    
    # Cargar transcripción
    transcript = ""
    transcript_file = f"{BASE}/data_hist/{VIDEO_ID}/{VIDEO_ID}.es.vtt"
    if os.path.exists(transcript_file):
        with open(transcript_file, 'r', encoding='utf-8') as f:
            transcript = f.read()[:500]
    
    result, elapsed, error = analyze_frame(frame_path, transcript)
    
    if result is None:
        print(f"  ERROR {frame_name}: {error}")
        results["errors"] = results.get("errors", [])
        results["errors"].append({"frame": frame_name, "error": str(error)})
    else:
        results["frame_results"].append({
            "frame": frame_name,
            "frame_idx": completed,
            "vision": result,
            "analyzed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        })
        completed += 1
    
    results["frames_processed"] = completed
    
    # Guardar checkpoint
    with open(analysis_file, 'w') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"  Frame {completed}: {frame_name} - {elapsed}s - JSON guardado")

# Marcar vision como true
entry["progress"]["vision"] = True
with open(f"{BASE}/experimental/results/historical_progress.json", 'w') as f:
    json.dump(DATA, f, ensure_ascii=False, indent=2)

print(f"\nCompletado: {completed} frames procesados")
print(f"Resultado: {analysis_file}")
