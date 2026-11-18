# FASE A.7.4 — Auditoría técnica de la causa raíz de los errores de visión

Fecha: 2026-11-15
Alcance: solo lectura. No se modificó ningún archivo de código, prompt, configuración o skill; no se cambió ningún modelo; no se reprocesó ningún video.
Vídeos auditados: `s3KxjqkzwKM`, `jeOFS1TZYQA`, `XLgPycsN0ls` (artefactos existentes).
Modelo de visión: `qwen2.5vl:3b` (Ollama 0.40.16, local). LLM del agente: `meituan/longcat-2.5:free` (Nous).

---

## FASE 1 — Auditoría de solo lectura

### 1. `VISION_PROMPT_TEMPLATE` — contenido íntegro

Archivo: `scripts/rss_priority_processor.py`, líneas **104-111**.

```
Analyze this trading chart. Return ONLY the following fields, one per line, in this exact format:

INSTRUMENT: (BTCUSD, ETHUSD, ES, NQ, XAUUSD, AMD, or UNKNOWN)
TIMEFRAME: (Weekly, Daily, 4H, 1H, 15m, 5m, or UNKNOWN)
PRICES: [list visible prices or null]
STRUCTURE: (trend, range, support, resistance, or UNKNOWN)
INDICATORS: (MA, Fibonacci, Volume, or none)
```

`VISION_MODELS = ["qwen3.5:9b-mlx", "qwen2.5vl:3b"]` — línea **100**.

### 2. Función que construye la solicitud a `qwen2.5vl:3b`

- `analyze_frame_vision()` — `scripts/rss_priority_processor.py:858-868`: lee el JPEG y lo codifica en base64 (líneas 862-866).
- `call_ollama_chat()` — `scripts/rss_priority_processor.py:834-852`: construye el payload y llama a `POST {ollama_url}/api/chat`.

Payload efectivo (líneas 837-846):

```json
{
  "model": "<model>",
  "messages": [{"role": "user", "content": "<prompt>", "images": ["<base64>"]}],
  "stream": false,
  "options": {"temperature": 0.1}
}
```

Invocación en `run_video.py:107-116` (lote de frames) y en `analyze_vision_batch.py:59-62`.

### 3. Resolución, dimensiones, formato y transformación de imagen

- **Sin transformación**: el JPEG se codifica a base64 y se envía tal cual (`rss_priority_processor.py:862-866`). No hay redimensionado, recorte, normalización ni escalado.
- Dimensiones medidas con `sips`: **640×352** px (JPEG baseline, 8 bits, RGB, sin alfa). `XLgPycsN0ls/frame_0024.jpg`: 640×346.
- El vídeo fuente es 640×352 (`ffprobe`), es decir, el frame no gana detalle al extraerse.
- Consecuencia: las etiquetas de precios del gráfico (texto pequeño de TradingView) quedan a muy pocos píxeles. **Esto es una observación medida, no una causalidad demostrada** (ver FASE 2, ítem C).

### 4. Parámetros efectivos de inferencia

- Único parámetro fijado en el código: **`temperature: 0.1`** (`rss_priority_processor.py:844`).
- **No se fijan** `top_p`, `top_k`, `num_predict`, `seed`, `repeat_penalty`, `stop`, `num_ctx`, `format`. Por tanto se aplican los **valores por defecto del servidor Ollama 0.40.16**.
- Esos defaults **no están declarados en el código ni en la documentación de la API consultada** → `[NO VERIFICADO]`. No se asume ningún valor.
- `format` no se usa: la respuesta es texto libre, no JSON estructurado.
- Timeout: `DEFAULT_VISION_TIMEOUT = 600` s (`rss_priority_processor.py:94`); en `analyze_vision_batch.py` se usa 300 s.

### 5. Procesamiento y validación de la respuesta

- `_save_analysis()` (`rss_priority_processor.py:925-973`) **guarda el string sin validar contenido**: solo comprueba duplicados por nombre de frame y actualiza `frames_processed`.
- `run_video.py:113`: la única comprobación es `if result.startswith('ERROR')`.
- `validate_video()` (`rss_priority_processor.py:871-918`): solo verifica que existan `video_path`, `frames_dir` con jpg, `transcript_path` y `analysis_file`, y que `frames_processed` sea distinto de cero (líneas 905-910). **No inspecciona la calidad del análisis.**
- No existe parser de `PRICES`/`INSTRUMENT`/`TIMEFRAME` en el pipeline. Los únicos parsers son scripts experimentales no invocados por el pipeline: `experimental/scripts/init_memory.py:31-41`, `experimental/scripts/audit_frames.py:19-28`, `experimental/scripts/vision_independence_test.py:20-23`.

