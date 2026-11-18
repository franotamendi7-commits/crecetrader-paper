# PROPUESTA DEL CHECKPOINT 2C

**Proyecto:** YouTubeTradingAgent
**Fecha:** 10 de noviembre de 2026
**Modelo verificado:** upstage/solar-mini4:free (Nous)
**Orquestador:** Hermes

---

## 1. OBJETIVOS

El CHECKPOINT 2C tiene como objetivo principal:

> Que YouTubeTradingAgent aprenda la metodología de Bitcoin Hoy / CreceTrader
> desde los 11 videos históricos pendientes, procesando cada video por completo
> (audio, transcripción, timestamps, frames, gráficos) y construyendo conocimiento
> acumulativo sobre tendencias, temporalidades, niveles, estructuras, operaciones
> y condiciones de no operación.

Objetivos específicos:
1. Procesar los 11 videos históricos pendientes (de más reciente a más antiguo).
2. Integrar audio, transcripción, timestamps y evidencia visual por video.
3. Actualizar la memoria operativa con conocimiento acumulado.
4. Comparar los videos y detectar cambios de metodología.
5. Validar que el sistema distingue `[DICHO]`, `[OBSERVADO]` e `[INFERIDO]`.

---

## 2. TAREAS

### 2.1 Procesamiento progresivo de videos

Orden cronológico descendente (más recientes primero):

| Orden | ID | Fecha |
|-------|----|-------|
| 1 | subONxt5iag | 10/11/2026 |
| 2 | rTtXDLq2kOQ | 09/11/2026 |
| 3 | o6n6UDNVtCk | 07/11/2026 |
| 4 | 0prmrS6nnRk | 06/11/2026 |
| 5-11 | (pendientes) | (por consultar RSS) |

**Criterio de aceptación:** Cada video procesado genera:
- Transcripción con timestamps
- Frames seleccionados
- Evidencia visual
- Análisis de instrumento/temporalidad
- Registro en memoria operativa

### 2.2 Integración multimodal

Para cada video:
- Audio extraído (ffmpeg)
- Transcripción con timestamps (Whisper o alternativa gratuita)
- Frames clave extraídos (detección de cambios de escena)
- Análisis visual con qwen2.5vl:3b

**Criterio de aceptación:** Cada proceso se ejecuta sin depender de información futura.

### 2.3 Actualización de la memoria operativa

Para cada nuevo video:
- Extraer reglas metodológicas
- Identificar instrumentos ytemporalidades
- Registrar niveles y zonas
- Registrar contradicciones
- Actualizar la memoria operativa

**Criterio de aceptación:** Cada entrada guardada tiene:
- ID del video
- Título
- Fecha
- Timestamp
- Frame
- Evidencia textual o visual
- Clasificación epistemológica

### 2.4 Comparación entre videos

Usar `compare_videos()` para identificar:
- Entradas compartidas
- Cambios de metodología
- Contratrodicciones
- Evolución de niveles

**Criterio de aceptación:** La comparación es trazable a su evidencia.

---

## 3. ORDEN DE EJECUCIÓN

| Fase | Tarea | Entregable |
|------|-------|------------|
| 2C.1 | Auditar los 11 videos pendientes | `reports/checkpoint_2C_auditoria.md` |
| 2C.2 | Procesar el video más reciente | `experimental/results/historical/subONxt5iag_...md` |
| 2C.3 | Procesar los demás videos en orden | `experimental/results/historical/<id>_report.md` |
| 2C.4 | Actualizar memoria operativa | `memory/operativa/memory.json` actualizado |
| 2C.5 | Comparar videos y documentar cambios | `reports/checkpoint_2C_comparativas.md` |
| 2C.6 | Validar clasificación epistemológica | `reports/checkpoint_2C_validacion.md` |

---

## 4. CRITERIOS DE ACEPTACIÓN

| Criterio | Detalle |
|----------|---------|
| 1 | 11/11 videos procesados |
| 2 | Memoria consolidada sin duplicados |
| 3 | Trazabilidad de todas las entradas |
| 4 | Comparación entre videos documentada |
| 5 | Control de calidad: ≥80% de entradas con soporte ≥2 |
| 6 | Sistema distingue `[DICHO]`, `[OBSERVADO]`, `[INFERIDO]` |

---

## 5. RIESGOS

| Riesgo | Severidad | Mitigación |
|--------|-----------|------------|
| Instrumento/temporalidad no identificados en un video | Medio | Fallback con transcripción + OCR |
| Contradicciones sin resolver | Medio | Registrar como `[NO VERIFICADO]` |
| Entradas sin evidencia | Alto | No guardar, poner en estado `pendiente` |
| Tiempo de procesamiento: 5-10 minutos por video | Medio | Usar qwen2.5vl:3b (17.5s/frame aprox) |
| RAM: dos modelos no pueden cargar simultáneamente | Medio | Model manager con mutual exclusion |

---

## 6. RECURSOS NECESARIOS

| Recurso | Cantidad | Estado |
|-----------|----------|--------|
| qwen2.5vl:3b (Ollama) | 3.2GB | ✅ Instalado |
| RAM disponible | ~14GB | ✅ Suficiente |
| Espacio en disco | Versátil | ✅ Disponible |
| qwen3.5:9b-mlx (text) | 8.9GB | ✅ Instalado |
| API de vision remota | No | ❌ No requerida |

---

## 7. DEPENDENCIAS

| Dependencia | Estado |
|-------------|--------|
| Ollama | ✅ Disponible |
| qwen2.5vl:3b | ✅ Instalado |
| Model manager | ✅ Desarrollado |
| Comparación entre videos | ✅ Corregida |
| Memoria operativa | ✅ Creada |
| RSS de CreceTrader | ✅ Funciona |
| Biblioteca de video | ✅ Alta disponibilidad |

---

## 8. ESTIMACIÓN DE TIEMPO Y CONSUMO

| Tarea | Estimación |
|-------|------------|
| Procesar 1 video (audio + transcript + 69 frames) | ~20-30 min |
| Procesar 11 videos | ~4-6 horas |
| Actualizar memoria | ~1 hora |
| Comparar videos | ~30 min |
| Validar | ~1 hora |

**Consumo estimado de RAM:** Mínimo 6GB (mediante model manager).

---

## 9. ESTRATEGIA PARA PROCESAR LOS 11 VIDEOS

1. **Prioridad:** más recientes primero.
2. **Progreso:** se conserva en `historical_progress.json`.
3. **Duplicación:** se verifica antes de procesar.
4. **Reanudación:** si falla, se puede reanudar desde el último estado.
5. **Documentación:** cada video conserva su evidencia original.

---

## 10. ACCIONES POST-CHECKPOINT 2C

Tras completar el CHECKPOINT 2C:
- Validar YouTube Analyst (Fase 5)
- Construir Trading Agent y Risk Manager (Fase 6)
- Dashboard y Discord (Fase 7)

---

## RESUMEN

| Área | Estado |
|------|--------|
| Objetivos | [PROPUESTO] |
| Tareas | [PROPUESTO] |
| Orden de ejecución | [PROPUESTO] |
| Criterios de aceptación | [PROPUESTO] |
| Riesgos | [PROPUESTO] |
| Recursos | [VERIFICADO] |
| Dependencias | [VERIFICADO] |
| Tiempo estimado | [PROPUESTO] |
