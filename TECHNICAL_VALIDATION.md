# TECHNICAL VALIDATION — FASE 1

## Fecha: 2026-11-09

## 1. HERRAMIENTAS RECOMENDADAS

### Stack validado (100% gratuito, open source)

| Componente | Herramienta | Licencia | Coste | Estado |
|---|---|---|---|---|
| Descarga video/audio | yt-dlp | Unlicense | $0 | [VERIFICADO] disponible via pip |
| Procesamiento multimedia | ffmpeg | LGPL/GPL | $0 | [VERIFICADO] instalado |
| Transcripción | faster-whisper (small) | MIT | $0 | [PROPUESTO] |
| Detección de escenas | PySceneDetect | BSD 3-Clause | $0 | [PROPUESTO] |
| Análisis estructural charts | chart-vision-mcp | MIT | $0 | [PROPUESTO] |
| OCR | Tesseract | Apache 2.0 | $0 | [PROPUESTO] |
| Visión semántica | Moondream 2 / Qwen2.5-VL | Apache 2.0 | $0 | [PROPUESTO] |
| Reconstrucción gráficos | Lightweight Charts | Apache 2.0 | $0 | [PROPUESTO] |
| Indicadores | pandas-ta | MIT | $0 | [PROPUESTO] |
| Orquestación | Scripts Python | — | $0 | [PROPUESTO] |

## 2. MODELOS GRATUITOS EVALUADOS

### Vision local (Apple Silicon)

| Modelo | RAM | Coste | Open source | Compatibilidad Mac | Evaluación |
|---|---|---|---|---|---|
| Moondream 2 | 2-4 GB | $0 | Apache 2.0 | Buena | [PROPUESTO] — ligero, ideal para Mac |
| Qwen2.5-VL 7B | 8-16 GB | $0 | Apache 2.0 | Parcial (CPU) | [PROPUESTO] — más capaz pero pesado |
| LLaVA 7B | 8-16 GB | $0 | Apache 2.0 | Parcial (CPU) | [PROPUESTO] — alternativa |
| BLIP-2 | 4-8 GB | $0 | BSD | Buena | [PROPUESTO] — OCR + captioning |

### Modelos de transcripción

| Modelo | RAM | Coste | Idiomas | Evaluación |
|---|---|---|---|---|
| faster-whisper (small) | 1-2 GB | $0 | Multilingüe (incl. español) | [PROPUESTO] |
| faster-whisper (medium) | 2-4 GB | $0 | Multilingüe (mejor español) | [PROPUESTO] |
| whisper.cpp | 1-4 GB | $0 | Multilingüe | [PROPUESTO] (alternativa) |

## 3. ARQUITECTURA HÍBRIDA DE VISIÓN

Basado en hallazgo de roman-rr/trading-skills:

### A. ANÁLISIS ESTRUCTURAL (chart-vision-mcp)
- Velas (colores, tamaño)
- OHLC (niveles)
- Tendencias (máximos/mínimos)
- Indicadores (líneas)
- Volumen (barras)
- Escalas y temporalidades

### B. OCR Y EXTRACCIÓN VISUAL (Tesseract)
- Precios
- Nombres de instrumentos
- Temporalidades
- Indicadores y parámetros
- Anotaciones
- Niveles visibles

### C. INTERPRETACIÓN SEMÁNTICA (Moondream/Qwen2.5-VL)
- Relacionar lo hablado con lo mostrado
- Comprender el escenario del analista
- Detectar condiciones e invalidaciones
- Comparar cambios de criterio

### D. VALIDACIÓN
- Contrastar interpretación con datos reales
- Registrar errores
- No inventar valores
- Clasificar: [DICHO], [OBSERVADO], [INFERIDO]

## 4. ALTERNATIVAS DE TRADINGVIEW

| Plataforma | Licencia | Coste | Función | Recomendación |
|---|---|---|---|---|
| TradingView (free) | Propietario | $0 | Referencia visual | Usar solo para referencia |
| Lightweight Charts | Apache 2.0 | $0 | Gráficos OHLCV interactivos | ADOPTAR |
| Plotly | MIT | $0 | Gráficos interactivos | Alternativa |
| mplfinance | BSD | $0 | Gráficos estáticos | Alternativa simple |
| pandas-ta | MIT | $0 | 100+ indicadores | ADOPTAR |

## 5. APIs DE MERCADO GRATUITAS

Ver FREE_APIS.md para detalle completo.

**Recomendación principal:** Kraken (crypto) + Yahoo Finance (stocks/ETFs/indices)

## 6. RIESGOS Y LIMITACIONES

| Riesgo | Severidad | Mitigación |
|---|---|---|
| Vision LLMs no confiables para charts | Alto | Arquitectura híbrida (estructural + semántico) |
| Transcripción en español puede tener errores | Medio | Probar con modelo medium, validar manualmente |
| yt-dlp puede romperse con cambios de YouTube | Medio | Actualizar frecuentemente, tener alternativas |
| Free tiers de APIs pueden cambiar | Medio | No depender de un solo proveedor |
| Modelos locales lentos en CPU | Medio | Usar modelos pequeños, procesamiento secuencial |
| Reconstrucción de gráficos sin repo específico | Alto | Investigar más en Fase 1 |

## 7. CLASIFICACIÓN

- [VERIFICADO]: ffmpeg instalado, Ollama disponible, Kraken API accesible
- [PROPUESTO]: Stack completo (requiere validación en Fase 1)
- [PENDIENTE]: Pruebas de transcripción en español, vision de gráficos, chart-vision-mcp
