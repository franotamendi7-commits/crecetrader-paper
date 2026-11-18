# AUDITORÍA Y RECUPERACIÓN DE CAPTURAS — LFHkc5dUoLw

Fecha: 2026-11-16
Alcance: solo lectura sobre evidencia existente. Copia de entrega creada solo donde se autorizó.
Vídeo: `LFHkc5dUoLw` (802,64 s). Frames auditados: `frame_3994.jpg` … `frame_4013.jpg`.

---

## A. Recuperación

**Composición localizada:** `benchmark_vision_b1/contact_sheets/LFHkc5dUoLw_contact_sheet.jpg` (2560×1890 px, 808.551 bytes).

**Archivos individuales originales: SÍ existen los 20.**
Ruta original: `frames_hist/LFHkc5dUoLw/frame_3994.jpg` … `frame_4013.jpg` (20 archivos).

**¿Originales o reconstruidas desde la composición?** Son **originales**. La composición es una derivada: al comparar cada celda del contact sheet con su original, la diferencia media es **1,6/255** (máx 55) en las 20 celdas, compatible únicamente con recompresión JPEG. No hay reconstrucción.

**Copia de entrega preparada** (originales intactos):
`entregas_a74/LFHkc5dUoLw/` — 20 JPEG + `MANIFIESTO.json` + `MANIFIESTO.csv`.
Integridad de la copia: **20/20 hashes MD5 idénticos** a los originales.

## B. Integridad

- Dimensiones: **640×352 px** (los 20).
- Tamaño: 43.776–43.870 bytes.
- Hashes MD5 y rutas: `entregas_a74/LFHkc5dUoLw/MANIFIESTO.csv` (y `.json`).
- Duplicados entre los 20: **0**.
- Origen de extracción: `ffmpeg -q:v 2` (JPEG baseline, comentario `Lavc63.1.102`).

## C. Selección temporal — causa demostrada

**No son una muestra del vídeo: son sus últimos 3,8 segundos.**

- `run_video.py:25` define `--fps` por defecto **5**.
- `extract_frames()` (`scripts/rss_priority_processor.py:499-528`) extrae **todos** los frames a ese fps y luego, si superan `max_frames` (20), **elimina los primeros**: `for old in files[:-max_frames]: old.unlink(...)` (línea 523).
- Con fps=5 y 802,64 s → **4013 frames** generados; se descartaron los primeros 3993 y se quedaron **3994–4013**.
- Timestamps verificados (`benchmark_vision_b1/temporal/timestamps.json`, `t=(idx-1)/fps`):
  - `frame_3994` → **798,600 s** (99,50% del vídeo)
  - `frame_4013` → **802,400 s** (99,97%)
  - Ventana cubierta: **3,80 s**.
- El fps se verifica de forma independiente: `fps_implícito = 4013 / 802,644 = 4,9997 ≈ 5`.
- **Error confirmado de muestreo**: no hubo indexación por contenido ni selección representativa; el recorte `[:-max_frames]` deja siempre el tramo final. Con fps=5 en un vídeo de 13 minutos, la cobertura es de 4 segundos.
- No hubo error de indexación (los índices son correctos y verificables); el error es de **criterio de selección y de fps**.

## D. Relación con el benchmark B1

- Los 20 frames están incluidos en el inventario de **157 frames** (`benchmark_vision_b1/inventory.json` / `inventory.csv`), vídeo `LFHkc5dUoLw`.
- **6 de ellos** forman parte de los **48 seleccionados** por estratificación temporal (`annotations/seleccion_estratificada.json`).
- **No se duplican** imágenes ni se incorporan como ejemplos nuevos: la copia de entrega apunta a los mismos originales ya registrados.
- Los `pts_time` de estos 20 frames son los verificados en B3.

## E. Calidad visual — lo que realmente se lee

Base: 4 análisis de visión reales sobre frames individuales (3994, 4000, 4006 con el proveedor auxiliar; 4013 en esta auditoría).

