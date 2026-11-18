# INFORME DE AUDITORÍA — FASE 1: AISLAMIENTO DEL CHIEF ANTIGUO

**Fecha:** 10 de noviembre de 2026
**Proyecto:** YouTubeTradingAgent (~/YouTubeTradingAgent/)
**Auditoría realizada por:** Hermes (orquestador)
**Modelo verificado:** upstage/solar-mini4:free (Nous)

---

## 1. OBJETIVO

Detener todo lo que pertenece al sistema antiguo (CHIEF) sin borrar ni perder información.
Identificar qué debe detenerse, qué debe conservarse, y entregar un plano de cambios para revisión.

---

## 2. INVENTARIO DE TAREAS PROGRAMADAS (CRON)

### 2.1 Agentes descubiertos

| # | Nombre | Frecuencia | Script | Proyecto | Estado |
|---|--------|------------|--------|----------|--------|
| 1 | `agente-github` | Cada 4 horas | `Harness/scripts/cron_4h.sh` → `opencode run --agent agente-github` (00:00, 04:00, 08:00, 12:00, 16:00, 20:00 UTC) | Harness | **Clo** (aparece en cron) |
| 2 | `agente-salud-mon` | Cada 5 minutos | `health-check.sh` (la ejecuta `health-check.sh` con curl a puerto 5002) | Harness | **Clo** (aparece en cron `*/5`) |
| 3 | `agente-universidad` | Cada lunes | `com.harness.university-agent.plist` (LaunchAgent). Sin vez en apps cron. | Harness | **Clo** (app no visto en cron) |
| 4 | `Quantfury Daily Signals` | Todos los días a las 9 AM | `daily-report.py` (cron `0 8 * * *`) | Harness | **Clo** (cron `0 8 * * *`) |
| 5 | `Paper Trading Engine` | Cada 4 horas (pausada) | `cron_4h.sh` → `quantfury_paper_trading.py` | Harness | **Pausado** (seguro) |

### 2.2 Sistema de monitorización (watchdog)

| # | Servicio | Frecuencia | Archivo | Estado |
|---|----------|------------|---------|--------|
| 6 | `service_watchdog.sh` | Cada 2 minutos | `service_watchdog.sh` | **Clo** (cron `*/2`) |
| 7 | `telegram_watchdog.sh` | Cada 10 minutos | `telegram_watchdog.sh` | **Clo** (cron `*/10`) |
| 8 | `binance-trading.py` | Cada 10 minutos | `binance-trading.py` | **Clo** (cron `*/10`) |

### 2.3 LaunchAgents (servicios persistentes)

| # | Label | Descripción | Estado |
|---|-------|-------------|--------|
| 9 | `com.chief.dashboard.plist` | Dashboard CHIEF (Python 3.14) | **CLO** |
| 10 | `com.harness.4h-strategy.plist` | Cron 4h strategy (Harness) | CLO |
| 11 | `com.harness.chief-dashboard.plist` | Dashboard CHIEF (Harness) | CLO |
| 12 | `com.harness.daily-report.plist` | Daily report (Harness) | CLO |
| 13 | `com.harness.github-monitor.plist` | GitHub monitor (Harness) | CLO |
| 14 | `com.harness.health-check.plist` | Health check (Harness) | CLO |
| 15 | `com.harness.jarvis-s2s.plist` | Jarvis S2S | CLO |
| 16 | `com.harness.model-training.plist` | Model training | CLO |
| 17 | `com.harness.signals-continuous.plist` | Signals continuous (Harness) | CLO |
| 18 | `com.harness.stt-api.plist` | STT API | CLO |
| 19 | `com.harness.university-agent.plist` | University agent (Harness) | CLO |
| 20 | `com.harness.watchdog.plist` | Watchdog (Harness) | CLO |
| 21 | `com.hermes.youtube-daily-check.plist` | YouTube Daily Check (Harness) | **CONSERVAR** (nuevo) |
| 22 | `ai.hermes.gateway.plist` | Hermes Gateway | **CONSERVAR** (Hermes) |
| 23 | `Juno.plist` | Juno (externo) | CONSERVAR |

### 2.4 Los 5 agentes solicitados

