# B4 — Protocolo de evaluación de comprensión visual (TradingView)

Estado: **PREPARADO — NO EJECUTADO**. Falta la referencia humana independiente (2 anotadores).
Video: `LFHkc5dUoLw` · 20 frames consecutivos `frame_3994`–`frame_4013` · últimos **3,80 s** del vídeo (798,60–802,40 s).
Alcance: mide comprensión de **una escena concreta**, no del vídeo completo ni del agente en general.

## 1. Modelo y configuración (a registrar en cada ejecución)

| Ítem | Valor |
|---|---|
| Modelo | `qwen2.5vl:3b` (Ollama local `localhost:11434`) |
| Arquitectura / parámetros | qwen25vl, 3,8B |
| Cuantización | Q4_K_M |
| Contexto | 128000 |
| Temperatura | 0,1 (idéntica a producción, para comparabilidad) |
| `top_p` / `num_predict` / `repeat_penalty` | **no configurados** (defaults del servidor; **NO VERIFICADOS**) |
| Formato | texto (el prompt pide JSON; no se usa `format: json` de la API) |
| Imagen | frame individual original, 640×352, base64 sin preprocesar |
| Prompt | el de la sección 2 (idéntico en los 20 frames) |
| Entrada extra | **ninguna**: sin anotaciones, sin niveles esperados, sin respuestas previas |

## 2. Prompt experimental (NO es el prompt de producción)

```
You are analyzing ONE screenshot of a TradingView chart. Answer ONLY with a single JSON object with exactly these keys:

{
  "instrument": "BTCUSD, ETHUSD, ES, NQ, XAUUSD, AMD, MDT, SPX, or UNKNOWN",
  "exchange": "exchange or source if visible, otherwise UNKNOWN",
  "timeframe": "Weekly, Daily, 4H, 1H, 15m, 5m, or UNKNOWN",
  "visible_price_labels": [
    {"value": "number as written", "location": "approximate position in image",
     "legibility": "clear|partial|illegible", "confidence": 1-5,
     "justification": "what in the image shows this value"}
  ],
  "horizontal_levels": [{"level": "...", "role": "support|resistance|UNKNOWN", "label_visible": true|false}],
  "trendlines": [{"direction": "ascending|descending|horizontal|UNKNOWN", "description": "..."}],
  "market_structure": "trend|range|support|resistance|UNKNOWN",
  "liquidity_zones": [{"zone": "...", "evidence": "..."}],
  "indicators": ["MA", "Fibonacci", "Volume"],
  "visible_candlestick_information": "legible OHLC/body/wick detail, or UNKNOWN",
  "unreadable_information": ["list of elements you could not read"],
  "confidence": 1-5,
  "abstentions": ["fields you could not determine"]
}

RULES (mandatory):
- Transcribe ONLY values that are actually written in the image.
- Do NOT invent, complete, or deduce numbers. If a digit is uncertain, mark it illegible.
- Do NOT produce enumerations, sequences, or lists of numbers that are not printed on the chart.
- Maximum 12 price labels.
- If a field cannot be read, use "UNKNOWN" (or empty list where applicable).
- Do NOT guess the function of a line if it could have several interpretations; describe it.
- If the chart is not legible enough, abstain.
```

## 3. Ejecución (solo cuando exista referencia humana validada)

```
# NO EJECUTAR AUN
.venv/bin/python3 benchmark_vision_b1/scripts/b4_ejecutar_evaluacion.py \
    --frames entregas_a74/LFHkc5dUoLw \
    --out benchmark_vision_b1/resultados/B4_resultados_modelo.json
```
- Cada frame se envía **por separado**. Nunca contact sheets.
- Se registran: modelo, prompt, dimensiones, parámetros, fecha, duración, respuesta cruda.

## 4. Referencia humana

- Fichas: `B4_fichas_anotacion/ficha_frame_*.md` (una por frame).
- Esquema de campos: `B4_ESQUEMA_ANOTACION.md` (asignación no ambigua).
- Volcado normalizado: `B4_referencia_humana_template_v2.csv` (plantilla vigente; la v1 queda como respaldo).
- Dos anotadores independientes + adjudicación de desacuerdos.
- Escala por campo: `1 claro · 2 parcial · 3 no legible · 4 no presente`.

**Criterio de duda (coherente en guía, esquema y prompt):** si existe texto pero el valor exacto no es determinable con seguridad → `NO LEGIBLE`. No se anota el valor "más probable". La confianza no habilita a completar información.

## 5. Métricas (Etapa C) — por separado, sin promediar en una sola nota

| # | Métrica | Detalle |
|---|---|---|
| 1 | Instrumento | accuracy + confusión |
| 2 | Temporalidad | accuracy |
| 3 | Lectura de precios | precisión y exhaustividad por nivel; solo contra etiquetas humanas |
| 4 | Niveles horizontales | precisión de niveles y su rol |
| 5 | Directrices | identificación y dirección |
| 6 | Estructura de mercado | accuracy |
| 7 | Zonas de liquidez | exhaustividad y falsos positivos |
| 8 | Indicadores | F1 por etiqueta |
| 9 | Abstención correcta | precisión/exhaustividad |
| 10 | Invenciones / alucinaciones | % de valores no presentes en la referencia ni legibles en la imagen |
| 11 | Consistencia | acuerdo entre repeticiones (si se ejecuta 3×) |

Clasificación de cada discrepancia: **error de lectura · error de clasificación · error de interpretación · dato ilegible · abstención correcta · alucinación**.

## 6. Criterios de aceptación (fijados; no modificables para aprobar)

Instrumento ≥95% · Temporalidad ≥95% · Números inventados <2% · Indicadores F1 ≥0,85 · Abstención correcta ≥90% · Correspondencia temporal medible ≥90%.

Estos umbrales **no** habilitan declarar aprobado el YouTube Analyst: la muestra es una sola escena.

## 7. Aislamiento

El experimento vive en `benchmark_vision_b1/`. No se conecta al pipeline. No modifica prompts ni modelos de producción. No reutiliza CHIEF/Jarvis/Harness/Dashboard. Sin APIs pagas. Sin reentrenamiento.