### 6. ¿Existe algún límite o validación de calidad?

**No.** Verificado por inspección y por los artefactos:
- Sin límite de cantidad de precios: hay respuestas con **157** y **134** números.
- Sin detección de duplicados ni de secuencias artificiales: respuestas con cuentas atrás (`70.000, 69.000, … 1.000, 0`).
- Sin rangos imposibles por instrumento.
- Sin detección de instrumentos contradictorios.
- Sin detección de texto de plantilla sin rellenar (`PRICES: [list visible prices or null]`).

### 7. Extracción de frames y recuperación del timestamp real

`extract_frames()` — `rss_priority_processor.py:499-528`:
- Comando: `ffmpeg -y -hide_banner -loglevel error -i <video> -vf fps=<fps> -q:v 2 <frames_dir>/frame_%04d.jpg` (líneas 509-511).
- **No registra el instante temporal de cada frame.** El nombre es solo un contador.
- Si `len(files) > max_frames`, **borra los primeros** (`files[:-max_frames]`, línea 523): el muestreo queda sesgado al tramo final del vídeo.
- Los JPEG no tienen metadata temporal: `sips -g all` no muestra `DateTime`/EXIF; `file` solo revela `comment: "Lavc63.1.102"`.
- La numeración observada (`3994-4013`, `4914-4933`) no procede de una extracción `frame_%04d` desde 1, por lo que **el nombre del archivo no permite derivar el timestamp**.
- **Vía de recuperación verificada (solo lectura, sin re-extraer)**: `ffmpeg -vf "fps=1/30,showinfo"` emite `pts_time` por frame. Comprobado: `pts_time:0`, `pts_time:30`, `pts_time:60` para los tres primeros frames. Mapeando el N-ésimo frame de la extracción a la N-ésima línea de `showinfo` se recupera el timestamp real.
- Alternativa: extraer con `-frame_pts 1` o nombrar con el `pts_time`.

### 8. Comparación del comportamiento en los tres vídeos

Métricas recomputadas de los `*_analysis.json` (números de frame y prefijos exactos):

| Métrica | s3KxjqkzwKM | jeOFS1TZYQA | XLgPycsN0ls |
|---|---|---|---|
| frames | 20 | 20 | 20 |
| respuestas con plantilla sin rellenar | 2 | 3 | 3 |
| respuestas que omiten los prefijos (`UNKNOWN / Daily / …`) | 0 | 0 | 2 (f0030, f0031) |
| enumeraciones >40 números | 2 (máx 157) | 3 (máx 101) | 5 (máx 97) |
| `PRICES: [null]` | 2 | 0 | 1 |
| instrumentos claramente incompatibles con la magnitud | 3 (f0025, f0026, f0027) | 3 (f0019, f0022, f0023) | 2 (f0034, f0035) |

Evidencia literal:

- `s3KxjqkzwKM/frame_0027.jpg`: `INSTRUMENT: BTCUSD | PRICES: [3.944.8, 3.900.0, 3.820.0, 3.623.4, 3.500.0, 3.472]` → magnitudes de **oro (XAUUSD)**, no de BTC.
- `s3KxjqkzwKM/frame_0025.jpg`: `INSTRUMENT: ES | PRICES: [2478.6, 2373, 2215.1, 2077, 1896.5, 1780]` → magnitudes de **ETHUSD**.
- `s3KxjqkzwKM/frame_0024.jpg`: `PRICES: [78,241, 76,832, … 1,000, 0]` → enumeración artificial descendente.
- `jeOFS1TZYQA/frame_0019.jpg`: `INSTRUMENT: NQ | PRICES: [201.40, 230.52, 259.64, …]` → magnitudes de **AMD**.
- `jeOFS1TZYQA/frame_0023.jpg`: `INSTRUMENT: AMD | PRICES: [15.89, 16.00, 16.20, …]` → enumeración con paso 0,10.
- `XLgPycsN0ls/frame_0030.jpg`: `UNKNOWN | Daily | [136.0 MS] | trend | MA` → **forma de plantilla sin prefijos**.
- `XLgPycsN0ls/frame_0031.jpg`: `UNKNOWN | UNKNOWN | [null] | UNKNOWN | MA` → ídem.

