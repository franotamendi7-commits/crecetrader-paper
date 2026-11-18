# Resource Lifecycle Manager V1 — Arquitectura

## Resumen ejecutivo

El *Resource Lifecycle Manager* (RLM) es el módulo central de administración de recursos para **YouTubeTradingAgent**. Su objetivo es garantizar que los servicios y modelos se utilicen solo cuando sean necesarios, liberando recursos cuando terminan su trabajo, y prevenir consumo innecesario de RAM, CPU y temperatura elevada.

Este documento describe la arquitectura, componentes, interfaces y flujos operativos del RLM, tal como se implementó bajo la autorización proporcionada.

---

## 1. Antecedentes y objetivo

El Macintosh Air M4 (24 GB de RAM) ejecuta varios servicios que compiten por recursos:
- **Hermes Gateway** — orquestador de tareas
- **OpenCode** — ejecución de tareas de programación
- **Ollama** — inferencia de modelos locales
- **YouTubeTradingAgent** — análisis de videos (descarga, frames, transcripciones, visión, validación)

Sin un gestor de recursos, los modelos Ollama (como `qwen2.5vl:3b`) permanecen en memoria durante largos períodos, consumiendo ~3,86 GB de RAM y generando presión térmica en el equipo.

El **Resource Lifecycle Manager V1** introduce un control riguroso del ciclo de vida de estos servicios, asegurando que:
- **OpenCode** inicie solo cuando se necesite programación y cierre cuando no haya más tareas.
- **Ollama** cargue modelos bajo demanda y descargue inmediatamente después de cada tarea.
- No se inicien tareas pesadas cuando exista presión térmica o de memoria elevada.

---

## 2. Arquitectura general

```
                        ┌─────────────────────────────┐
                        │      YouTubeTradingAgent     │
                        │  (run_cycle, processors)     │
                        └───────────────┬─────────────┘
                                        │
                        ┌───────────────▼─────────────┐
                        │   Resource Lifecycle Manager │
                        │  (scripts/resource_lifecycle_manager.py) │
                        │  • State persistente (JSON) │
                        │  • Locks propios            │
                        │  • Monitoreo RAM/CPU/Swap   │
                        │  • Detección de presión      │
                        └───────────────┬─────────────┘
                                        │
        ┌───────────────────────────────┼───────────────┐
        │                               │               │
┌────────▼────────┐             ┌────────▼────────┐    ┌────────▼────────┐
│   OpenCode      │             │   Ollama        │    │   Twitch       │
│   (opencode serve)│             │   (llama-server)│    │   (hermes)      │
└─────────────────┘             └─────────────────┘    └─────────────────┘
```

### Componentes principales

1. **State Persistence** — Archivo JSON (`resource_lifecycle_state.json`) que guarda:
   - Estado del gestor (`idle`, `busy`, `pause`, `error`)
   - Ubicación de lockfiles
   - Modelos cargados y su tiempo de carga
   - Memoria/CPU antes/después de cada tarea
   - Checkpoints de tareas
   - Historial de eventos

2. **Lock Manager** — Bloqueo atómico mediante `os.O_CREAT | os.O_EXCL | os.O_WRONLY`, que evita ejecuciones concurrentes.

3. **Model Manager** — Carga y descarga de modelos Ollama.
   - Usa el parámetro `keep_alive: 0` para descargar modelos después de cada tarea.
   - Verifica cargas con `/api/ps`.

4. **OpenCode Manager** — Inicia y detiene OpenCode de forma ordenada.
   - Solo inicia cuando se necesita programación.
   - Solo cierra cuando no hay tareas activas.

5. **Resource Monitor** — Registra consumo de RAM, CPU y swap antes/después de cada tarea.
   - Detecta presión térmica y de memoria.
   - Implementa prioridades de respuesta.

6. **Checkpoint Manager** — Guarda puntos de verificación de tareas.
   - Permite recuperación segura tras interrupciones.

---

## 3. Componentes de implementación

