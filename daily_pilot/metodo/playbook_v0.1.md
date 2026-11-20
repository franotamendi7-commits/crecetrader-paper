# PLAYBOOK CreceTrader — v0.1

Fecha: 2026-11-19 · Fuente: `store.db` (**18.562 claims**, 102 videos) + `analisis/*.json`

## Estado de la aprobación (H-01)

**FIRMADO por Francisco el 2026-11-19 (12:13 UTC).**
Declaración: «te digo yo ahora francisco firmo todo! lo aseguro y acredito!»

Artefacto de la firma: `daily_pilot/metodo/FIRMA_C01_C12.md`, con el sha256 de **esta versión**:
`b4db713f392f9a17f1a60d97346ad5c3f02dda3a28bcfb20caecf2415562568a`.

- `aprobado_por_francisco` — **estado de las 12 reglas (C01–C12).**
- Si el playbook cambia, la firma **queda anclada a ese hash** y hay que **re-firmar**.
- `aprobado_por_francisco` — regla **firmada formalmente** (fecha + canal + firma explícita).
- `propuesto` / `a_validar` / `rechazado` — sin aprobación.

> **El registro ya existe** (la conversación). Lo que no hay es una **firma separada**; el chat del
> 2026-11-18 **es** el registro. Si Francisco quiere una firma formal adicional, se añade.

## Cómo validar
Marcá cada regla con: **de acuerdo** / **no** / **matiz: …**
Sin tu marca, queda `propuesto` o `a_validar`. Pasa a `aprobado_por_francisco` solo con tu firma.

## Reglas

| id | nombre | TF | estado | tu marca |
|---|---|---|---|---|
| C01 | Tendencia / marcos (semanal manda) | W→D→4H | **aprobado_en_conversacion** (long 5% en 2-3 entradas, corrección 1-2%) | ✅ |
| C02 | Ejecución: descuento vs confirmación | D | **aprobado_en_conversacion** (30% oferta / 70% confirmación en 2 tramos; solo 5 pares en oferta) | ✅ |
| C03 | Estructura 4H / cambio de fase | 4H | **aprobado_en_conversacion** (fase 3 = corrección; 4H+diario = long) | ✅ |
| C04 | Niveles intradía (abanico) | 1H | **aprobado_en_conversacion** (scalping, no confirmación; 9 niveles ±0.25) | ✅ |
| C05 | Zonas calculadas (Fibonacci) | W/D/4H | **aprobado_en_conversacion** (retrocesos 50/61/78 · extensiones 50/100/150/200 · no es S/R ni OB/FVG) | ✅ |
| C06 | Liquidez institucional | 4H/intradía | **aprobado_en_conversacion** (fibo + 1 de enero + pools; sesión NY) | ✅ |
| C07 | Régimen (tendencia/rango/reversión) | W/D/4H | **aprobado_en_conversacion** (3 regímenes; corrección dentro de tendencia; «supera y consolida») | ✅ |
| C08 | Invalidación (no-ocurrencia del cambio) | TF entrada | **aprobado_en_conversacion** (cierra posición, espera escenario nuevo) | ✅ |
| C09 | Objetivos / toma parcial | W/D/4H | **aprobado_en_conversacion** (4 extensiones C05 · 25% c/u · stop a break even) | ✅ |
| C10 | Escenarios por confianza | todas | **aprobado_en_conversacion** (confianza %; CAUTELA en corrección; stop+BV) | ✅ |
| C11 | Gestión de riesgo | entrada | **aprobado_en_conversacion** (riesgo = confianza, tope 5%) | ✅ |
| C12 | Order block / FVG / BOS-CHoCH | 4H/1H | **aprobado_en_conversacion**: OB = zona de liquidez, **por timeframe** | ✅ |

## Detalle

