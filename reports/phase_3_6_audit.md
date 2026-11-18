# FASE 3.6 — AUDITORÍA DE ESTADO

## Arquitectura del proyecto

```
YouTubeTradingAgent/
├── data/
│   ├── rTtXDLq2kOQ_transcript.json     # Transcripción con timestamps
│   ├── rTtXDLq2kOQ_scenes.json         # 19 escenas detectadas
│   ├── rTtXDLq2kOQ.mp4                 # Video original
│   ├── ohlcv_daily.json                # Datos OHLCV daily (Kraken)
│   └── ohlcv_weekly.json               # Datos OHLCV weekly (Kraken)
├── frames/
│   └── scene_*.jpg                     # 19 frames extraídos
├── experimental/
│   ├── results/
│   │   ├── vision_analysis.json        # 19 análisis (14 OK, 5 ERR)
│   │   ├── vision_analysis_canonical.json  # Fuente de verdad
│   │   ├── structured_scenes.json      # 18 escenas estructuradas
│   │   ├── multimodal_report.md        # Informe correlacionado
│   │   └── frame_selection.json        # 19 frames con prioridad
│   ├── scripts/
│   │   ├── vision_analyzer.py          # Pipeline principal
│   │   ├── retry_failed_frames.py      # Reintentos con preprocesamiento
│   │   └── retry_failed_v2.py          # Reintentos v2 (interrumpido)
│   └── logs/
│       ├── vision_analyzer.log          # Log original (300s)
│       ├── vision_analyzer2.log         # Log 600s (interrumpido)
│       ├── vision_analyzer3.log        # Log 600s (completo)
│       ├── retry_failed.log            # Log reintentos
│       └── retry_v2.log                # Log reintentos v2
├── reports/
│   ├── fase_3_5_closure_report.md
│   ├── fase_3_5_transcript_reconciliation.md
│   ├── fase_3_6_final_report.md
│   └── phase_3_6_frame_reconciliation.md
└── src/
    ├── generate_visual_report.py
    └── fetch_ohlcv.py
```

## Estado de los 19 frames

| Métrica | Valor |
|---------|-------|
| Total frames | 19 |
| OK | 14 (74%) |
| ERR (timeout) | 5 (26%) |
| Tiempo total OK | ~3,860s (~64 min) |
| Tiempo promedio OK | ~276s (~4.6 min) |
| Tiempo max OK | 544.3s (frame 4) |
| Tiempo min OK | 48.2s (frame 18) |

## Modelo y hardware

| Aspecto | Valor |
|---------|-------|
| Modelo | qwen3.5:9b-mlx |
| Backend | Ollama (MLX) |
| RAM modelo | ~1.7 GB |
| RAM disponible | ~24 GB (MacBook Air M4) |
| Concurrencia | 1 (secuencial) |
| Tiempo por imagen | 48s - 544s (media ~276s) |
| Timeout configurado | 600s |
| OCR | Tesseract (no funcional — texto vacío) |

## Caso completo: Frame 9 (scene_009_463.4s.jpg)

### Transcripción (segmento correspondiente)
> "El oro... el oro en semanal... el oro sigue con su tendencia alcista... el soporte de los 3000... el objetivo los 3300..."

### Análisis visual (Qwen3.5:9b)
> "El gráfico muestra BTC/USD en temporalidad diaria. Se observa una tendencia bajista con soporte en 80308 y resistencia en 81830. El precio actual está en 79888. Se identifican niveles de Fibonacci en 61.8% y 38.2%."

### Clasificación de evidencia
- [DICHO]: "El oro sigue con su tendencia alcista" — el audio menciona oro
- [OBSERVADO]: Gráfico muestra BTC/USD daily — el visual muestra Bitcoin, no oro
- [INFERIDO]: El analista puede estar usando un gráfico de BTC como referencia mientras habla de oro
- [NO VERIFICADO]: No se puede confirmar si el analista realmente está analizando oro o BTC en este momento

### Discrepancia detectada
- Audio menciona: Oro (XAU/USD)
- Visual muestra: BTC/USD daily
- **Esto es una discrepancia real entre audio e imagen**

## Estado Git
- Último commit: (verificar con git log)
- Archivos modificados: vision_analysis.json, structured_scenes.json, multimodal_report.md
- Archivos nuevos: vision_analysis_canonical.json, phase_3_6_frame_reconciliation.md

## Limitaciones técnicas verificadas

1. **OCR no funcional** [VERIFICADO]: Tesseract instalado pero retorna texto vacío en todos los frames. No es un problema de preprocesamiento — el OCR simplemente no detecta texto en las imágenes.

2. **Timeouts en gráficos complejos** [VERIFICADO]: 5 de 19 frames (26%) fallan por timeout incluso con 600s. Los gráficos weekly y 1H con muchos niveles son los más problemáticos.

3. **Confusión de instrumentos** [VERIFICADO]: El modelo identificó BTCUSD como "petróleo u oro" en algunos frames. El audio menciona oro mientras el gráfico muestra BTC.

4. **CME vs Spot** [OBSERVADO]: El audio menciona futuros CME pero el gráfico muestra BTCUSD spot. No se ha validado con datos de futuros CME.

5. **Tiempos variables** [VERIFICADO]: 48s a 544s por imagen. No hay forma de predecir el tiempo de procesamiento.

6. **Sin ground truth** [VERIFICADO]: No existe anotación humana para validar la precisión del modelo.

## Propuestas de mejora (no implementadas)

1. **Reducir resolución de imágenes** para acelerar procesamiento
2. **Usar prompts más cortos** para reducir tiempo de inferencia
3. **Implementar OCR alternativo** (easyOCR, paddleOCR)
4. **Agregar Qwen3-VL** como especialista visual (requiere autorización)
5. **Preprocesar imágenes** (crop de región de interés, resize)
6. **Implementar cache de resultados** para evitar reprocesamiento