#!/usr/bin/env ".venv/bin/python"
"""
Prototipo mínimo para análisis de video de YouTube.

Procesa un video de YouTube para:
1. Descargar audio usando yt-dlp (solo audio, formato wav)
2. Transcribir el audio con faster-whisper (modelo small, español, con timestamps a nivel de segmento)
3. Detectar escenas con PySceneDetect (ContentDetector)
4. Extraer 1 frame por escena detectada usando OpenCV
5. Analizar cada frame con Tesseract OCR (español + inglés)
6. Generar un informe Markdown en reports/ con:
   - Identificación del video
   - Transcripción completa con timestamps
   - Frames extraídos con timestamps
   - Texto OCR de cada frame
   - Resumen de hallazgos clasificados como [DICHO], [OBSERVADO], [INFERIDO]
"""

import os
import sys
import subprocess
import json
from datetime import datetime

# ---------------------------------------------------------------------------
# Rutas basadas en la ubicación del script
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")
FRAMES_DIR = os.path.join(BASE_DIR, "frames")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(FRAMES_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

# Configuración del video
VIDEO_URL = "https://www.youtube.com/watch?v=rTtXDLq2kOQ"
VIDEO_ID = "rTtXDLq2kOQ"
VIDEO_TITLE = "Bitcoin and Chicago Futures: Where Institutional Money Is Waiting"

AUDIO_FILE = os.path.join(DATA_DIR, f"{VIDEO_ID}.wav")
TRANSCRIPT_FILE = os.path.join(DATA_DIR, f"{VIDEO_ID}_transcript.json")
SCENES_FILE = os.path.join(DATA_DIR, f"{VIDEO_ID}_scenes.json")
FRAMES_METADATA_FILE = os.path.join(DATA_DIR, f"{VIDEO_ID}_frames.json")
REPORT_FILE = os.path.join(REPORTS_DIR, f"{VIDEO_ID}_report.md")

VIDEO_MP4 = os.path.join(DATA_DIR, f"{VIDEO_ID}.mp4")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def run_cmd(cmd, description=""):
    """Ejecutar un comando y lanzar RuntimeError si falla."""
    print(f"Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        msg = f"{description} failed.\nstdout: {result.stdout}\nstderr: {result.stderr}"
        raise RuntimeError(msg)
    return result


def download_video():
    """Descargar el video completo de YouTube usando yt-dlp."""
    print(f"[INFO] Descargando video de: {VIDEO_URL}")
    if not os.path.exists(VIDEO_MP4):
        run_cmd([
            "yt-dlp",
            "-f", "best",
            "-o", VIDEO_MP4,
            VIDEO_URL,
        ], "Video download")
        print(f"[OK] Video guardado en: {VIDEO_MP4}")
    else:
        print(f"[OK] Video ya existe: {VIDEO_MP4}")


def extract_audio():
    """Descargar el audio del video usando yt-dlp (solo audio, formato WAV)."""
    print(f"[INFO] Extrayendo audio del video...")
    if os.path.exists(AUDIO_FILE):
        os.remove(AUDIO_FILE)
    run_cmd([
        "yt-dlp",
        "-x",
        "--audio-format", "wav",
        "-o", AUDIO_FILE,
        VIDEO_URL,
    ], "Audio extraction")
    print(f"[OK] Audio guardado en: {AUDIO_FILE}")


# ---------------------------------------------------------------------------
# Paso 2: Transcripción con faster-whisper
# ---------------------------------------------------------------------------

def transcribe_audio():
    """Transcribir el audio con faster-whisper (modelo small, español, timestamps)."""
    print(f"[INFO] Transcribiendo audio con faster-whisper (modelo small, idioma: es)...")
    try:
        from faster_whisper import WhisperModel

        model = WhisperModel("small", compute_type="float32")
        segments, info = model.transcribe(
            AUDIO_FILE,
            language="es",
            without_timestamps=False,
        )

        transcription = {
            "language": info.language,
            "language_probability": info.language_probability,
            "segments": [],
        }

        for segment in segments:
            transcription["segments"].append({
                "id": segment.id,
                "start": round(segment.start, 2),
                "end": round(segment.end, 2),
                "text": segment.text.strip(),
            })

        print(f"[OK] Transcripción completada: {len(transcription['segments'])} segments")
        print(f"[INFO] Idioma detectado: {info.language} (probabilidad: {info.language_probability:.2f})")

        # Guardar transcription
        with open(TRANSCRIPT_FILE, "w", encoding="utf-8") as f:
            json.dump(transcription, f, ensure_ascii=False, indent=2)

        return transcription
    except ImportError as e:
        print(f"[ERROR] faster-whisper no disponible: {e}")
        raise
    except Exception as e:
        print(f"[ERROR] Error durante la transcripción: {e}")
        raise


# ---------------------------------------------------------------------------
# Paso 3: Detección de escenas con PySceneDetect (ContentDetector)
# ---------------------------------------------------------------------------

def detect_scenes():
    """Detectar escenas con PySceneDetect usando ContentDetector (CLI)."""
    print(f"[INFO] Detectando escenas con PySceneDetect (ContentDetector)...")
    try:
        # Usar el CLI de PySceneDetect con detect-content
        # El comando: scenedetect -i input.mp4 -o output_dir detect-content -t threshold
        cmd = [
            ".venv/bin/scenedetect",
            "-i", str(VIDEO_MP4),
            "-o", str(DATA_DIR),
            "detect-content",
            "-t", "30.0",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[ERROR] Error en scene detection CLI: {result.stderr}")
            # Create empty scenes placeholder
            scenes = []
            with open(SCENES_FILE, "w", encoding="utf-8") as f:
                json.dump(scenes, f, ensure_ascii=False, indent=2)
            return {"scenes": scenes, "count": 0}

        # Leer la lista de escenas generada por PySceneDetect (archivo CSV)
        csv_path = os.path.join(DATA_DIR, f"{VIDEO_ID}-Scenes.csv")
        scenes = []
        if os.path.exists(csv_path):
            with open(csv_path, encoding="utf-8") as f:
                lines = f.readlines()
            # Parsear el CSV - saltar las 2 primeras líneas (cabecera)
            for line in lines[2:]:
                line = line.strip()
                if not line or line.startswith("---"):
                    continue
                parts = line.split(",")  # CSV uses commas, not pipes
                if len(parts) >= 7:
                    try:
                        scene_id = int(parts[0].strip())
                        start_frame = int(parts[1].strip())
                        start_time_str = parts[2].strip()
                        # end_frame = int(parts[3].strip())  # Not needed
                        end_time_str = parts[5].strip()  # End timecode is at index 5

                        # Convertir tiempo formato HH:MM:SS.mmm a segundos
                        def timecode_to_seconds(tc):
                            parts_tc = tc.split(":")
                            if len(parts_tc) == 3:
                                h, m, s = parts_tc
                                return int(h) * 3600 + int(m) * 60 + float(s)
                            return 0.0

                        start_sec = timecode_to_seconds(start_time_str)
                        end_sec = timecode_to_seconds(end_time_str)
                        duration = round(end_sec - start_sec, 2)

                        scenes.append({
                            "id": scene_id - 1,  # 0-indexed
                            "start": start_sec,
                            "end": end_sec,
                            "duration": duration,
                            "start_timecode": start_time_str,
                            "end_timecode": end_time_str,
                        })
                    except (ValueError, IndexError) as e:
                        print(f"[WARNING] Could not parse scene line: {line} - {e}")
                        continue

        # Guardar metadatos de escenas
        with open(SCENES_FILE, "w", encoding="utf-8") as f:
            json.dump(scenes, f, ensure_ascii=False, indent=2)

        scene_count = len(scenes) if scenes else 0
        print(f"[OK] {scene_count} escenas detectadas via CLI")

        return {"scenes": scenes, "count": scene_count}
    except Exception as e:
        print(f"[ERROR] Error detecting scenes: {e}")
        import traceback
        traceback.print_exc()
        scenes = []
        with open(SCENES_FILE, "w", encoding="utf-8") as f:
            json.dump(scenes, f, ensure_ascii=False, indent=2)
        return {"scenes": scenes, "count": 0}


# ---------------------------------------------------------------------------
# Paso 4: Extraer 1 frame por escena usando OpenCV
# ---------------------------------------------------------------------------

def extract_frames(scenes):
    """Extraer 1 frame por escena detectada usando OpenCV."""
    print(f"[INFO] Extrayendo 1 frame por escena detectada...")
    extracted_frames = []

    try:
        import cv2

        video_manager = cv2.VideoCapture(str(VIDEO_MP4))
        if not video_manager.isOpened():
            raise RuntimeError(f"No se puede abrir el video: {VIDEO_MP4}")

        for scene in scenes:
            start_sec = scene["start"]
            # Tomar el frame en el centro de la escena
            frame_sec = start_sec + (scene["duration"] / 2)

            # Seek a la posición del frame
            video_manager.set(cv2.CAP_PROP_POS_MSEC, frame_sec * 1000)

            success, frame = video_manager.read()
            if not success:
                print(f"[WARNING] No se pudo leer el frame en {frame_sec}s para escena {scene['id']}")
                continue

            # Nombre de archivo del frame
            frame_filename = os.path.join(
                FRAMES_DIR, f"scene_{scene['id']:03d}_{start_sec:.1f}s.jpg"
            )

            # Guardar frame
            cv2.imwrite(str(frame_filename), frame)

            # Propiedades del frame
            frame_data = {
                "id": scene["id"],
                "start_time": scene["start"],
                "end_time": scene["start"] + scene["duration"],
                "duration": scene["duration"],
                "frame_path": str(frame_filename),
                "timestamp": frame_sec,
                "width": frame.shape[1],
                "height": frame.shape[0],
                "ocr_text": "",
                "ocr_language": "spa+eng",
            }

            extracted_frames.append(frame_data)
            print(f"[OK] Frame escena {scene['id']} en {frame_sec:.1f}s -> {frame_filename}")

        video_manager.release()

        # Guardar metadatos de frames
        with open(FRAMES_METADATA_FILE, "w", encoding="utf-8") as f:
            json.dump(extracted_frames, f, ensure_ascii=False, indent=2)

        return extracted_frames
    except Exception as e:
        print(f"[ERROR] Error extracting frames: {e}")
        raise


# ---------------------------------------------------------------------------
# Paso 5: OCR con Tesseract (español + inglés)
# ---------------------------------------------------------------------------

def ocr_frame(frame_path, languages="spa+eng"):
    """Analizar un frame con Tesseract OCR (español + inglés)."""
    try:
        import pytesseract
        import cv2
        import numpy as np

        img = cv2.imread(str(frame_path))
        if img is None:
            return ""

        # Convertir BGR a RGB
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Convertir a escala de grises
        gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)

        # Aplicar umbral para obtener imagen binaria
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Operaciones morfológicas para eliminar ruido
        kernel = np.ones((2, 2), np.uint8)
        cleaned = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

        # OCR con pytesseract
        text = pytesseract.image_to_string(
            cleaned,
            lang=languages,
            config="--psm 6",
        ).strip()

        return text
    except Exception as e:
        print(f"[ERROR] OCR error for {frame_path}: {e}")
        return ""


def classify_frame(text):
    """Clasificar el texto OCR en [DICHO], [OBSERVADO] o [INFERIDO]."""
    if not text:
        return "[INFERIDO] - No hay texto detectable"

    text_lower = text.lower().strip()

    # [DICHO] - afirmaciones directas, datos específicos
    dicho_keywords = [
        "bitcoin", "futuros", "institucional", "chicago", "cme",
        "price", "dollar", "percentage", "data", "report"
    ]

    # [OBSERVADO] - cosas visibles, patrones, características
    observado_keywords = [
        "chart", "graph", "line", "bar", "image", "text",
        "visible", "appears", "shows", "display"
    ]

    # [INFERIDO] - conclusiones, suposiciones, análisis
    inferido_keywords = [
        "implies", "suggests", "indicates", "means",
        "therefore", "consequently", "analysis"
    ]

    # Heurística de puntuación
    dicho_score = sum(1 for kw in dicho_keywords if kw in text_lower)
    observado_score = sum(1 for kw in observado_keywords if kw in text_lower)
    inferido_score = sum(1 for kw in inferido_keywords if kw in text_lower)

    if dicho_score > 0 and observado_score == 0 and inferido_score == 0:
        return "[DICHO]"
    elif observado_score > 0:
        return "[OBSERVADO]"
    elif inferido_score > 0:
        return "[INFERIDO]"
    elif dicho_score > 0:
        return "[DICHO]"
    else:
        # Si hay texto pero no coincide con categorías
        if len(text) > 20:
            return "[INFERIDO] - Texto detectado pero no clasificable"
        return "[INFERIDO] - Sin contenido relevante"


# ---------------------------------------------------------------------------
# Paso 6: Generar informe Markdown
# ---------------------------------------------------------------------------

def generate_report(transcription, frames, video_info):
    """Generar informe Markdown en reports/."""
    print(f"[INFO] Generando informe Markdown...")

    # Clasificar cada frame
    for frame in frames:
        frame["ocr_classification"] = classify_frame(frame.get("ocr_text", ""))

    # Contadores para el resumen
    dijo_count = sum(1 for f in frames if "[DICHO]" in f["ocr_classification"])
    observado_count = sum(1 for f in frames if "[OBSERVADO]" in f["ocr_classification"])
    inferido_count = sum(1 for f in frames if "[INFERIDO]" in f["ocr_classification"])

    report_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    md_lines = []

    # Título
    md_lines.append("# Informe de Análisis de Video de YouTube")
    md_lines.append("=" * 60)
    md_lines.append("")

    # Identificación del video
    md_lines.append("## Identificación del Video")
    md_lines.append("")
    md_lines.append(f"- **ID del Video:** {video_info.get('video_id', 'N/A')}")
    md_lines.append(f"- **Título:** {video_info.get('video_title', 'N/A')}")
    md_lines.append(f"- **URL:** {video_info.get('video_url', 'N/A')}")
    md_lines.append(f"- **Fecha de análisis:** {report_time}")
    md_lines.append("")

    # Transcripción completa
    md_lines.append("## Transcripción Completa con Timestamps")
    md_lines.append("")
    md_lines.append("```")
    for seg in transcription.get("segments", []):
        start = seg.get("start", 0)
        end = seg.get("end", 0)
        text = seg.get("text", "").replace("\n", " ")
        md_lines.append(f"[{start:.2f}s - {end:.2f}s] {text}")
    md_lines.append("```")
    md_lines.append("")

    # Frames extraídos
    md_lines.append("## Frames Extraídos por Escena")
    md_lines.append("")
    md_lines.append(f"- **Total de escenas detectadas:** {len(frames)}")
    md_lines.append(f"- **Frames con [DICHO]:** {dijo_count}")
    md_lines.append(f"- **Frames con [OBSERVADO]:** {observado_count}")
    md_lines.append(f"- **Frames con [INFERIDO]:** {inferido_count}")
    md_lines.append("")

    for frame in frames:
        md_lines.append(f"### Frame Escena {frame['id']:03d} - {frame['timestamp']:.1f}s")
        md_lines.append("")
        md_lines.append(f"- **Timestamp inicial:** {frame['start_time']:.2f}s")
        md_lines.append(f"- **Timestamp final:** {frame['end_time']:.2f}s")
        md_lines.append(f"- **Duración de escena:** {frame['duration']:.2f}s")
        md_lines.append(f"- **Resolución:** {frame['width']}x{frame['height']}")
        md_lines.append(f"- **Archivo:** `{os.path.basename(frame['frame_path'])}`")
        md_lines.append("")

        md_lines.append("#### Texto OCR")
        md_lines.append("```")
        ocr_text = frame.get("ocr_text", "") or ""
        md_lines.append(ocr_text.replace("```", "\\```") if ocr_text else "Ningún texto detectable")
        md_lines.append("```")
        md_lines.append("")

        md_lines.append("#### Clasificación")
        md_lines.append(frame["ocr_classification"])
        md_lines.append("")

    # Resumen de hallazgos
    md_lines.append("## Resumen de Hallazgos")
    md_lines.append("")
    md_lines.append(f"- **Total de frames analizados:** {len(frames)}")
    md_lines.append(f"- **Frames con [DICHO]:** {dijo_count} - Contiene afirmaciones directas o datos específicos")
    md_lines.append(f"- **Frames con [OBSERVADO]:** {observado_count} - Contiene patrones visibles, gráficos, elementos visuales")
    md_lines.append(f"- **Frames con [INFERIDO]:** {inferido_count} - Contiene conclusiones, análisis o texto no clasificable")
    md_lines.append("")

    # Hallazgos destacados
    md_lines.append("### Hallazgos Destacados")
    md_lines.append("")
    for frame in frames:
        classification = frame.get("ocr_classification", "[INFERIDO]")
        ocr_text = frame.get("ocr_text", "") or ""
        if classification != "[INFERIDO]" or (ocr_text.strip() and len(ocr_text.strip()) > 10):
            md_lines.append(f"- **Frame {frame['id']}** ({frame['timestamp']:.1f}s): {classification} - '{ocr_text[:80]}...'")
    md_lines.append("")

    # Escribir el reporte
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    print(f"[OK] Informe guardado en: {REPORT_FILE}")


# ---------------------------------------------------------------------------
# Función principal
# ---------------------------------------------------------------------------

def main():
    """Ejecutar el flujo completo de análisis de video."""
    print("=" * 60)
    print("Prototipo: Análisis de Video de YouTube")
    print("=" * 60)
    print("")

    video_info = {
        "video_id": VIDEO_ID,
        "video_title": VIDEO_TITLE,
        "video_url": VIDEO_URL,
    }

    try:
        # Paso 1: Descargar video
        print("--- Paso 1: Descargar video ---")
        download_video()

        # Paso 2: Extraer audio
        print("\n--- Paso 2: Extraer audio ---")
        extract_audio()

        # Paso 3: Transcribir audio
        print("\n--- Paso 3: Transcribir audio ---")
        transcription = transcribe_audio()

        # Paso 4: Detectar escenas
        print("\n--- Paso 4: Detectar escenas ---")
        scenes_result = detect_scenes()
        scene_count = scenes_result.get("count", 0)

        # Paso 5: Extraer frames por escena
        print("\n--- Paso 5: Extraer frames ---")
        if scene_count > 0:
            frames = extract_frames(scenes_result.get("scenes", []))
        else:
            print("[WARNING] No se detectaron escenas")
            frames = []

        # Paso 6: OCR en frames
        print("\n--- Paso 6: Análisis OCR de frames ---")
        for frame in frames:
            frame_path = frame["frame_path"]
            if os.path.exists(frame_path):
                ocr_text = ocr_frame(frame_path, languages="spa+eng")
                frame["ocr_text"] = ocr_text
                print(f"[OK] Frame {frame['id']}: OCR ({len(ocr_text)} chars)")
            else:
                frame["ocr_text"] = ""
                print(f"[WARNING] Archivo de frame no encontrado: {frame_path}")

        # Paso 7: Generar informe Markdown
        print("\n--- Paso 7: Generar informe Markdown ---")
        generate_report(transcription, frames, video_info)

        print("\n" + "=" * 60)
        print("ANÁLISIS COMPLETADO")
        print("=" * 60)
        print(f"Informe: {REPORT_FILE}")
        print(f"Frames: {FRAMES_DIR}")
        print(f"Audio: {AUDIO_FILE}")

    except KeyboardInterrupt:
        print("\n[INTERRUMPIDO] El usuario interrumpió el proceso.")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()