### C01 · Tendencia / marcos temporales — **aprobado_en_conversacion** (2026-11-18)
> «Lo que le decís "sesgo" es **tendencia** en realidad. La tendencia la determina en mayor medida el **semanal**.
> Un cambio de tendencia en semanal **no es lo mismo** que una micro tendencia dentro del diario.»

- **Modelo de Francisco**:
  - **BTC ejemplo**: semanal en **tendencia alcista**; diario en **corrección bajista** → corrección
    **sin cambio de tendencia** en el semanal.
  - **Se opera intradía** si hay oportunidades en bajista, pero se **holdea el long alcista**.
  - Las operaciones diarias bajistas **sirven para encontrar las mejores zonas de compra** y seguir en long.
- **Distribución de riesgo (refina C11)**:
  - Operación de **corrección**: **1–2%**.
  - Operativa **long**: **5%**, **distribuido en 2–3 entradas** (el precio siempre tiene 2–3 zonas donde buscar liquidez).
- **Implementación**: `Signal.tipo_operacion ∈ {long, correccion}` + `Config(riesgo_correccion_pct=0.015, riesgo_long_pct=0.05, entradas_long=2..3)`.
- **Aplicación**: `core/manager.py`, `risk_manager/risk_manager.py`.

### C02 · Ejecución: descuento vs confirmación — **aprobado_en_conversacion** (2026-11-18)
> «En **precio de descuento** sí se compra, aunque no sepamos cuándo confirma la tendencia. Eso es una
> **zona enorme de liquidez**. Se compra el **descuento** y se opera el **cambio de tendencia**.»

**Modelo de Francisco** (ejemplo con 100 USD = el 10% de una cartera de 1.000 USD):
- **30% en oferta/descuento** → p.ej. 30 USD.
- **70% en confirmación** → **2 tramos de 35%** (35 + 35), p.ej. en **69.000 y 71.000**.

**Reglas derivadas**:
- **Zona de oferta** = zona de liquidez grande → **sí se compra**, sin confirmación.
- **Zona de confirmación** = cambio de tendencia → completa el **70%** restante.
- **Universo de oferta**: **las 5 del proyecto** (BTCUSD, ETHUSD, SPX, QQQ, XAUUSD) — **todas se compran en oferta**.
  Cualquier otro activo → **solo en tendencia**.
  *(Corrección de Francisco: «las 5 que usamos se compran todas en oferta».)*
- **Acciones sin baliu enorme / desconocidas** → **no se compran en oferta**.

**Asignación máxima por activo** (después, con Risk Manager):
- **BTC**: hasta **30–45%** de la cartera.
- **SPX**: hasta **10%** — **también se compra en oferta** (corrección de Francisco).
- **ADA / criptos cualquiera**: no aplican las normas de BTC.

**Implementación**: `core/allocacion.py` (`ALLOCATION_MAX`, `OFERTA_UNIVERSE`, `GASTO_OFERTA_PCT=0.30`).

### C03 · Estructura 4H / cambio de fase — **aprobado_en_conversacion** (2026-11-18)
> «La **fase número tres** ahora es la **fase de corrección**. Para que sea alcista tenemos que, por ejemplo
> en **4H**, ver que el precio **recupera** y empieza a tener máximos crecientes. Una vez que tenemos
> **cambio de fase en 4H con niveles calculados alcanzados**, empezamos a tomar **decisiones de entrada**.
> Si en 4H hay **cambio de tendencia con máximos crecientes** ya tenemos **señal**, y si el **diario lo confirma**
> entramos **long**, porque se juntan **precios calculados y zonas de compras»**.

- **Implementación**: `core/confluencia.py` — `evaluar(cambio_fase_4h, niveles_calculados_alcanzados,
  confirmacion_diaria, zona_de_compra)`.
- **Vocabulos**: el corpus dice **«fase número tres»** (5 claims) y **«recuperación»** (78 claims);
  «máximos crecientes/decrecientes» es **término del experto** (0 claims) → se registra como su equivalente.
