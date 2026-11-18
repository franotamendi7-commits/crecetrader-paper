# Risk Manager — Especificación Funcional v0

**Fecha:** 2026-11-12
**Estado:** ESPECIFICACIÓN — no implementada. Este documento no autoriza ninguna implementación ni modificación de código.
**Rol del módulo:** evaluador de riesgo y capital. **NUNCA ejecuta órdenes** (decisión permanente nº 7 de `DECISIONS.md`: "Operativa: Manual. El sistema nunca ejecuta ordenes").
**Ubicación futura prevista:** componente RISK MANAGER de la arquitectura (`ARCHITECTURE.md`, fase 3: "Risk Manager + Dashboard + Discord").

---

## 0. Convención de marcas

- **[CONFIRMADO]** — decisión ya tomada por el usuario (fuente: `DECISIONS.md` o esta orden de trabajo). No se cuestiona sin autorización.
- **[PENDIENTE]** — requisito identificado pero cuyo valor/parámetro requiere decisión del usuario. La especificación no inventa el valor.
- **[DISEÑO]** — propuesta de diseño de esta especificación, sujeta a aprobación.

---

## 1. Propósito y alcance

### 1.1 Propósito

El Risk Manager es el **evaluador único de riesgo y capital** del sistema. Ante cualquier propuesta de operación (originada por el YouTube Analyst, por el usuario o por análisis futuros), responde tres preguntas:

1. ¿Hay capital asignado disponible para esta operación en esta cuenta y esta categoría?
2. ¿La operación respeta los límites de riesgo (por operación, por activo, agregados, diarios, semanales)?
3. ¿Qué pérdida máxima asumiría el usuario si la invalidación se cumple, con este tamaño de posición y este apalancamiento?

La salida es un **dictamen de riesgo** (aprobable / rechazable / requiere aprobación humana) más la trazabilidad completa del cálculo. La decisión final de operar es siempre del usuario.

### 1.2 Alcance de v0

**Dentro del alcance:**
- Modelo conceptual de capital, cuentas y categorías de posición.
- Reglas de riesgo evaluables de forma determinista.
- Formatos de entrada/salida y registro auditable.
- Contrato de integración futura con el YouTube Analyst.

**Fuera del alcance de v0 (explícito):**
- Conexiones reales a Binance o Quantfury (sin API keys, sin lecturas de saldo en v0) [DISEÑO: la primera versión trabaja con capital declarado manualmente].
- Ejecución de órdenes de cualquier tipo [CONFIRMADO: el sistema nunca ejecuta].
- Cálculo de señales, recomendaciones de entrada/salida o estrategia [gobernanza: no generar señales].
- Dashboard y alertas Discord (fase posterior).
- Backtesting o simulación histórica de estrategias.

---

## 2. Arquitectura funcional

### 2.1 Estructura interna (propuesta) [DISEÑO]

```
ENTRADAS
  ├── CapitalSnapshot   (saldos declarados por el usuario, por cuenta)
  ├── PositionBook      (posiciones abiertas declaradas, por cuenta y categoría)
  ├── RiskProposal      (la operación que se propone evaluar)
  └── RiskPolicy        (parámetros de límites, versionados)
           │
           ▼
RISK MANAGER (evaluador puro, sin I/O de trading)
  ├── 1. Validador de capital        → capital disponible en la cuenta/categoría
  ├── 2. Calculador de tamaño        → tamaño máximo admisible por riesgo por operación
  ├── 3. Evaluador de exposición     → agregada por activo y por correlación
  ├── 4. Evaluador de apalancamiento → margen usado y disponible
  ├── 5. Evaluador de stops          → stop loss / invalidación / pérdida máxima
  ├── 6. Evaluador de límites        → diario, semanal, racha de pérdidas
  ├── 7. Simulador de escenarios     → impacto del peor caso en el capital
  └── 8. Emisor de dictamen          → veredicto + condiciones + trazabilidad
           │
           ▼
SALIDAS
  ├── RiskVerdict    (dictamen estructurado)
  └── RiskLedger     (registro auditable append-only)
```

