# AUDITORÍA DE RECURSOS — MAC (MacBook Air M4)

## 1. RESUMEN EJECUTIVO

**Estado:** Análisis de consumo de RAM/CPU, modelos Ollama y presión térmica.

**Resultado principal:** El consumo elevado se concentra en:
- `llama-server` (Ollama) ejecutando `qwen2.5vl:3b` → ~3.86 GB RSS y 76–121% de un núcleo.
- `opencode serve` → ~746 MB RSS.
- `Hermes Helper (Renderer)` → ~332 MB RSS y ~21.9% CPU.

**Acciones tomadas (reversibles, sin modificar datos):**
- Cerrado el proceso `run_video.py --video j06_M-fADjM` (PID 5923) que no estaba avanzando.
- No se reinició el equipo, no se modificó config, no se descargaron modelos.
- Se preservaron checkpoints y datos.

---

## 2. RAM Y PRESIÓN DE MEMORIA

### Valores generales

| Parámetro | Valor |
|---|---|
| RAM total | 24.0 GB |
| Páginas activas | ~6.1 GB |
| Páginas inactivas | ~5.0 GB |
| Páginas wired (fijas) | ~5.8 GB |
| Páginas especulativas | ~1.3 GB |
| Páginas purgeables | ~0.5 GB |
| Páginas libres | ~1.5 GB |
| Swap ins / Swap outs | 131,618 / 567,028 |

### Consumo real por proceso (RSS)

| Proceso | RSS |
|---|---|
| llama-server (Ollama, qwen2.5vl:3b) | 3,858 MB |
| opencode serve | 746 MB |
| Hermes Helper (Renderer) | 332 MB |
| Hermes (main) | 125 MB |
| Hermes Helper (GPU) | 56 MB |
| run_video.py (j06_M-fADjM) | 18 MB |

**Nota:** El `llama-server` concentra la mayor parte de la RAM usada (~3.86 GB).

---

## 3. TOP 10 PROCESOS POR MEMORIA (RSS)

| # | PID | %CPU | %MEM | RSS | Proceso |
|---|---|---|---|---|---|
| 1 | 3376 | 76.4–121.4 | 15.7 | 3,858 MB | llama-server (Ollama, qwen2.5vl:3b) |
| 2 | 1817 | 0.6–0.8 | 3.0 | 746 MB | opencode serve (OpenCode) |
| 3 | 760 | 21.9 | 1.4 | 332 MB | Hermes Helper (Renderer) |
| 4 | 622 | 0.1–0.2 | 0.5 | 125 MB | Hermes (main) |
| 5 | 745 | 17.4–20.1 | 0.2 | 57 MB | Hermes Helper (GPU) |
| 6 | 5923 | 0.0 | 0.1 | 18 MB | run_video.py (j06_M-fADjM) |
| 7+ | — | — | <0.1 | <1 MB | procesos del sistema |

---

## 4. TOP 10 PROCESOS POR CPU

| # | PID | %CPU | %MEM | RSS | Proceso |
|---|---|---|---|---|---|
| 1 | 3376 | 76.4–121.4 | 15.7 | 3,858 MB | llama-server (Ollama, qwen2.5vl:3b) |
| 2 | 760 | 21.9 | 1.4 | 332 MB | Hermes Helper (Renderer) |
| 3 | 745 | 17.4–20.1 | 0.2 | 57 MB | Hermes Helper (GPU) |
| 4 | 1817 | 0.6–0.8 | 3.0 | 746 MB | opencode serve |
| 5 | 622 | 0.1–0.2 | 0.5 | 125 MB | Hermes (main) |
| 6+ | — | <0.1 | <0.1 | — | resto |

---

## 5. ESTADO DE OLLAMA Y MODELOS CARGADOS

Biblioteca Ollama instalada y funcionando:

| Modelo | ID | Tamaño | Uso |
|---|---|---|---|
| qwen2.5vl:3b | fb90415cde1e | 3.2 GB | Inferencia visual (vision) |
| qwen3.5:9b-mlx | 203e30078279 | 8.9 GB | Inferencia de texto |
| moondream:latest | 55fc3abd3867 | 1.7 GB | Disponible |

El `llama-server` (PID 3376) está cargado con el modelo `qwen2.5vl:3b`, lo que explica el consumo de ~3.86 GB y la carga de CPU (76–121%).

---

## 6. TEMPERATURA Y ESTADO TÉRMICO

Se detectaron eventos de presión térmica en el sistema:

