# INFORME — Benchmark de fiabilidad de visión (B1 + B3 + B6)

Fecha: 2026-11-16
Autor: Hermes Agent
Directorio aislado: `~/YouTubeTradingAgent/benchmark_vision_b1/`
Restricciones respetadas: solo lectura sobre production; sin cambios de código, prompts, modelos, skills ni configuración; sin reprocesar videos; sin servicios pagos; `PAPER_ONLY` intacto.

---

## B1 — Dataset y material de anotación

### Inventario real (recomputado de disco)

- **157 frames** en 8 vídeos (7 vídeos × 20 + `LzPTdClLo_w` × 17).
- **Duplicados por MD5: 0.**
- Dimensiones: `640×352` (80), `640×346` (40), `600×360`→`640×360` (20), `640×336` (17). Todas 640 de ancho; el alto varía por alineación de ffmpeg.
- Legibilidad básica (desviación estándar de luminancia): mín 21,57 / media 60,04 / máx 116,2. **Ningún frame por debajo de 20** → no hay frames vacíos o ilegibles por varianza.
- Registro: `benchmark_vision_b1/inventory.json` y `inventory.csv` (frame, idx, dimensiones, bytes, std, md5, pts_time, verificación).

### Conjunto estratificado

- **48 frames** seleccionados (6 por vídeo), estratificados por **tramo temporal** (temprano/medio/tardío) usando el `pts_time` verificado.
- La selección **no usa** las identificaciones del modelo.
- Detalle: `annotations/seleccion_estratificada.json`.
- Plantilla de anotación (48 filas, columnas vacías): `annotations/template_anotacion.csv`.

### Material para anotadores

- Contact sheets por vídeo (8): `benchmark_vision_b1/contact_sheets/*_contact_sheet.jpg`, con ID único `video__frame` visible en cada celda. Índice: `contact_sheets/contact_sheets_index.json`.
- Instrucciones: `templates/INSTRUCCIONES_ANOTADORES.md`.
- Mecanismo de desacuerdos: `templates/ADJUDICACION.md` + `scripts/b1_adjudicacion.py`.

### Estado de la referencia humana

**PENDIENTE.** No hay dos anotadores humanos disponibles en este entorno. No se inventaron anotaciones ni se simuló una segunda opinión. **No se ejecutó B4 ni B5.**

---

## B3 — Recuperación temporal (VERIFICADA)

### Método

`extract_frames` numera los archivos con `frame_%04d` desde 1 (ffmpeg). Por tanto **el número de archivo es el índice 1-based de extracción**. El `fps` efectivo se recupera como `fps_implícito = max_idx / duración`.

Comprobación con `ffmpeg -vf "fps=<fps>,showinfo"` (solo lectura): se capturaron los `pts_time` de la extracción completa y se verificó que `pts_time(n) == (n-1)/fps` para cada frame existente.

### Resultados

| vídeo | duración (s) | max idx | fps implícito | fps esperado | frames | `pts_time` verificados |
|---|---|---|---|---|---|---|
| EJoLhxbwYxo | 986,73 | 4933 | 4,9993 | 5 | 20 | **20/20** |
| LFHkc5dUoLw | 802,64 | 4013 | 4,9997 | 5 | 20 | **20/20** |
| LzPTdClLo_w | 524,47 | 17 | 0,03241 | 1/30 | 17 | **17/17** |
| XLgPycsN0ls | 1215,52 | 41 | 0,03373 | 1/30 | 20 | **20/20** |
| dPHvRw1wzYQ | 2015,03 | 67 | 0,03325 | 1/30 | 20 | **20/20** |
| jeOFS1TZYQA | 773,69 | 26 | 0,03361 | 1/30 | 20 | **20/20** |
| s3KxjqkzwKM | 993,21 | 33 | 0,03323 | 1/30 | 20 | **20/20** |
| scJ-ai2FRiE | 884,22 | 29 | 0,03280 | 1/30 | 20 | **20/20** |

**157/157 frames con `pts_time` verificado.** Fórmula: `t = (idx-1)/fps`, con `fps=5` para los dos vídeos antiguos y `fps=1/30` para los seis procesados en A.7.4.
Registro: `temporal/timestamps.json`.

### Deduplicación de transcripciones (sin modificar originales)

Dedup por **texto consecutivo idéntico** (los originales no se tocaron; salidas en `temporal/*_transcript_dedup.json`):

| vídeo | cues originales | tras dedup | eliminados |
|---|---|---|---|
| EJoLhxbwYxo | 878 | 869 | 9 |
| LFHkc5dUoLw | 622 | 619 | 3 |
| LzPTdClLo_w | 487 | 483 | 4 |
| XLgPycsN0ls | 1086 | 1073 | 13 |
| dPHvRw1wzYQ | 1780 | 1756 | 24 |
| jeOFS1TZYQA | 600 | 594 | 6 |
| s3KxjqkzwKM | 843 | 842 | 1 |
| scJ-ai2FRiE | 801 | 800 | 1 |

