# FASE 3.3 — Frame Selection Audit

## 1. Problema actual

El pipeline actual extrae 1 frame por escena detectada por PySceneDetect. Esto resulta en:
- 17 frames para 17 escenas
- Escenas largas (293.7s) con 1 solo frame
- No se detectan cambios de gráfico dentro de una escena
- No se priorizan momentos importantes

## 2. Propuesta de muestreo adaptativo

### Estrategia propuesta

1. **Muestreo base:** 1 frame cada 30 segundos en escenas largas (>60s)
2. **Detección de cambios visuales:** Usar histograma de color para detectar cambios de gráfico
3. **Priorización por audio:** Extraer frames en momentos donde el autor menciona niveles, instrumentos o escenarios
4. **Deduplicación:** Evitar frames redundantes (hash perceptual)
5. **Máximo por escena:** 5 frames por escena larga

### Implementación propuesta (no ejecutada)

```python
# Pseudocódigo
def adaptive_frame_selection(video, scenes, transcript):
    frames = []
    for scene in scenes:
        if scene.duration > 60:
            # Extraer frames cada 30s
            for t in range(scene.start, scene.end, 30):
                frames.append(extract_frame(video, t))
        else:
            # 1 frame en el centro
            frames.append(extract_frame(video, scene.start + scene.duration/2))
        
        # Priorizar momentos con menciones de niveles
        for segment in transcript.segments:
            if segment.start >= scene.start and segment.end <= scene.end:
                if contains_price_level(segment.text):
                    frames.append(extract_frame(video, segment.start))
    
    # Deduplicar
    frames = deduplicate_frames(frames)
    return frames
```

## 3. Resultados esperados

| Métrica | Actual | Propuesto |
|---------|--------|-----------|
| Frames por video | 17 | ~30-40 |
| Cobertura de escenas largas | 1 frame | 3-5 frames |
| Cambios de gráfico detectados | No | Sí (histograma) |
| Momentos importantes priorizados | No | Sí (audio) |
| Frames redundantes | Posibles | Eliminados |

## 4. Estado

**[PROPUESTO]** — Muestreo adaptativo no implementado
**[PROPUESTO]** — Detección de cambios visuales no implementada
**[PROPUESTO]** — Priorización por audio no implementada
**[PROPUESTO]** — Deduplicación no implementada

**[PENDIENTE]** — Autorización para implementar
EOF