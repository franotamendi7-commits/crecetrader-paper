# FASE 3.6 — BENCHMARK DE MODELOS

## Modelos disponibles actualmente

| Modelo | Backend | Visión | RAM | Estado |
|--------|---------|--------|-----|--------|
| qwen3.5:9b-mlx | Ollama/MLX | Sí | ~1.7 GB | Instalado y funcional |
| qwen2.5:1.5b | Ollama | No (texto) | ~1 GB | Instalado (usado por JARVIS) |

## Modelos NO disponibles (requieren autorización para instalar)

| Modelo | Backend | Visión | RAM estimada | Notas |
|--------|---------|--------|--------------|-------|
| Qwen3-VL | Ollama/MLX | Sí (especializado) | ~4-8 GB | Especialista visual, requiere descarga |
| LLaVA | Ollama | Sí | ~4-7 GB | Alternativa visual |
| Moondream | Ollama | Sí | ~1.5 GB | Ligero, menos preciso |

## Investigación de Qwen3-VL

### Requisitos
- **RAM**: ~4-8 GB para 7B-9B (dependiendo de cuantización)
- **Backend**: Ollama con soporte MLX en macOS
- **Compatibilidad**: macOS M4, Apple Silicon
- **Costo**: Gratuito (open-source)
- **Velocidad estimada**: 1-3 min por imagen (vs 4.6 min de Qwen3.5)

### Ventajas potenciales
- Especializado en visión (mejor identificación de instrumentos)
- Mejor lectura de niveles de precio
- Menos alucinaciones visuales
- Mejor distinción de temporalidades

### Desventajas
- Requiere descarga (~4-8 GB)
- No probado en este hardware
- Puede tener los mismos problemas de timeout en gráficos complejos

## Benchmark propuesto (NO ejecutado — requiere autorización)

### Frames seleccionados para benchmark
| Frame | Tipo | Complejidad |
|-------|------|-------------|
| 17 | Gráfico Weekly BTC | Alta |
| 9 | Gráfico Daily BTC | Media |
| 18 | Gráfico 4H BTC | Baja |
| 7 | Página web (no gráfico) | N/A |
| 0 | Escritorio/terminal (no gráfico) | N/A |

### Criterios de evaluación
1. Detección correcta de gráficos (sí/no)
2. Identificación de instrumento (correcto/incorrecto)
3. Identificación de temporalidad (correcta/incorrecta)
4. Lectura de niveles (cantidad correcta)
5. Identificación de estructura de mercado (correcta/incorrecta)
6. Detección de contradicciones audio-imagen (sí/no)
7. Alucinaciones (cantidad)
8. Capacidad de expresar incertidumbre (sí/no)
9. Tiempo real por imagen (segundos)
10. Consumo máximo de memoria (MB)

### Arquitectura secuencial propuesta
1. Cargar Qwen3.5:9b-mlx → procesar frames → guardar resultados → descargar modelo
2. Verificar liberación de memoria
3. Cargar Qwen3-VL → procesar mismos frames → guardar resultados → descargar modelo
4. Comparar resultados

### Decisión pendiente
**NO se ha instalado ni probado Qwen3-VL.** Se requiere autorización del usuario para:
- Descargar el modelo (~4-8 GB)
- Instalar dependencias adicionales
- Ejecutar el benchmark

### Recomendación preliminar
Basado en la evidencia actual:
- Qwen3.5:9b-mlx **funciona** para gráficos simples (74% éxito)
- Los problemas principales son **timeouts** y **confusión de instrumentos**, no la capacidad visual del modelo
- Antes de instalar Qwen3-VL, se debería:
  1. Optimizar el preprocesamiento de imágenes (resize, crop)
  2. Mejorar los prompts (separación audio/imagen)
  3. Implementar OCR funcional
- Si después de optimizar sigue habiendo problemas de identificación de instrumentos, entonces considerar Qwen3-VL

## Conclusión
El benchmark no se ha ejecutado. Se requiere autorización para instalar Qwen3-VL. La recomendación es optimizar primero el pipeline actual con Qwen3.5 antes de agregar un segundo modelo.