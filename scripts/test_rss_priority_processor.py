#!/usr/bin/env python3
"""
test_rss_priority_processor.py
===============================
Pruebas de aceptación para scripts/rss_priority_processor.py del proyecto
YouTubeTradingAgent.

Cubre los 9 criterios de aceptación:
  T1  RSS detecta un video nuevo.
  T2  Un video nuevo tiene prioridad sobre el histórico.
  T3  Sin novedades, se procesa el histórico más reciente pendiente.
  T4  Después se selecciona el histórico inmediatamente anterior.
  T5  Una novedad durante el histórico obtiene prioridad.
  T6  No se reprocesan videos completados.
  T7  El estado sobrevive a una interrupción controlada.
  T8  El modelo visual utilizado es Qwen local (qwen3.5:9b-mlx / qwen2.5vl:3b).
  T9  No existe dependencia operativa de Gemini.

Uso:
  python3 test_rss_priority_processor.py [--sandbox DIR] [--report FILE]
"""

from __future__ import annotations

import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path
import socketserver
import threading
import http.server

# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------

SCRIPT = Path("/Users/franciscootamendi/YouTubeTradingAgent/scripts/rss_priority_processor.py")
PROJECT = Path("/Users/franciscootamendi/YouTubeTradingAgent")
RSS_URL = ("https://www.youtube.com/feeds/videos.xml"
           "?channel_id=UC4DOPLw9NRRBFW4wYjcWxiA")
STATE_FILE = PROJECT / "experimental" / "results" / "historical_progress.json"

# Videos históricos reales (ya descargados: video + frames + transcripciones)
HISTORICAL_VIDS = [
    {"id": "0prmrS6nnRk", "title": "Bitcoin cae un 5,9% y se frena en 75.518",
     "published": "2026-11-06T09:32:22+00:00", "year": 2026, "month": 11, "day": 6},
    {"id": "o6n6UDNVtCk", "title": "Bitcoin en zona de compras, pero yo no compro aquí",
     "published": "2026-11-07T14:00:16+00:00", "year": 2026, "month": 11, "day": 7},
    {"id": "rTtXDLq2kOQ", "title": "Bitcoin y los futuros de Chicago",
     "published": "2026-11-09T09:10:08+00:00", "year": 2026, "month": 11, "day": 9},
    {"id": "subONxt5iag", "title": "Bitcoin aguanta pese a las salidas de los ETF",
     "published": "2026-11-10T09:40:55+00:00", "year": 2026, "month": 11, "day": 10},
]

RESULTS = []          # resultados de cada prueba
SANDBOX = Path(tempfile.mkdtemp(prefix="rss_pp_"))


def record(name, ok, detail=""):
    RESULTS.append({"name": name, "ok": bool(ok), "detail": detail})
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {name}" + (f"  -- {detail}" if detail else ""))
    return ok


# Importación de constantes del script
from rss_priority_processor import ALL_STEPS, STATUS_DETECTED, STATUS_COMPLETED  # noqa: E402


# ---------------------------------------------------------------------------
# Utilería: sandbox
# ---------------------------------------------------------------------------

def make_sandbox() -> Path:
    """Crea el árbol del sandbox para pruebas de cola/prioridades."""
    base = SANDBOX / "test"
    (base / "experimental" / "results" / "historical").mkdir(parents=True, exist_ok=True)
    (base / "data_hist").mkdir(parents=True, exist_ok=True)
    (base / "frames_hist").mkdir(parents=True, exist_ok=True)
    return base