Principio: el evaluador es una **función pura** sobre las cuatro entradas. No consulta exchanges, no mantiene estados ocultos, no llama a modelos de lenguaje para decidir límites. Todo cálculo es reproducible y explicable.

### 2.2 Cuentas y categorías de capital [CONFIRMADO + DISEÑO]

Decisión permanente nº 5: "CAPITAL: Separar Binance Spot (largo plazo) de Quantfury (trading manual)".

Modelo de dos cuentas, cada una con su capital y sus reglas propias [CONFIRMADO]:

| Cuenta | Uso declarado | Categorías internas | Apalancamiento |
|---|---|---|---|
| **Binance Spot** | largo plazo | Spot de largo plazo | Sin apalancamiento (spot) |
| **Quantfury** | trading manual | Operaciones apalancadas | Con apalancamiento [PENDIENTE: máximo permitido] |

Reglas estructurales derivadas [CONFIRMADO por el requisito 3 de la orden]:
- El capital de Binance Spot y el de Quantfury **no se suman** para calcular límites de riesgo de trading: son presupuestos independientes.
- Las posiciones spot de largo plazo **no se usan como colateral** ni se liquidan para cubrir operaciones apalancadas.
- Una misma evaluación de riesgo solo puede mezclar categorías si el usuario lo aprueba explícitamente en la propuesta (registro obligatorio de esa aprobación).

### 2.3 Responsabilidades y límites

**El Risk Manager SÍ hace:**
1. Validar que existe capital asignado suficiente en la cuenta/categoría de la propuesta.
2. Calcular el tamaño de posición máximo compatible con el riesgo por operación declarado.
3. Evaluar exposición agregada por activo y por grupo de correlación.
4. Verificar apalancamiento y margen disponible en Quantfury.
5. Exigir stop loss / nivel de invalidación en toda operación propuesta y calcular la pérdida máxima resultante.
6. Verificar límites diarios y semanales de pérdida y de nº de operaciones.
7. Ejecutar simulaciones de escenarios (peor caso, gap, liquidación) sobre el capital.
8. Emitir dictamen con veredicto, cálculos y trazabilidad, y registrarlo de forma auditable.
9. Marcar toda operación sin stop explícito como **rechazada por construcción**.

**El Risk Manager NO hace:**
1. No ejecuta, modifica ni cancela órdenes en ninguna plataforma [CONFIRMADO].
2. No genera señales ni recommienda direcciones [gobernanza].
3. No contacta APIs de exchanges en v0 [DISEÑO].
4. No modifica el capital ni las posiciones: solo las **lee** de las entradas declaradas.
5. No aprueba operaciones por sí solo: sin aprobación humana explícita no hay operación [CONFIRMADO].
6. No persiste estado más allá de su registro auditable (los saldos viven en las entradas).

---

## 3. Entradas y salidas

### 3.1 Entradas

#### A. `CapitalSnapshot` — capital por cuenta [ENTRADA del usuario]

```json
{
  "snapshot_id": "cap-2026-11-12-001",
  "created_at": "<ISO8601>",
  "declared_by": "usuario",
  "accounts": [
    {
      "name": "BinanceSpot",
      "total_capital": <valor>,
      "currency": "USDT|USD",
      "positions": [
        {"asset": "BTC", "category": "spot_long_term", "qty": <valor>, "entry_cost": <valor>}
      ]
    },
    {
      "name": "Quantfury",
      "total_capital": <valor>,
      "currency": "USD",
      "positions": [
        {"asset": "BTC", "category": "leveraged", "direction": "long|short",
         "qty": <valor>, "leverage": <valor>, "margin_used": <valor>,
         "stop_loss": <valor|null>, "invalidation_level": <valor|null>}
      ]
    }
  ]
}
```

- En v0 el snapshot se declara **manualmente** por el usuario [DISEÑO]. La sincronización automática con exchanges es una extensión futura y requiere autorización explícita.
- Los valores en fiat o cripto se normalizan a una divisa de referencia [PENDIENTE: USD vs USDT como referencia; la divisa de referencia afecta a todos los límites].

#### B. `RiskProposal` — la operación que se propone

