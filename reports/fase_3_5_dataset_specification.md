# FASE 3.5 — Especificación del Dataset

## 1. Inventario de imágenes

- 17 frames existentes (scene_0 a scene_16)
- 1 frame por escena detectada
- Resolución: frames de video completo (no verificada exactamente)
- 9 frames con texto OCR, 8 sin texto
- 7 niveles ilegibles (scene_15)

## 2. Tamaño real de muestra

- **17 imágenes**, no 170 preguntas
- 10 preguntas por imagen = dimensiones de evaluación
- No son muestras independientes

## 3. Metadatos

Cada imagen debe tener:
- ID (scene_XXX)
- Timestamp
- Escena de origen
- Contenido visible (OCR)
- Instrumento (si identificable)
- Temporalidad (si identificable)

## 4. Reglas de inclusión y exclusión

**Incluir:** Todos los 17 frames existentes
**Excluir:** Ninguno (todos son relevantes para evaluación)
**Casos negativos:** scene_0 (intro), scene_8 (promoción), scene_13 (calendario)
**Casos ambiguos:** scene_15 (precios ilegibles), scene_3 (cobertura insuficiente)

## 5. Limitaciones

- Solo 1 video
- 17 frames con cobertura insuficiente
- Sin anotación manual independiente
- 7 niveles ilegibles
- Sin casos de gráficos de alta calidad

**[VERIFICADO]** — Dataset especificado
**[PENDIENTE]** — Anotación manual
EOF