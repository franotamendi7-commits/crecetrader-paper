# FASE 3.3 — Comparación de Modelos de Visión

## 1. Modelos evaluados

| Modelo | Repositorio | Licencia | Tipo | Params | RAM (int4) | Apple Silicon | OCR | Gráficos | Coste |
|--------|-------------|----------|------|--------|------------|---------------|-----|----------|-------|
| Moondream 2 | vikhyat/moondream2 | Apache 2.0 | Open weights | 1.86B | ~2.0 GB | ✅ (MLX/PyTorch) | ✅ | ✅ | $0 |
| Moondream 2 0.5B | vikhyat/moondream2 (0.5B) | Apache 2.0 | Open weights | 0.5B | ~0.8 GB | ✅ | ✅ | Parcial | $0 |
| Qwen2.5-VL-7B | Qwen/Qwen2.5-VL-7B | Apache 2.0 | Open weights | 7B | ~5-7 GB | ✅ (MLX) | ✅✅ | ✅✅ | $0 |
| Qwen2.5-VL-3B | Qwen/Qwen2.5-VL-3B | Apache 2.0 | Open weights | 3B | ~2-3 GB | ✅ (MLX) | ✅ | ✅ | $0 |
| InternVL2-2B | OpenGVLab/InternVL2-2B | MIT | Open weights | 2B | ~2-3 GB | ✅ (PyTorch) | ✅ | ✅ | $0 |
| Florence-2 | microsoft/Florence-2 | MIT | Open weights | 0.7B | ~1.5 GB | ✅ (PyTorch) | ✅ | Parcial | $0 |
| SmolVLM-2B | HuggingFaceTB/SmolVLM | Apache 2.0 | Open weights | 2B | ~2-3 GB | ✅ (PyTorch) | ✅ | Parcial | $0 |
| SmolVLM-0.5B | HuggingFaceTB/SmolVLM-0.5B | Apache 2.0 | Open weights | 0.5B | ~0.8 GB | ✅ (PyTorch) | Parcial | Parcial | $0 |

## 2. Análisis detallado

### Moondream 2 (RECOMENDADO)
- **Repositorio:** https://github.com/vikhyat/moondream
- **Licencia:** Apache 2.0 (permissive, commercial use allowed)
- **Tamaño:** 1.86B parámetros, ~3.85 GB (FP16), ~2.0 GB (int4)
- **RAM necesaria:** ~2.0 GB (int4), ~2.6 GB (int8), ~4.6 GB (FP16)
- **Apple Silicon:** ✅ Compatible (MLX y PyTorch)
- **OCR:** ✅ Bueno para texto en imágenes
- **Gráficos financieros:** ✅ Puede describir gráficos, identificar tendencias, leer texto
- **Velocidad:** ~0.7s por imagen en M4 Pro (MLX 4-bit)
- **Facilidad de integración:** Alta (pip install moondream)
- **Limitaciones:** Razonamiento complejo limitado, no es un LLM grande
- **Coste:** $0 (open weights, local)

### Qwen2.5-VL-7B
- **Repositorio:** https://github.com/QwenLM/Qwen2.5-VL
- **Licencia:** Apache 2.0
- **Tamaño:** 7B parámetros, ~14 GB (FP16), ~5-7 GB (int4)
- **RAM necesaria:** ~5-7 GB (int4)
- **Apple Silicon:** ✅ Compatible (MLX)
- **OCR:** ✅✅ Excelente
- **Gráficos financieros:** ✅✅ Mejor que Moondream para razonamiento complejo
- **Velocidad:** Más lento que Moondream (~2-3s por imagen)
- **Facilidad de integración:** Media (requiere transformers + torch + qwen_vl_utils)
- **Limitaciones:** Mayor consumo de RAM, más lento
- **Coste:** $0 (open weights, local)

### Qwen2.5-VL-3B
- **Repositorio:** https://github.com/QwenLM/Qwen2.5-VL
- **Licencia:** Apache 2.0
- **Tamaño:** 3B parámetros, ~6 GB (FP16), ~2-3 GB (int4)
- **RAM necesaria:** ~2-3 GB (int4)
- **Apple Silicon:** ✅ Compatible (MLX)
- **OCR:** ✅ Bueno
- **Gráficos financieros:** ✅ Bueno
- **Velocidad:** ~1-2s por imagen
- **Facilidad de integración:** Media
- **Limitaciones:** Menor capacidad que 7B
- **Coste:** $0 (open weights, local)