```json
{
  "proposal_id": "prop-...",
  "created_at": "<ISO8601>",
  "origin": "youtube_analyst|user|future_module",
  "account": "BinanceSpot|Quantfury",
  "category": "spot_long_term|leveraged",
  "instrument": "BTC",
  "direction": "long|short",
  "entry_ref_price": <valor>,
  "proposed_size": <valor|null>,
  "leverage": <valor|null>,
  "stop_loss": <valor>,
  "invalidation_level": <valor>,
  "thesis_ref": {
    "video_id": "<youtube id|null>",
    "timestamp": "<segundo|null>",
    "scenario": "<escenario declarado|null>"
  },
  "human_pre_approval": {"approved_by": "usuario", "at": "<ISO8601>|null"}
}
```

#### C. `RiskPolicy` — parámetros de límites, versionados

```json
{
  "policy_id": "policy-v0-...",
  "approved_by": "usuario",
  "approved_at": "<ISO8601>",
  "risk_per_trade_max": {"BinanceSpot": null, "Quantfury": null},
  "daily_loss_max": {"BinanceSpot": null, "Quantfury": null},
  "weekly_loss_max": {"BinanceSpot": null, "Quantfury": null},
  "max_concurrent_trades": {"BinanceSpot": null, "Quantfury": null},
  "exposure_max_per_asset": {"BinanceSpot": null, "Quantfury": null},
  "exposure_max_total": {"BinanceSpot": null, "Quantfury": null},
  "leverage_max": {"Quantfury": null},
  "correlation_groups": {"BTC": ["ETH"], "SP500": ["SPX", "QQQ"], "GOLD": []},
  "mandatory_stop_loss": true
}
```

- Todo valor `null` = **parámetro pendiente de decisión del usuario**; mientras esté en `null`, la regla correspondiente queda **desactivada y el dictamen lo declara** ("regla no configurada") [DISEÑO: nunca se asume un valor por defecto implícito en reglas de riesgo].

#### D. Opcional: `AnalysisRef` — análisis del YouTube Analyst

Ver §6 (integración futura).

### 3.2 Salidas

#### A. `RiskVerdict` — dictamen

```json
{
  "verdict_id": "ver-...",
  "proposal_id": "prop-...",
  "policy_id": "policy-...",
  "snapshot_id": "cap-...",
  "evaluated_at": "<ISO8601>",
  "verdict": "APPROVABLE|REQUIRES_HUMAN_APPROVAL|REJECTED",
  "checks": [
    {"rule": "capital_available",        "status": "PASS|FAIL|NOT_CONFIGURED", "detail": "..."},
    {"rule": "risk_per_trade_max",       "status": "...", "detail": "..."},
    {"rule": "exposure_per_asset",       "status": "...", "detail": "..."},
    {"rule": "exposure_correlation",     "status": "...", "detail": "..."},
    {"rule": "leverage_margin",          "status": "...", "detail": "..."},
    {"rule": "stop_loss_present",        "status": "...", "detail": "..."},
    {"rule": "max_loss_vs_limits",       "status": "...", "detail": "..."},
    {"rule": "daily_limit",              "status": "...", "detail": "..."},
    {"rule": "weekly_limit",             "status": "...", "detail": "..."},
    {"rule": "human_pre_approval",       "status": "...", "detail": "..."}
  ],
  "worst_case": {
    "max_loss": <valor>,
    "max_loss_pct_of_account": <valor>,
    "max_loss_pct_of_assigned_capital": <valor>,
    "survival_after_scenario": true|false
  },
  "conditions": ["..."],
  "calc_trace": "<cálculo completo reproducible>"
}
```

Semántica de veredictos [DISEÑO]:
- `REJECTED` — alguna regla crítica falla (sin stop, sin capital, límite duro superado). No requiere decisión: es matemática.
- `REQUIRES_HUMAN_APPROVAL` — pasa todas las reglas pero requiere la decisión del usuario (siempre es el caso por defecto; ver §5.3).
- `APPROVABLE` — la propuesta es admisible **condicionada a aprobación humana**; el dictamen nunca ejecuta nada por sí.

