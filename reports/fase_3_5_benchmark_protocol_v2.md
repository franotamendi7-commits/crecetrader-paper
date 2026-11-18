# FASE 3.5 — Protocolo de Benchmark v2

## 1. Preguntas (10 por imagen)

1. ¿Qué instrumento aparece en el gráfico?
2. ¿Se puede identificar la temporalidad?
3. ¿Se observan velas japonesas?
4. ¿Qué indicadores son claramente visibles?
5. ¿Hay líneas horizontales?
6. ¿Se identifica un soporte o una resistencia?
7. ¿Qué valores de precio pueden leerse con confianza?
8. ¿La escala del gráfico es legible?
9. ¿Hay suficiente evidencia para interpretar la estructura?
10. ¿Qué información no puede determinarse?

## 2. Rúbrica de evaluación

### Lectura de precios
- **Exacta:** coincide con el valor legible y su formato normalizado
- **Parcial:** identifica una parte del valor sin afirmar lectura completa
- **Incorrecta:** valor distinto
- **Alucinación:** inventa un valor o presenta como legible uno que no lo es

### Soportes y resistencias
- Exigir evidencia visual identificable
- No aceptar respuesta basada únicamente en audio
- Diferenciar línea visible de interpretación confirmada

### Indicadores y velas
- No aceptar indicadores/patrones que no se distingan visualmente
- Registrar limitaciones de resolución

### Temporalidad
- Aceptar "no determinable" cuando la imagen no aporte evidencia suficiente
- Distinguir temporalidad del gráfico de horizonte del escenario

## 3. Métricas

| Métrica | Fórmula | Denominador |
|---------|---------|-------------|
| Exactitud por categoría | Aciertos / Total aplicable | Preguntas aplicables |
| Exactitud de instrumentos | Aciertos / Total | Imágenes con instrumento visible |
| Exactitud de temporalidad | Aciertos / Total | Imágenes con temporalidad visible |
| Precisión de precios | Exactos / Total legible | Precios legibles |
| Tasa de alucinaciones | Alucinaciones / Total | Todas las respuestas |
| Tasa de abstención | Abstenciones / Total | Todas las respuestas |
| Latencia | Tiempo por imagen | Segundos |
| Memoria | RAM máxima | GB |

## 4. Umbrales propuestos

- Exactitud de instrumentos: ≥ 70%
- Exactitud de temporalidad: ≥ 50% (muchas imágenes no muestran temporalidad)
- Precisión de precios: ≥ 80% (precios exactos requieren alto estándar)
- Tasa de alucinaciones: ≤ 10%
- Tasa de abstención: ≥ 20% (capacidad de reconocer ilegible)

## 5. Procedimiento reproducible

1. Registrar versiones de modelos, dependencias, parámetros
2. Guardar logs de ejecución
3. Guardar resultados en JSON estructurado
4. Permitir re-ejecución con los mismos datos
5. No mezclar preguntas no aplicables con errores

## 6. Estado

**[PROPUESTO]** — Protocolo diseñado, no ejecutado
**[PROPUESTO]** — Métricas definidas
**[PENDIENTE]** — Autorización para ejecutar
EOF