### 3.1. `scripts/resource_lifecycle_manager.py`

Módulo principal que implementa:
- Clase `ResourceLifecycleManager`
  - `acquire_lock()` — Bloqueo atómico con `os.O_CREAT | os.O_EXCL | os.O_WRONLY`
  - `release_lock()` — Libera el bloqueo (solo dueño)
  - `is_locked()` — Verifica si el lock está en posesión
  - `load_model(model_name, keep_alive)` — Carga modelo Ollama
  - `unload_model(model_name)` — Descarga modelo (keep_alive: 0)
  - `get_running_models()` — Listado de modelos cargados
  - `is_model_loaded(model_name)` — Verifica residencia del modelo
  - `get_memory_snapshot()` — Instantánea de recursos (RAM, CPU, swap)
  - `detect_thermal_pressure()` — Detección de presión térmica
  - `detect_memory_pressure()` — Detección de presión de memoria
  - `create_checkpoint(task_id, data)` — Checkpoint de tareas
  - `load_checkpoint(task_id)` — Carga checkpoint
  - `auto_recover()` — Recuperación tras interrupción
  - `safe_shutdown()` — Cierre seguro

### 3.2. Modificaciones a `scripts/rss_priority_processor.py`

El procesador ahora utiliza el RLM para:
- Antes de procesar un video: verificar estado del modelo Ollama
- Durante el pipeline: cargar el modelo si no está en memoria
- Después de completar cada etapa: verificar resguardo de checkpoints
- Finalizar la tarea: descargar modelo con `keep_alive: 0`

### 3.3. Documentación

- `docs/architecture/resource_lifecycle_manager_v1.md` — Esta arquitectura
- `reports/resource_lifecycle_manager_v1_implementation.md` — Reporte de implementación

### 3.4. Pruebas automatizadas

- Pruebas de carga y descarga de modelo
- Verificación de residencia de modelo
- Pruebas de OpenCode (inicio, tarea, cierre)
- Pruebas de coordinación (doble solicitud)
- Pruebas de interrupción y recuperación
- Pruebas de presión de memoria antes de iniciar tarea

---

## 4. Políticas operativas

### 4.1. YouTube Analyst

1. Comprobar disponibilidad de RAM y presión térmica.
2. Cargar el modelo local autorizado (solo si no está en memoria).
3. Procesar video y frames.
4. Guardar transcripciones, resultados, evidencias y checkpoints.
5. Verificar que los archivos se escribieron correctamente.
6. Esperar a que finalicen todas las inferencias.
7. Descargar modelo con `keep_alive: 0`.
8. Verificar que el modelo ya no está residente.

### 4.2. Hermes Memory Vault

- Cargar modelo únicamente durante la consolidación semanal.
- Al terminar: descargarlo y verificar que no permanezca residente.
- No modificar la frecuencia ni activar la consolidación.

### 4.3. OpenCode

- Iniciar cuando Hermes delegue programación.
- Cerrar ordenadamente al finalizar la tarea.
- No cerrar Hermes ni Gateway.

---

## 5. Restricciones

- No cambiar modelos ni proveedores.
- No descargar ni instalar modelos nuevos.
- No cambiar el scheduler RSS.
- No modificar Harness ni CHIEF.
- No reiniciar Hermes ni Gateway.
- No modificar el comportamiento metodológico del YouTube Analyst.
- No reanudar A.7.4 como parte de esta implementación.
- No construir dashboard de trading.
- No iniciar Risk Manager ni Analyst Manager.

---

## 6. Criterios de aceptación

- Ollama carga bajo demanda y descarga después de cada tarea.
- OpenCode no permanece ejecutándose innecesariamente.
- No se descargan modelos durante inferencias activas.
- No se pierden checkpoints.
- Los agentes no compiten por recursos sin coordinación.
- El sistema recupera correctamente una tarea interrumpida.

---

*Documento generado como parte de la implementación del Resource Lifecycle Manager V1.*
