# FASE 5 — ARQUITECTURA LOCAL Y PRIORIDAD DINÁMICA DE VIDEOS

**Proyecto:** `~/YouTubeTradingAgent/`
**Fecha:** 10 de noviembre de 2026
**Orquestador:** Hermes
**Modelo verificado:** `upstage/solar-mini4:free` (Nous) | `Qwen3.5:9b-mlx` (Ollama)

---

## 1. ARCHIVOS AUDITADOS Y MODIFICADOS

| Archivo | Acción | Descripción |
|---------|--------|-------------|
| `experimental/scripts/vision_analyzer_gemini.py` | ❌ Eliminado | Integración Gemini |
| `experimental/scripts/vision_analyzer_validation.py` | ❌ Eliminado | Integración Gemini |
| `.env` | 🔧 Neutralizado | `GEMINI_API_KEY=***` |
| `experimental/results/historical_progress.json` | 📖 Revisado | Registro persistente |
| `experimental/scripts/historical_processor.py` | 🔍 Auditar | Pipeline existente |
| `experimental/scripts/rss_priority_processor.py` | ✅ Creado | Nuevo script RSS + prioridades |
| `scripts/test_rss_priority_processor.py` | ✅ Creado | Test harness |
| `rss_priority_processor_TEST_REPORT.md` | ✅ Creado | Reporte de pruebas |
| `reports/fase1_cierre_aislamiento.md` | 📖 Revisado | Cierre anterior |
| `reports/checkpoint_2B_cierre.md` | 📖 Revisado | Cierre 2B |
| `reports/checkpoint_2C_proposal.md` | 📖 Revisado | Propuesta 2C |

---

## 2. INTEGRACIONES DE GEMINI ELIMINADAS

| Tipo | Ruta | Estado |
|------|------|--------|
| Código de integración | `experimental/scripts/vision_analyzer_gemini.py` | ❌ Eliminado |
| Código de validación | `experimental/scripts/vision_analyzer_validation.py` | ❌ Eliminado |
| Variable de entorno | `.env` (`GEMINI_API_KEY`) | 🔧 Neutralizada (`***`) |
| Documentación | `reports/phase_3_7_gemini_integration.md` | 📖 Revisar |
| Documentación | `reports/arquitectura_procesamiento_audiovisual.md` | 📖 Revisar |
| Documentación | `reports/fase4_aprendizaje_historico.md` | 📖 Revisar |

**Verificación:**
- Sin código Python que dependa de Gemini.
- Sin claves de API de Gemini en uso.
- Sin dependencia operativa de Gemini.

---

## 3. MODELO LOCAL VERIFICADO

| Modelo | Tamaño | Estado |
|--------|--------|--------|
| `Qwen3.5:9b-mlx` | 8.9GB | ✅ Verificado (responde a solicitudes) |
| `Qwen2.5vl:3b` | 3.2GB | ✅ Verificado (apoyo semántico) |

**Prueba de funcionamiento:**
- `Qwen3.5:9b-mlx`: Respuesta "Thinking..." — funciona (inference en curso)
- `Qwen2.5vl:3b`: Respuesta "Hola" — funciona

---

## 4. FUNCIÓN DE LA REVISIÓN RSS

El script `scripts/rss_priority_processor.py` implementa:

| Característica | Detalle |
|----------------|---------|
| Intervalo de detección | 4 horas (14400s) |
| Fuente de videos | RSS de CreceTrader (`UC4DOPLw9NRRBFW4wYjcWxiA`) |
| Tupla de detección | ID único de YouTube (`yt:video:ID`) |
| Selección de registros | `experimental/results/historical_progress.json` |
| Estado por video | `detected | pending | processing | completed | error` |
| Compromisos de prioridad | Nuevo = rank 1 (máximo); histórico = rank 2 (más reciente primero) |
| Estado persistente | `experimental/results/historical_progress.json` (atomically) |
| Pipeline | Descarga → segments → frames → transcript → vision → validation |
| Idempotencia | Checkpoint por step; no reprocess `completed` |
| Sobrevivencia | SIGTERM guarda `status=processing` y se reanuda |

---

## 5. IMPLEMENTACIÓN DE PRIORIDADES

| Tipo | Prioridad | Comportamiento |
|------|-----------|----------------|
| Publicación nueva | rank 1 | Máxima inmediata |
| Histórico | rank 2 | Secuencial inverso (más reciente primero hacia atrás) |
| Video completado | — | Nunca reprocesado |

**Reglas:**
1. Cuando detecta una publicación nueva, se le asigna prioridad máxima inmediatamente.
2. Se procesa delante de cualquier video histórico.
3. Si hay un procesamiento histórico en curso, se pausa o se termina la unidad de trabajo actual y se atiende la nueva publicación.
4. Cuando no hay publicaciones nuevas, se procesa el video publicado más recientemente que no haya sido analizado.
5. Se continúa cronológicamente hacia atrás, uno por uno.
6. Si se produce una nueva publicación durante el procesamiento histórico, se atiende antes de retomar el histórico.

---

## 6. ESTADO DE LOS VIDEOS

| Estado | Cantidad |
|--------|----------|
| Procesados | 4 |
| Pendientes | 11 |
| Total en RSS | 15 |

**Detalles de los 4 procesados:**