- **PREGUNTA ABIERTA** — **RESUELTA por Francisco (2026-11-18)**:
  > «En la imagen tenés **mínimos decrecientes**, sin reversión todavía. Solo cuando el precio esté
  > **por encima de esa vela roja con una vela verde en 4H** va a ser cambio de tendencia,
  > **pero no confirmado**: se necesitan **dos velas más** para que ya tengas **dos máximos crecientes**.»
- **Secuencia exacta (implementada en `core/confluencia.secuencia`)**:
  `CORRECCION (mínimos decrecientes) → RANGO → RUPTURA (vela verde sobre la roja)
  → CAMBIO_NO_CONFIRMADO (1 vela verde) → CONFIRMADO (2 máximos crecientes)`.
  Lo que antes escribí como «máximo decrecientes» era **mínimos decrecientes**.

### C04 · Niveles intradía (abanico) — **aprobado_en_conversacion** (2026-11-18)
> «Cuando CreceTrader habla de **intradía** es porque marca unos **9 niveles** de precios donde comienza
> el precio en el día. En mi caso **hora 9 de la noche**: ahí marca el **punto cero**. Tira
> **Fibonacci pero distinto** al que conocemos: lo lleva de **0 a -1 y a 1**, escala de **0.25** cada uno
> (0.25, 0.50, 0.75, 1.00) y así con los negativos. Esos son los valores intradía donde el precio se
> puede **negociar** durante el día, y **al otro día se vuelve a 0** con el valor del precio a esa hora.
> Es más complejo pero es para **scalping**, no para confirmación de nada con respecto a 4H o a daily.
> Es solo una forma de ver dónde puede estar el precio durante la sesión.»

- **Implementación**: `core/intradia.py` — `abanico(precio_base, paso=0.25, n=4)` → **9 niveles**.
- **Dato NUEVO del experto** (no del corpus): «fibonacci» **0 claims**, «punto cero» **0**, «0.25» **0**,
  «21:00» **0**. El corpus solo tiene **«promedios intradiarios»** (3 claims exactos; «promedio»: 17).
- **Equivalencia registrada**: corpus «promedios intradiarios» ↔ experto «niveles intradía / abanico».
- **Resuelto por Francisco**: son **9 niveles** (hasta ±1.00), no 7.
- **Punto cero (resuelto)**: es el **precio de cierre diario a las 00:00 UTC** — en Argentina son las
  **21 hs**. *«Si BTC a las 21 hs está en 67.000, para todo el día siguiente ese es el precio 0,
  y cada día se mide así.»* → `HORA_ANCLA = 21` · `HORA_ANCLA_UTC = 0`.

### C05 · Zonas calculadas (Fibonacci) — **aprobado_en_conversacion** (2026-11-18)
> «Una zona es un **nivel calculado**. CreceTrader utiliza **fibo normal** para detectar zonas, pero las
> diferencia en **largo, media y corto plazo**: si es a largo plazo se hace en **semanal**, media en
> **diario** y corto en **4H**. **De un mínimo a un máximo** se tira fibo. Las **zonas de compra** están
> en el retroceso de **50, 61 y 78** de fibo, y las **extensiones** están en la **ruptura del máximo** y
> van **50%, 100%, 150% y 200%**. Como se detecta la tendencia: cuando tenemos **máximos mayores**,
> hasta que se termina, cambia a **mínimos menores**, **ahí se tira fibo**. No tiene nada que ver con
> **soportes y resistencias** ni con **orden block / FVG**.»

- **Implementación**: `core/zonas.py` — `zonas(minimo, maximo, plazo)`.
  `RETROCESOS = (0.50, 0.618, 0.786)` · `EXTENSIONES = (0.50, 1.00, 1.50, 2.00)` · `TF_POR_PLAZO`.
