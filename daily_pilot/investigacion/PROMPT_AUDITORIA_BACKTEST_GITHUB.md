# Auditoría de METODOLOGÍA DE BACKTEST — repositorios de GitHub

Ancla: `4eaeac6` · Fecha: 2026-11-24
Modo: **solo lectura y propuesta. No ejecutar nada, no instalar nada.**

## Contexto

Tenemos un piloto de trading **PAPER_ONLY** con datos reales de Binance
(velas 1w/1d/4h/1h) para **33 criptomonedas de Quantfury**.

Queremos **una estrategia distinta por par**, y antes de construir nada necesitamos
**la metodología correcta de backtest**: qué se hace bien, qué se hace mal y
qué soluciones ya existen en GitHub.

Ya construimos varios backtests propios (ver abajo). Todos tienen el mismo
problema de base: **pocos datos, muestras chicas, y riesgo de sobreajuste**.

## Lo que ya hicimos (para que veas el punto de partida)

| script | qué mide | resultado |
|---|---|---|
| `backtest_afavor.py` | operar a favor del tramo, con confirmación | +0,599R en 412 ops (24 pares) |
| `validar_33.py` | lo mismo en las 33 criptos | 16/24 pares positivos |
| `validar_gestor_33.py` | gestor de racha | baja dd, no lo cura |
| `backtest_stop.py` | comparativa de stops | R bajo con stop estructural |

**Debilidades que ya conocemos:**
- Ventanas de 90–150 velas diarias (~3–5 meses).
- Una sola TF por corrida (1d).
- Sin walk-forward formal.
- Sin Monte Carlo ni test de significancia.
- Riesgo de que los resultados sean suerte de una ventana.

## Los 33 pares

```
AAVE APT ARB ATOM AVAX BCH BTC DOGE DOT ETC ETH FIL HBAR INJ LINK LTC MANA
NEAR NEO ONDO OP POL RUNE SAND SNX SOL STX THETA UNI XRP S TON ADA
```

(TON está en BREAK en Binance; S = Sonic, ex-FTM.)

## Lo que quiero de vos

### 1 · Repositorios de GitHub — búsqueda concreta

Buscá y **listá los repos relevantes** (con URL, estrellas, última actividad)
sobre:

| categoría | qué buscar |
|---|---|
| **Backtests de crypto** | frameworks serios (vectorizados, sin look-ahead) |
| **Walk-forward / purged cross-validation** | implementaciones de KFX, embargo, purging |
| **Monte Carlo sobre equity curve** | simulación de rutas, probabilidad de ruina |
| **Gestión de riesgo** | Kelly fraccional, position sizing |
| **Análisis de significancia** | tests contra random, deflated Sharpe |

Para cada repo: **URL, estrellas, última vez actualizado, y si está vivo**.

**Descartá** lo que sea:
- solo indicadores (no backtest)
- scripts de trading en vivo
- repos sin tests o sin documentación
- lo que no tenga al menos 2 años de antigüedad y actividad reciente

### 2 · Metodología mínima exigible

Decime, con justificación, el **protocolo mínimo** que deberíamos implementar:

- **Tamaño de ventana** y cuántos años de datos hacen falta.
- **Cómo hacer walk-forward** (anchoring vs rolling, tamaño del paso).
- **Cuándo usar Monte Carlo** y qué nos dice (probabilidad de ruina, peor dd).
- **Cómo evitar el sobreajuste** cuando hay 33 pares y pocos datos.
- **Qué métricas reportar** y con qué umbrales decidir «esto sirve».

### 3 · Recomendación concreta

Con los repos y la metodología:

1. **Qué framework usarías** (si conviene usar uno existente en vez del nuestro).
2. **Plan de implementación**: cómo adaptar nuestros scripts a esa metodología.
3. **Orden**: por dónde empezar (¿BTC solo? ¿todos a la vez?).
4. **Señales de alerta**: qué nos diría que estamos sobreajustando.

## Restricciones

- **No instalar nada** ni correr código de terceros.
- **PAPER_ONLY**: nada de ejecución real.
- No modificar `daily_pilot/metodo/` ni la FIRMA.
- Las fuentes tienen que ser **verificables**: citá URL y fecha.

## Entregable

1. **Tabla de repos** (URL, estrellas, actividad, por qué sirve).
2. **Protocolo mínimo** de backtest con sus umbrales.
3. **Recomendación y plan**.
4. **Lo que NO conviene** (y por qué).

Si encontrás que **no vale la pena usar nada externo** y conviene mejorar el nuestro,
decilo con argumentos. No quiero complejidad innecesaria.
