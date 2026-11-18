# FASE 3.8 — INFORME FINAL: ARQUITECTURA OLLAMA DOS MODELOS

## Resumen ejecutivo

Se implementó y probó la arquitectura de dos modelos independientes en Ollama:

1. **YouTube Analyst**: qwen2.5vl:3b (vision) — 18/18 frames OK, 0 errores, 17.5s/frame
2. **Memory Manager**: qwen3.5:9b-mlx (text) — disponible, no probado para memoria

**Estado: IMPLEMENTACIÓN FUNCIONAL — PENDIENTE DE VALIDACIÓN COMPLETA.**

## Comparación de modelos de visión probados

| Modelo | Tamaño | Velocidad | Calidad | Disponibilidad |
|--------|--------|-----------|---------|----------------|
| Qwen3.5:9b-mlx | 8.9 GB | 276s/frame (MUY LENTO) | Buena | Ya instalado |
| Moondream | 1.7 GB | 18.5s/frame | Pobre (texto repetitivo) | Descargado |
| Qwen2.5VL:3b | 3.2 GB | 17.5s/frame | Buena (identifica instrumentos, precios) | Descargado |
| Gemini 2.5 Flash | Cloud | 7.8s/frame | Excelente | API key (cuota 20/día) |

## Resultados de qwen2.5vl:3b en video subONxt5iag (18 frames, 1/60s)

- **18/18 frames procesados** (100%)
- **0 errores**
- **315.7s total** (~5.3 min)
- **17.5s promedio por frame**
- Identificó correctamente: BTC, ETH, ES, NASDAQ, AMD
- Extrajo precios: ETH (2100-2300), ES (7.4-7.8), NASDAQ (27,950-28,026), AMD (658.5)
- Detectó temporalidades: Weekly, Daily, 4H, 5m
- Algunos frames UNKNOWN (transiciones, no-gráficos)

### Comparación con Gemini 2.5 Flash

| Métrica | Gemini 2.5 Flash | Qwen2.5VL:3b (Ollama) |
|---------|-----------------|----------------------|
| Velocidad | 7.8s/frame | 17.5s/frame |
| Precisión instrumentos | Excelente | Buena |
| CME vs Spot | Distingue | No probado |
| NOT_A_CHART | Correcto | Parcial (algunos UNKNOWN) |
| Costo | Gratis (20/día) | Gratis (ilimitado) |
| Dependencia externa | Sí (Google) | No (local) |
| Cuota diaria | 20 req/día | Sin límite |

## Arquitectura propuesta

### Modelo A: Memory Manager
- **Modelo**: qwen3.5:9b-mlx (ya instalado, 8.9 GB)
- **Función**: Razonamiento textual, consolidación de memoria, organización de conocimiento
- **No analiza imágenes ni videos**
- **RAM**: ~8.9 GB cuando cargado

### Modelo B: YouTube Analyst
- **Modelo**: qwen2.5vl:3b (3.2 GB)
- **Función**: Análisis audiovisual, interpretación de gráficos
- **No gestiona memoria**
- **RAM**: ~3.2 GB cuando cargado

### Administrador de modelos
- Carga uno a la vez (nunca simultáneos)
- YouTube Analyst: carga → procesa video → guarda → descarga
- Memory Manager: carga → consolida → guarda → descarga
- Verificación de liberación de RAM

## Limitaciones conocidas de qwen2.5vl:3b
1. Algunos frames retornan UNKNOWN (transiciones, no-gráficos)
2. Precisión de precios inferior a Gemini
3. No distingue CME vs Spot (no probado)
4. Velocidad: 17.5s/frame (vs 7.8s Gemini)

## Próximos pasos
1. Implementar administrador de modelos (carga/descarga secuencial)
2. Procesar video completo con qwen2.5vl:3b
3. Validar resultados contra transcripción
4. Implementar Memory Manager con qwen3.5:9b-mlx
5. Preparar integración con Risk Manager

## Costo real de operación
- **USD 0** — Modelos locales, sin API, sin cuotas
- **RAM**: Máximo 8.9 GB (uno a la vez)
- **Tiempo**: ~5.3 min para 18 frames (video completo: ~20 min para 69 frames)

## Archivos generados
- `experimental/scripts/vision_analyzer_qwen25vl.py` — Pipeline qwen2.5vl
- `experimental/results/vision_analysis_qwen25vl.json` — Resultados (18 frames, 0 errores)
- `reports/phase_3_8_ollama_architecture.md` — Este informe