- **Criterio de conteo**: claims cuyo texto matchea el regex (case-insensitive, sin anclar).
  **Snapshot: `store.db` 18.562 claims / 102 videos** (2026-11-19).
  Valores reales: `revers` 134 · `correcci[oó]n` 73 · `proyecci[oó]n` 205 · `romp` 208 ·
  `ruptura` 33 · `máximos` 92 · `mínimos` 61 · `rango` 42 · `consolida` 131 ·
  `Nueva York` 163 · `tendencia` 20 · `soporte` 17.
- **Corpus verificado**: «**máximos y mínimos decrecientes**» **sí** aparece (muchos claims, ej.
  `LzPTdClLo_w` 00:02:15 «no voy a comprar»; `bCc--rvyHpY` 00:04:42 «sin señal de reversión»).
  «**extensión**» **sí** (`i0qXzL0eSYs` 00:15:11 «una extensión que iría confirmando la reversión»).
  «**si nos ofertan un 50%**» (`LFHkc5dUoLw` 00:02:19).
- **Vocabulario del experto** (0 claims): «retroceso», «0.618», «0.786», «fibonacci».
- **Dirección (resuelto por Francisco)**: en tendencia **bajista** se calcula **a la inversa** —
  mismo rango, niveles **hacia abajo** (`zonas(..., direccion='bajista')`).

### C06 · Liquidez institucional — **aprobado_en_conversacion** (2026-11-18)
> «La liquidez es **el lugar donde tienen las órdenes los institucionales**. Generalmente ese cálculo se
> hace con la **combinación de un par de cosas**: lo de **fibo** que recién te expliqué, con los
> **precios de comienzo de año** y con los **pools de volumen**, como **order block**. Es complejo,
> pero con eso es suficiente por ahora. **Nueva York es más para el diario**, pero **dentro de la
> sesión de NY** es donde se pueden ir a buscar los **niveles de volumen grande**, donde está la
> **liquidez institucional**.»

- **Implementación**: `core/liquidez.py` — `calcular(zonas_fibo, precios_comienzo_ano, pools_volumen)`.
  `COMPONENTES = ('zonas_fibo_c05', 'precios_comienzo_ano', 'pools_volumen_order_block')` · `SESION = 'Nueva York'`.
- **Corpus verificado**: «**institucional**» **52** claims (ej. `0prmrS6nnRk` 00:07:25 «si el **dinero
  institucional** empieza a entrar ahí»), «**Nueva York**» **54** (ej. `LFHkc5dUoLw` 00:09:34 «las
  compras que entró justo cuando **abrió la sesión de Nueva York**»), «**1 de enero**» **4**
  (`subONxt5iag` 00:09:58 «se preparan **desde el 1 de enero**»).
- **Vocabulario del experto** (0 claims): «pool», «order block».
- **ACLARACIÓN**: el *order block* acá es **ingrediente del cálculo de liquidez**, **no** una zona de
  trading (C05 lo excluye explícitamente). No se mezclan.

### C07 · Régimen: tendencia / rango / reversión — **aprobado_en_conversacion** (2026-11-18)
> **Régimen = tendencia / rango / reversión.**
> - **Tendencia**: máximos y mínimos crecientes (alcista) o decrecientes (bajista).
> - **Rango**: lateralidad («metido en un rango»).
> - **Reversión**: el cambio de régimen (máximos mayores → mínimos menores).
> - **La corrección es parte de la tendencia**, no un régimen aparte.
> - **Confirmación**: el canal dice **«supera y consolida»**.

- **Implementación**: `core/regimen.py` — `detectar(maximos, minimos)`, `es_cambio()`, `supera_y_consolida()`.
- **Corpus**: «reversión» **105**, «fase» **87**, «alcista» **80**, «bajista» **64**, «corrección» **35**,
  «tendencia» **13**, «rango» **13**, «consolida» **14**.
  Ej.: `0prmrS6nnRk` 00:07:18 «una parte de la tendencia que se llama **reversión**»;
  `LFHkc5dUoLw` 00:11:55 «el SP500 está **metido en un rango**»;
  `LzPTdClLo_w` 00:05:42 «comprar si el precio **supera y consolida** los 78.746».
