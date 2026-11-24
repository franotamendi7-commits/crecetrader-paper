# Auditoría de METODOLOGÍA DE BACKTEST

**Ancla:** `4eaeac6` · **Fecha:** 2026-11-24 · **Modo:** solo lectura y propuesta.
No se instaló nada, no se ejecutó código de terceros, no se tocó `daily_pilot/metodo/` ni la FIRMA.

**Datos de GitHub:** consultados el 2026-11-24 vía `api.github.com/repos/<owner>/<repo>`
(stars, `pushed_at`, `created_at`, licencia, `archived`). Comandos de verificación en el Anexo A.
**Datos del repo:** leídos de los JSON/`.py` locales, sin correr los backtests.

---

## 0 · Resumen ejecutivo

1. **El número +0,599R no está medido sobre 412 observaciones independientes.** Está medido
   sobre **una sola** (short de crypto en una caída de 16 meses). En el artefacto
   `datos/validacion_33_pct_F1.json` **los 27 pares con muestra tienen `dir = "bajista"`**.
   No hay estrategia por par: hay un *short* replicado 27 veces.
2. **El dataset diario no son 3–5 meses de ventana: son 500 velas totales.**
   Las 39 series `1d` arrancan el **2025-07-13** y terminan el **2026-11-24** (16,4 meses).
   Ese techo lo impone el código (`limite=500`), no Binance: la API permite **1000** por request
   y paginar con `startTime`, o sea historia completa desde 2017. **El problema de "pocos datos"
   es autoimpuesto.** En `1w` ya hay 485 velas desde 2017-08-14.
3. **Hay look-ahead en el filtro F1**, el que más mejora el resultado. F1 exige que la vela
   **cierre** a favor del nivel, pero la entrada se ejecuta **al precio del nivel**, que ocurrió
   antes del cierre. Se cobra un precio que no se podía saber que era bueno. Es el sesgo clásico
   de "confirmo con el cierre, entro al mínimo".
4. **El drawdown está calculado en orden no cronológico** (se agrupa por nivel, no por fecha) y el
   **gestor de racha también se aplica en ese orden falso**. Por eso "P2 baja el dd de −10R a −6R"
   no significa nada: se midió sobre una secuencia de trades que nunca existió.
5. **Cada pérdida no resuelta se cuenta como −1R** (stop completo), lo que mezcla "stop" con
   "seguía abierta". Y **no hay fees, ni slippage, ni gap de apertura**.
6. Con la dispersión real entre pares (media 1,059R, sd 1,957R, n=27) el **t clusterizado da
   t≈2,8**; con el número pooled (0,599R) da **t≈1,6**, que no pasa ni el umbral naive de 2,0.
   Y si la unidad de independencia es el régimen de mercado, **n=1**.
7. **Conclusión sobre frameworks:** no conviene migrar el simulador a Lean / Nautilus / freqtrade.
   Conviene **arreglar 8 defectos del propio motor** (~300 líneas) y **tomar prestadas 3 librerías
   como hojas**: `skfolio` (walk-forward + CPCV), `arch` (bootstrap + SPA/Reality Check),
   `statsmodels` (FDR). Todo BSD/NCSA, sin GPL, sin reescribir nada.
8. **"Una estrategia distinta por par" es, con este dataset, una máquina de sobreajuste.**
   La propuesta es: una familia de reglas, parámetros globales, y *gating* por par con
   contracción jerárquica (empirical Bayes). Un par se habilita solo si su expectancy
   *encogida* sigue positiva con n≥30.

---

## 1 · Auditoría del punto de partida (código propio)

Esto va primero porque cambia la interpretación de todo lo demás. Cada defecto tiene archivo y línea.

### 1.1 Defectos que invalidan los números actuales

| # | Defecto | Dónde | Efecto medible |
|---|---|---|---|
| D1 | **Look-ahead en F1**: se filtra por `x['close']` y se entra a `nivel` en la misma vela | `scripts/backtest_afavor.py:154-159`, entrada usada en `:162-179` | Infla la esperanza. Es el filtro que más "mejora" (BTC +0,599R → +1,718R). El resultado de F1 **no es alcanzable en vivo**. |
| D2 | **Drawdown no cronológico**: `ops_planas` se llena en el loop de niveles (`:143`), `resumen` acumula en ese orden (`:116-124`) | `:143-189` | DD subestimado/inconsistente. Concatenar nivel A (todos sus trades) con nivel B rompe la curva real. |
| D3 | **Gestor de racha sobre secuencia falsa**: mismo orden por nivel | `:192-196`; `validar_gestor_33.py:84-92` | El "P2 baja el dd de −10R a −6R" mide una secuencia que no ocurrió. El resultado es un artefacto. |
| D4 | **Sin costos**: 0 fees, 0 slippage, 0 funding, sin gap de apertura | todo el archivo | En 1d con stop 2%, 0,2% ida y vuelta + slippage se comen ~10-20% de la esperanza; en niveles "tocados" el fill optimista es peor. |
| D5 | **No resueltas = −1R**: `oc, hit = -1.0, 'stop'` y si nunca toca nada queda así | `:167` | Confunde "stop" con "abierta". Debe ser mark-to-market al cierre o time-stop explícito. Sesga a la baja y hace incomparables los scripts (`backtest_stop.py` sí usa MtM). |
| D6 | **Un solo tramo para 150 velas**: `tramo_ciclo(v[:inicio],3,60)` y `side` fijo | `:43-57`, `:144` | No es una estrategia: es **una apuesta direccional** repetida en ~6-8 niveles. Genera la pseudorreplicación de D7. |
| D7 | **Ops correlacionadas contadas como independientes** | `:143-189` | Los "412 ops" son ~24 apuestas; los pares además comparten beta cripto. n_eff ≈ 1 régimen. |
| D8 | **Datos no reproducibles**: `velas()` pega a la API en vivo si el cache tiene >5 min y lo sobrescribe | `core/velas.py:26,56,88`; `backtest_afavor.py:39` | Dos corridas con el mismo comando dan datasets distintos. Los artefactos ya no coinciden: el prompt dice 412 ops / 16 de 24 pares; `datos/validacion_33_pct_F1.json` dice **421 ops / 18 de 27** y **27/27 bajista**. |
| D9 | **`min_muestra=5`** para declarar un par "válido" | `:128`, `validar_33.py:44` | Pares con n=2 (ATOM) o n=3 (ETH, esp +6,558R) entran al conteo de "pares positivos". |
| D10 | **Universo declarado ≠ universo corrido**: `PARES` incluye BNB, ALGO, EGLD, FTM y `'SUI'` (ticker inválido) | `validar_33.py:20-25` | Faltan BCH, ETC, POL, SNX, S de la lista de 33; sobran 4 que no están en Quantfury. El "16/24" no es sobre los 33. |

