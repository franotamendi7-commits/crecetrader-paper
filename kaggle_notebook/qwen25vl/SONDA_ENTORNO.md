# Sonda de entorno Kaggle — resultado real

Ejecutada: 2026-11-16 (kernel privado `franciscootamendi/yt-analyst-env-probe-no-project-data`).
Sin material del proyecto (solo impresión de entorno).

| Recurso | Valor |
|---|---|
| Python | 3.13.18 |
| SO | Linux x86_64 |
| PyTorch | **2.11.0+cpu** |
| CUDA disponible | **False → NO hay GPU** |
| CPU | 4 núcleos |
| RAM | 32,87 GB |
| Disco /kaggle | 8.157 GB total · 7.190 usados · **967 GB libres** |
| transformers | 5.20.2 (soporte Qwen2.5-VL) |
| accelerate | 1.15.0 |
| qwen_vl_utils | **NO instalado** (requiere `pip install qwen-vl-utils`) |
| PIL | 13.0.0 |

## Consecuencias

1. **Sin GPU**: la inferencia del modelo 3B en CPU es muy lenta. Estimación (no medida): **60-180 s/frame** → 157 frames ≈ **2,6-7,8 h**. Inviable en una sesión.
2. `qwen_vl_utils` falta: debe añadirse al notebook.
3. Un intento anterior (13-15/11) con Qwen3-VL falló por errores de red (`Temporary failure in name resolution`) y 401/403/404. No se reutilizó.
4. Coincide con la nota del skill: el sandbox gratuito de Kaggle no asigna GPU.

## Procedimiento propuesto (requiere autorización)

1. Crear dataset **privado** con los frames (autorización expresa para transferir material).
2. Notebook `qwen25vl_vision.py` con `pip install qwen-vl-utils`, `LIMIT` para lotes y salida a `/kaggle/working`.
3. Si Kaggle no asigna GPU: limitar a lotes pequeños (5-10 frames) o evaluar Colab.
4. Coste: 0 USD; cuota 30 h/semana de GPU (no asignada en la práctica).
5. Privacidad: dataset privado, borrar después, no publicar.

## Estado

- Notebook preparado: `qwen25vl/qwen25vl_vision.py`.
- Imagen de prueba sintética (no pertenece a los vídeos): `test_image_sintetica.png` — **no usada**.
- **No se ejecutó inferencia ni se transfirió material del proyecto.**
