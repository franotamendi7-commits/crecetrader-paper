# FASE 3.5 — Informe Final

## 1. Dictamen técnico

**[APTO CON LIMITACIONES]**

La fase completó la preparación del benchmark visual: protocolo corregido, dataset especificado, anotación guide creada, compatibilidad de Qwen3.5 verificada, y aislamiento auditado. El ground truth independiente NO existe aún.

## 2. Alcance autorizado

- Auditoría READ-ONLY del estado actual
- Creación/modificación de documentación dentro del proyecto
- Preparación de materiales de anotación
- Prueba mínima de compatibilidad de entrada de imágenes con Qwen3.5

## 3. Resultados

### 3.1 Compatibilidad de Qwen3.5
**[VERIFICADO]** — Qwen3.5:9b-mlx acepta imágenes y devuelve descripciones.
- Modelo: qwen3.5:9b-mlx (9.4B params, nvfp4, 8.9GB)
- Capacidad declarada: vision ✅
- Prueba: imagen scene_004_303.7s.jpg enviada via API
- Respuesta: descripción de gráfico técnico con velas, anotaciones en español
- Tiempo: ~180s (timeout anterior, respuesta en segunda prueba)
- Sin modificar Ollama

### 3.2 Discrepancia de transcripción
**[VERIFICADO]** — 145 segmentos (vigente) vs 192 (FASE 2)
- Diferencia por configuración de faster-whisper
- No hay pérdida de datos
- Transcripción de 145 es completa (0.0s a 897.52s)

### 3.3 Ground truth
**[PENDIENTE]** — No existe ground truth independiente
- Se preparó guía de anotación
- Se diseñó procedimiento de doble anotación
- Se identificaron los 17 frames y 10 preguntas
- Requiere intervención humana

### 3.4 Aislamiento
**[VERIFICADO]** — No se modificaron archivos originales
- No se instaló ningún modelo
- No se modificó Ollama
- No se ejecutó benchmark

## 4. Limitaciones y bloqueos

1. **Ground truth no existe** — Requiere anotación humana independiente
2. **Solo 1 video** — No se puede generalizar
3. **17 frames con cobertura insuficiente** — Muestreo adaptativo no implementado
4. **Qwen3.5 es lento** — ~180s por imagen (puede ser limitante)
5. **Sin comparación** — No se comparó con otros modelos

## 5. Hashes y evidencia

- qwen3.5:9b-mlx: ID 203e30078279, 8.9GB, nvfp4
- Frame de prueba: frames/scene_004_303.7s.jpg
- Respuesta obtenida: descripción de gráfico técnico

## 6. Riesgos residuales

1. Qwen3.5 puede ser demasiado lento para benchmark completo (17 frames × ~180s = ~51 min)
2. Sin ground truth, no se puede medir precisión
3. Solo 1 video, sin validación cruzada

## 7. Recomendación

**[APTO CON LIMITACIONES]**

La preparación está completa. Se recomienda:
1. Autorizar creación de ground truth (anotación humana)
2. Evaluar si Qwen3.5 es suficientemente rápido para el benchmark
3. Considerar Moondream 2 como alternativa más rápida

**La decisión de autorizar el benchmark corresponde exclusivamente a Francisco.**

---

**PRINCIPIO DE AUDITORÍA: NO CREER. PROBAR.**
EOF