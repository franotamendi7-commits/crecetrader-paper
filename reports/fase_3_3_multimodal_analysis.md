# FASE 3.3 — Análisis Multimodal

## 1. Concepto

El análisis multimodal combina evidencia verbal (transcripción) y visual (frames) para construir una interpretación coherente del video.

## 2. Estructura propuesta

Para cada momento del video:
- Timestamp
- Transcripción correspondiente
- Frame(s) extraído(s)
- Análisis visual (Moondream)
- Análisis verbal (transcripción)
- Clasificación: EVIDENCIA_VERBAL, EVIDENCIA_VISUAL, EVIDENCIA_VERBAL_Y_VISUAL, INFERENCIA, NO_CONFIRMADO

## 3. Ejemplo de análisis multimodal

### Momento 1: 305.5s-332.8s (scene_5)
- **Transcripción:** "refugiadas institucionales entre los 72.554 hasta los 69.000"
- **Frame:** scene_5 (318s) — "Fase de Acumulación"
- **Análisis visual (Moondream):** [PROPUESTO] "Gráfico de velas con anotación 'Fase de Acumulación', zona rectangular marcada entre 72.554 y 69.000"
- **Clasificación:** EVIDENCIA_VERBAL_Y_VISUAL
- **Confianza:** Alta (texto visible + audio coincide)

### Momento 2: 106.2s-124.8s (scene_4)
- **Transcripción:** "le esperan los 72.838, 69.840, 65.520"
- **Frame:** scene_4 (115s) — "BITCOIN, Serie semanal"
- **Análisis visual (Moondream):** [PROPUESTO] "Gráfico semanal de Bitcoin con línea de tendencia descendente"
- **Clasificación:** EVIDENCIA_VERBAL (niveles no visibles en el frame)
- **Confianza:** Media (audio menciona niveles, visual no los muestra)

## 4. Estado

**[PROPUESTO]** — Análisis multimodal no implementado
**[PROPUESTO]** — Sincronización audiovisual no implementada
**[PROPUESTO]** — Clasificación de evidencia no implementada

**[PENDIENTE]** — Autorización para implementar
EOF