### 1.2 Un detalle estadístico que explica todo lo demás

La distribución de resultados es **lotería**: acierto medio **20,6%** con **factor de beneficio
mediano 1,59** y R objetivo de 3x a 20x (porque el target es el *siguiente nivel* de Fibonacci,
que puede estar lejísimos). Consecuencias:

- La **media** de R por par la determina **1 o 2 trades**. ETH: n=3, esp +6,558R.
  Sacá ese trade y el par es negativo. Eso no es una muestra, es una anécdota.
- Con colas así, el error estándar de la media es enorme y **no es gaussiano**:
  hay que usar bootstrap y mediana recortada, no `mean`.
- El "+0,599R" y el "16/24" son, en la práctica, **"¿a cuántos pares les tocó el trade de 10R?"**.

### 1.3 El cálculo de significancia, hecho bien y hecho mal

Con la dispersión real entre pares del artefacto (media **1,059R**, sd **1,957R**, n=27):

```
naive sobre 421 ops      : SE ≈ 1,5/√421  = 0,073  →  t ≈ 8,2   (falso: pseudorreplicación)
clusterizado por par     : SE ≈ 1,957/√27 = 0,377  →  t ≈ 2,8
con el pooled 0,599R     : SE ≈ 0,377             →  t ≈ 1,59   (p ≈ 0,06, una cola)
unidad = régimen         : n = 1                  →  no estimable
```

El mismo resultado pasa de "evidencia abrumadora" a "no concluyente" según la unidad de
independencia. **Ese es el problema central de esta auditoría**, más que cualquier parámetro.

### 1.4 Lo que está bien y hay que conservar

- `stop_de(..., datos[:i+1])` **no** usa velas futuras para detectar swings (exige `n=3` a la
  derecha ya vistas). La intención es correcta; el problema es el `i` inclusive (D11 menor:
  el ATR usa el cierre de la vela de entrada).
- **Regla conservadora intrabar**: si la vela toca stop y target, gana el stop. Correcto.
  Falta **reportar el % de velas ambiguas** (si es >25%, el resultado depende de esa regla).
- Los niveles y el tramo se calculan **antes** de la ventana de simulación. Eso sí es walk-forward
  de features. Lo que falta es walk-forward de **evaluación**.
- La separación `core/` (cálculo) vs `scripts/` (medición) es una buena base para agregar un
  protocolo sin reescribir el método.

---

## 2 · Repositorios de GitHub (verificados 2026-11-24)

**Criterio de "vivo":** push ≤ 90 días y no archivado. **Criterio de admisión:** ≥ 2 años de
antigüedad, documentación, tests, y no ser solo indicadores ni bot de ejecución.

### 2.1 Los que sirven (5)