**Corrección de un hallazgo anterior**: en el informe de validación de LFHkc5dUoLw se afirmó que la transcripción estaba "triplicada". Los datos muestran **3 duplicados de 622** (0,5%), no un triplicado. La repetición observada en `full_text` era un artefacto de visualización, no de los cues. Se corrige ese punto.

---

## B6 — Prototipo aislado de parser y calidad (NO conectado a producción)

Script: `scripts/b6_quality_parser.py`. Lee los `*_analysis.json` existentes; **no reproduce videos**.

Reglas implementadas: R1 texto de plantilla sin rellenar · R2 campos ausentes · R3 instrumento no listado · R4 magnitud improbable (plausibilidad, no verificación visual) · R5 exceso de niveles (>12) · R6 duplicados · R7 secuencia artificial (cuenta atrás / paso constante) · R8 respuesta truncada · R9 UNKNOWN con precios.

### Resultados (157 frames)

| vídeo | total | valid | needs_review | rejected |
|---|---|---|---|---|
| EJoLhxbwYxo | 20 | 0 | 1 | 19 |
| LFHkc5dUoLw | 20 | 1 | 3 | 16 |
| LzPTdClLo_w | 17 | 3 | 13 | 1 |
| XLgPycsN0ls | 20 | 3 | 4 | 13 |
| dPHvRw1wzYQ | 20 | 1 | 3 | 16 |
| jeOFS1TZYQA | 20 | 4 | 6 | 10 |
| s3KxjqkzwKM | 20 | 2 | 11 | 7 |
| scJ-ai2FRiE | 20 | 8 | 7 | 5 |
| **TOTAL** | **157** | **22** | **48** | **87** |

Motivos frecuentes: `R2_campo_ausente` 83 · `R1_plantilla` 43 · `R5_exceso_niveles` 34 · `R8_truncada` 29 · `R4_magnitud` 29 · `R7_cuenta_atras` 16 · `R6_duplicados` 14 · `R7_paso_constante` 14 · `R3_instrumento` 1.

Salida: `results/b6_parser_report.json`.

### Hallazgo nuevo relevante: respuestas truncadas y degeneración por repetición

- **29/157 respuestas están truncadas** (no contienen el campo final `INDICATORS:` o dejan un corchete sin cerrar).
- `LFHkc5dUoLw`: **13/20** respuestas truncadas. Ejemplo `frame_3994`: la respuesta termina en `…, 87100, 87100, 87100, …` (repetición infinita del mismo número) y **no cierra el corchete** de `PRICES`.
- Es la huella de **degeneración por repetición** con corte por límite de generación.
- `ollama show qwen2.5vl:3b`: contexto 128000, cuantización Q4_K_M, `temperature 0.0001` en el Modelfile (el código la sobreescribe a 0.1). **No expone `num_predict` ni `repeat_penalty`** → `[NO VERIFICADO]` cuál es el límite efectivo que produjo el corte.

---

## Limitaciones

- **R4 (magnitud) es propenso a falsos positivos** por la ambigüedad del separador de miles (`78.71` puede ser 78,71 o 78.710). No debe usarse como prueba de error sin revisión humana.
- **R7 paso constante** puede dar falsos positivos en ejes con rejilla regular.
- Los **rangos de plausibilidad** son orientativos y no verifican que un número esté escrito en el gráfico.
- El parser es un **prototipo aislado**: no está conectado al pipeline ni a la producción.
- El dataset (157 frames, 48 estratificados) es **pequeño**; las métricas finales tendrán potencia estadística limitada.

## Separación de estado

- **VERIFICADO**: inventario (157 frames, 0 duplicados, dimensiones, std); recuperación temporal 157/157; dedup VTT; resultados del parser sobre los artefactos existentes.
- **CORREGIDO**: el hallazgo de "transcripción triplicada" (era 3 duplicados de 622).
- **NO VERIFICADO**: valores por defecto de `num_predict`/`repeat_penalty`; causa exacta del truncado; precisión del modelo (requiere ground truth).
- **PENDIENTE**: anotación humana independiente (2 anotadores) y adjudicación; B4 y B5; conexión del parser (no autorizada).
- **REQUIERE AUTORIZACIÓN**: ejecutar B4/B5; modificar producción; cambiar modelos o configuración.

## Próximo paso

Presentar el material (contact sheets + plantilla + instrucciones) para anotación humana independiente. **No se ejecuta B4/B5 hasta existir referencia validada.**
