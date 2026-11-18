# INVESTIGACIÓN — Repositorios para amplificar el diseño (modo investigación, sin cambios)

Fecha: 2026-11-18 · Estado: **solo lectura** · Datos verificados vía API de GitHub (stars/licencia/último push).

---

## A. Price action / SMC / niveles calculados — *lo más cercano a CreceTrader*

| Repo | ⭐ | Licencia | Último push | Aporte y justificación |
|---|---|---|---|---|
| **joshyattridge/smart-money-concepts** | 2.244 | **MIT** | 2026-04-03 | ICT/SMC en Python: order blocks, FVG, BOS/CHoCH, liquidity sweeps, market structure. **Referente directo** del "analista de TradingView": implementa los conceptos que el canal nombra. MIT → reutilizable. |
| **LuxAlgo/Vela** | 1.328 | **Apache-2.0** | 2026-11-17 | Price action (TS): FVG, order block, liquidity; estados *half-fill / fill / sweep / break*. Lógica de detección **reusable como especificación**, aunque sea TypeScript. Muy activo. |
| kxngHADES/SMC-Marking | 47 | NOASSERTION | 2026-11-10 | Marcado SMC. Poca madurez. |
| nashit8421/price-action-lib | 20 | MIT | 2025-09-02 | BOS/ChoCH/FVG. Orientado a bolsa india; útil como idea, no como base. |
| ksu-hmi/Supply-and-Demand-Zones | — | — | — | Detección de zonas S/D. |
| cmike444/SupplyAndDemand | — | — | — | Zonas S/D en TypeScript. |

**Conclusión A**: `smart-money-concepts` (MIT) como **base de niveles calculados** + `Vela` como **especificación de estados** de zona. Ambos cubren lo que CreceTrader dice (zonas, liquidez, FVG) sin necesidad de "adivinar" la estrategia.

## B. Datos de mercado / lectura de gráficos TradingView

| Repo | ⭐ | Licencia | Push | Aporte |
|---|---|---|---|---|
| **tradesdontlie/tradingview-mcp** | 7.229 | **NOASSERTION** ⚠️ | 2026-10-21 | Puente CDP con **TradingView Desktop**: lee lo que un indicador Pine dibuja (líneas horizontales, zonas). **Exactamente "leer gráficos de TradingView"**. Riesgo: licencia no declarada. |
| **nessos666/chart-vision-mcp** | 3 | **MIT** | 2026-06-14 | OpenCV + Tesseract **offline, sin GPU, sin API keys**, detección de niveles/zonas por color. **Encaja con las restricciones** (Mac sin GPU, sin servicios externos). Poca madurez → prueba de concepto. |
| **rongardF/tvdatafeed** | 688 | MIT | 2024-08-08 | Histórico de TradingView (5.000 barras/timeframe) sin login. **Estancado** → validar antes de depender. |
| **ccxt/ccxt** | 44.909 | **MIT** | 2026-11-17 | Datos unificados de exchanges. Para BTC/ETH reales (PAPER_ONLY). Referente de facto. |

## C. Motores de backtest / forward test

| Repo | ⭐ | Licencia | Push | Aporte |
|---|---|---|---|---|
| **QuantConnect/Lean** | 22.577 | **Apache-2.0** | 2026-11-17 | Motor estándar: backtest + **forward/paper**, multi-mercado, Python, institution-grade. **Recomendado como motor serio**. |
| **polakowo/vectorbt** | 9.878 | NOASSERTION ⚠️ | 2026-11-11 | Vectorizado: barridos rápidos de parámetros. |
| freqtrade/freqtrade | 56.997 | **GPL-3.0** ⚠️ | 2026-11-17 | Backtest/walk-forward crypto. **GPL contagioso: solo referencia, no copiar código.** |
| mementum/backtrader | 23.756 | **GPL-3.0** ⚠️ | 2024-08-19 | Clásico, estancado. GPL. |
| jesse-ai/jesse | 8.818 | **MIT** | 2026-11-17 | Backtest + optimización, crypto, activo. |

**Conclusión C**: `Lean` (Apache-2.0) como motor; `jesse` (MIT) como alternativa más liviana. **Evitar freqtrade/backtrader por GPL-3.0**.

## D. Monte Carlo / robustez

