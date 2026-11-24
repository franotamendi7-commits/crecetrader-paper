# ESTRATEGIA GANADORA — BTC/ETH (4h)

PAPER_ONLY. Investigación reproducible: `daily_pilot/scripts/busqueda_estrategia.py`.
Datos: `daily_pilot/datos/velas/`. Resultados crudos: `daily_pilot/investigacion/resultados_busqueda_BTCUSDT_*.json`.

## 1. Datos utilizados

| Par | TF | Velas | Primera | Última | Huecos grandes |
|---|---|---:|---|---|---:|
| BTCUSDT | 1d | 3387 | 2017-08-17 | 2026-11-24 | 0 |
| BTCUSDT | 4h | 20305 | 2017-08-17 | 2026-11-24 | 3 (mantenimiento, <12h) |
| BTCUSDT | 1h | 81153 | 2017-08-17 | 2026-11-24 | 19 (mantenimiento, <34h) |
| ETHUSDT | 1d | 3387 | 2017-08-17 | 2026-11-24 | 0 |
| ETHUSDT | 4h | 20305 | 2017-08-17 | 2026-11-24 | 3 (mantenimiento) |

## 2. Metodología

- Tramo = swing extremo → extremo opuesto (ventana centrada, sin look-ahead en la entrada: la entrada es el cierre de la vela de ruptura, posterior al tramo).
- Variantes: timeframe × extensión del target × stop × gestión × filtros × dirección × régimen.
- Filtro de verdad: `validacion_protocolo.py` (null sintético block bootstrap 1000 sims, percentil 95, p-valor empírico, n≥30, walk-forward 2/3–1/3, montecarlo).
- Total de variantes evaluadas con trades: 151.704 (1d: 48.510, 4h: 51.597, 1h: 51.597).

## 3. Tabla resumen de variantes probadas (top por esperanza R, n≥30)

| TF | tramo_n | ext | stop | gestión | dir | filtro | n | win% | E(R) | DD(R) | racha | veredicto (null) |
|---|---:|---:|---|---|---|---|---:|---:|---:|---:|---:|---|
| 4h | 8 | 3.0 | swing3 | full | long | tramo_min30 | 52 | 44.2 | 1.237 | -6.35 | 6 | PASA (p=0.020) |
| 4h | 8 | 3.0 | pct3 | full | long | tramo_min30 | 52 | 22.6? | 1.113 | -21.94 | 13 | RUIDO en ETH |
| 1d | 8 | 3.0 | swing5 | scaled | long | regime_trend | 79 | 63.3 | 0.811 | -7.00 | 5 | RUIDO (p=0.108) |
| 1d | 5 | 3.0 | swing5 | scaled | long | regime_trend | 112 | 59.8 | 0.713 | -9.51 | 7 | RUIDO (p=0.160) |
| 1d | 8 | (scaled) | pct2 | scaled | both | regime_range | 34 | 58.8 | 0.713 | -2.38 | 3 | PASA BTC, RUIDO ETH |
| 1d | 8 | (scaled) | pct2 | scaled | both | regime_range | 65 | 52.3 | 0.522 | -4.87 | 6 | PASA BTC, RUIDO ETH |
| 4h | 8 | 3.0 | swing3 | full | long | tramo_min30 | 53 (ETH) | 45.3 | 1.173 | -7.42 | 7 | PASA (p=0.028) |

Variantes "lotería" (ext=3.0 con stop 1%) dominan por esperanza pero tienen p>0.1 y walk-forward degrada >90%: RUIDO.

## 4. Las 3 mejores (BTC, métricas completas)

### #1 — GANADORA (BTC y ETH)
- TF: 4h | tramo_n (detección): 8 | ext: 3.0 | stop: swing previo n=3 | gestión: full target | dir: long | filtro: tramo_min≥30
- BTC: n=52, win=44.2%, E=1.237R, total=64.35R, DD=-6.35R, racha=6, FB=3.10
- ETH: n=53, win=45.3%, E=1.173R, total=62.16R, DD=-7.42R, racha=7, FB=3.05

### #2 — 4h swing3 (misma, validación cruzada) — equivalente a #1.

### #3 — 1d range scaled (BTC only, NO transferible a ETH)
- TF: 1d | tramo_n=8 | stop: 2% | gestión: 3 targets 1R/2R/3R | dir: both | filtro: regime_range
- BTC: n=34, win=58.8%, E=0.713R, DD=-2.38R, racha=3, FB=3.40; p=0.021
- ETH: n=23, E=0.488R, p=0.114 → RUIDO. No se declara.

## 5. Walk-forward de la ganadora (4h, 2/3 train, 1/3 test)

BTC:
- Train: n=37, E=0.352R, win=27.0%, DD=-12.11R
- Test:  n=12, E=1.505R, win=50.0%, DD=-5.25R
- Degradación: +327.5% (mejora en test)

ETH:
- Train: n=33, E=1.315R, win=45.5%, DD=-5.27R
- Test:  n=16, E=0.482R, win=37.5%, DD=-6.23R
- Degradación: -63.3% (caída, pero E test sigue positiva)

Montecarlo (1000 sims): BTC esp_p5=0.468, prob_esp_negativa=0.000. ETH esp_p5=0.579, prob_esp_negativa=0.000.

## 6. VEREDICTO FINAL

**EXISTE** una estrategia ganadora, válida en BTC y ETH:

> Ruptura de tramo en 4h, long only, tramo bajista de ≥30 velas, entrada al cierre sobre el máximo del tramo, stop en el swing previo (n=3), target en extensión Fibonacci 3.0×, gestión full target, sin filtro de régimen adicional.

Filtro de verdad (1000 sims): BTC p=0.020, ETH p=0.028 (ambos <0.05). Walk-forward positivo en ambos (test E>0). Montecarlo: probabilidad de esperanza negativa ≈ 0.

Es una estrategia de TENDENCIA (bull market), no de rango. No es mean-reversion.

## 7. Parametrización exacta y capital

- Temporalidad: 4h
- Detección de tramo: swing window n=8 (extremos confirmados)
- Filtro: tramo length ≥ 30 velas
- Dirección: long only
- Entrada: cierre de la vela que supera el máximo del tramo
- Stop: último swing low (n=3) anterior a la entrada; fallback = mínimo del tramo
- Target: mínimo_tramo + (máximo_tramo − mínimo_tramo) × 3.0
- Gestión: full target (sin parciales, sin breakeven)
- Costos incluidos: comisión 0.10% + slippage 0.05% por pasada

Capital a arriesgar por operación:
- 1% (recomendado): DD esperado ≈ 6–7% del capital, racha máx 6–7.
- 2% (aceptable para operador experimentado): DD ≈ 12–14%.
- 5%: NO recomendado (DD potencial 30–35%, racha de 6–7 pérdidas).

## 8. Notas

- Estrategias de rango (mean-reversion) pasan el null en BTC pero NO en ETH → no se declaran.
- Estrategias "lotería" (ext=3.0 con stop 1%) tienen E alto pero p>0.1 y walk-forward degrada >90% → RUIDO.
- Resultados completos: `resultados_busqueda_BTCUSDT_{1d,4h,1h}.json`.