---

## FASE 2 — Diagnóstico por causa

Etiquetas: `[CONFIRMADO]` (evidencia directa), `[INFERIDO]` (deducción razonable no verificada), `[NO VERIFICADO]`.

### A. Prompt — `[CONFIRMADO]` como factor contribuyente

1. `PRICES: [list visible prices or null]` es ambiguo: no define si se piden niveles etiquetados, precios del eje, OHLC ni cuántos. El modelo responde enumerando.
2. La plantilla se reproduce literalmente cuando el modelo no "rellena": `[list visible prices or null]` aparece en los artefactos.
3. `INSTRUMENT` ofrece una lista cerrada de 7 símbolos, pero los gráficos del canal incluyen más (SP500, BX, MDT, VX1!, etc.). La lista incompleta fuerza respuestas `UNKNOWN` o asignaciones erróneas.
4. No se instruye la abstención ("si no es legible, responde null"), lo que favorece la invención.

### B. Capacidad del modelo — `[CONFIRMADO]` como factor contribuyente

1. Confusión sistemática entre instrumentos con magnitud similar o no: ES↔ETH (2.478/2.870), NQ↔AMD (201/230), BTC↔oro (3.944).
2. Invención de secuencias numéricas con paso constante y cuentas atrás hasta cero.
3. Omisión de los prefijos de campo (fuga del formato) en varios frames.

`qwen2.5vl:3b` es un modelo de 3B; su capacidad de OCR fino sobre texto pequeño es limitada. `[INFERIDO]` que sea la causa dominante; **no verificado** sin benchmark comparativo.

### C. Resolución y preprocesamiento — `[INFERIDO]`

1. Imagen enviada a 640×352, sin escalado ni realce (`rss_priority_processor.py:862-866`). `[CONFIRMADO]` (medido).
2. Que esa resolución sea causa de los errores de lectura **no está verificado**: no se ha comparado con una versión escalada del mismo frame. Requiere benchmark A/B.

### D. Parser y validación — `[CONFIRMADO]` como causa raíz de la persistencia del error

1. El pipeline no parsea ni valida la respuesta: `_save_analysis` (925-973), `run_video.py:113`, `validate_video` (905-910).
2. Por tanto **ningún defecto se detecta ni se marca**: frames con precios inventados, instrumentos contradictorios o plantillas se almacenan como válidos y el vídeo se marca `completed`.
3. No hay límites de cantidad, duplicados, rangos, secuencias ni texto de plantilla.

Este es el factor que convierte errores de modelo en **datos incorrectos aceptados como resultados**.

### E. Muestreo y sincronización temporal — `[CONFIRMADO]`

1. `extract_frames` no registra el timestamp (`499-528`).
2. El recorte `files[:-max_frames]` (línea 523) sesga la muestra al final del vídeo.
3. La numeración de archivos no deriva del tiempo → no hay correspondencia frame↔timestamp.
4. Sin timestamp no hay forma de contrastar cada frame con el audio/transcripción. La correspondencia verbal↔gráfico queda sin verificar.
5. Agravante: la transcripción está **triplicada** (622 cues → texto ×3), sin deduplicar, lo que dificulta cualquier alineación.

### Resumen de causalidad

| Causa | Estado | Rol |
|---|---|---|
| Parser/validación inexistente | CONFIRMADO | **Raíz de la persistencia**: acepta y propaga errores |
| Prompt ambiguo e incompleto | CONFIRMADO | **Raíz de la invención/enumeración** |
| Capacidad del modelo 3B | CONFIRMADO (confusiones), INFERIDO (dominancia) | Genera los errores |
| Resolución 640×352 sin preprocesar | INFERIDO | Posible agravante de lectura |
| Muestreo sin timestamps | CONFIRMADO | Imposibilita la validación temporal |

---

## FASE 3 — Propuesta (NO ejecutada; requiere autorización)

### P1. Prompt
- Campos cerrados y formato JSON estricto (usar `format: json` de la API de Ollama).
- Instrucción explícita: "transcribe SOLO los niveles con etiqueta visible; máximo 12; si no es legible, `null`".
- Prohibir enumeraciones: "no generes secuencias numéricas; solo valores escritos en el gráfico".
- Ampliar `INSTRUMENT` a los símbolos del canal o permitir `OTHER:<texto>`.
- Abstención obligatoria por campo.

