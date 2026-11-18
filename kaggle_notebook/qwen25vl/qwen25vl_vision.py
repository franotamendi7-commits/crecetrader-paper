"""Qwen2.5-VL — inferencia sobre frames (notebook Kaggle, AISLADO).

NO ejecutar sin autorizacion. No contiene material del proyecto.
Entrada esperada: /kaggle/input/<dataset>/frame_*.jpg
Salida: /kaggle/working/resultados.csv y resultados.json
"""
import glob
import json
import os
import time

PROMPT = """Analyze this trading chart. Answer ONLY with a JSON object with keys:
instrument, exchange, timeframe, visible_price_labels, horizontal_levels,
trendlines, market_structure, liquidity_zones, indicators,
visible_candlestick_information, unreadable_information, confidence, abstentions.
RULES: transcribe ONLY values written in the image. Do NOT invent numbers or
sequences. Max 12 price labels. If a field cannot be read, use "UNKNOWN".
Abstain when the chart is not legible."""

INPUT_DIR = os.environ.get('INPUT_DIR', '/kaggle/input')
OUT_DIR = os.environ.get('OUT_DIR', '/kaggle/working')
MODEL_ID = os.environ.get('MODEL_ID', 'Qwen/Qwen2.5-VL-3B-Instruct')
LIMIT = int(os.environ.get('LIMIT', '0'))


def main():
    import torch
    from transformers import Qwen2_5_VLForConditionalGeneration, AutoProcessor
    from qwen_vl_utils import process_vision_info

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print('device:', device, '| model:', MODEL_ID, flush=True)

    frames = sorted(glob.glob(os.path.join(INPUT_DIR, '**', 'frame_*.jpg'), recursive=True))
    if LIMIT:
        frames = frames[:LIMIT]
    print('frames:', len(frames), flush=True)

    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        MODEL_ID, torch_dtype='auto', device_map='auto')
    processor = AutoProcessor.from_pretrained(MODEL_ID)

    rows = []
    for f in frames:
        t0 = time.time()
        messages = [{'role': 'user', 'content': [
            {'type': 'image', 'image': f'file://{f}'},
            {'type': 'text', 'text': PROMPT}]}]
        text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        image_inputs, video_inputs = process_vision_info(messages)
        inputs = processor(text=[text], images=image_inputs, videos=video_inputs,
                           padding=True, return_tensors='pt').to(device)
        out = model.generate(**inputs, max_new_tokens=256)
        res = processor.batch_decode([o[len(i):] for i, o in zip(inputs.input_ids, out)],
                                     skip_special_tokens=True)[0]
        rows.append({'frame': os.path.basename(f), 'segundos': round(time.time() - t0, 1),
                     'respuesta': res})
        print(os.path.basename(f), rows[-1]['segundos'], 's', flush=True)

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, 'resultados.json'), 'w') as fh:
        json.dump(rows, fh, ensure_ascii=False, indent=2)
    try:
        import csv
        with open(os.path.join(OUT_DIR, 'resultados.csv'), 'w', newline='') as fh:
            w = csv.writer(fh)
            w.writerow(['frame', 'segundos', 'respuesta'])
            for r in rows:
                w.writerow([r['frame'], r['segundos'], r['respuesta']])
    except Exception as e:
        print('csv error:', e, flush=True)
    print('OK', len(rows), 'frames', flush=True)


if __name__ == '__main__':
    main()
