# INFORME DE CONSOLIDACIÓN — Analyst, Manager y Dashboard

Fecha: 2026-11-16 · Componentes aislados en `daily_pilot/` · `PAPER_ONLY=true`

## 1. Qué se corrigió

- **Modelo de planes (9 tipos)**: se separaron `PLAN_OPERATIVO_INCOMPLETO` y `PLAN_OPERATIVO_COMPLETO`; un plan **no** es completo por tener solo un nivel y un objetivo. Completo = condición + entrada/método + invalidación + objetivos.
- **Procedencias A/B/C/D** obligatorias; los campos nuevos (`justificacion`, `metodo_calculo`, `temporalidad_origen`, `relacion_temporalidades`, `info_faltante`) están en el contrato y en los datos.
- **Manager con 4 dimensiones separadas**: calidad del análisis, completitud del plan, viabilidad técnica, riesgo y capital. Propone invalidación con **procedencia D** y su método, sin presentarla como dato del analista.
- **Dashboard reconstruido** (84.634 bytes): desplegables por instrumento, planes agrupados en incompletos/completos/oportunidades validadas, y verificación campo a campo contra el JSON.

## 2. Qué funciona realmente (verificado)

| Comprobación | Resultado |
|---|---|
| Bloque de datos del HTML == `dashboard_data.json` | **idéntico** |
| HTML válido (html.parser) | 0 errores, 0 tags sin cerrar |
| Recursos externos / fetch / XHR / WS | **0** |
| Suites: core / clasificador / risk manager | **18/18 · 10/10 · 14/14** |
| Escenarios reales clasificados y evaluados | 8/8 |

## 3. Escenarios evaluables (del vídeo `s_GjovZxQqY`)

| Escenario | Clasificación | Manager | Calidad | Completitud | Stop propuesto (D) |
|---|---|---|---|---|---|
| BTC Weekly 71.509/69.000 | PLAN_OPERATIVO_INCOMPLETO | ESPERAR_CONFIRMACION | alta | incompleto | 68.655 |
| BTC 4H sin reversal → 56.750 | ESCENARIO_CONDICIONAL | ESPERAR_CONFIRMACION | media | incompleto | — |
| BTC intradía 66.617–64.004 | ZONA_DE_INTERES | FALTA_INFORMACION | media | incompleto | — |
| BTC vigilar 65.520 | ZONA_DE_INTERES | FALTA_INFORMACION | alta | incompleto | — |
| ETH 1.780–2.286 | PLAN_OPERATIVO_INCOMPLETO | ESPERAR_CONFIRMACION | media | incompleto | 1.771,10 |
| Oro 3.906→3.623 | PLAN_OPERATIVO_INCOMPLETO | ESPERAR_CONFIRMACION | media | incompleto | 3.925,53 |
| SPX 7.592→6.612 | NIVEL_REFERENCIADO | FALTA_INFORMACION | media | incompleto | — |
| NQ 28.400→25.479 | ZONA_DE_INTERES | FALTA_INFORMACION | media | incompleto | — |

## 4. Escenarios potencialmente operables

**Ninguno en este momento.** Los 3 planes incompletos están **cerca** (tienen condición, entrada y objetivos; les falta la invalidación, que el Manager propone como D). Para pasar a `OPORTUNIDAD_VALIDABLE` haría falta: verificación visual de los niveles (B4) o confirmación explícita del analista del stop, y una R/B calculable.

## 5. Datos que faltan

- **Invalidación** en los 3 planes incompletos (no declarada por CreceTrader).
- **Condición de activación explícita** en el 4H, la intradía, 65.520 y NQ.
- **Entrada** en el 4H y en 65.520.
- **Verificación visual** de todos los niveles (sin análisis de gráfico).
- **Feed de precios** en tiempo real.
- **Relación entre temporalidades** solo parcial (Weekly→Daily citada; 4H e intradía no desarrolladas).

## 6. Limitaciones pendientes

1. B4 sin anotadores humanos → la lectura visual sigue sin validar.
2. Sin GPU: la inferencia de visión es poco práctica (60-180 s/frame en CPU).
3. El clasificador legado (`signal_classifier.py`) queda como versión anterior; el vigente es `core/plan_classifier.py`.
4. El bloque `mercado` del JSON no declara procedencia en todos sus campos → el dashboard los muestra como **SIN PROCEDENCIA** (correcto).
5. QQQ y NQ aparecen como instrumentos distintos; el dashboard avisa.

## 7. Pruebas ejecutadas

| Suite | Casos | Resultado |
|---|---|---|
| `tests/test_core.py` | 18 (incluye los 10 exigidos: sin stop, sin entrada, sin condición, objetivo sin invalidación, contradictorios, nivel explícito + cálculo C, invalidado por precio, requiere confirmación, stop propuesto D, plan completo) | **18/18** |
| `test_signal_classifier.py` | 10 | **10/10** |
| `risk_manager/test_risk_manager.py` | 14 | **14/14** |
| Dashboard (HTML + correspondencia) | parseo, igualdad de datos, 0 recursos externos | **OK** |

## Confirmaciones

- Producción intacta; scheduler con `--no-vision`; LaunchAgent de Harness sin tocar.
- Sin inferencia audiovisual en el Mac; sin frames enviados a servicios externos.
- Decisiones del usuario solo locales (`localStorage`). Ninguna operación financiera. `PAPER_ONLY=true`.
