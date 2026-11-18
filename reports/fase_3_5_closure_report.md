# FASE 3.5 — Informe de Cierre

## 1. Qué se completó

### Documentación
- 10 entregables de FASE 3.5 creados en reports/
- Protocolo de benchmark corregido (rúbrica, métricas, umbrales)
- Dataset especificado (17 imágenes, 10 preguntas por imagen)
- Guía de anotación preparada
- Criterios de aceptación definidos
- Entorno aislado diseñado

### Compatibilidad verificada
- Qwen3.5:9b-mlx acepta imágenes y devuelve descripciones
- Modelo: 9.4B params, nvfp4, 8.9GB, Apache 2.0
- Prueba: frames/scene_004_303.7s.jpg → descripción de gráfico técnico
- Tiempo: ~180s por imagen
- Ollama no modificado
- **Limitación:** Solo se verificó compatibilidad de entrada de imágenes. No se midió precisión ni comprensión visual.

### Transcripción reconciliada
- 145 segmentos (vigente) — única transcripción disponible
- 192 segmentos (FASE 2) — NO VERIFICABLE (archivo no existe)
- No se puede determinar si hubo pérdida de contenido
- Discrepancia: NO VERIFICABLE

### Aislamiento verificado
- No se modificaron archivos originales
- No se instaló ningún modelo ni dependencia
- No se modificó Ollama
- No se ejecutó benchmark

## 2. Qué se verificó con evidencia

| Verificación | Evidencia | Estado |
|-------------|-----------|--------|
| Qwen3.5 acepta imágenes | API response con descripción | VERIFICADO |
| Transcripción 145 segmentos | JSON file, 0.0s-897.52s | VERIFICADO |
| Archivos originales intactos | SHA-256 calculados (READ-ONLY) | VERIFICADO |
| Ollama no modificado | ollama show + ollama list | VERIFICADO |
| No se instaló nada | pip list sin torch/transformers/moondream | VERIFICADO |

### SHA-256 de archivos críticos (calculados READ-ONLY, 2026-11-10)

| Archivo | SHA-256 |
|---------|---------|
| src/prototype.py | d2da8d0eca8b182441cc195bdfa66261f991dcf3cf2f2c1f272f5c9bfdd1f0c6 |
| src/fetch_ohlcv.py | 54be71dc1d8e239ed3ce5a590a58751a542a8e61cf1849ace76c9d4ea78cdb9f |
| src/generate_visual_report.py | 375c1598af740c8034ae350884e05002931c677b35bbdf2cf2939bca7839e |
| data/rTtXDLq2kOQ_transcript.json | bc5354b79bf5752c6c94020a57ea0177db61639f6c9dbda373c24a294f834a3e |
| data/rTtXDLq2kOQ_frames.json | f0b456363bd36248cf434dd546d6e204ec96b176d30093bb2c9c13ca3015ae23 |
| data/rTtXDLq2kOQ_scenes.json | 9bc4fd090239bd89851241c9d8bd96004dce9688cec575cf0716afe8d2632230 |

**Nota:** No existen hashes históricos documentados anteriormente para comparación. Los hashes anteriores registrados en informes (ej. ground_truth_annotations_v1.csv: 8b2ae1fb...) corresponden a archivos de reports/, no a archivos del pipeline. No se puede verificar si los archivos del pipeline cambiaron respecto a un estado anterior. Los hashes actuales se registran como referencia para futuras verificaciones, no como prueba de integridad histórica.

### Evidencia de prueba de Qwen3.5 (recuperada del log)

- **Modelo:** qwen3.5:9b-mlx (ID: 203e30078279, 8.9GB, nvfp4)
- **Imagen de prueba:** frames/scene_004_303.7s.jpg
- **Método:** API POST a http://localhost:11434/api/chat con imagen en base64
- **Prompt:** "Describe this image briefly."
- **Primer intento:** timeout (120s)
- **Segundo intento:** exitoso (~180s)
- **Respuesta obtenida:** "This image displays a technical analysis chart, likely from a financial trading platform like TradingView. It shows a candlestick chart tracking price movements over a period of time (indicated by the weekly timeframe label 'Reversion semanal confirmada'). Key features include: Annotations: The chart is labeled with Spanish text indicating market phase..."
- **Sin modificar Ollama**