#### B. `RiskLedger` — registro auditable [CONFIRMADO requisito 11]

- Registro **append-only** (una línea por evaluación, sin ediciones ni borrados).
- Cada entrada incluye: veredicto completo + hashes de las entradas usadas (snapshot, policy, proposal) para reproducibilidad + decisión humana final si existió + timestamp.
- Formato: JSONL en disco (coherente con el resto del proyecto; sin base de datos en v0).
- Propósito: reconstruir **por qué** se aprobó o rechazó cualquier operación, meses después.

---

## 4. Reglas de evaluación (detalle)

### 4.1 Riesgo máximo por operación [CONFIRMADO el requisito / PENDIENTE el valor]

- Toda propuesta debe declarar `stop_loss` o `invalidation_level` [CONFIRMADO requisito 7].
- Riesgo de la propuesta = `|entry_ref_price - stop_loss| × tamaño × (1 si spot, leverage si apalancada)`, en divisa de referencia.
- Regla: `riesgo_propuesta ≤ risk_per_trade_max × capital_asignado_categoría` [PENDIENTE: valor].
- Sin stop declarado → `REJECTED` (regla `mandatory_stop_loss`) [DISEÑO].

### 4.2 Exposición agregada por activo y correlación [CONFIRMADO el requisito / PENDIENTE los límites]

- Exposición por activo = suma del valor nocional de todas las posiciones abiertas del activo (en ambas cuentas) + nocional de la propuesta.
- Grupos de correlación declarados en la política (BTC–ETH; SPX–QQQ; Oro) [DISEÑO inicial; la matriz fina de correlaciones es extensión futura].
- Reglas: `exposición_activo ≤ exposure_max_per_asset` y `exposición_grupo ≤ exposure_max_total` [PENDIENTE: valores].
- Nota de diseño: las posiciones spot de largo plazo de Binance **cuentan** para la exposición por activo (informan el riesgo total del usuario) pero **no compiten** por el presupuesto de riesgo de trading de Quantfury (§2.2).

### 4.3 Apalancamiento y margen [CONFIRMADO el requisito / PENDIENTE el máximo]

- Solo aplica a Quantfury (spot de Binance no se apalanca) [CONFIRMADO].
- Margen usado = suma de `margin_used` de posiciones abiertas; margen requerido de la propuesta = `nocional / leverage`.
- Reglas: `leverage ≤ leverage_max` [PENDIENTE], `margen_total ≤ capital asignado` y margen libre ≥ margen requerido [DISEÑO].
- El dictamen reporta el **nivel de liquidación estimado** de la propuesta cuando los datos lo permitan [PENDIENTE: confirmar cómo obtiene Quantfury el nivel exacto; en v0 se calcula con la fórmula estándar y se declara la aproximación].

### 4.4 Stop loss, invalidación y pérdida máxima [CONFIRMADO el requisito]

- `invalidation_level` = nivel de mercado que anula la tesis (lenguaje del analista); `stop_loss` = nivel de ejecución de la protección. Deben declararse ambos cuando difieran [DISEÑO].
- Pérdida máxima de la propuesta = riesgo a stop (§4.1). Pérdida máxima del portafolio = suma de pérdidas a stop de todas las posiciones + propuesta.
- Regla: la pérdida máxima del portafolio tras la propuesta no puede superar el límite semanal/de portafolio vigente [PENDIENTE: valor].

### 4.5 Límites diarios y semanales [CONFIRMADO el requisito / PENDIENTE los valores]

- Ventanas: día calendario local y semana calendario local [PENDIENTE: definir zona horaria y si la semana es lun-dom].
- Pérdida realizada del período = suma de resultados de operaciones cerradas en la ventana (declaradas por el usuario en v0; sin APIs).
- Reglas: si la pérdida realizada de la ventana ≥ `daily_loss_max` / `weekly_loss_max` → toda nueva propuesta queda `REJECTED` (cool-down de pérdida) hasta la siguiente ventana [DISEÑO].
- Racha de pérdidas consecutivas: contador informativo en el dictamen [PENDIENTE: si se convierte en regla dura].