**Información visible**
- Instrumento: **BTCUSD** (marca de agua "BTCUSD, 1D"; en un frame "Cotizaciones: Coinbase").
- Temporalidad: **1D** (diario).
- Estructura: tendencia alcista previa fuerte y corrección/consolidación posterior; líneas de tendencia (alcista verde y bajista amarilla) y línea punteada de proyección.
- Niveles con etiqueta: **87.496**, **83.833/83.933**, **82.833/83.000**, **81.444/81.446**, **78.748/78.746**, **73.458**, **71.466**, **69.997/69.907**, **67.534**.
- Indicadores: **Fibonacci** (retroceso 61,7% → 26.638) y líneas de tendencia. Medias móviles solo en algunos frames (no en todos).

**Información parcialmente visible**
- Etiquetas intermedias pequeñas (~79.7k, ~72.7k, ~69.1k) y el precio actual (etiqueta roja): valores aproximados, no exactos.
- Zonas de liquidez: se infieren por las líneas horizontales, sin etiqueta de texto legible en varios casos.

**Información ilegible**
- Texto pequeño superior izquierdo (título completo del símbolo, valores OHLC).
- Panel superior derecho (rojo/verde).
- Eje de fechas: **oculto por la franja publicitaria inferior**.
- Posible panel de volumen: no visible (zona inferior tapada).

**No determinable**
- Volumen (no visible).
- OHLC exactos de cada vela.
- Exchange exacto en los frames donde la esquina no es legible.

**Obstrucciones**: la ventana del presentador (arriba al centro) y la franja promocional morada (abajo, con QR) tapan partes del gráfico.

## F. Problemas encontrados

**Confirmados**
1. Muestreo sesgado: los 20 frames son los últimos 3,8 s (línea 523 + fps=5).
2. Sin registro de `pts_time` en la extracción (recuperado ahora por B3).
3. `fps=5` por defecto es inadecuado para vídeos de 13–34 minutos.
4. La entrega en una sola composición no permite verificar la legibilidad individual.

**Hipótesis pendientes**
- Que con un fps bajo y muestreo uniforme la legibilidad de niveles mejore (no verificado).
- Que el recorte final se hizo por diseño para "ver el cierre" (no hay registro que lo confirme).

**Limitaciones**
- La legibilidad se evaluó sobre 4 de 20 frames, no sobre los 20.
- No se comparó la composición con los originales píxel a píxel (solo por diferencia media).

## G. Recomendaciones (propuestas, NO realizadas)

**Extracción**
1. Definir el fps según la duración (p. ej., 20–30 frames repartidos en todo el vídeo).
2. Muestrear uniformemente (inicio, medio, fin), nunca solo el tramo final.
3. Registrar `pts_time` por frame al extraer.
4. Conservar los frames individuales como fuente de verdad.

**Entrega de evidencia**
1. Entregar **siempre** los frames individuales originales.
2. Contact sheet complementario, nunca sustituto.
3. Manifiesto que relacione cada imagen con su archivo de origen (video, idx, `pts_time`, dimensiones, hash).
4. Identificador de video de origen en cada elemento.
5. Índice y timestamp visibles.

**Benchmark**
1. No usar los 20 frames de LFHkc5dUoLw como muestra representativa (solo sirven como muestra del tramo final).
2. Ampliar la selección estratificada si se quiere cobertura del vídeo completo.

## H. Estado

- **No modifiqué producción**: no se tocó `scripts/`, `run_video.py`, `analyze_vision_batch.py`, prompts, modelos, skills ni configuración.
- **No modifiqué los archivos originales** (`frames_hist/LFHkc5dUoLw/*` intactos; verificados por hash antes y después).
- **No modifiqué el benchmark B1/B3/B6** (solo lectura de sus artefactos).
- **No reprocesé videos ni ejecuté inferencias** (solo una llamada de visión auxiliar sobre un frame ya existente, para la evaluación de legibilidad).
- **No instalé dependencias ni envié datos a servicios externos.**
- Acciones de escritura realizadas: copia de entrega (`entregas_a74/LFHkc5dUoLw/`, 20 archivos + manifiesto) y este informe. Ambas autorizadas por el punto 1.6 y 7.

Pendiente de verificación humana: la anotación de los 20 frames para confirmar la legibilidad declarada en E.