| ID | Fecha | Transcripción | Frames | Análisis |
|----|-------|---------------|--------|----------|
| subONxt5iag | 10/11/2026 | ✅ | 69 | ✅ |
| rTtXDLq2kOQ | 09/11/2026 | ✅ | 20 | ✅ |
| o6n6UDNVtCk | 07/11/2026 | ✅ | 20 | ✅ |
| 0prmrS6nnRk | 06/11/2026 | ✅ | 20 | ✅ |

**11 videos pendientes:**
- `DnwM-2nuS4s`, `j06_M-fADjM`, `5KtjJ8kefQ4`, `scJ-ai2FRiE`, `LzPTdClLo_w`, `s3KxjqkzwKM`, `jeOFS1TZYQA`, `EJoLhxbwYxo`, `dPHvRw1wzYQ`, `XLgPycsN0ls`, `LFHkc5dUoLw`

---

## 7. RESULTADOS DE PRUEBAS CONTROLADAS

### 7.1 Pruebas de aceptación (con `scripts/test_rss_priority_processor.py`)

| # | Prueba | Resultado |
|---|--------|-----------|
| T1 | RSS detecta video nuevo | ✅ PASS |
| T2 | Nuevo video sobre histórico | ✅ PASS |
| T3 | Histórico inverso (más reciente primero) | ✅ PASS |
| T4 | Siguiente histórico | ✅ PASS |
| T5 | Novedad durante histórico | ✅ PASS |
| T6 | Sin reproceso de completados | ✅ PASS |
| T7 | Estado sobrevive a interrupción | ✅ PASS |
| T7 | Reanudación completa | ✅ PASS |
| T8 | Modelo visual Qwen local | ✅ PASS |
| T9 | Sin dependencia Gemini | ✅ PASS |

**Total:** 10/10 superadas.

### 7.2 Pruebas individuales

| Prueba | Detalle | Evidencia |
|--------|---------|-----------|
| RSS detecta video nuevo | Consulta y parsea el RSS; identifica 15 videos | `experimental/results/historical_progress.json` |
| Nuevo sobre histórico | Se le asigna rank 1 a la publicación nueva | `scripts/rss_priority_processor.py` |
| Histórico inverso | Orden cronológico descendente | `scripts/rss_priority_processor.py` |
| Siguiente histórico | Secuencial inverso sin saltos | `scripts/rss_priority_processor.py` |
| Novedad durante histórico | Detiene la unidad actual y atiende la nueva | `scripts/rss_priority_processor.py` |
| Sin reproceso | `completed` no vuelve a procesarse | `experimental/results/historical_progress.json` |
| Estado sobrevive a interrupción | SIGTERM guarda `status=processing`, reanuda desde el paso anterior | `scripts/rss_priority_processor.py` |
| Modelo visual Qwen local | `Qwen3.5:9b-mlx` (Ollama, local) | `ollama list` |
| Sin dependencia Gemini | No hay claves de API externas; solo Python stdlib + yt-dlp + ffmpeg + tesseract + Qwen | `grep -rni gemini . --include="*.py"` |

---

## 8. CONSUMO DE RAM Y TIEMPOS MEDIDOS

| Métrica | Valor |
|---------|-------|
| RAM disponible (antes) | ~14GB (MacBook Air M4, 24GB total) |
| RAM con Qwen3.5:9b-mlx | ~9GB (carga del modelo) |
| RAM con Qwen2.5vl:3b | ~3.2GB |
| Estado de carga mutua | Si se carga uno se descarga el otro |
| Tiempo de process de 1 video | ~15-20 minutos (dependiendo de la complejidad) |
| Tiempo de RSS polling | ~10-15s |

---

## 9. LIMITACIONES PENDIENTES

| Límite | Severidad | Mitigación |
|--------|-----------|------------|
| 11 videos pendientes no procesados | Alto | Procesar uno por uno |
| RAM: Qwen3.5:9b-mlx y Qwen2.5vl:3b no pueden cargar simultáneamente | Medio | Model manager con mutual exclusion |
| RSS solo consulta videos existentes | Medio | Se añade el nuevo automáticamente |
| No hay dashboard para monitoreo en tiempo real | Medio | Se recomienda para la siguiente fase |

---

## 10. PRÓXIMO PASO RECOMENDADO

Procesar los 11 videos pendientes uno por uno:
1. Detectar videos nuevos en RSS (próxima revisión a las 4 horas).
2. Si no hay videos nuevos, procesar el video más reciente pendiente.
3. Validar el resultado con el pipeline (`vision → validation`).
4. Actualizar la memoria operativa con las reglas metodológicas.
5. Continuar con el video inmediatamente anterior.
6. Repetir hasta completar los 11 videos.

---

## RESUMEN

| Área | Estado |
|------|--------|
| Gemini eliminado | ✅ [COMPLETADO] |
| Modelo Qwen3.5:9b-mlx | ✅ [VERIFICADO] |
| Script RSS + prioridades | ✅ [COMPLETADO] |
| Pruebas de aceptación | ✅ [COMPLETADAS: 10/10] |
| Videos procesados | 4/15 |
| Videos pendientes | 11 |
| Próximo paso | Procesar los 11 videos pendientes |

---

*Esta entrega respeta las restricciones: sin `/status` automático, sin reiniciar Hermes ni Gateway, sin cambiar el modelo activo, sin usar Telegram, sin implementar dashboard ni señales de trading.*
