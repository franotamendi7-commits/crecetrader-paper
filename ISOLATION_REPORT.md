# ISOLATION REPORT — FASE 1

## Fecha: 2026-11-09

## A. COMPONENTES IDENTIFICADOS Y DETENIDOS

| Componente | Servicio/PID | Estado inicial | Acción | Estado final |
|---|---|---|---|---|
| CHIEF Dashboard | com.harness.chief-dashboard (PID 34243) | Activo | launchctl bootout | DETENIDO |
| CHIEF Dashboard (legacy) | com.chief.dashboard | Activo | launchctl bootout | DETENIDO |
| Signals Continuous | com.harness.signals-continuous (PID 27133) | Activo | launchctl bootout | DETENIDO |
| 4H Strategy | com.harness.4h-strategy | Activo | launchctl bootout | DETENIDO |
| Daily Report | com.harness.daily-report | Activo | launchctl bootout | DETENIDO |
| Model Training | com.harness.model-training (PID 78) | Activo | launchctl bootout | DETENIDO |
| University Agent | com.harness.university-agent (PID 78) | Activo | launchctl bootout | DETENIDO |
| GitHub Monitor | com.harness.github-monitor | Activo | launchctl bootout | DETENIDO |
| STT API | com.harness.stt-api (PID 62165) | Activo | launchctl bootout | DETENIDO |
| Watchdog | com.harness.watchdog (PID 736) | Activo | launchctl bootout | DETENIDO |
| Binance Agent | PID 922 (proceso directo) | Activo | kill (ya terminado) | DETENIDO |
| Speech to Text API | PID 864 (proceso directo) | Activo | kill (ya terminado) | DETENIDO |

## B. COMPONENTES NO TOCADOS (COMPARTIDOS/DESCONOCIDOS)

| Componente | Servicio/PID | Razón |
|---|---|---|
| Jarvis S2S | com.harness.jarvis-s2s (PID 728) | Voice AI — no es parte del sistema de trading. Compartido con JARVIS. |
| Hermes Gateway | PID 22143 | Servicio core de Hermes. No tocar. |
| Ollama | (servicio) | Infraestructura compartida. No tocar. |
| tmp-voice-ai | PID 728 (venv) | Voice AI. No es parte del trading. |

## C. VERIFICACIÓN

- Procesos antiguos de trading: NO en ejecución (verificado con ps)
- LaunchAgents de trading: TODOS desactivados (verificado con launchctl list)
- Puertos antiguos (5002, 5003, 8000): LIBRES (verificado con lsof)
- Archivos y datos: INTACTOS (verificado con ls)
- Plists y configuraciones: NO ELIMINADOS (solo desactivados)
- Discord: No se encontró proceso de bot Discord separado. Las notificaciones NO_SIGNAL eran enviadas por signals-continuous (ahora detenido).

## D. NOTAS

- Los plists permanecen en ~/Library/LaunchAgents/ para posible reactivación futura
- No se eliminó ni modificó ningún archivo, base de datos, modelo ni configuración
- Hermes Memory Vault NO fue tocado
- Ollama NO fue modificado
- El sistema anterior queda guardado pero fuera de funcionamiento

## E. ESTADO FINAL DEL SISTEMA ANTERIOR

OPERATIVAMENTE DETENIDO Y AISLADO.
Archivos, datos y configuraciones: INTACTOS.
Reactivación posible mediante: launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/<plist>