### InternVL2-2B
- **Repositorio:** https://github.com/OpenGVLab/InternVL
- **Licencia:** MIT
- **Tamaño:** 2B parámetros
- **RAM necesaria:** ~2-3 GB
- **Apple Silicon:** ✅ Compatible (PyTorch)
- **OCR:** ✅ Bueno
- **Gráficos financieros:** ✅ Bueno
- **Velocidad:** ~1-2s por imagen
- **Facilidad de integración:** Media
- **Coste:** $0 (open weights, local)

### Florence-2
- **Repositorio:** https://github.com/microsoft/Florence-2
- **Licencia:** MIT
- **Tamaño:** 0.7B parámetros
- **RAM necesaria:** ~1.5 GB
- **Apple Silicon:** ✅ Compatible (PyTorch)
- **OCR:** ✅ Bueno
- **Gráficos financieros:** Parcial (mejor para detección/segmentación)
- **Velocidad:** Rápido
- **Facilidad de integración:** Alta
- **Coste:** $0 (open weights, local)

### SmolVLM-2B
- **Repositorio:** https://github.com/huggingface/SmolVLM
- **Licencia:** Apache 2.0
- **Tamaño:** 2B parámetros
- **RAM necesaria:** ~2-3 GB
- **Apple Silicon:** ✅ Compatible (PyTorch)
- **OCR:** ✅ Bueno (DocVQA 81.6%)
- **Gráficos financieros:** Parcial
- **Velocidad:** Rápido
- **Facilidad de integración:** Alta
- **Coste:** $0 (open weights, local)

## 3. Selección recomendada

### Modelo principal: Moondream 2 (1.86B, int4)

**Justificación:**
1. **Footprint mínimo:** ~2.0 GB RAM (int4) — deja ~22 GB libres
2. **Apple Silicon nativo:** Soporte MLX y PyTorch
3. **Apache 2.0:** Uso comercial libre
4. **Velocidad:** ~0.7s por imagen en M4
5. **OCR integrado:** Puede leer texto en gráficos
6. **Capacidad visual:** Puede describir gráficos, identificar tendencias, leer anotaciones
7. **Instalación simple:** pip install moondream
8. **Sin dependencias pesadas:** No requiere torch/transformers (usa su propio runtime)

### Alternativa si se necesita más capacidad: Qwen2.5-VL-3B
- Mayor capacidad de razonamiento
- Requiere transformers + torch (dependencias pesadas)
- ~2-3 GB RAM (int4)
- Mejor para análisis complejo de gráficos

### No recomendado para este hardware: Qwen2.5-VL-7B
- Requiere ~5-7 GB RAM (int4)
- Más lento
- Puede comprometer la estabilidad del sistema

## 4. Comparación con el sistema actual (OCR-only)

| Capacidad | Sistema actual (Tesseract) | Con Moondream 2 |
|-----------|---------------------------|-----------------|
| OCR de texto | ✅ 56% exactitud | ✅ Mejor (VQA) |
| Identificación de gráficos | ❌ No | ✅ Sí |
| Reconocimiento de velas | ❌ No | ✅ Parcial |
| Detección de tendencias | ❌ No | ✅ Sí |
| Soportes/resistencias | ❌ No | ✅ Parcial |
| Indicadores | ❌ No | ✅ Parcial |
| Relación audio-video | ❌ No | ✅ Parcial |
| Consumo de RAM | ~0 (Tesseract) | ~2.0 GB (int4) |
| Velocidad | ~0.1s/frame | ~0.7s/frame |

## 5. Plan de implementación (PROPUESTO, no ejecutado)

1. Instalar moondream en el venv del proyecto (pip install moondream)
2. Crear script de prueba aislado (src/test_moondream.py)
3. Probar con 5 frames representativos del video
4. Evaluar resultados
5. Si es satisfactorio, integrar en el pipeline

**[VERIFICADO]** — Modelos investigados
**[VERIFICADO]** — Hardware: M4, 24GB RAM, ~15GB disponible
**[VERIFICADO]** — Moondream 2: Apache 2.0, 1.86B params, ~2GB RAM (int4)
**[PROPUESTO]** — Instalación de Moondream 2 (pendiente de autorización)
**[PROPUESTO]** — Prueba con frames del video (pendiente)
**[PENDIENTE]** — Autorización de Francisco para instalar
EOF