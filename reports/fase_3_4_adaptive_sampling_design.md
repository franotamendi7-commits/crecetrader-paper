# FASE 3.4 — Diseño de Muestreo Adaptativo

## 1. Estrategia propuesta

### 1.1 Muestreo temporal base
- Extraer 1 frame cada 30 segundos en escenas > 60s
- Extraer 1 frame en el centro de escenas < 60s

### 1.2 Detección de cambios visuales
- Usar histograma de color (HSV) para detectar cambios significativos
- Umbral: diferencia > 0.3 en histograma normalizado
- NO asumir que histograma identifica cambios de gráfico (solo cambios visuales)

### 1.3 Priorización por audio
- Extraer frames en momentos donde la transcripción menciona:
  - Niveles de precio (regex de números)
  - Instrumentos (BTC, ETH, Oro, S&P, NASDAQ)
  - Temporalidades (semanal, diario, 4H, intradía)
  - Escenarios (alcista, bajista, lateral)

### 1.4 Deduplicación perceptual
- Calcular hash perceptual (pHash) de cada frame
- Eliminar frames con hamming distance < 5
- Mantener el frame con mayor calidad (nitidez)

### 1.5 Límites
- Máximo 5 frames por escena larga
- Máximo 40 frames por video
- Mínimo 1 frame por escena

## 2. Metadatos por frame

Cada frame debe conservar:
- Timestamp del video
- Escena de origen
- Segmento de audio relacionado (si existe)
- Motivo de selección
- Hash perceptual
- Estado de validación

## 3. Estado

**[PROPUESTO]** — No implementado
**[PROPUESTO]** — Pseudocódigo incluido
**[PENDIENTE]** — Autorización para implementar
EOF