- **Vocabulario del experto** (0 claims): «cambio de tendencia», «lateralidad».
- **Aprobado sin matiz**: «las 3 preguntas se responden solas y están bien».

### C08 · Invalidación — **aprobado_en_conversacion** (2026-11-18)
> «La invalidación es cuando **esperamos que un cambio de tendencia suceda y no sucede**.
> **Se cierra la posición** hasta tener en claro un nuevo escenario.»

- **Implementación**: `core/invalidacion.py` — `evaluar(cambio_de_tendencia_esperado, cambio_ocurrido, escenario_nuevo_claro)`.
  `INVALIDADO → CERRAR POSICION` + `esperar_nuevo_escenario`.
- **ACLARACIÓN**: la invalidación **NO es perder un nivel de precio**. Es la **no ocurrencia del cambio
  de tendencia esperado**. (El corpus usa «si pierde este nivel…» como **activación del siguiente
  escenario**, 42 claims, y «no se ha **invalidado** el escenario», 6.)
- **Stop**: el corpus lo liga a la **liquidez** — `_Lxz34x7eGg` 00:02:31 «vinieron a hacer una
  **cacería de stops**». No se define stop separado de la liquidez.

### C09 · Objetivos y toma de ganancias — **aprobado_en_conversacion** (2026-11-18)
> «Son **siempre los objetivos que dijimos antes** y los del punto 3: las **extensiones** de C05
> (**50%, 100%, 150%, 200%**). La **toma de ganancia es parcial**. Las ganancias se **reparten en
> 25% cada una**. **Cuando se toma ganancia, se sube el stop loss a break even**.»

- **Implementación**: `core/objetivos.py` — `plan(entrada, minimo, maximo)`.
  `EXTENSIONES = (0.50, 1.00, 1.50, 2.00)` · `TRAMOS = 4` × `PCT_TRAMO = 0.25` · stop `break_even` tras el 1º.
- **Corpus**: «objetivo» **233**, «proyección» **108**, «primer/segundo/tercer objetivo» **12/8/11**.
  Ej.: `j06_M-fADjM` 00:01:03 «lo llevó hasta el **primer objetivo**, 78.580»;
  `XLgPycsN0ls` 00:15:33 «**Primer objetivo**, 2245. **Le falta llegar al segundo** si continúa».
- **Conexiones**: objetivos = **extensiones de C05** · stop a break even se apoya en **C08** (invalidación).

### C10 · Escenarios por confianza — **aprobado_en_conversacion** (2026-11-18)
> «Los escenarios deberían ser por la **confianza en porcentaje**. Si tenemos una **zona de compra en
> semanal, diario y 4H** con fibos y precios calculados, **el escenario es validado, compramos**.
> Si en **4H** hay un escenario validado pero **se contradice en semanal y diario**, la **fiabilidad
> es menor, baja el riesgo, pero se puede tradear intradía**. Es **la confianza dentro de las
> posibilidades**. Si tenemos una **corrección dentro de una tendencia alcista**, el escenario es
> **CAUTELA**: estamos en corrección a esos números, pero sabemos que el precio va a ir a buscarlos,
> **por eso es menos riesgo**. Si no llega, igual protegemos con **stop y luego BV** (break even).
> Y nuestro **profit está donde está la zona de compra** para seguir subiendo. **Y así a la inversa**
> si estamos en una tendencia bajista.»

- **Implementación**: `core/escenarios.py` — `evaluar(marcos_confluentes, correccion_dentro_de_tendencia, contradicho)`.
  `CONFIANZA_POR_MARCOS = {3: 1.00, 2: 0.75, 1: 0.50}` · `RIESGO_MAX = 0.05` (C11).
  `VALIDADO` / `MENOR_FIABILIDAD` (+`tradear_intradia`) / `CAUTELA` / `RECHAZADO`.
