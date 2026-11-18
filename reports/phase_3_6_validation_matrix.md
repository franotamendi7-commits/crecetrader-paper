# FASE 3.6 — MATRIZ DE VALIDACIÓN

## Matriz de evaluación

| # | Criterio | Resultado | Evidencia | Estado |
|---|----------|-----------|-----------|--------|
| 1 | Trazabilidad completa de cada frame | 19 frames con ID, imagen, timestamp, tipo de escena | vision_analysis_canonical.json | APROBADO |
| 2 | Asociación temporal audio-imagen | Timestamps de escena vinculados a transcripción | structured_scenes.json | PARCIAL |
| 3 | Identificación de instrumento | BTC/USD identificado en 14/14 gráficos OK | vision_analysis.json | PARCIAL |
| 4 | Identificación de temporalidad | Weekly, Daily, 4H, 1H identificados correctamente | vision_analysis.json | PARCIAL |
| 5 | Separación datos observados/inferencias | No implementado sistemáticamente | — | PENDIENTE |
| 6 | Ausencia de alucinaciones críticas | Confusión de instrumentos detectada (BTC→oro/petróleo) | vision_analysis.json | NO APROBADO |
| 7 | Validación de precios con fuente compatible | No implementado | — | PENDIENTE |
| 8 | Gestión de incertidumbre | Parcial — modelo a veces dice "no puedo determinar" | vision_analysis.json | PARCIAL |
| 9 | Consistencia entre reportes | Reconciliado — 14 OK / 5 ERR canónico | phase_3_6_frame_reconciliation.md | APROBADO |
| 10 | Rendimiento razonable | 4.6 min/frame promedio, 26% timeout | vision_analysis.json | NO APROBADO |
| 11 | Reproducibilidad | No verificada — solo una ejecución completa | — | PENDIENTE |

## Errores críticos detectados

### E1. Confusión de instrumentos [CRÍTICO]
- **Frame**: Múltiples
- **Error**: Modelo identifica BTCUSD como "petróleo u oro" en algunos frames
- **Causa**: El audio menciona oro mientras el gráfico muestra BTC
- **Impacto**: El modelo fusiona audio e imagen en lugar de distinguirlas
- **Estado**: NO RESUELTO

### E2. CME Futures vs BTC Spot [CRÍTICO]
- **Frame**: Múltiples
- **Error**: El audio menciona futuros CME pero el gráfico muestra BTCUSD spot
- **Causa**: No hay distinción entre instrumento mencionado y visible
- **Impacto**: Validación de precios incorrecta si se usa OHLCV spot para niveles CME
- **Estado**: NO RESUELTO

### E3. OCR no funcional [CRÍTICO]
- **Frame**: Todos
- **Error**: Tesseract retorna texto vacío en todos los frames
- **Causa**: Desconocida — puede ser preprocesamiento, configuración o motor
- **Impacto**: No se pueden extraer precios visibles automáticamente
- **Estado**: NO RESUELTO

### E4. Timeouts persistentes [ALTO]
- **Frame**: 1, 2, 6, 12, 16
- **Error**: 5 frames (26%) fallan por timeout incluso con 600s
- **Causa**: Gráficos complejos con muchos niveles
- **Impacto**: 26% de los frames no tienen análisis visual
- **Estado**: NO RESUELTO

### E5. Fechas inventadas [MEDIO]
- **Frame**: Escenas con calendario macro
- **Error**: El modelo inventa fechas de eventos macroeconómicos
- **Causa**: El modelo intenta completar información ausente
- **Impacto**: Datos incorrectos en el análisis
- **Estado**: NO RESUELTO

## Qué puede interpretar correctamente hoy
- [VERIFICADO] Instrumento: BTC/USD en gráficos (14/14 frames OK)
- [VERIFICADO] Temporalidad: Weekly, Daily, 4H, 1H (identificadas correctamente)
- [VERIFICADO] Estructura de mercado: Tendencias, soportes, resistencias
- [VERIFICADO] Niveles de precio: Extrae valores visibles (87826, 81830, etc.)
- [VERIFICADO] Detección de no-gráficos: Identifica desktop, páginas web, personas

## Qué NO puede interpretar de manera confiable
- [NO VERIFICADO] Distinguir audio de imagen (confunde BTC con oro/petróleo)
- [NO VERIFICADO] Distinguir CME futures de BTC spot
- [NO VERIFICADO] Extraer texto con OCR (no funcional)
- [NO VERIFICADO] Procesar gráficos complejos (26% timeout)
- [NO VERIFICADO] Validar niveles con datos de mercado (no implementado)
- [NO VERIFICADO] Generar clasificación [DICHO]/[OBSERVADO]/[INFERIDO]/[NO VERIFICADO] sistemáticamente

## Recomendación
**NO APROBAR FASE 3.6** — El YouTube Analyst no está listo para la siguiente fase.

Razones:
1. 26% de frames no procesados (5/19 timeout)
2. Confusión crítica de instrumentos (BTC→oro/petróleo)
3. OCR no funcional
4. No hay validación de precios con datos de mercado
5. No hay clasificación sistemática de evidencia