| Repo | ⭐ | Licencia | Push | Aporte |
|---|---|---|---|---|
| **pdj555/monte-carlo** | 0 | MIT | 2026-11-15 | Forward simulation + **walk-forward validation**. Activo. |
| **carlowenbelen/trading-strategy-monte-carlo** | 0 | MIT | 2026-09-30 | 10.000 curvas de equity, drawdown, risk-of-ruin, report HTML. |
| aleks-drozy/Trading-Strategy-Monte-Carlo-Simulation | — | — | — | Bootstrap + reordenamiento + drawdown. |

**Conclusión D**: el patrón está claro (bootstrap + reshuffle + curva de equity). Con `Lean` + uno de estos, **Monte Carlo queda cubierto**. No hace falta dependencia nueva si se implementa con `numpy`.

## E. Visualización para el Dashboard (gráfico simulado)

| Repo | ⭐ | Licencia | Push | Aporte |
|---|---|---|---|---|
| **tradingview/lightweight-charts** | 17.891 | **Apache-2.0** | 2026-11-16 | **La librería de TradingView**. Canvas, velas, líneas horizontales (niveles), zonas. **Encaja perfecto con el dashboard `file://`** (JS inline). **Recomendada.** |
| louisnw01/lightweight-charts-python | 2.173 | MIT | 2024-09-28 | Wrapper Python (estancado). |
| plotly/plotly.py | 18.910 | MIT | 2026-11-17 | Alternativa, más pesada. |
| matplotlib/mplfinance | 4.469 | NOASSERTION | 2024-08-08 | PNG estático. Secundario. |

**Conclusión E**: `lightweight-charts` **inline** en el HTML → gráfico simulado con velas + niveles + zonas, sin servidor ni red.

## F. Visión de gráficos (desbloquea E3)

| Repo | ⭐ | Licencia | Aporte |
|---|---|---|---|
| **LPOSP/FinVQA-Chart** | 1 | sin licencia ⚠️ | **9.960 gráficos reales (2020-2024) + 149.400 QA**. Es un **benchmark**, no un motor. Sirve para *evaluar* un modelo con referencia humana (coherente con el criterio "2 anotadores"). |
| vis-nlp/ChartQA | 267 | GPL-3.0 | Benchmark QA de gráficos. |
| khuangaf/Awesome-Chart-Understanding | — | — | Lista curada del estado del arte. |

## G. Arquitectura de agente (referente)

| Repo | ⭐ | Licencia | Push | Aporte |
|---|---|---|---|---|
| **TauricResearch/TradingAgents** | 122.979 | **Apache-2.0** | 2026-11-17 | Multi-agente LLM de trading (analistas + gestores + riesgo). **Referente de arquitectura** para el "analista inteligente". No se usaría directo (APIs de pago), pero sí su separación de roles. |
| merovinh/best-of-algorithmic-trading | 1.038 | CC-BY-SA-4.0 | 2026-11-14 | Mapa curado del ecosistema (120 proyectos). |

---

# Propuesta de arquitectura (INVESTIGACIÓN — no implementada)

```
Datos        : tvdatafeed (histórico) + ccxt (si se quiere exchange)  [PAPER_ONLY]
Niveles      : smart-money-concepts (MIT) + especificación de Vela
Gráfico      : tradingview/lightweight-charts  → inline en el dashboard (simulado)
Backtest/Fwd : QuantConnect/Lean (Apache-2.0)  |  alternativa: jesse (MIT)
Monte Carlo  : numpy propio + patrón pdj555/carlowenbelen
Visión       : FinVQA-Chart como benchmark  ·  chart-vision-mcp como PoC offline
Agente       : patrón TradingAgents adaptado a local
```

## Alertas
1. **GPL-3.0** (freqtrade, backtrader, ChartQA): solo referencia; **no copiar código**.
2. **`tradingview-mcp`** sin licencia declarada → revisar antes de depender.
3. **`tvdatafeed`** estancado (2024-08) → validar.
4. El gráfico del dashboard debe ser **simulado y etiquetado** como tal (no cotización en vivo).
5. `nessos666/chart-vision-mcp` es una **PoC** (3 ⭐), no un producto.
6. Verificación de referencias humanas (2 anotadores) sigue siendo obligatoria para cualquier métrica de visión.