### 4.6 Escenarios de riesgo y simulaciones [CONFIRMADO el requisito]

El simulador evalúa la cartera (posiciones + propuesta) contra escenarios estándar y devuelve el impacto en capital:

| Escenario | Definición | Uso |
|---|---|---|
| `stop_all` | todos los stops se ejecutan | pérdida máxima esperada |
| `gap_X` | gap de X% en contra sin ejecución a stop [PENDIENTE: X] | riesgo de liquidación/gap |
| `liquidation_sweep` | barrido de liquidación intradía [PENDIENTE: profundidad] | supervivencia del margen |
| `corr_shock` | shock simultáneo de todo el grupo de correlación | exposición real del grupo |

- Supervivencia: `capital_restante ≥ capital mínimo de operación` [PENDIENTE: definir umbral de "capital de reserva intocable"].
- Los resultados van en `worst_case` del dictamen y se registran en el ledger.

### 4.7 Aprobación humana obligatoria [CONFIRMADO]

- Ninguna propuesta se considera operable sin `human_pre_approval` registrado [CONFIRMADO, coherente con decisión nº 7].
- El dictamen `APPROVABLE` describe **condiciones** (tamaño máximo, stop, límites restantes) — nunca ordena.
- La aprobación humana se registra con usuario y timestamp en el ledger, junto al veredicto evaluado [CONFIRMADO requisito 11].

---

## 5. Reglas de seguridad (de diseño del propio módulo)

1. **Solo lectura de capital/posiciones**: el Risk Manager no escribe saldos; los `CapitalSnapshot` los declara el usuario [DISEÑO v0].
2. **Fail-closed**: ante datos incompletos, snapshot vencido o política con regla crítica en `null`, el dictamen es `REQUIRES_HUMAN_APPROVAL` o `REJECTED`, nunca "aprobable" por omisión [DISEÑO].
3. **Snapshot fresco**: toda evaluación exige un snapshot con fecha ≤ N horas [PENDIENTE: N; propuesta 24 h].
4. **Policy versionada e inmutable**: cada dictamen referencia el `policy_id` exacto; cambiar la política no altera dictámenes pasados [DISEÑO].
5. **Append-only del ledger**: sin UPDATE/DELETE; corrección de errores = entrada nueva de tipo `correction` referenciando la anterior [DISEÑO].
6. **Divisa única de cálculo** dentro de cada dictamen [PENDIENTE: USD o USDT].
7. **Sin dependencia de red** en v0: todo funciona offline [CONFIRMADO: sin APIs cloud].
8. **Aislamiento**: sin dependencias del sistema CHIEF/Harness ni de proyectos externos [CONFIRMADO decisión nº 11].

---

## 6. Integración futura con el YouTube Analyst [CONFIRMADO requisito 12]

- El YouTube Analyst produce análisis de videos de CreceTrader con afirmaciones clasificadas [DICE]/[OBSERVADO]/[INFERIDO] y escenarios con niveles de activación/invalidación (ver `ARCHITECTURE.md` y las investigaciones de Fase A).
- **Contrato propuesto [DISEÑO]:** cuando el usuario decida adoptar un escenario del analista, el puente construye un `RiskProposal` con:
  - `origin: "youtube_analyst"`,
  - `thesis_ref: {video_id, timestamp, scenario}` — trazabilidad directa al minuto del video que sustenta el escenario,
  - `invalidation_level` — tomado del nivel de invalidación declarado en el análisis,
  - `entry_ref_price` — precio de referencia observado en el análisis.
- El Risk Manager **no invoca** al analista ni lee videos: recibe el `RiskProposal` ya formado (interfaz por fichero JSON en v0). El flujo es unidireccional: *análisis → propuesta → dictamen → decisión humana*.
- Toda evaluación ligada a un video conserva en el ledger la referencia `{video_id, timestamp}` para auditoría de la metodología aprendida.
- **El dictamen nunca re-alimenta el análisis** (previene sesgo de confirmación; coherente con el principio de cuarentena documentado en las investigaciones de Fase A).

---