| Repo | ⭐ | Último push | Antigüedad | Lic. | Para qué exactamente |
|---|---|---|---|---|---|
| [skfolio/skfolio](https://github.com/skfolio/skfolio) | 2.671 | 2026-11-23 | 2023-12 | **BSD-3** | **Lapieza más útil.** Verificado en fuente: `model_selection/` exporta `WalkForward`, `CombinatorialPurgedCV`, `MultipleRandomizedCV`, `optimal_folds_number`. Splitters sklearn-compatibles: se usan con *cualquier* estimador, no obliga a su motor de portfolios. |
| [bashtage/arch](https://github.com/bashtage/arch) | 1.696 | 2026-11-21 | 2014-08 | NCSA | **Significancia y bootstrap.** Verificado en `arch/bootstrap/__init__.py`: `StationaryBootstrap`, `CircularBlockBootstrap`, `optimal_block_length`, `SPA`, `RealityCheck`, `StepM`, `MCS`. Es White (2000) y Hansen (2005) listos para usar. |
| [statsmodels/statsmodels](https://github.com/statsmodels/statsmodels) | 11.764 | 2026-11-24 | 2011-06 | BSD-3 | `multipletests` (Benjamini-Hochberg / FDR), test de proporciones, IC. Para el problema de 33 pares × N variantes. |
| [QuantConnect/Lean](https://github.com/QuantConnect/Lean) | 22.684 | 2026-11-24 | 2014-11 | Apache-2.0 | **No para ahora.** Es el motor de referencia si algún día se necesita cartera multi-activo, funding, tipos de orden y paridad paper/live. C#/Python, curva de aprendizaje alta. |
| [nautechsystems/nautilus_trader](https://github.com/nautechsystems/nautilus_trader) | 31.779 | 2026-11-24 | 2018-06 | LGPL-3.0 | Alternativa moderna a Lean (Rust+Python), event-driven, crypto-first. Mismo veredicto: sobreingeniería para 33 pares en 1d. LGPL es OK para uso interno (no copiar código al repo). |

### 2.2 Los que sirven solo como referencia metodológica (no como dependencia)

| Repo | ⭐ | Último push | Lic. | Qué copiar (la idea, no el código) |
|---|---|---|---|---|
| [freqtrade/freqtrade](https://github.com/freqtrade/freqtrade) | 57.219 | 2026-11-24 | **GPL-3.0** | Tiene dos comandos que deberíamos imitar: `lookahead-analysis` y `recursive-analysis` (docs verificadas en el repo). El primero detecta automáticamente el sesgo D1 de nuestra lista. **GPL: solo referencia, no copiar.** |
| [stefan-jansen/machine-learning-for-trading](https://github.com/stefan-jansen/machine-learning-for-trading) | 22.033 | 2026-11-22 | MIT | Código de libro con capítulos de purged CV, embargo y backtest. Bueno para entender, no para importar. |
| [robcarver17/pysystemtrade](https://github.com/robcarver17/pysystemtrade) | 3.641 | 2026-11-02 | **GPL-3.0** | **La mejor referencia de position sizing y vol targeting** que existe en abierto (Carver). Futuros, no crypto; GPL. Se lee, no se copia. |
| [ranaroussi/quantstats](https://github.com/ranaroussi/quantstats) | 7.911 | 2026-11-02 | Apache-2.0 | Reporte de métricas (Sharpe, Sortino, DD, rachas). Cosmético; se puede usar o reimplementar en 40 líneas. |
| [polakowo/vectorbt](https://github.com/polakowo/vectorbt) | 9.929 | 2026-11-11 | Apache-2.0 + **Commons Clause** | Barridos vectorizados rápidos. **Dos problemas:** (a) la Commons Clause prohíbe vender el software; (b) vectorizar un stop/target intrabar es exactamente donde se cuela look-ahead. No lo usaría para *este* motor. |

### 2.3 Descartados, y por qué (esto es la mitad del valor del informe)

| Repo | ⭐ | Push | Motivo de descarte |
|---|---|---|---|
| [mementum/backtrader](https://github.com/mementum/backtrader) | 23.797 | **2024-08-19** | 27 meses sin actividad. GPL-3.0. Falla el criterio de "vivo". |
| [hudson-and-thames/mlfinlab](https://github.com/hudson-and-thames/mlfinlab) | 4.977 | **2023-10-02** | Es *la* implementación canónica de purging/CPCV, pero lleva 3 años parada, licencia propietaria/no declarada (`NOASSERTION`) y las versiones libres ya no se mantienen. **Idea sí, dependencia no.** |
| [esvhd/pypbo](https://github.com/esvhd/pypbo) | 146 | 2026-07-06 | AGPL-3.0. El README dice literalmente `TODO: Add test cases`. Y es de 2018, sin actualizar los papers. Útil como fórmula, no como dependencia. |
| [quantskills/skill-backtest-overfit](https://github.com/quantskills/skill-backtest-overfit) | 42 | 2026-11-05 | Creado 2026-07. **4 meses de vida**, GPL-3.0. No cumple antigüedad. |
| [eslazarev/purged-cross-validation](https://github.com/eslazarev/purged-cross-validation) | 65 | 2026-11-22 | Creado 2026-05. **6 meses**. Técnicamente prometedor (MIT, sklearn-compatible, purging+embargo+CPCV), pero no pasó el filtro de 2 años. **Vigilar, no depender.** |
| [carlowenbelen/trading-strategy-monte-carlo](https://github.com/carlowenbelen/trading-strategy-monte-carlo) | **0** | 2026-09-30 | Creado 2026-05, 0 estrellas, sin tests. Y lo que hace son ~40 líneas de `numpy.random.choice`. |
| [mrbcuda/pbo](https://github.com/mrbcuda/pbo) | 51 | **2022-05-26** | 4,5 años parado. |
| [kernc/backtesting.py](https://github.com/kernc/backtesting.py) | 9.289 | 2026-08-05 | AGPL-3.0, un solo activo, sin cartera, sin walk-forward. No encaja. |
| [quantopian/alphalens](https://github.com/quantopian/alphalens) | 4.524 | **2024-02-12** | 2,8 años parado. Además es análisis de factores, no backtest. |
| [microsoft/qlib](https://github.com/microsoft/qlib) | 50.540 | 2026-11-04 | Excelente, pero para equities/China. Sin capa crypto. |
| [AI4Finance-Foundation/FinRL](https://github.com/AI4Finance-Foundation/FinRL) | 17.174 | 2026-11-18 | RL + live trading. Fuera de alcance y con riesgo de sobreajuste mucho mayor. |
| [blankly-finance/blankly](https://github.com/blankly-finance/blankly) | 2.486 | **2024-12-30** | 23 meses sin push. LGPL. |
| [jesse-ai/jesse](https://github.com/jesse-ai/jesse) | 8.831 | 2026-11-23 | **No lo descarto por calidad** (MIT, vivo, crypto). Lo descarto porque exige reescribir la estrategia en su API y no aporta nada que no tengamos para un motor de barras con stop/target. Si algún día se quiere un segundo motor independiente, es el candidato MIT. |
| [edtechre/pybroker](https://github.com/edtechre/pybroker) | 3.728 | 2026-11-23 | Tiene walk-forward nativo y es serio, pero **Commons Clause** y orientado a ML. Mismo argumento que jesse. |
| [robertmartin8/PyPortfolioOpt](https://github.com/robertmartin8/PyPortfolioOpt) | 6.182 | 2026-07-07 | Optimización de cartera, **no** position sizing por trade. No resuelve Kelly. |
| [TonyMa1/walk-forward-backtester](https://github.com/TonyMa1/walk-forward-backtester) | 13 | 2025-03-24 | 13 estrellas, 1,7 años, sin tracción. El walk-forward son 30 líneas; no vale la dependencia. |
| [Lumiwealth/lumibot](https://github.com/Lumiwealth/lumibot), [51bitquant/howtrader](https://github.com/51bitquant/howtrader), [gbeced/basana](https://github.com/gbeced/basana) | 2.252 / 973 / 878 | activos | Ejecución en vivo / brokers. Fuera de alcance PAPER_ONLY y sin metodología de validación. |

**Lectura del descarte:** el ecosistema de "Monte Carlo / deflated Sharpe / PBO" en GitHub son
**repos de 0–65 estrellas creados en 2026**. Ninguno tiene 2 años, tests y tracción a la vez.
Eso no es un problema: **son 30–60 líneas de numpy cada uno**, y las fórmulas están publicadas.
La conclusión práctica es que **no hay nada que valga la pena instalar en esa categoría**.

### 2.4 ¿Y Kelly / position sizing?

No existe un repo dedicado que pase el filtro. Y está bien: **Kelly no es lo que necesitamos
todavía**. Kelly óptimo requiere `p` (probabilidad de acierto) y `b` (payoff) **estables**.
Con acierto 20% y R de 3–20x, el `p` estimado tiene un IC de ±10 puntos: **Kelly con `p` mal
estimado sobreapuesta y quiebra**. La literatura (Thorp, *The Kelly Criterion in Blackjack,
Sports Betting, and the Stock Market*, 2006) es explícita: se usa **medio Kelly o menos** y solo
con `p` bien conocido. Acá no lo tenemos. Ver §4.4 y §6.

---

## 3 · Protocolo mínimo exigible

Diseñado para *este* caso: 33 pares, reglas de niveles, 1d/4h/1w, PAPER_ONLY, un solo operador.
Cada punto tiene su justificación; no hay nada decorativo.

### 3.1 Datos — la raíz del problema (resolver primero)

| Requisito | Número | Justificación |
|---|---|---|
| Historia por par | **desde el listing** (BTC/ETH ≥ 8 años; alts lo que haya) | La API de Binance permite `limit=1000` y paginar con `startTime` (doc oficial verificada). Con 500 velas solo se ven 16 meses = 1 régimen. |
| Ventana mínima para *decidir* | **≥ 4 años o ≥ 1 ciclo completo bull+bear** | Un edge que solo existe en un régimen no es un edge. Con 4 años entran al menos 2 regímenes. |
| Pares con < 3 años | marcar **`exploratorio`**, no asignarles riesgo | ONDO, S, TON, ARB, OP no tienen historia para concluir nada. Se reportan aparte. |
| Snapshot congelado | `parquet` + **sha256** + fecha de descarga, versionado en git | Elimina D8. Sin esto, ningún resultado es reproducible ni auditable. |
| Universo | USDT spot, **mediana de volumen diario > $5M** | Evita que el slippage se coma el edge en alts ilíquidas. |
| Supervivencia | incluir pares **delistados/renombrados** (FTM→S) | Si solo se testean los que sobrevivieron, el resultado está sesgado al alza. |
| Costos | fee **0,10% por lado** + **slippage = 1 tick o 0,05%** + **gap de apertura** | En 1d con stop 2%, ida y vuelta ≈ 0,25% = 12% del riesgo. Si el edge no sobrevive a eso, no es edge. |
| Fills | si la vela **abre más allá** del nivel, entra al **open**, no al nivel | Un limit "en el nivel" cuando el precio saltó es un fill imaginario. |

**Acción concreta:** reemplazar `limite=500` por un `fetch_historico(par, tf)` paginado, con
`startTime` desde el listing, y guardar snapshot inmutable. Es ~40 líneas en `core/velas.py`.
No cambia el método; cambia el tamaño de la muestra de 500 a 2.000–3.000 velas diarias.

### 3.2 Walk-forward

La estrategia tiene **poquísimos parámetros** (stop 2%, `detalle`, `min_velas`, niveles).
El sesgo dominante **no** es el ajuste de parámetros: es la **selección entre variantes y pares**
(ver §3.4). Aun así, hace falta WF formal para medir estabilidad temporal.

| Decisión | Elección | Por qué |
|---|---|---|
| Tipo | **Rolling** (ventana fija), no anchored | Anchored arrastra regímenes viejos y hace que el OOS temprano pese distinto que el tardío. Rolling mantiene el test comparable. |
| Ventana de calibración | **3 años** (o 40% de la historia, lo que sea mayor) | Suficiente para ver un bull y un bear; más corto no contiene régimen. |
| Paso | **6 meses** (o `ventana/6`) | Da ≥ 4–6 folds con 4 años. Paso = ventana genera 1 fold: inútil. |
| Test | **6 meses** inmediatamente después, sin solape | Con holding máximo H, **purgar H+1 velas** entre train y test y **embargo de 1%** del sample (López de Prado, *AFML*, cap. 7). |
| Nested | sí, si se optimiza algo: **WF externo para evaluar**, WF interno para elegir | Evita que la selección de parámetros vea el test. |
| Reporte | **por fold**, no solo el agregado | 6 folds con 4 positivos y 2 negativos es información; un promedio lo esconde. |

**Umbral:** walk-forward efficiency `WFE = expectancy_OOS / expectancy_IS ≥ 0,5`
y **≥ 60% de folds OOS positivos**. Con menos, el "edge" es del período de calibración.

### 3.3 Monte Carlo — qué sí y qué no

Hay cuatro usos distintos y **solo uno valida el edge**:

| Uso | Qué responde | Cómo | Cuándo |
|---|---|---|---|
| **(a) Null sintético** ⭐ | **¿el edge es real o es geometría del método?** | Generar 1.000 series con **random walk** calibrado a la vol/autocorrelación del par (bootstrap por bloques de retornos) y correr **la misma regla**. Comparar la esperanza real contra la distribución nula. | **Siempre, antes de creer cualquier resultado.** Es el "test contra random" que falta. |
| (b) Bootstrap de trades (i.i.d.) | dispersión del DD si el edge es el observado | `np.random.choice(outs, n, replace=True)`, 10.000 rutas | Solo después de (a) y del OOS. |
| (c) Bootstrap estacionario / por bloques | lo mismo pero preservando autocorrelación y clusters | `arch.bootstrap.StationaryBootstrap` / `optimal_block_length` | Preferible a (b), que es demasiado optimista. |
| (d) Ruina | P(perder X% del capital) con un sizing dado | rutas de equity con riesgo fijo por trade + regla de stop-out | Para dimensionar, no para validar. |

**Lo que Monte Carlo NO hace:** no arregla un backtest malo, no convierte un +0,2R en evidencia,
y **no sustituye el out-of-sample**. Es cuantificación de riesgo de camino, no prueba de edge.

**Umbrales:** `P(maxDD > 20R) ≤ 10%` · `P(ruina con 0,5%/trade) ≤ 1%` ·
**percentil 5 de la esperanza del null sintético < esperanza real** (o sea, p < 0,05 empírico).

### 3.4 Sobreajuste con 33 pares y pocos datos

Este es el punto donde hay que ser duro, porque es el que más plata cuesta.

1. **Contar los intentos y escribirlos.** Ya se probaron F1/F2/F3, P1/P2/P3, 5 tipos de stop,
   varios `detalle`, 33 pares. Son **cientos de configuraciones**. El máximo Sharpe esperado
   *por azar* crece con `√(2·ln N)`. Cualquier métrica hay que **deflactarla por N** (Deflated
   Sharpe Ratio, Bailey & López de Prado 2014) o directamente **no mirar el mejor**.
2. **Pre-registro.** Antes de correr: escribir la regla exacta, el universo, la métrica primaria
   (una sola) y los umbrales. Se guarda con hash. Todo lo que se pruebe después es
   **exploratorio** y no cuenta como evidencia.
3. **Holdout de pares, no solo de tiempo.** Desarrollar en 16 pares, **no tocar** 17. Eso testea
   lo que realmente se afirma ("la regla generaliza"), no "esta serie tenía tendencia".
4. **Holdout temporal final**: los **últimos 12–18 meses** no se miran hasta el final. Se usan una vez.
5. **Contracción jerárquica en vez de "una estrategia por par"**. Modelo normal-normal
   (empirical Bayes) sobre la esperanza por par: cada par se encoge hacia la media del grupo
   según su n. Un par con n=3 se encoge casi por completo; uno con n=60 conserva su señal.
   **~25 líneas de numpy**, sin dependencias. Habilitar un par solo si
   `P(edge > 0 | datos) > 0,8` **y** `n ≥ 30`.
6. **Un solo juego de parámetros globales**, normalizado por ATR (para que sea comparable entre
   un par de $0,02 y BTC). Diferencias por par solo si hay una razón *estructural* (tick, liquidez),
   no porque "optimizado da mejor".
7. **Presupuesto de pruebas**: máximo 1 familia de reglas × 1 métrica primaria. Si se quiere
   comparar 5 variantes, se hace con **FDR (Benjamini-Hochberg)** sobre los p-valores, no
   eligiendo el máximo.

**Números de potencia** (σ≈1R, α=0,05 dos colas, potencia 80%): `n ≈ 15,7/δ²`

| edge a detectar | trades independientes necesarios |
|---|---|
| 0,50R | **63** |
| 0,30R | **174** |
| 0,20R | **393** |
| 0,10R | **1.570** |

Con 1d y ~15–20 trades por par por año, **un par solo no alcanza ni para detectar 0,3R en 10 años**.
De ahí que la única salida honesta sea **pooling + shrinkage**, no 33 backtests separados.

### 3.5 Métricas y umbrales de decisión

Una sola tabla, con el umbral que decide "esto sirve".

| Métrica | Umbral mínimo | Por qué ese |
|---|---|---|
| **N efectivo** (clusters, no ops) | ≥ 30 por par · ≥ 100 pooled | Por debajo, el IC es más ancho que el efecto. |
| **Expectancy neta** (R, con costos) | **≥ +0,15R** y **IC95% inferior > 0** | 0,15R es el piso para sobrevivir a un DD normal; el IC evita el "mean de lotería". |
| **t clusterizado** (por par/mes) | **≥ 2,5** | Harvey & Liu (2015): con múltiples pruebas, t=2 es demasiado flojo; t>3 para un factor "nuevo". 2,5 es el mínimo para una estrategia pre-registrada. |
| **Deflated Sharpe** | **DSR > 0** con N de intentos **declarado** | Corrige el "mejor de N". Si no se puede contar N, no se puede creer el Sharpe. |
| **PBO** | **≤ 0,20** | P(que la mejor config IS sea peor que la mediana OOS). Por encima de 0,2, es ruido. |
| **WFE** | **≥ 0,50** | Si OOS rinde la mitad o menos, no hay estabilidad. |
| **Folds OOS positivos** | **≥ 60%** y ≥ 3 de 4 | Un fold bueno no es una estrategia. |
| **Max DD (realizado y MC p95)** | ≤ **15R** · `P(DD>20R) ≤ 10%` | Es el problema declarado; hay que ponerle número. |
| **P(ruina)** a 0,5%/trade | ≤ **1%** | PAPER_ONLY, pero el sizing se diseña igual. |
| **Concentración** | top-3 trades ≤ **50%** del P&L | Si 3 trades hacen todo, es un lotto, no un edge. |
| **Robustez a costos** | expectancy ≥ **0,7×** con costos ×2 y entrada 1 barra tarde | El fill optimista y el look-ahead mueren acá. |
| **Robustez a parámetros** | variación < **30%** en una grilla ±25% de cada parámetro | Un pico aislado es sobreajuste; una meseta es señal. |
| **Ambigüedad intrabar** | reportar % de velas que tocan stop y target | Si > 25%, el resultado depende de una regla arbitraria. |

**Regla de decisión:** un par se habilita solo si pasa *todas* las filas de N, expectancy, t y
robustez. La estrategia global se habilita si pasa DSR, PBO y WFE. **No hay "casi pasa".**

---

## 4 · Recomendación concreta

### 4.1 ¿Framework existente o el nuestro?

**El nuestro, arreglado. No migrar el motor.** Argumentos:

1. La regla es **path-dependent intrabar**: en la misma vela puede tocar stop y target, y la
   resolución importa. Ese es el caso que los motores vectorizados manejan mal y los
   event-driven manejan bien pero con 10× el código y un adaptador de datos propio.
2. El simulador actual son **~200 líneas** y ya tiene la lógica correcta (stop conservador,
   swings sin futuro). Los defectos D1–D10 son **corregibles en un día**, no son de arquitectura.
3. Migrar a Lean/Nautilus implica: reescribir el método en su API, adaptar datos a su formato,
   aprender su modelo de ejecución, y **perder la trazabilidad con `metodo/` y la FIRMA**.
   El costo es de semanas y el beneficio es cero para 33 series diarias.
4. `freqtrade`/`jesse`/`pybroker` están pensados para **señales por indicador**, no para
   "niveles calculados sobre un tramo con target al siguiente nivel". Forzar el método a su
   abstracción es donde se introducen los bugs.

**Lo que sí conviene tomar de afuera (3 dependencias, todas permisivas):**

```
Datos/snapshot   : stdlib + pandas/parquet (ya está)      # paginar Binance, sha256
CV / WF / CPCV   : skfolio.model_selection (BSD-3)        # WalkForward, CombinatorialPurgedCV
Bootstrap / tests: arch.bootstrap (NCSA)                  # StationaryBootstrap, SPA, RealityCheck
Múltiples tests  : statsmodels.stats.multitest (BSD-3)    # FDR (Benjamini-Hochberg)
Reporte          : opcional quantstats (Apache-2.0)       # o 40 líneas propias
```

Nada de GPL en el camino crítico. Nada de reescribir. **Cero instalaciones nuevas fuera de
`skfolio` y `arch`**, y ambas son reemplazables por 60 líneas si se prefiere no depender.

**Cuándo sí migraría:** el día que se necesite (a) cartera multi-activo con márgenes y funding,
(b) paridad exacta paper/live, o (c) más de ~50 activos con órdenes limit complejas.
Ahí el candidato es **Nautilus** (LGPL, crypto-first) o **Lean** (Apache-2.0, más maduro).

### 4.2 Plan de implementación (6 fases, cada una con criterio de salida)

**Fase 0 — Reparar el motor (1–2 días). Sin esto, todo lo demás mide ruido.**
1. Snapshot inmutable de datos + paginación hasta el listing (D8). Sha256 en el nombre.
2. Borrar/aislar F1 o **entrar al cierre de la vela de confirmación** (D1). Reportar ambas.
3. Ordenar trades **por timestamp de entrada** antes de DD y de gestión de racha (D2, D3).
4. Time-stop explícito a H velas + MtM al cierre (D5). Reportar % de ambiguas.
5. Costos: fee 0,10%/lado, slippage 0,05%, fill al open si hay gap (D4).
6. Unificar el universo con los 33 de Quantfury y arreglar `'SUI' → 'SUIUSDT'` (D10).
7. Test de regresión: mismo snapshot → mismo resultado, bit a bit.

> **Criterio de salida:** dos corridas idénticas dan el mismo JSON; el DD es monótono en el
> tiempo; los trades están ordenados por fecha.

**Fase 1 — Línea base honesta en BTC (2 días).**
Correr la regla con historia completa 2017→2026 en 1d, sin filtros, con costos.
**Expectativa: el +0,599R se va a derrumbar.** Ese es el resultado, no un fracaso.
Reportar por año y por régimen (bull/bear/rango).

**Fase 2 — El test que falta: null sintético (2 días).**
1.000 random walks con la vol y autocorrelación de BTC; correr la misma regla; comparar.
Si la esperanza real cae dentro del 90% central del null, **la estrategia no tiene edge**:
lo que se midió es la geometría "target = siguiente nivel" + tendencia del período.
Este test es el que decide si vale la pena seguir.

**Fase 3 — Walk-forward rolling formal (2 días).**
3 años de calibración / 6 meses de test, purga H+1, embargo 1%. Reportar por fold.
Recién acá se puede decir "hay algo".

**Fase 4 — Escalar a 33 pares con jerarquía (3–4 días).**
Pooled primero (un solo juego de parámetros), después shrinkage por par. Holdout de 17 pares
que no se tocan. FDR sobre los p-valores de los 33. Universo declarado = el de Quantfury.

**Fase 5 — Robustez y decisión (2 días).**
Monte Carlo estacionario (DD, ruina), costos ×2, grilla ±25%, DSR con N de intentos contado,
PBO. Documento de pre-registro + veredicto por par (habilitar / observar / descartar).

**Fase 6 — Forward test real.**
3–6 meses en PAPER con la config congelada y **sin tocar parámetros**. Ese es el único OOS
que no se puede sobreajustar. Si en 6 meses el forward se desvía > 1 sd del backtest, se para.

### 4.3 Orden: ¿BTC solo o todos a la vez?

**BTC solo, después 8 majors, después los 33.** Razones:

1. BTC tiene **9 años** de historia diaria; es el único par donde el test de null y el WF tienen
   potencia suficiente para distinguir señal de ruido. Si la regla no pasa ahí, no pasa en ningún lado.
2. Los 33 a la vez **multiplican el problema de selección** por 33 antes de tener el protocolo
   probado. Es la forma más rápida de sobreajustar.
3. Los majors (ETH, SOL, BNB, XRP, ADA, DOGE, LINK, AVAX) tienen ≥ 4 años y alta liquidez:
   sirven para el **holdout de pares** de la Fase 4.
4. Los nuevos (ONDO, S, TON, ARB, OP, INJ, STX…) se reportan como **exploratorios** hasta tener
   ≥ 3 años. No se les asigna riesgo.

### 4.4 Sizing: qué hacer en vez de Kelly

- **Nada de Kelly completo.** Con `p` estimado en 20% ± 10 puntos, el f* de Kelly tiene un IC
  que incluye el sobreapueste. Kelly completo con `p` incierto = ruina por varianza.
- **Riesgo fijo por trade: 0,25–0,50% del capital** hasta que el edge pase DSR + PBO + forward.
  Con DD esperado de 15R, 0,5% ⇒ −7,5%; 1% ⇒ −15%. Ese es el número que importa.
- **Normalización por volatilidad** (riesgo constante en R vía ATR) en vez de tamaño fijo en USD.
- Si más adelante se quiere Kelly: **medio Kelly como techo**, con `p` y `b` calculados sobre
  **≥ 100 trades OOS**, y recortado por el IC inferior de `p`, no por el punto estimado.

---

## 5 · Lo que NO conviene (y por qué)

| No hacer | Por qué |
|---|---|
| **Instalar Lean/Nautilus/freqtrade/jesse para esto** | Semanas de migración, pérdida de trazabilidad con `metodo/`, y cero beneficio para 33 series diarias. El motor propio son 200 líneas reparables. |
| **Usar vectorbt como motor principal** | El stop/target intrabar es justo donde la vectorización introduce look-ahead. Y la Commons Clause restringe el uso comercial. |
| **Adoptar los repos de Monte Carlo / DSR / PBO de GitHub** | Los que existen tienen 0–65 estrellas, nacieron en 2026, o no tienen tests (pypbo: `TODO: add test cases`). Son 40 líneas de numpy. Dependencia sin beneficio. |
| **Usar mlfinlab** | 3 años sin mantenimiento y licencia propietaria. La idea (purging/embargo/CPCV) es la correcta; el paquete no. |
| **"Una estrategia distinta por par" como objetivo** | 33 búsquedas independientes = 33 oportunidades de sobreajustar, con ~20 trades por par. Es el escenario de máxima probabilidad de overfitting. Reemplazar por "una familia + shrinkage". |
| **Seguir con ventanas de 150 velas** | Con 500 velas totales, 150 es el 30% de los datos y cubre un solo régimen. La ventana no es el problema: el total sí. |
| **Bajar a 4h para "tener más muestras"** | Multiplica por 6 las barras pero también el ruido, el costo relativo y la autocorrelación. Da falsa sensación de n. Si se usa 4h, es para *ejecución*, no para *inferencia*. |
| **Kelly completo ahora** | `p` incierto con colas gordas ⇒ sobreapuesta ⇒ ruina. |
| **"Gestor de racha" como solución al DD** | Reduce el tamaño después de perder: baja el DD **y** la esperanza. No agrega edge. Y el resultado actual está medido sobre una secuencia no cronológica (D3). |
| **Reportar el mejor Sharpe de una grilla** | Es el máximo de N ruidos. Sin DSR/PBO no significa nada. |
| **ML / RL (FinRL, qlib) en esta etapa** | Muchos más parámetros que datos. El problema no es el modelo, es el n. |
| **Operar con sizing real antes del forward test** | PAPER_ONLY. El forward es el único OOS honesto que queda. |

---

## 6 · Veredicto en una frase

**No hace falta nada externo para el motor, y casi nada para la estadística.** El problema no es
que falte un framework: es que **el dataset es 10× más chico de lo que debería** (500 velas por
un `limite=500`), **el filtro que más aporta tiene look-ahead**, **el DD y la gestión de racha se
miden en orden falso**, y **los 412 trades son en realidad una sola apuesta direccional en un solo
régimen**. Arreglar eso (≈300 líneas, 2 días), traer historia completa, y agregar null sintético +
WF rolling + DSR/PBO con `skfolio`/`arch`/`statsmodels` es todo lo que se necesita. El resto es
complejidad que no compra información.

---

## Anexo A — Verificación de las fuentes

**GitHub (2026-11-24):**

```bash
curl -s https://api.github.com/repos/skfolio/skfolio | jq '{stars:.stargazers_count,pushed:.pushed_at,created:.created_at,lic:.license.spdx_id}'
curl -s https://api.github.com/repos/bashtage/arch  | jq '{stars:.stargazers_count,pushed:.pushed_at,lic:.license.spdx_id}'
```

Verificación de capacidades en el código fuente (no en el README):

```bash
# skfolio: WalkForward + CombinatorialPurgedCV
curl -s https://raw.githubusercontent.com/skfolio/skfolio/main/src/skfolio/model_selection/__init__.py

# arch: StationaryBootstrap, SPA, RealityCheck, MCS
curl -s https://raw.githubusercontent.com/bashtage/arch/main/arch/bootstrap/__init__.py

# freqtrade: comandos lookahead-analysis / recursive-analysis
curl -s https://raw.githubusercontent.com/freqtrade/freqtrade/develop/docs/lookahead-analysis.md
```

**Binance (doc oficial, verificada):** `GET /api/v3/klines`, `limit` *Default: 500; Maximum: 1000*,
con `startTime`/`endTime` para paginar.
`https://raw.githubusercontent.com/binance/binance-spot-api-docs/master/rest-api.md`

**Datos locales (lectura, sin ejecutar backtests):**

| Hecho | Fuente |
|---|---|
| 39 series `1d` = 500 velas, 2025-07-13 → 2026-11-24 | `daily_pilot/datos/velas/*_1d.json` |
| 1w = 485 velas, 2017-08-14 → 2026-11-23 | `.../BTCUSDT_1w.json` |
| 4h = 500 velas, 2026-09-02 → 2026-11-24 (83 días) | `.../BTCUSDT_4h.json` |
| 27 pares con n>0, 421 ops, 18/27 positivos, acierto medio 20,6%, mediana FB 1,587 | `daily_pilot/datos/validacion_33_pct_F1.json` |
| **27/27 pares con `dir = "bajista"`** | ídem |
| media 1,059R · sd 1,957R · mediana 0,536R | ídem (calculado sobre `por_par`) |

**Referencias metodológicas (publicadas, no repos):**

- López de Prado, *Advances in Financial Machine Learning* (2018), cap. 7 (purging/embargo) y 12 (CPCV).
- Bailey & López de Prado, *The Deflated Sharpe Ratio* (Journal of Portfolio Management, 2014).
- Bailey, Borwein, López de Prado & Zhu, *Pseudo-Mathematics and Financial Charlatanism* (Notices of the AMS, 2014) — PBO y MinBTL.
- White, *A Reality Check for Data Snooping* (Econometrica, 2000); Hansen, *A Test for Superior Predictive Ability* (2005).
- Harvey & Liu, *Backtesting* (Journal of Portfolio Management, 2015) — el umbral t > 3.
- Politis & Romano, *The Stationary Bootstrap* (JASA, 1994).
- Thorp, *The Kelly Criterion in Blackjack, Sports Betting, and the Stock Market* (2006) — Kelly fraccional.

---

## Anexo B — Checklist operativo (para pegar en el próximo prompt)

```
[ ] Datos congelados con sha256 y fecha; paginados hasta el listing
[ ] Universo = los 33 de Quantfury; SUIUSDT, no 'SUI'
[ ] Trades ordenados por timestamp de entrada
[ ] Sin look-ahead: entrada al cierre de confirmación o sin F1
[ ] Time-stop + MtM; % de velas ambiguas reportado
[ ] Fees 0,10%/lado + slippage + fill al open en gaps
[ ] Null sintético (1.000 random walks) antes de cualquier conclusión
[ ] Walk-forward rolling 3a/6m, purga H+1, embargo 1%
[ ] Holdout: 17 pares nunca vistos + últimos 12-18 meses
[ ] Shrinkage jerárquica; n>=30 por par para habilitar
[ ] DSR con N de intentos declarado; PBO <= 0,20
[ ] Costos x2 y entrada +1 barra: la esperanza debe seguir > 0,15R
[ ] Tabla de decisión con TODOS los umbrales de §3.5
```
