# PROMPT — Auditoría OpenCode (pegar en OpenCode)

> Contexto: proyecto `/Users/franciscootamendi/YouTubeTradingAgent` (YouTubeTradingAgent). Trabajamos en `daily_pilot/`, aislado de producción. `PAPER_ONLY=true` es obligatorio: nadie ejecuta órdenes ni se conecta a brokers.
>
>Estado actual (verificado):
> - Dashboard autocontenido `daily_pilot/dashboard/index.html` (generado por `daily_pilot/scripts/generar_dashboard.py`), abre con `file://`, sin fetch.
> - Knowledge Store SQLite `daily_pilot/knowledge/store.db`: 21 vídeos, 17.462 cues, 3.802 claims (tabla `claims`, columna `temporalidad`).
> - Risk Manager aislado `daily_pilot/risk_manager/risk_manager.py` (19/19 tests).
> - Métricas `daily_pilot/metrics/metrics.py` (10/10). Relaciones `daily_pilot/relaciones/relaciones.py`. Escenarios `daily_pilot/escenarios/`. Seguimiento `daily_pilot/seguimiento/`.
> - Tests totales 69/69.
>
> IDEA QUE QUEREMOS EVALUAR (investigación, no implementación todavía):
> 1. Un "analista de mercado" experto en la estrategia de CreceTrader (price action / SMC: zonas, liquidez, order blocks, FVG, BOS/CHoCH) que **calcule niveles** sobre datos reales.
> 2. Que pueda **leer gráficos de TradingView** (o equivalente) y extraer niveles/zonas.
> 3. Integrar un **gráfico simulado** en el dashboard (velas + niveles + zonas), **no en vivo**, claramente etiquetado.
> 4. **Backtest + forward test + Monte Carlo** sobre la estrategia.
> 5. Que se **combine con el analista de YouTube** (claims diarios) para robustecer el sistema y mejorar las probabilidades por fase de mercado (diario/semanal + 4H/1H para entradas).
>
> Repositorios a tener en cuenta (verificados por mí):
> - `joshyattridge/smart-money-concepts` (MIT) — SMC/ICT: order blocks, FVG, BOS/CHoCH.
> - `LuxAlgo/Vela` (Apache-2.0) — lógica de zonas/liquidez.
> - `tradingview/lightweight-charts` (Apache-2.0) — gráfico para el dashboard.
> - `QuantConnect/Lean` (Apache-2.0) — backtest/forward serio. Alternativa `jesse-ai/jesse` (MIT).
> - `pdj555/monte-carlo` (MIT) / `carlowenbelen/trading-strategy-monte-carlo` (MIT) — Monte Carlo.
> - `tradesdontlie/tradingview-mcp` (licencia NOASSERTION, revisar) — leer lo que Pine dibuja.
> - `nessos666/chart-vision-mcp` (MIT) — PoC offline OpenCV+Tesseract.
> - `LPOSP/FinVQA-Chart` — benchmark de visión (9.960 gráficos + 149.400 QA).
> - `TauricResearch/TradingAgents` (Apache-2.0) — arquitectura multi-agente (referente).
> - **Evitar por GPL-3.0**: `freqtrade`, `backtrader`, `ChartQA`.
>
> TU TAREA — **auditoría y propuesta, NO implementes nada todavía**:
> 1. **Audita el código actual** de `daily_pilot/` (generador del dashboard, risk_manager, metrics, relaciones, escenarios, knowledge/store.py, scripts/control_diario.py). Reportá bugs reales con archivo:línea, riesgos de integridad de datos y contratos que no coinciden.
> 2. **Brecha**: qué falta hoy para cada uno de los 5 puntos de la idea (datos, niveles, gráfico, backtest/Monte Carlo, combinación con YouTube).
> 3. **Plan de integración por fases**: qué módulo nuevo, dónde (dentro de `daily_pilot/`), qué dependencia, qué prueba, y qué NO se debe tocar (skill `youtube-trading-agent`, E1 sin backup, scheduler/cron/LaunchAgents, `dashboard_data.json`, `registro.json`, `config.yaml`).
> 4. **Riesgos concretos**: licencias, datos falsos/éticos, backtest sobreajustado, look-ahead bias, fugas de información, y cómo el gráfico simulado evita pasar por real.
> 5. **Estimación honesta**: esfuerzo por fase y qué se puede validar con evidencia.
>
> RESTRICCIONES DURAS:
> - `PAPER_ONLY=true` siempre. Sin órdenes, sin brokers, sin trading real.
> - No modificar la skill `youtube-trading-agent` (locked+pinned).
> - No tocar `cron`, scheduler ni LaunchAgents.
> - No instalar dependencias nuevas sin lista explícita y justificación.
> - No cambiar `qwen2.5vl:3b` ni ningún modelo.
> - No usar servicios externos sin autorización.
> - No hacer commits.
> - Todo en `daily_pilot/`, con backup antes de tocar E1.
>
> Entregá: hallazgos por severidad, plan por fases con pruebas de aceptación, riesgos y una lista de dependencias candidatas con licencia. Si algo no aplica, decilo explícitamente.
