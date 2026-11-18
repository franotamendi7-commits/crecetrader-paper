#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
sys.path.insert(0, '.')

def main():
    import argparse
    import json
    import logging
    from pathlib import Path
    
    parser = argparse.ArgumentParser(description='Run a single video through the RSS pipeline')
    parser.add_argument('--video', required=True, help='Video ID')
    parser.add_argument('--progress-file', default='experimental/results/historical_progress.json')
    parser.add_argument('--log-file', default='experimental/results/rss_priority_processor.log')
    parser.add_argument('--no-vision', action='store_true', help='Skip vision analysis')
    parser.add_argument('--max-retries', type=int, default=5)
    parser.add_argument('--data-dir', type=Path, default=Path('data_hist'))
    parser.add_argument('--frames-dir', type=Path, default=Path('frames_hist'))
    parser.add_argument('--results-dir', type=Path, default=Path('experimental/results'))
    parser.add_argument('--ollama-url', default='http://localhost:11434')
    parser.add_argument('--vision-model', default='qwen3.5:9b-mlx')
    parser.add_argument('--vision-timeout', type=int, default=600)
    parser.add_argument('--fps', type=int, default=5)
    parser.add_argument('--max-frames', type=int, default=20)
    parser.add_argument('--vision-prompt', default=None)
    
    args = parser.parse_args()
    
    progress_file = Path(args.progress_file)
    log_file = Path(args.log_file)
    
    with open(progress_file) as f:
        state = json.load(f)
    
    video_id = args.video
    entry = state['videos'].get(video_id)
    if entry is None:
        print(f"Video {video_id} not found")
        sys.exit(1)
    
    from scripts.rss_priority_processor import (
        log, save_state, STATUS_PROCESSING, STATUS_COMPLETED,
        download_video, extract_frames, extract_transcript,
        analyze_frame_vision, choose_vision_model,
        _save_analysis, validate_video
    )
    from pathlib import Path as _Path
    from scripts.rss_priority_processor import VISION_PROMPT_TEMPLATE
    
    entry['status'] = STATUS_PROCESSING
    entry['retry_count'] = entry.get('retry_count', 0)
    save_state(state, progress_file, log_file)
    
    entry_artifacts = entry.get('artifacts', {})
    for key in ('video_path', 'frames_dir', 'transcript_path', 'analysis_file'):
        val = entry_artifacts.get(key)
        if isinstance(val, str):
            entry['artifacts'][key] = _Path(val)
    
    data_dir = args.data_dir / video_id
    frames_dir = args.frames_dir / video_id
    results_dir = args.results_dir / 'historical'
    
    # Paso 1: Descarga (ya completada)
    if not entry['progress'].get('download', False):
        vp = download_video(video_id, args.data_dir, args.max_retries)
        if vp is None:
            entry['last_error'] = 'no se pudo descargar el video'
            sys.exit(1)
        entry['artifacts']['video_path'] = vp
        entry['progress']['download'] = True
        save_state(state, progress_file, log_file)
    
    # Paso 2: Frames (ya completados)
    if not entry['progress'].get('frames', False):
        if not extract_frames(video_id, entry['artifacts']['video_path'],
                              frames_dir, args.max_frames, args.fps):
            entry['last_error'] = 'no se pudieron extraer frames'
            sys.exit(1)
        entry['progress']['frames'] = True
        entry['artifacts']['frames_dir'] = frames_dir
        save_state(state, progress_file, log_file)
    
    # Paso 3: Transcripción (ya completada)
    if not entry['progress'].get('transcript', False):
        tp = extract_transcript(video_id, args.data_dir)
        if tp is None:
            entry['last_error'] = 'no se pudo extraer la transcripción'
            sys.exit(1)
        entry['artifacts']['transcript_path'] = tp
        entry['progress']['transcript'] = True
        save_state(state, progress_file, log_file)
    
    # Paso 4: Visión
    if not entry['progress'].get('vision', False) and not args.no_vision:
        model = choose_vision_model(args.ollama_url, args.vision_model)
        if model is None:
            entry['last_error'] = 'modelo visual Qwen no disponible en Ollama'
            sys.exit(1)
        
        log(f"Vision model: {model}", verbose=False)
        frames = sorted(frames_dir.glob('frame_*.jpg'))
        analyzed_all = True
        
        for frame in frames:
            prompt = args.vision_prompt or VISION_PROMPT_TEMPLATE
            result = analyze_frame_vision(frame, model, prompt,
                                          args.ollama_url, args.vision_timeout)
            _save_analysis(entry['artifacts'].get('analysis_file'), video_id, 
                          {'title': video_id}, frame, result, args)
            if result.startswith('ERROR'):
                analyzed_all = False
        
        entry['progress']['vision'] = bool(frames) and analyzed_all
        save_state(state, progress_file, log_file)
    
    # Paso 5: Validación
    if not entry['progress'].get('validation', False):
        if not validate_video(state, video_id, entry['artifacts']):
            entry['last_error'] = entry.get('last_error') or 'validación fallida'
            sys.exit(1)
        entry['progress']['validation'] = True
    
    # Marcar como completado
    entry['status'] = STATUS_COMPLETED
    entry['last_error'] = None
    save_state(state, progress_file, log_file)
    
    print(f"Video {video_id} completado exitosamente")
    print(f"Status: {entry['status']}")
    print(f"Progress: {entry['progress']}")

if __name__ == '__main__':
    main()
