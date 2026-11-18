# FASE 3.7 — COMPARACIÓN DE PIPELINE

## 1. Pipeline actual (vision_analyzer.py)

### Características
- Prompt: "Describe this trading chart: instrument, timeframe, indicators, price levels, and market bias. Be concise."
- Sin OCR
- Sin preprocesamiento de imágenes
- Sin separación audio/imagen
- Sin campos de distinción CME/Spot
- Timeout: 600s
- Resultado: 14/19 OK (74%), 5 timeout

### Problemas identificados
1. Prompt genérico no separa evidencia visual de audio
2. Modelo fusiona audio e imagen → confusión de instrumentos
3. Sin instrucción de null para valores no legibles → inventa fechas
4. Sin OCR → no se extrae texto de la imagen
5. Sin campos de distinción CME/Spot

## 2. Pipeline optimizado (propuesto)

### Prompt estructurado
```
You are analyzing a trading chart image. Follow these rules strictly:

1. ONLY describe what you ACTUALLY SEE in the image. Do NOT infer from audio.
2. Identify the instrument visible in the chart (e.g., BTCUSD, XAUUSD). If you cannot identify it, respond "UNKNOWN".
3. Identify the timeframe ONLY if visible (e.g., Weekly, Daily, 4H, 1H). If not visible, respond "UNKNOWN".
4. List ONLY price levels that are CLEARLY VISIBLE in the chart. If you cannot read a price, respond "null".
5. Do NOT invent dates, events, or indicator values.
6. Distinguish between: (a) what the chart shows, (b) what a speaker might say about it.
7. If the image is NOT a trading chart (e.g., desktop, webpage, person), respond "NOT_A_CHART".

Respond in this exact format:
A. VISUAL_EVIDENCE: [instrument, timeframe, visible prices, indicators]
B. AUDIO_CONTEXT: [what the transcription says about this moment]
C. INTERPRETATION: [your analysis based ONLY on visual evidence]
D. UNCERTAIN: [what you cannot determine from the image]
```

### Mejoras propuestas
1. Prompt estructurado con separación de fuentes
2. OCR integrado (Tesseract spa+eng, PSM 6)
3. Campos de distinción CME/Spot en el schema
4. Instrucción de null para valores no legibles
5. Instrucción de UNKNOWN para instrumentos no identificables
6. Instrucción de NOT_A_CHART para no-gráficos

### Schema mejorado
```json
{
    "scene_idx": 0,
    "start": 0.0,
    "end": 8.3,
    "frame": "scene_000_0.0s.jpg",
    "transcript": "...",
    "ocr_text": "texto extraído por Tesseract",
    "ocr_time_seconds": 1.2,
    "vision_analysis": {
        "asset_visual": "BTCUSD",
        "asset_audio": "BTC",
        "timeframe_visual": "Weekly",
        "market_reference": "spot",
        "visible_price_levels": [87826, 81830],
        "market_structure": "bearish correction",
        "directional_bias": "bearish",
        "audio_visual_consistency": "consistent",
        "uncertainties": ["OCR quality moderate"],
        "evidence_classification": {
            "visual": ["BTCUSD chart", "Weekly timeframe", "Price 87826"],
            "audio": ["Analyst mentions BTC weekly"],
            "inferred": ["Bearish bias based on structure"],
            "not_verified": ["Exact Fibonacci levels"]
        }
    },
    "time_seconds": 276.0,
    "preprocessed": false
}
```

## 3. Comparación esperada

| Métrica | Pipeline actual | Pipeline optimizado (esperado) |
|---------|----------------|-------------------------------|
| Frames procesados | 14/19 (74%) | 14-19/19 |
| Confusión de instrumentos | Sí (BTC→oro) | No (prompt estructurado) |
| OCR | No se ejecuta | Integrado |
| Fechas inventadas | Sí | No (instrucción null) |
| CME/Spot distinción | No | Sí (campos en schema) |
| Tiempo promedio | ~276s | ~180-276s (prompt más corto) |
| Expresión de incertidumbre | Parcial | Sistemática |

## 4. Prueba comparativa

### Frames seleccionados
| Frame | Tipo | Motivo de selección |
|-------|------|---------------------|
| 4 | Gráfico daily BTC | Confusión de instrumento (recuperado con 2x) |
| 10 | Gráfico 4H BTC | Confusión de instrumento (recuperado con 2x) |
| 1 | Gráfico weekly BTC | Timeout persistente |
| 2 | Gráfico 1H BTC | Timeout persistente |
| 6 | Gráfico daily BTC | Timeout persistente |
| 12 | Gráfico daily BTC | Timeout persistente |
| 16 | Gráfico daily BTC | Timeout persistente |
| 13 | Gráfico daily BTC | Indicadores de sentimiento |
| 15 | Gráfico 4H BTC | Fechas y calendario |
| 17 | Gráfico daily BTC | Fechas y calendario |

### Evaluación
1. Detección de gráficos (sí/no)
2. Identificación de instrumentos (correcto/incorrecto/UNKNOWN)
3. Temporalidades (correcta/incorrecta/UNKNOWN)
4. Lectura de precios (cantidad correcta vs null)
5. OCR (texto extraído vs vacío)
6. Coherencia audio-imagen (consistente/inconsistente)
7. Contradicciones (detectadas/no detectadas)
8. Alucinaciones (cantidad)
9. Tiempo de procesamiento (segundos)
10. Incertidumbre correctamente expresada (sí/no)

## 5. Restricciones
- No instalar Qwen3-VL
- No descargar modelos nuevos
- Conservar resultados originales
- Generar resultados experimentales separados
- No declarar mejora sin evidencia comparable

## 6. Estado
**PENDIENTE DE IMPLEMENTACIÓN.** El pipeline optimizado ha sido diseñado pero no implementado. Se requiere delegación a OpenCode para la implementación y ejecución de pruebas.