## 7. Parámetros pendientes de decisión del usuario (consolidado)

Ninguno de estos valores se inventa; el módulo no entra en operación con ellos en `null` [DISEÑO].

| # | Parámetro | Afecta a | Nota |
|---|---|---|---|
| P1 | Capital total y asignado por cuenta (Binance Spot / Quantfury) | todo | dato declarado por el usuario |
| P2 | Divisa de referencia del cálculo | todo | USD vs USDT |
| P3 | Riesgo máximo por operación (por cuenta/categoría) | §4.1 | % del capital asignado |
| P4 | Límite de pérdida diario | §4.5 | por cuenta |
| P5 | Límite de pérdida semanal | §4.5 | por cuenta |
| P6 | Exposición máxima por activo y por grupo | §4.2 | nocional o % |
| P7 | Apalancamiento máximo permitido | §4.3 | solo Quantfury |
| P8 | Máximo de operaciones concurrentes | §4.1 | por cuenta/categoría |
| P9 | Profundidad de escenarios (gap %, barrido de liquidación) | §4.6 | simulaciones |
| P10 | Capital mínimo de reserva intocable | §4.6 | supervivencia |
| P11 | Frescura máxima del snapshot de capital | §5.3 | horas |
| P12 | Zona horaria y definición de semana | §4.5 | límites temporales |
| P13 | Si las posiciones spot de largo plazo cuentan para exposición total pero no para límites de trading | §4.2 | confirmación explícita |

---

## 8. Criterios de aceptación (para la futura implementación)

La implementación v0 se considerará correcta solo si cumple **todo** esto:

1. **Pureza y determinismo**: la misma terna (snapshot, policy, proposal) produce siempre el mismo dictamen, byte a byte en `calc_trace`.
2. **No-ejecución**: el código no contiene llamadas a APIs de trading ni existe cualquier vía de envío de órdenes [CONFIRMADO].
3. **Separación de cuentas**: es imposible que una evaluación de Quantfury consuma el presupuesto de riesgo de Binance Spot o viceversa [CONFIRMADO].
4. **Spot vs apalancado**: ninguna regla de apalancamiento se aplica a posiciones `spot_long_term` [CONFIRMADO].
5. **Fail-closed**: con política en `null` (sin configurar), ningún dictamen sale como aprobable sin intervención humana; el estado `NOT_CONFIGURED` aparece en los checks.
6. **Stop obligatorio**: una propuesta sin stop/invalidación produce `REJECTED` con la regla `stop_loss_present` en `FAIL` [DISEÑO].
7. **Auditoría completa**: cada dictamen queda en el ledger con hashes de entradas; el dictamen se puede reproducir desde las entradas archivadas.
8. **Aprobación humana**: sin `human_pre_approval`, el veredicto nunca pasa de `APPROVABLE` (que ya exige decisión humana posterior) [CONFIRMADO].
9. **Simulaciones**: los cuatro escenarios de §4.6 producen números coherentes con el capital declarado y quedan registrados.
10. **Pruebas**: suite de tests unitarios cubriendo las reglas §4.1–§4.7, casos fail-closed y casos límite (capital exacto, límite exacto, stop idéntico a entrada).
11. **Documentación**: el módulo documenta qué reglas usan parámetros `null` y cómo degrada su comportamiento.

---

## 9. Gobernanza y pasos futuros (no comprometidos)

1. El usuario define los parámetros P1–P13 (o declara explícitamente que algunas reglas no aplican) → se genera `RiskPolicy` v1 firmada.
2. Se implementa el evaluador puro + suite de tests (sin I/O).
3. Se integra la captura manual de `CapitalSnapshot` (comando/script declarativo).
4. Solo después: puente con el YouTube Analyst (§6) y, si el usuario lo aprueba, sincronización de saldos con exchanges.
5. Dashboard/Discord queda para la fase 3 del roadmap (`ARCHITECTURE.md`).

---

*Documento creado el 2026-11-12 como entregable de la orden "Cierre A.7.4 + Diseño Risk Manager". Es una especificación: no implementa nada, no cambia código, no define parámetros financieros por cuenta propia.*
