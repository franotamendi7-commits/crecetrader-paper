# FASE 3.4 — Diseño del Dataset Experimental

## 1. Muestras del video existente

### Frames existentes (17)
- scene_0 a scene_16, 1 frame por escena
- 9 frames con texto OCR, 8 sin texto
- 7 niveles ilegibles (scene_15)

### Momentos representativos para evaluación

| Momento | Timestamp | Frame | Contenido | Instrumento | Temporalidad |
|---------|-----------|-------|-----------|-------------|--------------|
| 1 | 305.5s | scene_5 | "Fase de Acumulación", zona 72.554-69.000 | BTC | Diario |
| 2 | 106.2s | scene_4 | "BITCOIN, Serie semanal" | BTC | Semanal |
| 3 | 317.9s | scene_5 | "83.366, 71.509, 69.000" | BTC CME | Semanal |
| 4 | 481.2s | scene_12 | "74.761 eje central" | BTC | Intradía |
| 5 | 558.3s | scene_10 | "ETHEREUM, 2.077" | ETH | Semanal |
| 6 | 682.6s | scene_14 | "3.906" (Oro) | Oro | Mediano |
| 7 | 757.2s | scene_16 | "7.139, 6.544" (S&P) | S&P | Corrección |
| 8 | 765.3s | scene_16 | "25.400, 25.479, 28.000" (NASDAQ) | NASDAQ | Largo |

### Casos negativos (sin gráfico)
- scene_0: Intro del video
- scene_8: Promoción de curso (475€)
- scene_13: Calendario macroeconómico

### Casos ambiguos
- scene_15: Precios ilegibles (4.400, 4340, 3906, 3472)
- scene_3: 293.7s con 1 frame (cobertura insuficiente)

## 2. Preguntas de evaluación (por imagen)

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

## 3. Ground truth

**[PENDIENTE]** — No existe ground truth independiente.
**[PROPUESTO]** — Crear anotación manual de los 17 frames existentes con respuestas a las 10 preguntas.
**[PROPUESTO]** — Usar la transcripción como referencia verbal, no como ground truth visual.

## 4. Limitaciones del dataset

- Solo 1 video
- 17 frames con cobertura insuficiente
- Sin anotación manual independiente
- 7 niveles ilegibles
- Sin casos de gráficos de alta calidad (resolución baja)

**[VERIFICADO]** — Dataset evaluado
**[PROPUESTO]** — Anotación manual necesaria
**[PENDIENTE]** — Autorización para crear ground truth
EOF