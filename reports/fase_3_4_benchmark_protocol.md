# FASE 3.4 — Protocolo de Benchmark

## 1. Diseño del experimento

### 1.1 Mismo video, mismas imágenes, mismas preguntas
- Usar el mismo video (rTtXDLq2kOQ)
- Usar los mismos frames (17 existentes + nuevos con muestreo adaptativo)
- Usar las mismas 10 preguntas por imagen

### 1.2 Modelos a comparar
- Moondream 2 (principal)
- Qwen2.5-VL-3B (alternativa)
- Tesseract (baseline actual)

### 1.3 Métricas separadas

| Métrica | Qué mide | Estándar |
|---------|----------|----------|
| Identificación de instrumento | Aciertos sobre instrumentos visibles | Exacto |
| Temporalidad | Identificación correcta de timeframe | Exacto |
| OCR de precios | Valores exactos vs ground truth | Exacto |
| Indicadores | Reconocimiento correcto | Exacto |
| Velas | Identificación de estructuras | Exacto |
| Líneas y zonas | Detección de elementos gráficos | Exacto |
| Soportes/resistencias | Identificación con evidencia | Exacto |
| Alucinaciones | Afirmaciones sin respaldo visual | Conteo |
| Abstención | Capacidad de reconocer ilegible | Conteo |
| Latencia | Tiempo por imagen | Segundos |
| Memoria | RAM máxima durante inferencia | GB |
| Estabilidad | Errores, bloqueos | Conteo |

### 1.4 Criterios de aceptación

1. El modelo se ejecuta localmente sin errores
2. El consumo de RAM se mide y documenta
3. Los precios exactos tienen estándar superior a descripción general
4. Un modelo que inventa niveles NO es aceptable
5. La abstención (decir "no sé") es un resultado válido

### 1.5 Reproducibilidad

- Registrar versiones de modelos, dependencias, parámetros
- Guardar logs de ejecución
- Guardar resultados en formato JSON estructurado
- Permitir re-ejecución con los mismos datos

## 2. Estado

**[PROPUESTO]** — Protocolo diseñado, no ejecutado
**[PROPUESTO]** — Métricas definidas
**[PENDIENTE]** — Autorización para ejecutar
EOF