### P2. Parser y validación (lo de mayor impacto)
- Validar esquema y tipos; rechazar si falta un campo o si aparece texto de plantilla.
- Detección de invención: números que no aparezcan en una lista blanca de niveles etiquetados (vía OCR de referencia).
- Detección de secuencias artificiales (diferencias constantes, monotonicidad perfecta, valores consecutivos "redondos").
- Rango plausible por instrumento; duplicados; conteo máximo.
- Marcar `needs_review` en lugar de `completed` cuando haya anomalías.

### P3. Preprocesamiento
- Escalar el lado largo a ≥1024 px conservando proporción; opcionalmente realce de contraste.
- Comparar con/ sin escalado en el benchmark antes de adoptarlo.

### P4. Muestreo y timestamps
- Registrar `pts_time` de cada frame (vía `showinfo` o `-frame_pts`).
- Muestrear uniformemente de todo el vídeo, no solo los últimos 20.
- Persistir `timestamp` en `frame_results` y alinear con el VTT deduplicado.

### P5. Transcripción
- Deduplicar cues (el VTT del canal triplica el texto) antes de any analysis.

### Protocolo de benchmark

**Dataset**: los 117 frames ya extraídos de los 8 vídeos de A.7.4, más los frames de LFHkc5dUoLw. Subconjunto estratificado por instrumento/temporalidad para anotación.

**Anotación humana independiente** (2 anotadores, doble ciego, desacuerdos por tercero):
- `instrument` (lista cerrada ampliada)
- `timeframe` (lista cerrada)
- `price_levels` (lista de niveles etiquetados, con tolerancia de ±1 en el último dígito)
- `indicators` (multi-etiqueta: MA, Fibonacci, Volumen, ninguno)
- `structure` (tendencia/rango/soporte/resistencia)
- `abstention` (por campo: "no legible")
- `audio_segment` (rango temporal del audio que describe el gráfico, si aplica)

**Condiciones**: mismo prompt, misma imagen, 3 repeticiones por frame a `temperature 0.1` (medir variabilidad). Variantes: prompt nuevo vs actual; resolución 640×352 vs escalada. Modelo invariado (`qwen2.5vl:3b`).

**Métricas por separado**:
| Criterio | Métrica |
|---|---|
| Instrumento | accuracy + matriz de confusión |
| Temporalidad | accuracy |
| Precios | precisión/exhaustividad por nivel; **tasa de números inventados** |
| Indicadores | F1 multi-etiqueta |
| Estructura | accuracy |
| Abstención | precisión/exhaustividad de abstenciones correctas |
| Correspondencia temporal | IoU entre el rango de audio anotado y el `pts_time` del frame |

**Criterios de aceptación propuestos**: instrumento ≥95%; temporalidad ≥95%; números inventados <2%; indicadores F1 ≥0,85; abstención correcta ≥90%; correspondencia temporal medible en ≥90% de frames.

---

## Estado de hallazgos

- **CONFIRMADO**: prompt ambiguo; ausencia de parser/validación; confusión de instrumentos; enumeraciones artificiales; reproducción de plantilla; omisión de prefijos; ausencia de timestamps y muestreo sesgado; transcripción triplicada; resolución 640×352 sin preprocesamiento.
- **INFERIDO**: que la resolución sea causa dominante de los errores de lectura; que la capacidad del 3B sea el límite principal.
- **NO VERIFICADO**: valores por defecto de `top_p`/`num_predict`/etc. en Ollama 0.40.16; la calidad de las respuestas a mayor resolución; la correspondencia temporal (imposible sin timestamps).
- **PROPUESTA**: P1-P5 y protocolo de benchmark (sin ejecutar).
- **REQUIERE AUTORIZACIÓN**: cualquier cambio de prompt, código, validación, muestreo o modelo; ejecutar el benchmark; usar servicios externos.

## Conclusión

La causa raíz de los errores de visión **no es un único fallo**: el modelo genera errores (instrumentos, precios, formato), pero el pipeline **los acepta y los propaga sin validación** (`_save_analysis` / `run_video.py:113` / `validate_video`). El prompt actual induce enumeración e invención. La corrección de mayor impacto es P2 (parser y validación), seguida de P1 (prompt) y P4 (timestamps). La resolución y la capacidad del modelo deben evaluarse con el benchmark antes de cualquier cambio.

Fin del informe. No se ejecutó ningún cambio. Quedo a la espera de autorización.
