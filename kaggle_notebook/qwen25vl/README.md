# Qwen2.5-VL — análisis de frames (notebook Kaggle, AISLADO)

**Estado:** preparado, **NO ejecutado**. Sin material real cargado.
**Restricción vigente:** no transferir frames ni transcripciones del proyecto sin autorización expresa.

## Propósito

Analizar frames de gráficos de TradingView con `Qwen/Qwen2.5-VL-3B-Instruct` (el modelo más pequeño disponible de la familia; el 2B-Instruct no existe).

## Recursos necesarios (verificados)

| Requisito | Valor |
|---|---|
| Modelo | `Qwen/Qwen2.5-VL-3B-Instruct` (image-text-to-text, 2 shards safetensors) |
| Licencia | familia Qwen (7B: apache-2.0); 3B sin licencia declarada en cardData → **verificar antes de uso** |
| transformers | versión reciente con soporte `Qwen2_5_VLForConditionalGeneration` |
| RAM | ≥ 16 GB recomendado |
| GPU | recomendado (CPU muy lento) |

## Procedimiento (cuando se autorice)

1. Crear un **dataset privado** en Kaggle con los frames (requiere autorización).
2. Ejecutar este notebook con `enable_gpu: true` y el dataset adjunto.
3. El notebook recorre los frames, aplica el prompt estructurado y guarda `resultados.csv` / `.json`.
4. Descargar los resultados; no dejar el dataset con material privado publicado.

## Uso del modelo

```python
from transformers import Qwen2_5_VLForConditionalGeneration, AutoProcessor
from qwen_vl_utils import process_vision_info

model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
    "Qwen/Qwen2.5-VL-3B-Instruct", torch_dtype="auto", device_map="auto")
processor = AutoProcessor.from_pretrained("Qwen/Qwen2.5-VL-3B-Instruct")

messages = [{"role": "user", "content": [
    {"type": "image", "image": "file:///kaggle/input/<dataset>/frame_0001.jpg"},
    {"type": "text", "text": PROMPT}]}]
text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
image_inputs, video_inputs = process_vision_info(messages)
inputs = processor(text=[text], images=image_inputs, videos=video_inputs,
                   padding=True, return_tensors="pt").to("cuda")
out = model.generate(**inputs, max_new_tokens=256)
res = processor.batch_decode([o[len(i):] for i, o in zip(inputs.input_ids, out)],
                             skip_special_tokens=True)[0]
```

## Prompt (propuesto, experimental)

El de `benchmark_vision_b1/B4_PROTOCOLO_EVALUACION.md` (JSON de 13 campos con abstención).

## Límites y privacidad

- **Transferencia:** los frames son contenido del canal; enviarlos a Kaggle (servicio externo) **requiere autorización expresa**. No se ha hecho.
- **Persistencia:** usar siempre datasets **privados**; borrar después.
- **Coste:** 0 USD en el tier gratuito; cuota de 30 h/semana de GPU; el sandbox puede no asignar GPU.
- **Rendimiento estimado (no medido):** 3B en GPU ≈ 5-15 s/frame; en CPU ≈ 60-180 s/frame.
- **Fallos previos documentados:** un intento anterior con Qwen3-VL falló por errores de red (`Temporary failure in name resolution`) y 401/403/404. No se reutiliza ese notebook.

## Archivos

- `qwen25vl_vision.py` — notebook de inferencia.
- `probe_env.py` — sonda de entorno (sin material real).
- `kernel-metadata.json` — metadatos del kernel (privado, GPU, internet).
