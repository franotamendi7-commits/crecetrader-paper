# PLAN DE EJECUCIÓN ORDENADA — FASES 2 A 7

**Fecha:** 10 de noviembre de 2026
**Proyecto:** YouTubeTradingAgent
**Modelo verificado:** upstage/solar-mini4:free (Nous)
**Estado:** Primera ejecución completada. Esperar autorización antes de ejecutar.

---

## 1. ESTADO ACTUAL DE YouTubeTradingAgent Y CHECKPOINT 2B

### 1.1 Estado del proyecto

```
YouTubeTradingAgent/
├── README.md
├── ARCHITECTURE.md
├── PROJECT_SCOPE.md
├── DECISIONS.md
├── ROADMAP.md
├── YOUTUBE_AGENT_RESEARCH.md
├── MODEL_DELEGATION.md
├── RESOURCE_BUDGET.md
├── SECURITY.md
├── NEXT_STEPS.md
├── reports/
└── experimental/
    ├── memory/ (memoria histórica)
    ├── results/ (resultados)
    └── scripts/ (scripts)
```

Proyecto en **Fase 0** (documentación e investigación). No se ha programado el agente todavía.

### 1.2 Estado de CHECKPOINT 2B

| Módulo | Entradas | Estado |
|--------|----------|--------|
| filosofia | 4 | Completo |
| multitemporal | 3 | Completo |
| tendencias | 6 | Completo |
| estructuras | 4 | Completo |
| operaciones | 4 | Completo |
| activos | 4 | Completo |
| comparaciones | 6 | Completo |
| **Total** | **31** | **Parcialmente completado** |

Problemas detectados:
- 14 pares de entradas duplicadas (idénticas)
- 16 entradas compartidas entre `subONxt5iag` y `o6n6UDNVtCk`
- 11 entradas con soporte=1 (un solo video)
- 2 entradas con estado `provisional`
- `compare_videos()` no comparaba correctamente

Ver: `reports/checkpoint_2B_memoria.md`, `reports/fase1_auditoria_chief.md`

---

## 2. PLAN DE EJECUCIÓN ORDENADA

### FASE 2 — SEPARACIÓN DE MEMORIA Y CONTEXTO

**Objetivo:** Separar la memoria histórica CHIEF de la memoria operativa del nuevo proyecto.

| Tarea | Entregable |
|-------|------------|
| Crear `memory/operativa/` vacío para la memoria del nuevo proyecto | `memory/operativa/memory.json` (vacía) |
| Conservar `experimental/memory/` como memoria histórica CHIEF | Documentar en `reporte_memoria.md` |
| No cargar memoria antigua en cada sesión | Dependencias configuradas |
| Documentar la separación | `reporte_memoria.md` |

**Criterios de aceptación:**
- La memoria operativa es exclusiva del nuevo proyecto.
- La memoria histórica CHIEF está conservada e intacta.
- No hay mezcla de contextos.

**Entregables:**
- `memory/operativa/memory.json`
- `reports/reporte_memoria.md`

---

### FASE 3 — CHECKPOINT 2B Y CHECKPOINT 2C

**Objetivo:** Revisar y cerrar CHECKPOINT 2B, presentar propuesta de CHECKPOINT 2C.

| Tarea | Criterio de aceptación |
|-------|------------------------|
| Resolver la discrepancia 13 vs 14 pares deduplicados (14 es correcto) | Documentado en un reporte |
| Verificar la clasificación de versiones duplicadas | Todas marcadas correctamente |
| No confundir versiones duplicadas con evidencias independientes | Separados por campo `tipo` |
| Corregir y probar `compare_videos()` | Devuelve las entradas compartidas |
| Revisar las 11 entradas con soporte=1 | Todas clasificadas y revisadas |
| Revisar la entrada `9EE6CADA` | Corregida según evidencia |
| Verificar la trazabilidad de cada entrada | Todos tienen video, timestamp, frame |
| Conservar el historial de cambios | `historial` poblado |

**Criterios de aceptación de CHECKPOINT 2C:**
- Todas las entradas verificables sin duplicados.
- `compare_videos()` funcional.
- 11 entradas con soporte=1 revisadas.
- La memoria distingue `[DICHO]`, `[OBSERVADO]`, `[INFERIDO]`.
- La comparación entre videos documentada.

**Entregables:**
- `reports/checkpoint_2C_proposal.md`
- `reports/checkpoint_2B_replica_corregida.md`

---

### FASE 4 — APRENDER LA METODOLOGÍA DE BITCOIN HOY / CRECETRADER

**Objetivo:** Que YouTube Analyst aprenda la metodología del analista.