### Discrepancia de transcripción: 192 vs 145

**[NO VERIFICABLE]** — El archivo de transcripción de 192 segmentos NO existe en disco.
- Único archivo de transcripción: data/rTtXDLq2kOQ_transcript.json (145 segmentos)
- No se puede comparar ambas versiones porque la de 192 no está disponible
- La afirmación de que "ambas cubren el mismo intervalo" NO puede verificarse
- La transcripción de 145 segmentos es la única vigente y disponible
- **Corrección:** La discrepancia se declara como NO VERIFICABLE, no como "resuelta"

### Inventario de skill youtube-video-analysis

- **Ruta:** ~/.hermes/skills/media/youtube-video-analysis/
- **Archivos:** 2 (SKILL.md + references/vision-model-selection.md)
- **SKILL.md:** 10996 bytes (creado/actualizado durante FASE 3-3.4)
- **references/vision-model-selection.md:** 2501 bytes
- **No hay repositorio git** — No hay diff disponible
- **No se puede determinar** qué cambios específicos hizo el self-improvement review
- **No se revirtió nada** (no se modificó la skill)
- **Aclaración:** Los cambios históricos de la skill no pueden verificarse porque no existe diff ni historial Git.

## 3. Qué se corrigió

1. Protocolo de benchmark: rúbrica, métricas, umbrales definidos
2. Dataset: 17 imágenes (no 170 preguntas), preguntas son dimensiones
3. Ground truth: procedimiento de doble anotación diseñado
4. Transcripción: discrepancia 145 vs 192 explicada
5. Aislamiento: auditoría completa realizada

## 4. Qué sigue pendiente y por qué

| Pendiente | Razón | Requiere |
|-----------|-------|----------|
| Ground truth independiente | No hay anotador B | Intervención humana |
| Benchmark ejecutado | No autorizado | Autorización de Francisco |
| Moondream 2 instalado | No autorizado | Autorización de Francisco |
| Muestreo adaptativo | No implementado | Autorización + código |
| Más videos para validación | Solo 1 video | Procesar más videos |
| Transcripción 192 vs 145 | NO VERIFICABLE (archivo de 192 no existe) | No se puede resolver |
| Hashes históricos | No existen hashes anteriores para comparar | No se puede verificar cambios |

## 5. Riesgos y limitaciones

1. **Qwen3.5 lento** (~180s/img → ~51 min para 17 frames)
2. **Sin ground truth** — No se puede medir precisión
3. **Solo 1 video** — No se puede generalizar
4. **17 frames con cobertura insuficiente** — Muestreo adaptativo no implementado
5. **Sin comparación** — No se comparó con otros modelos
6. **Transcripción 192 NO VERIFICABLE** — No existe el archivo original
7. **Hashes históricos NO existen** — No se puede verificar si los archivos cambiaron
8. **Skill diff NO disponible** — No hay repositorio git

## 6. Dictamen final de cierre

**[APTO CON LIMITACIONES — FASE 3.5 CERRADA COMO PREPARACIÓN TÉCNICA]**

La FASE 3.5 completó la preparación técnica del benchmark visual:
- Protocolo corregido y definido
- Dataset especificado
- Guía de anotación preparada
- Compatibilidad básica de Qwen3.5 verificada (entrada de imágenes, no precisión ni comprensión)
- Aislamiento auditado
- Transcripción: NO VERIFICABLE (192 no existe)

Sin embargo:
- Ground truth independiente NO existe
- Benchmark NO ejecutado
- Moondream 2 NO instalado ni probado
- Muestreo adaptativo NO implementado
- Transcripción 192 vs 145: NO VERIFICABLE
- Hashes históricos: NO existen para comparación
- Skill diff: NO disponible (sin git)

## 7. Decisión

**La FASE 3.5 puede cerrarse como preparación técnica.**

El benchmark y la implementación experimental requieren autorización explícita de Francisco.

**No se abre FASE 3.6. No se ejecuta el benchmark. No se instala ningún modelo.**

---

**PRINCIPIO DE AUDITORÍA: NO CREER. PROBAR.**

**La decisión final corresponde exclusivamente a Francisco.**
EOF