- **Corpus**: «escenario» **332**, «plan» **172**, «en caso de» **145**, «si el precio» **61**,
  «si pierde» **22**, «si aparece» **9**.
  Ej.: `Vm7nUxLCMZQ` 00:03:22 «**si no**, pues este escenario dicen que está **invalidado**»;
  `bCc--rvyHpY` 00:00:12 «el escenario que seguía estando **validado**».
- **Vocabulario del experto** (0 claims): «condicional», «activación».

### C11 · Gestión de riesgo — **aprobado_en_conversacion** (2026-11-18)
- **Regla de Francisco**: el riesgo por operación **depende de la confiabilidad del escenario** — la confiabilidad define el porcentaje.
- **Tope duro: 5%** de la cuenta. Nunca más, por muy confiable que sea el escenario.
- Ejemplo del corpus: `mv2VdVtXvDw` 00:11:20.839 — «cómo gestionar el riesgo por si el precio no termina de subir».
- Fórmula implementada (H-07): `riesgo = confianza x tope` · tope **5%** (long) / **2%** (corrección) · repartido entre entradas.
- `core/escenarios.py`, `risk_manager/risk_manager.py` y `core/manager.py` usan la MISMA fórmula (test cruzado `tests/test_c11_cruzado.py`).

### C12 · Order block / FVG / BOS-CHoCH — **adoptado por Francisco con redefinición** (2026-11-18)
- **Decisión de Francisco**:
  1. El **order block se adjunta a «zona de liquidez»** — no es zona de soporte.
  2. **Es relativo a la temporalidad**: el OB de 1 día y el de 1H son **zonas distintas**.
  3. Se decide en base a eso.
- **Implementación**: las zonas/niveles **llevan timeframe** (W/D/4H/1H). El mismo precio en distinto
  timeframe es una zona distinta. El corpus ya trae `claims.temporalidad` (E6).
- **Categoría SMC literal** (order block / FVG / BOS / CHoCH): **0 claims** → `NO_DETERMINABLE`.
  No se impone terminología que el canal no usa.
- Equivalentes en su lenguaje: ruptura (**10** claims) · «rompe» (**58**), zona (**216**), liquidez (**106**),
  reversión (**105**), máximos/mínimos (**153**).

## Verificación de este borrador
Ejemplos contrastados contra `store.db`: todos existen (12, 1, 15, 15, 3, 9, 3 claims).
Términos SMC: **0 claims**. El `NO_DETERMINABLE` de C12 es honesto.


---

## ANEXO C05-A — formulacion del fibo (validada 2026-11-20)

**El fibo se tira AL REVES: `0 = MINIMO` y `1 = MAXIMO`.**
Por eso las extensiones (`1 · 1,25 · 1,5 · 1,75 · 2 · 3`) quedan **ARRIBA del maximo**.

```
alcista :  nivel = minimo + rango * r
bajista :  nivel = maximo - rango * r
```

**Niveles**: retrocesos `0,382 / 0,5 / 0,61 / 0,786` · extensiones `1 / 1,25 / 1,5 / 1,75 / 2 / 3`

> **Ojo: es `0,61`, no `0,618`.**

**Validado contra las 3 capturas reales de BNB (2026-11-20)** — 12 niveles exactos:

| TF | tramo | 0,382 | 0,5 | 0,61 |
|---|---|---|---|---|
| **1W** | 537,21 → 1.371,90 | 856,06 | 954,55 | **1.046,37** |
| **1D** | 536,58 → 808,24 | 640,35 | 672,41 | **702,29** |
| **4H** | 530,54 → 809,57 | 637,13 | 670,05 | **700,75** |

**Criterio del tramo**: el **ultimo swing** (maximo y minimo relevantes) — a verificar con
Francisco (`investigacion/TRAMO_SWING_PROPUESTA.md`). Con `n=20` acierta en 1W y 1D.
