# Marco de evaluación visual — YouTube Analyst

Fecha: 2026-11-16 · Aislado en `daily_pilot/vision_mission/`
Muestra: **15 capturas** de 3 vídeos (`dPHvRw1wzYQ`, `XLgPycsN0ls`, `s3KxjqkzwKM`). Registro: `muestra_capturas.json`. Capturas: `capturas/`.

## 1. Motor de inferencia (BLOQUEADO)

No hay motor autorizado:
- **Mac**: prohibido (arquitectura).
- **Kaggle CPU**: 5-10 min/imagen → no operativo.
- **Servicios externos**: requieren autorización expresa.
- El script `evaluar_capturas.py` está preparado pero **no se ejecuta** sin autorización.

## 2. Rúbrica por captura (0-4 por campo)

| Campo | 0 | 1 | 2 | 3 | 4 |
|---|---|---|---|---|---|
| Instrumento | no legible | dudoso | parcial | correcto | correcto + mercado |
| Temporalidad | no legible | dudosa | parcial | correcta | correcta + confirmación |
| Estructura | no legible | dudosa | parcial | correcta | correcta + contexto |
| Niveles | no legibles | 1 legible | varios | varios + etiqueta | todos los etiquetados |
| Fibonacci | no visible | dudoso | parcial | niveles visibles | origen + niveles + objetivo |
| Liquidez | no visible | dudosa | parcial | zonas visibles | zonas + evidencia |
| Abstención | no se abstiene | — | — | se abstiene | se abstiene con motivo |

## 3. Estados por captura

`CONFIRMADO` · `PARCIAL` · `NO CONFIRMADO` · `INCORRECTO`

## 4. Correlación transcripción ↔ imagen

| Resultado | Criterio |
|---|---|
| COINCIDENCIA CONFIRMADA | el nivel dicho aparece legible en la captura |
| COINCIDENCIA PARCIAL | aparece el número pero sin contexto o con distinta temporalidad |
| NO CONFIRMADA | el número no aparece en la captura |
| DISCREPANCIA | la captura contradice lo dicho (instrumento/temporalidad distintos) |

## 5. Procedencias (contrato v1.1)

`A` explícito · `B` observado · `C` cálculo · `D` propuesta. Cada valor registrado con su procedencia.

## 6. Métricas (cuando se ejecute)

- acierto de instrumento / temporalidad / niveles / estructura / fibonacci
- correlación con la transcripción
- tasa de invención
- abstenciones correctas
- tiempo por captura

## 7. Alternativas investigadas (2026-11-16)

| Alternativa | Licencia | Coste | Requisito | Rendimiento | Nota |
|---|---|---|---|---|---|
| Qwen2.5-VL-3B-Instruct | Qwen (verificar) | 0 | T4 16 GB | ~7 GB VRAM; 10-15 s/imagen en T4 | OCRBench 864; CPU 5-10 min/imagen |
| Qwen2.5-VL-7B-Instruct | apache-2.0 | 0 | T4 (ajustado) | mejor | justo en T4 |
| AgentFinVQA (VectorInstitute) | verificar (GitHub) | 0 | VLM backend | pipeline Plan→OCR→Verify | trazabilidad + anti-alucinación |
| ChartMuseum / FinChart-Bench | verificar | 0 | — | benchmark 1.200 gráficos | evaluación de referencia |
| Kaggle GPU T4 x2 | — | 0 | 30 h/sem, 12 h/sesión | sí | la sonda inicial recibió CPU; se reintenta con `machine_shape: gpu` |
| Colab T4 | — | 0 | variable | sí | sin garantía de GPU |

## 8. Recomendación

Condicionada a autorización. Ver informe final.