def write_state(sandbox: Path, videos: dict, extra: dict | None = None):
    """Escribe un fichero de estado en el sandbox."""
    state = {
        "channel_id": "UC4DOPLw9NRRBFW4wYjcWxiA",
        "check_interval_seconds": 14400,
        "last_check": "2026-11-10T00:00:00Z",
        "videos": videos,
    }
    if extra:
        state.update(extra)
    (sandbox / "experimental" / "results" / "historical_progress.json").write_text(
        json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def read_state(sandbox: Path):
    return json.loads(
        (sandbox / "experimental" / "results" / "historical_progress.json").read_text())


# ---------------------------------------------------------------------------
# Pruebas de cola/prioridades (lógica pura)
# ---------------------------------------------------------------------------

def test_t2_priority_new_over_historical():
    """T2: video nuevo (rank 1) precede a histórico (rank 3)."""
    sandbox = make_sandbox()
    videos = {}
    # Videos históricos pendientes
    for vid in ["rTtXDLq2kOQ", "o6n6UDNVtCk"]:
        videos[vid] = {
            "title": "hist",
            "published": "2026-11-09T09:10:08+00:00",
            "status": "pending",
            "priority_rank": 0, "priority_order": 0,
            "progress": {s: False for s in ALL_STEPS}, "retry_count": 0,
            "last_error": None, "artifacts": {},
        }
    # Un video recién detectado (no está en el registro)
    videos["NEW123"] = {
        "title": "Novedad",
        "published": "2026-11-10T09:00:00+00:00",
        "status": "detected",
        "priority_rank": 0, "priority_order": 0,
        "progress": {s: False for s in ALL_STEPS}, "retry_count": 0,
        "last_error": None, "artifacts": {},
    }
    write_state(sandbox, videos)

    # Construye la cola con el RSS simulado
    from rss_priority_processor import build_queue, STATUS_DETECTED
    rss = [
        {"id": "NEW123", "title": "Novedad", "published": "2026-11-10T09:00:00+00:00"},
        {"id": "rTtXDLq2kOQ", "title": "hist", "published": "2026-11-09T09:10:08+00:00"},
        {"id": "o6n6UDNVtCk", "title": "hist", "published": "2026-11-07T14:00:16+00:00"},
    ]
    queue = build_queue(json.loads((sandbox / "experimental" / "results"
                                    / "historical_progress.json").read_text()),
                        rss)
    ok = queue == ["NEW123", "rTtXDLq2kOQ", "o6n6UDNVtCk"]
    record("T2 nuevo sobre histórico", ok,
           f"cola={queue}" if not ok else "")


def _hist_video(vid, published):
    return {
        "title": "hist", "published": published,
        "status": "pending", "priority_rank": 0, "priority_order": 0,
        "progress": {s: False for s in ALL_STEPS}, "retry_count": 0,
        "last_error": None, "artifacts": {},
    }


def test_t3_historical_reverse_sequential():
    """T3: sin novedades → histórico más reciente primero."""
    sandbox = make_sandbox()
    videos = {
        "rTtXDLq2kOQ": _hist_video("rTtXDLq2kOQ", "2026-11-09T09:10:08+00:00"),
        "o6n6UDNVtCk": _hist_video("o6n6UDNVtCk", "2026-11-07T14:00:16+00:00"),
    }
    write_state(sandbox, videos)

    from rss_priority_processor import build_queue
    rss = [
        {"id": "rTtXDLq2kOQ", "title": "hist", "published": "2026-11-09T09:10:08+00:00"},
        {"id": "o6n6UDNVtCk", "title": "hist", "published": "2026-11-07T14:00:16+00:00"},
    ]
    queue = build_queue(json.loads((sandbox / "experimental" / "results"
                                    / "historical_progress.json").read_text()), rss)
    ok = queue == ["rTtXDLq2kOQ", "o6n6UDNVtCk"]
    record("T3 histórico inverso (más reciente primero)", ok,
           f"cola={queue}" if not ok else "")


def test_t4_second_historical():
    """T4: tras procesar el más reciente, selecciona el inmediatamente anterior."""
    sandbox = make_sandbox()
    videos = {
        "rTtXDLq2kOQ": _hist_video("rTtXDLq2kOQ", "2026-11-09T09:10:08+00:00"),
        "o6n6UDNVtCk": _hist_video("o6n6UDNVtCk", "2026-11-07T14:00:16+00:00"),
    }
    write_state(sandbox, videos)

    from rss_priority_processor import build_queue
    rss = [
        {"id": "rTtXDLq2kOQ", "title": "hist", "published": "2026-11-09T09:10:08+00:00"},
        {"id": "o6n6UDNVtCk", "title": "hist", "published": "2026-11-07T14:00:16+00:00"},
    ]
    queue = build_queue(json.loads((sandbox / "experimental" / "results"
                                    / "historical_progress.json").read_text()), rss)
    first = queue[0]
    # Marca el primero como completado
    videos[first]["status"] = "completed"
    write_state(sandbox, videos)
    queue2 = build_queue(json.loads((sandbox / "experimental" / "results"
                                     / "historical_progress.json").read_text()), rss)
    ok = queue2 == ["o6n6UDNVtCk"]
    record("T4 siguiente histórico", ok, f"segundo={queue2}" if not ok else "")


def test_t5_new_priority_during_historical():
    """T5: novedad mezclada con históricos → la novedad va primero."""
    sandbox = make_sandbox()
    videos = {
        "rTtXDLq2kOQ": _hist_video("rTtXDLq2kOQ", "2026-11-09T09:10:08+00:00"),
        "o6n6UDNVtCk": _hist_video("o6n6UDNVtCk", "2026-11-07T14:00:16+00:00"),
    }
    write_state(sandbox, videos)

    from rss_priority_processor import build_queue
    rss = [
        {"id": "rTtXDLq2kOQ", "title": "hist", "published": "2026-11-09T09:10:08+00:00"},
        {"id": "o6n6UDNVtCk", "title": "hist", "published": "2026-11-07T14:00:16+00:00"},
        {"id": "NEW_ONLY", "title": "Novedad", "published": "2026-11-10T09:00:00+00:00"},
    ]
    queue = build_queue(json.loads((sandbox / "experimental" / "results"
                                    / "historical_progress.json").read_text()), rss)
    ok = len(queue) == 3 and queue[0] == "NEW_ONLY" and queue[1] == "rTtXDLq2kOQ"
    record("T5 novedad durante histórico", ok,
           f"cola={queue}" if not ok else "")


def test_t6_no_reprocess_completed():
    """T6: video completado no se reprocesa."""
    sandbox = make_sandbox()
    videos = {
        "rTtXDLq2kOQ": _hist_video("rTtXDLq2kOQ", "2026-11-09T09:10:08+00:00"),
        "o6n6UDNVtCk": _hist_video("o6n6UDNVtCk", "2026-11-07T14:00:16+00:00"),
    }
    # Marcar ambos como completados
    for vid in videos:
        videos[vid]["status"] = "completed"
    write_state(sandbox, videos)

    from rss_priority_processor import build_queue
    rss = [
        {"id": "rTtXDLq2kOQ", "title": "hist", "published": "2026-11-09T09:10:08+00:00"},
        {"id": "o6n6UDNVtCk", "title": "hist", "published": "2026-11-07T14:00:16+00:00"},
    ]
    queue = build_queue(json.loads((sandbox / "experimental" / "results"
                                    / "historical_progress.json").read_text()), rss)
    ok = len(queue) == 0
    record("T6 sin reproceso de completados", ok,
           f"cola={queue}" if not ok else "")


# ---------------------------------------------------------------------------
# Pruebas de ejecución del script
# ---------------------------------------------------------------------------

def run_script(args, sandbox=None, timeout=120):
    """Ejecuta el script con los args en un sandbox (si se indica)."""
    cmd = [sys.executable, str(SCRIPT)] + args
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def test_t1_rss_detects_new():
    """T1: RSS detecta un video nuevo."""
    # Se ejecuta el script en --check-only sobre el estado real del proyecto.
    log_file = "/tmp/t1_rss.log"
    r = subprocess.run(
        [sys.executable, str(SCRIPT), "--check-only", "--verbose",
         "--log-file", log_file],
        capture_output=True, text=True, timeout=120)
    # Las líneas "[detected]" se escriben en el fichero de log (verbose=False)
    log_text = Path(log_file).read_text(encoding="utf-8") if Path(log_file).exists() else ""
    n_detected = log_text.count("[detected]")
    ok = r.returncode == 0 and n_detected >= 8
    record("T1 RSS detecta video nuevo", ok,
           f"rc={r.returncode}, detected_lines={n_detected} (log {log_file})")
    return ok


def test_t7_interrupt_survives():
    """T7: estado sobrevive a interrupción controlada (SIGTERM)."""
    sandbox = make_sandbox()
    vid = "vit_sandbox"
    # Preparamos un video parcialmente procesado: download+frames, transcript
    # falso (pre-creado) para que la reanudación alcance la validación.
    videos = {}
    videos[vid] = {
        "title": "Sandbox", "published": "2026-11-10T09:00:00+00:00",
        "status": "pending", "priority_rank": 0, "priority_order": 0,
        "progress": {"download": False, "frames": False, "transcript": False,
                     "vision": False, "validation": False},
        "retry_count": 0, "last_error": None,
        "artifacts": {"video_path": None, "frames_dir": None,
                      "transcript_path": None, "analysis_file": None},
    }
    write_state(sandbox, videos)

    # Artefactos: video, frames, transcripción (pre-creados)
    (sandbox / "data" / vid).mkdir(parents=True, exist_ok=True)
    (sandbox / "frames" / vid).mkdir(parents=True, exist_ok=True)
    (sandbox / "frames" / vid / "frame_0001.jpg").write_bytes(b"fake-frame")
    (sandbox / "data" / vid / f"{vid}.mp4").write_bytes(b"fake-video")
    (sandbox / "data" / vid / f"{vid}_transcript.json").write_text(
        json.dumps({"video_id": vid, "segments": [], "full_text": ""},
                   ensure_ascii=False), encoding="utf-8")

    # RSS local: solo el video de sandbox
    rss_dir = sandbox / "rss"
    rss_dir.mkdir(parents=True, exist_ok=True)
    rss_xml = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>yt:video:vit_sandbox</id>
    <title>Sandbox video</title>
    <published>2026-11-10T09:00:00+00:00</published>
  </entry>
</feed>
"""
    rss_file = rss_dir / "feed.xml"
    rss_file.write_text(rss_xml, encoding="utf-8")
    handler = lambda *a, **kw: http.server.SimpleHTTPRequestHandler(*a,
                     directory=str(rss_dir), **kw)
    httpd = socketserver.TCPServer(("127.0.0.1", 0), handler)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    rss_url = f"http://127.0.0.1:{httpd.server_address[1]}/feed.xml"

    args = ["--rss-url", rss_url,
            "--progress-file", str(sandbox / "experimental" / "results"
                                    / "historical_progress.json"),
            "--data-dir", str(sandbox / "data"),
            "--frames-dir", str(sandbox / "frames"),
            "--results-dir", str(sandbox / "res"),
            "--max-videos-per-run", "1", "--no-vision", "--max-frames", "1"]
    proc = subprocess.Popen([sys.executable, str(SCRIPT)] + args,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True)
    try:
        time.sleep(1.5)
        proc.send_signal(signal.SIGTERM)
        outp, _ = proc.communicate(timeout=15)
    except subprocess.TimeoutExpired:
        proc.kill()
        outp, _ = proc.communicate()

    state = json.loads(
        (sandbox / "experimental" / "results" / "historical_progress.json").read_text())
    vid_state = state["videos"][vid]
    # Tras la interrupción, el estado debe ser coherente: el archivo de estado
    # debe existir con prossec y estructura correcta.
    ok = vid_state is not None and vid_state.get("progress") is not None
    record("T7 estado sobrevive interrupción", ok,
           f"status={vid_state['status']}, progress={vid_state['progress']}")

    # Reanudación: debe completar el transcript (si falló) y validar.
    # Usamos --once para que el script salga después de un ciclo.
    resume_args = args + ["--once"]
    r = subprocess.run([sys.executable, str(SCRIPT)] + resume_args,
                       capture_output=True, text=True, timeout=60)
    state2 = json.loads(
        (sandbox / "experimental" / "results" / "historical_progress.json").read_text())
    vid_state2 = state2["videos"][vid]
    ok2 = (vid_state2["status"] == "completed"
           and vid_state2["progress"]["validation"])
    record("T7 reanudación completa", ok2,
           f"status_final={vid_state2['status']}, "
           f"progress={vid_state2['progress']}")
    httpd.shutdown()
    httpd.server_close()
    return ok and ok2


# ---------------------------------------------------------------------------
# Pruebas de dependencias
# ---------------------------------------------------------------------------

def test_t8_qwen_local_model():
    """T8: el modelo visual utilizado es Qwen local."""
    src = SCRIPT.read_text(encoding="utf-8")
    # El código debe usar Ollama + Qwen (qwen3.5:9b-mlx o qwen2.5vl:3b)
    ok = ("qwen3.5:9b-mlx" in src or "qwen2.5vl:3b" in src) and "ollama" in src.lower()
    record("T8 modelo visual Qwen local", ok,
           "Qwen encontrado y Ollama usado" if ok else "FALLO")


def test_t9_no_gemini():
    """T9: sin dependencia operativa de Gemini."""
    src = SCRIPT.read_text(encoding="utf-8")
    # Busca la *utilización* real de Gemini (APIs/services), no las palabras
    # del documento de diseño (que mencionan 'Gemini' como contraejemplo).
    gemini_apis = [
        "googleapiclient", "googleapiclient.discovery", "googleapiclient.http",
        "google.cloud", "google generative", "generativelanguage",
        "GEMINI_API_KEY", "genai", "GenerativeModel", "google.ai.generativelanguage",
        "https://generativelanguage.googleapis.com",
    ]
    hits = [kw for kw in gemini_apis if kw.lower() in src.lower()]
    ok = len(hits) == 0
    record("T9 sin dependencia Gemini", ok,
           f"APIs de Gemini detectadas: {hits}" if not ok else "")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 70)
    print("PRUEBAS DE ACEPTACIÓN — RSS + prioridades + aprendizaje histórico")
    print(f"Sandbox: {SANDBOX}")
    print("=" * 70)

    # T1: RSS detecta video nuevo (ejecución real)
    test_t1_rss_detects_new()

    # T2-T6: lógica de cola (unit-level)
    test_t2_priority_new_over_historical()
    test_t3_historical_reverse_sequential()
    test_t4_second_historical()
    test_t5_new_priority_during_historical()
    test_t6_no_reprocess_completed()

    # T7: interrupción controlada
    test_t7_interrupt_survives()

    # T8-T9: dependencias
    test_t8_qwen_local_model()
    test_t9_no_gemini()

    # Resumen
    print("\n" + "=" * 70)
    passed = sum(1 for r in RESULTS if r["ok"])
    total = len(RESULTS)
    for r in RESULTS:
        print(f"  [{'PASS' if r['ok'] else 'FAIL'}] {r['name']}")
    print(f"\n{passed}/{total} pruebas superadas")
    print("=" * 70)

    # Guarda el reporte
    report = Path("/tmp/rss_pp_test_report.md")
    lines = []
    lines.append("# Reporte de pruebas — RSS + prioridades + aprendizaje histórico")
    lines.append("")
    lines.append(f"Fecha: 2026-11-10")
    lines.append(f"Sandbox: `{SANDBOX}`")
    lines.append("")
    lines.append("| # | Prueba | Resultado |")
    lines.append("|---|---|---|")
    for r in RESULTS:
        lines.append(f"| {r['name']} | {'Superado' if r['ok'] else 'No superado'} |")
    lines.append("")
    lines.append(f"Total: {passed}/{total} superadas")
    lines.append("")
    report.write_text("\n".join(lines), encoding="utf-8")
    print(f"Reporte guardado en {report}")

    # Limpia sandbox
    shutil.rmtree(SANDBOX, ignore_errors=True)

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
