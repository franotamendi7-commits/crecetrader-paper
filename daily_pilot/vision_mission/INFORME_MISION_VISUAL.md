# MISIÓN DE VALIDACIÓN VISUAL — INFORME

Fecha: 2026-11-16 · Aislado en `daily_pilot/vision_mission/` · `PAPER_ONLY=true`

## Estado de la misión

**BLOQUEADA en el núcleo (inferencia visual).** Se preparó toda la muestra, el marco de evaluación y el evaluador; **no se ejecutó ninguna inferencia** porque no existe un motor autorizado y las restricciones lo impiden. No se declara éxito ni aprobación.

## 0. Precondiciones

- Trabajos anteriores: **finalizados** (consolidación Analyst/Manager/Dashboard).
- Dashboard: `daily_pilot/dashboard/index.html` (archivo estático, verificado). **No está servido en localhost**; no levanté servicios. Servicios existentes observados: 5002/5003/5004/8765/11434 (intactos, no tocados).
- Scheduler y LaunchAgent de Harness: **no interrumpidos**.

## 1. Muestra preparada (sin procesar vídeos)

**15 capturas** de 3 vídeos, reutilizando frames y transcripciones existentes. Registro: `vision_mission/muestra_capturas.json`; copias en `vision_mission/capturas/`.

| Vídeo | Motivo de elección | Capturas |
|---|---|---|
| `dPHvRw1wzYQ` | tendencia y niveles (W/D/4H muy citados) | 5 |
| `XLgPycsN0ls` | multi-instrumento y escenarios (BTC/ETH/oro/SPX/NQ) | 5 |
| `s3KxjqkzwKM` | varias temporalidades + niveles citados (76.627, 83.366) | 5 |

Los niveles citados asociados a cada captura están en el registro. **Ninguna captura es redundante** entre vídeos; dentro de cada vídeo se cubren tramos distintos.

## 2. Resultados por captura

**NO DISPONIBLES** — no se ejecutó inferencia.

## 3. Comparación transcripción ↔ imagen

**NO DISPONIBLE** — requiere la lectura visual.

## 4. Métricas

**NO DISPONIBLES.** El marco de rúbrica (0-4 por campo) está listo en `MARCO_EVALUACION.md`.

## 5. Tecnologías investigadas (evidencia 2026-11-16)

| Alternativa | Licencia | Coste | Requisito | Rendimiento | Verificado |
|---|---|---|---|---|---|
| Qwen2.5-VL-3B-Instruct | Qwen (verificar) | 0 | T4 16 GB | ~7 GB VRAM; OCRBench 864 | sí (ficha HF) |
| Qwen2.5-VL-7B-Instruct | apache-2.0 | 0 | T4 ajustado | mejor | sí (ficha HF) |
| AgentFinVQA (VectorInstitute/GitHub) | verificar | 0 | backend VLM | Plan→OCR→Verify con traza | documentado, no ejecutado |
| ChartMuseum / FinChart-Bench | verificar | 0 | — | benchmark 1.200 gráficos reales | documentado |
| Kaggle GPU | — | 0 | T4 x2, 30 h/sem, 12 h/sesión | **no asignado** | **probado: CPU** |
| Colab T4 | — | 0 | variable | sí | documentado |
| OCR local en Mac | — | 0 | — | — | **prohibido por arquitectura** |

**Kaggle probado dos veces**: con y sin `machine_shape: gpu` → `torch 2.11.0+cpu`, `CUDA: False`. No asigna GPU.

## 6. Modelos probados

**Ninguno.** Bloqueado por autorización.

## 7. Costes y requisitos

- Sin coste en ningún escenario propuesto.
- Cuota Kaggle: 30 h/semana de GPU; 12 h por sesión.
- Colab: sin garantía de GPU.
- El Mac queda fuera de la inferencia.

## 8. Mejoras implementadas

- Muestra estructurada con timestamps y niveles citados.
- Marco de evaluación con rúbrica, estados y métricas.
- Evaluador listo (`evaluar_capturas.py`), bloqueado por defecto.

## 9. Limitaciones pendientes

1. **Sin motor de visión autorizado** → la misión no puede completar su objetivo.
2. Sin verificación visual, B4 sigue pendiente (faltan anotadores).
3. Sin feed OHLCV para contrastar niveles.

## 10. Recomendación

**NO APROBADO / INCONCLUSO (bloqueado).** No se puede afirmar que el YouTube Analyst interpreta correctamente los gráficos: **no se ha ejecutado ninguna prueba visual**. Cualquier afirmación de funcionamiento sería falsa.

### Desbloqueo concreto (requiere autorización expresa)

| Opción | Qué autoriza | Coste | Riesgo/condición |
|---|---|---|---|
| A. Colab T4 | transferir las **15 capturas** y ejecutar Qwen2.5-VL-3B | 0 USD | servicio externo; dataset/carpeta temporal; borrar después |
| B. Kaggle con GPU | reintentar con T4 | 0 USD | hoy no asigna GPU |
| C. Proveedor auxiliar de Hermes (Nous) | analizar las 15 capturas | 0 USD | servicio externo; no Gemini |
| D. Ollama en el Mac (puntual) | ejecutar 15 capturas en local | 0 USD | **viola la arquitectura**; solo con autorización explícita |

Se recomienda **A** (Colab T4) por rendimiento documentado (~7 GB VRAM, 10-15 s/imagen). Se necesitaría: dataset/carpeta temporal, ejecución por lotes, descarga de resultados y borrado.

## 11. Confirmaciones

- No se transfirió material del proyecto a ningún servicio externo.
- No se ejecutó inferencia audiovisual en el Mac.
- No se modificó producción, modelos, proveedores, skills ni configuración.
- Scheduler y LaunchAgent de Harness intactos.

**NO CREER. PROBAR.** Quedo a la espera de la autorización para la opción elegida.