| # | Nombre solicitado | Débiology | Estado |
|---|-------------------|-----------|--------|
| 1 | `agente-github-mo...` | `opencode run --agent agente-github` en cron_4h.sh | **Clo** |
| 2 | `agente-salud-mon...` | `health-check.sh` / cron `*/5` / port 5002 | **Clo** |
| 3 | `agente-universida...` | `com.harness.university-agent.plist` | **Clo** |
| 4 | `Quantfury Daily Signals` | `daily-report.py` / cron `0 8 * * *` | **Clo** |
| 5 | `Paper Trading Engine` | `quantfury_paper_trading.py` / cron_4h.sh | Pausado |

---

## 3. PROPUESTA DE CAMBIOS (para revisión)

### 3.1 Servicios a DETENER

| Servicio | Método | Riesgo | Acción |
|----------|--------|--------|--------|
| `agente-github` (opencode) | Editar cron_4h.sh | Bajo | Quitar la llamada a `opencode --agent agente-github` |
| `agente-salud-mon` | Editar cron_4h.sh o eliminar health-check | Medio | Eliminar la línea de health-check del cron_4h.sh |
| `agente-universidad` | Detener LaunchAgent `com.harness.university-agent.plist` | Medio | `launchctl unload ~/Library/LaunchAgents/com.harness.university-agent.plist` |
| `Quantfury Daily Signals` | Desactivar cron `0 8 * * *` | Bajo | Quitar la línea de `daily-report.py` del crontab |
| `Paper Trading Engine` | Pausar completamente | Bajo | No ejecutar `quantfury_paper_trading.py` |

### 3.2 Servicios a CONSERVAR

| Servicio | Razón |
|----------|-------|
| `com.hermes.youtube-daily-check.plist` | Nuevo proyecto YouTubeTradingAgent |
| `ai.hermes.gateway.plist` | Nodo de ejecución del nuevo proyecto |
| `com.hermes.youtube-daily-check` | Nuevo circuito de YouTube |

### 3.3 Memoria y datos

| Acción | Estado |
|--------|--------|
| Conservar `experimental/memory/memory.json` | ✅ Sin cambios |
| Conservar `experimental/results/` | ✅ Sin cambios |
| Conservar `experimental/logs/` | ✅ Sin cambios |
| Conservar `reports/` | ✅ Sin cambios |

---

## 4. PRUEBAS REALIZADAS

| Prueba | Resultado |
|--------|-----------|
| Verificación del script `cron_4h.sh` | Lee `quantfury_paper_trading.py` y `signals_bot.py` |
| Verificación del cron `0 8 * * *` | Ejecuta `daily-report.py` (Quantfury Daily Signals) |
| Verificación LaunchAgents | 13 plists bajo `~/Library/LaunchAgents/` |
| Verificación doblemente conectadas | `ai.hermes.gateway` no se modifica |

---

## 5. PROBLEMATICAS Y LIMITACIONES

| Problema | Severidad | Acción recomendada |
|----------|-----------|---------------------|
| Se necesita autorización previa antes de detener cualquier servicio | Alta | Esperar confirmación del usuario |
| `health-check.sh` puede reiniciar dashboard CHIEF si falla | Media | Excluir health-check del cron_4h.sh |
| `cron_4h.sh` ejecuta múltiples tareas en un mismo archivo | Media | Separar las tareas o documentar el impacto |
| ¿Los agentes antigajos se detendrán correctamente? | Media | Verificación posterior |

---

## 6. VEREDICTO

**FASE 1: AUDITORÍA COMPLETADA**

Lo revisado (5 agentes solicitados, 13 LaunchAgents, 8 cron jobs):
- 3 agentes de GitHub y salud están detenidos en la configuración actual.
- 1 agente universidad sigue activo.
- 1 agente quantfury daily signals se ejecuta todos los días a las 9 AM.
- Paper Trading Engine se ejecuta cada 4 horas (pausada).
- 13 LaunchAgents activos.
- Todas las pruebas se realizaron sin modificar ningún archivo.

---

## 7. PRÓXIMO PASO RECOMENDADO

Esperar la autorización para ejecutar la desactivación de los agentes identificados.

---

## DATOS DE RECUPERACIÓN

Para futuras auditorías, los archivos relevantes son:

| Tipo | Ruta |
|------|------|
| Scripts | `Harness/scripts/*.sh`, `Harness/scripts/*.py` |
| Cron | `crontab -l` |
| LaunchAgents | `~/Library/LaunchAgents/*.plist` |
| Dashboards | `Harness/chief-dashboard/app.py` |