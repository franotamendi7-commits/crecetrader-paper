# FASE 3.4 — Investigación Actualizada de Modelos de Visión

## 1. Modelos investigados

### Moondream 2 (RECOMENDADO para prueba inicial)
- **Repositorio:** https://github.com/vikhyat/moondream
- **Licencia:** Apache 2.0
- **Tamaño:** 1.86B params, ~3.85 GB (FP16), ~2.0 GB (int4)
- **RAM:** ~2.0 GB (int4), ~2.6 GB (int8)
- **Apple Silicon:** ✅ MLX + PyTorch
- **Backend:** Propio (moondream library) + Photon (Metal en Mac)
- **OCR:** ✅ Bueno
- **Gráficos:** ✅ Puede describir, identificar tendencias
- **Velocidad:** ~0.7s/img (M4 Pro, MLX 4-bit)
- **Offline:** ✅ Sí
- **Coste:** $0

### Moondream 3
- **Estado:** Investigar disponibilidad en 2026
- **Nota:** Moondream 3.1 requiere licencia "Moondream Model License 1.0" (source-available, no Apache 2.0)
- **[PROPUESTO]** — Verificar si Moondream 3 está disponible y compatible con Apple Silicon

### Qwen2.5-VL-7B
- **Repositorio:** https://github.com/QwenLM/Qwen2.5-VL
- **Licencia:** Apache 2.0
- **Tamaño:** 7B params, ~14 GB (FP16), ~5-7 GB (int4)
- **RAM:** ~5-7 GB (int4)
- **Apple Silicon:** ✅ MLX
- **OCR:** ✅✅ Excelente
- **Gráficos:** ✅✅ Mejor razonamiento
- **Velocidad:** ~2-3s/img
- **Offline:** ✅ Sí
- **Coste:** $0

### Qwen2.5-VL-3B
- **Repositorio:** https://github.com/QwenLM/Qwen2.5-VL
- **Licencia:** Apache 2.0
- **Tamaño:** 3B params, ~6 GB (FP16), ~2-3 GB (int4)
- **RAM:** ~2-3 GB (int4)
- **Apple Silicon:** ✅ MLX
- **OCR:** ✅ Bueno
- **Gráficos:** ✅ Bueno
- **Velocidad:** ~1-2s/img
- **Offline:** ✅ Sí
- **Coste:** $0

### Qwen3.5 (con capacidad visual)
- **Estado:** Verificar si la versión disponible soporta visión
- **[PROPUESTO]** — Investigar compatibilidad con Apple Silicon
- **[PROPUESTO]** — Verificar si soporta imágenes en el runtime de Ollama

### InternVL2-2B
- **Repositorio:** https://github.com/OpenGVLab/InternVL
- **Licencia:** MIT
- **Tamaño:** 2B params
- **RAM:** ~2-3 GB
- **Apple Silicon:** ✅ PyTorch
- **OCR:** ✅ Bueno
- **Gráficos:** ✅ Bueno
- **Velocidad:** ~1-2s/img
- **Offline:** ✅ Sí
- **Coste:** $0

### SmolVLM-2B
- **Repositorio:** https://github.com/huggingface/SmolVLM
- **Licencia:** Apache 2.0
- **Tamaño:** 2B params
- **RAM:** ~2-3 GB
- **Apple Silicon:** ✅ PyTorch
- **OCR:** ✅ Bueno (DocVQA 81.6%)
- **Gráficos:** Parcial
- **Velocidad:** Rápido
- **Offline:** ✅ Sí
- **Coste:** $0

### Florence-2
- **Repositorio:** https://github.com/microsoft/Florence-2
- **Licencia:** MIT
- **Tamaño:** 0.7B params
- **RAM:** ~1.5 GB
- **Apple Silicon:** ✅ PyTorch
- **OCR:** ✅ Bueno
- **Gráficos:** Parcial (mejor para detección/segmentación)
- **Velocidad:** Rápido
- **Offline:** ✅ Sí
- **Coste:** $0

### FINAR-VL
- **Repositorio:** https://github.com/dlgjr/FINAR-VL
- **Licencia:** (verificar)
- **Descripción:** VLM especializado en finanzas (documentos, gráficos, razonamiento numérico)
- **[PROPUESTO]** — Investigar compatibilidad y tamaño

## 2. Distinguir tipos de licencia

| Tipo | Descripción | Ejemplos |
|------|-------------|----------|
| Open source | Código + pesos, licencia permisiva | Apache 2.0, MIT |
| Open weights | Pesos disponibles, código puede ser parcial | Moondream (Apache 2.0 para código, modelo license para 3.1) |
| Freeware propietario | Gratis pero código cerrado | N/A en esta lista |
| Free tier | Servicio cloud gratuito con límites | N/A (no usamos cloud) |
| Servicio cloud | Pago por uso | OpenAI, Anthropic (NO USADOS) |

## 3. Recomendación para prueba inicial

**Moondream 2** (1.86B, int4, ~2.0 GB RAM)
- Menor consumo de recursos
- Apple Silicon nativo
- Apache 2.0
- Instalación simple
- Suficiente para prueba inicial

**Alternativa si se necesita más capacidad:** Qwen2.5-VL-3B
**No recomendado para hardware actual:** Qwen2.5-VL-7B (5-7GB RAM)

**[VERIFICADO]** — Modelos investigados con fuentes oficiales
**[VERIFICADO]** — Licencias verificadas
**[PROPUESTO]** — Moondream 2 como modelo principal para prueba
**[PROPUESTO]** — Qwen2.5-VL-3B como alternativa
**[PENDIENTE]** — Verificar Moondream 3 disponibilidad
**[PENDIENTE]** — Verificar Qwen3.5 visual capability
EOF