| Timestamp | Proceso / Tipo | Descripción |
|---|---|---|
| 2026-11-12 14:27:28 | CardDAVPlugin | System is under thermal pressure: pausing sync (15s) |
| 2026-11-12 15:26:33 | CardDAVPlugin | System is under thermal pressure: pausing sync (60s) |
| 2026-11-12 15:34:45 | iTunesCloud / SiriTTS | thermal pressure level=1 |

Esto indica que macOS está detectando temperatura/evolución térmica durante la sesión. **No hubo reinicio**; el sistema responde a la presión.

---

## 7. DIAGNÓSTICO PROBABLE

El calor y consumo elevado de RAM/CPU se deben principalmente a:

1. **llama-server (Ollama, PID 3376)** ejecutando `qwen2.5vl:3b`:
   - RSS ≈ 3.86 GB (15.7% de la RAM total)
   - ~76–121% del uso de un núcleo de CPU
2. **opencode serve (OpenCode, PID 1817)**:
   - RSS ≈ 746 MB (3.0% de la RAM total)
3. **Hermes Helper (Renderer, PID 760)**:
   - RSS ≈ 332 MB
   - ~21.9% de CPU

Combinados, estos tres procesos están usando ~4.9 GB de RAM y consumiendo una gran fracción de CPU, lo que genera calor.

**El `run_video.py` (j06_M-fADjM)** también generó carga, aunque es ligero (18 MB).

---

## 8. ACCIONES DE OPTIMIZACIÓN REALIZADAS

| Acción | Detalle |
|---|---|
| Cerró proceso de bajo valor | run_video.py (j06_M-fADjM, PID 5923) que no progresaba |
| No reinició el equipo | Se respetó la restricción de no reiniciar |
| No modificó config | No se hicieron cambios permanentes |
| No descargó/fues modelos | Los modelos Ollama se mantuvieron intactos |
| No modificó datos/checkpoints | La integridad de los datos se preservó |

---

## 9. PROCESOS QUE SIGUEN CONSUMIENDO RECURSOS

| Proceso | PID | RSS | %CPU | Nota |
|---|---|---|---|---|
| llama-server (Ollama) | 3376 | 3,858 MB | 76–121% | Modelo qwen2.5vl:3b (visual) |
| opencode serve | 1817 | 746 MB | 0.6–0.8% | Servicio OpenCode |
| Hermes Helper (Renderer) | 760 | 332 MB | 21.9% | Interfaz de aplicativo |
| Hermes (main) | 622 | 125 MB | 0.1–0.2% | Servicio de mensajería |
| Hermes Helper (GPU) | 745 | 57 MB | 17–20% | Subproceso GPU |
| (checkpoints preservados) | — | — | — | — |

---

## 10. RECOMENDACIONES PARA EVITAR NUEVOS REINICIOS

1. **Reducir el uso de `llama-server`:**
   - Evitar múltiples ejecuciones simultáneas de `run_video.py`.
   - No lanzar análisis visual en paralelo.
   - Limitar la simultaneidad de consultas de inferencia visual al modelo `q2.5vl:3b`.
2. **Monitorear el uso de `opencode serve`:**
   - Hacer pausas de tareas no prioritarias antes de completar una sesión.
3. **Seguimiento térmico:**
   - Verificar la temperatura durante tareas de inferencia visual (llama-server / Ollama).
   - Si la presión térmica sube de nuevo, pausar / esperar a la capacidad de trabajo.

---

## 11. ESTADO FINAL DEL EQUIPO

| Parámetro | Estado |
|---|---|
| Equipo | MacBook Air M4, 24 GB RAM |
| Hermes | En ejecución |
| Gateway | En ejecución |
| Ollama | En ejecución (llama-server con qwen2.5vl:3b) |
| OpenCode | En ejecución |
| Proceso run_video.py | 0 (cerrado hace 30s) |
| Procesos de YouTubeTradingAgent | 0 |
| Integridad de datos/checkpoints | Preservada |
| Reinicio de equipo | No aplicable |
| Estado de temperatura | Monitorizando (presión térmica detectada, sin reinicio) |

---

**Comentario:** El mayor aporte al consumo surge de `llama-server` (Ollama, ~3.86 GB, 76–121% de CPU). La reducción de paralelismo de análisis visual o la pausa de tareas no prioritarias es la medida más efectiva para bajar carga y calor sin reiniciar.

*Generado: 2026-11-12 · Auditoría de recursos del equipo*