| Tarea | Criterio de aceptación |
|-------|------------------------|
| Procesar los 11 videos históricos pendientes | 11/11 videos procesados |
| Priorizar los videos más recientes | Orden cronológico |
| Conservar: ID, título, fecha, transcripción, frames, evidencia | Cada video con campos completos |
| Identificar instrumentos y temporalidades | Salidas verificables |
| Extraer niveles y zonas | Con timestamps |
| Registrar contradicciones | Documentado |
| Comparar videos anteriores | Documentado |
| No inventar información | Solo con evidencia |

**Criterios de aceptación de CHECKPOINT 2C:**
- 15/15 videos procesados (4 históricos + 11 nuevos).
- Memoria consolidada sin duplicados.
- Trazabilidad de todas las entradas.
- La comparación entre videos documentada.

**Entregables:**
- `reports/checkpoint_2C_resultados.md`
- `experimental/results/historical/` completado

---

### FASE 5 — VALIDAR Y CERRAR YOUTUBE ANALYST

**Objetivo:** Demostrar que YouTube Analyst funciona correctamente.

| Prueba | Criterio de aceptación |
|--------|------------------------|
| Procesar un video completo | 1 video completo |
| Interpretar audio y gráficos conjuntamente | Salidas verificables |
| Identificar instrumentos y temporalidades | Correctos |
| Reconocer estructuras relevantes | Correctos |
| Extraer niveles con timestamps | Verificables |
| Comparar análisis de varios videos | Documentado |
| Detectar cambios de metodología | Documentado |
| Recuperar reglas de memoria | Con fuentes mostradas |
| Diferenciar evidencia de inferencia | `[DICHO]` vs `[OBSERVADO]` vs `[INFERIDO]` |
| Producir un informe comprensible | Documentado |

**Criterios de aceptación:**
- Solo se declara "funciona" si hay prueba verificable.
- No se declara "entiende la estrategia" sin evidencia.

**Entregables:**
- `reports/fase5_validacion.md`
- `experimental/results/validacion_video.md`

---

### FASE 6 — TRADING AGENT Y RISK MANAGER

**Objetivo:** Presentar el diseño técnico de ambos módulos (solo diseño, no implementación).

| Módulo | Responsabilidad |
|--------|----------------|
| Trading Agent | Evaluar oportunidades a partir de YouTube Analyst. No operar. |
| Risk Manager | Gestionar capital y riesgo independientemente del Trading Agent. |

**Criterios de aceptación:**
- Presentar prototipo de diseño.
- No ejecutar órdenes de trading.
- El usuario mantiene el control manual.

**Entregables:**
- `reports/diseño_trading_agent.md`
- `reports/diseño_risk_manager.md`

---

### FASE 7 — DASHBOARD Y DISCORD

**Objetivo:** Mostrar señales validadas en el dashboard y Discord.

| Tarea | Criterio de aceptación |
|-------|------------------------|
| Mostrar solo señales reales | No alertar sin señal |
| No reconstruir dashboard antiguo | Nuevo dashboard |
| Colaborar con Risk Manager | Integrado |
| Canales separados por función | Organizados |

**Entregables:**
- `reports/dashboard_discord.md`

---

## 3. RESUMEN DE EJECUCIÓN

| Fase | Tarea | Estado |
|------|--------|--------|
| Fase 1 | AISLAMIENTO DEL CHIEF | ✅ AUDITADA |
| Fase 2 | SEPARACIÓN DE MEMORIA | 📋 PENDIENTE |
| Fase 3 | CHECKPOINT 2B/2C | 📋 PENDIENTE |
| Fase 4 | APRENDER LA METODOLOGÍA | 📋 PENDIENTE |
| Fase 5 | VALIDAR Y CERRAR YOUTUBE ANALYST | 📋 PENDIENTE |
| Fase 6 | TRADING AGENT Y RISK MANAGER | 📋 PENDIENTE |
| Fase 7 | DASHBOARD Y DISCORD | 📋 PENDIENTE |

---

## 4. VEREDICTO

**FASE 1: AUDITORÍA COMPLETADA**

El conjunto CHIEF verificado y conservado. Nada se modificó.

**ESTADO FINAL DE LA EJECUCIÓN:**
- Checkpoints: `2B` parcial, `2C` en propuesta
- Agentes antiguos: verificados, pausados
- Inspector de memoria: listo para separación
- YouTubeTradingAgent: en Fase 0, listo para Fase 1

**PRÓXIMO PASO RECOMENDADO:**
Esperar autorización para ejecutar la Fase 2 (separación de memoria) y continuar con la Fase 3 (checkpoint 2B/2C).

---

## 5. RESTRICCIONES CIERRE

- Proyecto exclusivo: `~/YouTubeTradingAgent/`
- No modificar `~/Harness`
- No instalar nada ni pagar
- No usar Telegram
- Discord como canal
- No ejecutar `/status` automáticamente
- Cada fase entrega: auditado, modificado, conservado, pruebas, evidencias, problemas, veredicto, próximo paso
