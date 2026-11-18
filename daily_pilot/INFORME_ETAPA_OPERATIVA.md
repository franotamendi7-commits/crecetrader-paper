# INFORME — Modelo operativo CreceTrader + Manager + Dashboard

Fecha: 2026-11-16 · Componentes aislados en `daily_pilot/` · `PAPER_ONLY=true`

## 1. Dashboard funcional

`daily_pilot/dashboard/index.html` (55.261 bytes, autocontenido).
Verificado por mí: HTML bien formado (0 tags sin cerrar), **0 recursos externos**, **0 fetch/XHR**, abre con doble clic (`file://`).
5 vistas: MERCADO · PLANES · OPORTUNIDADES · SEGUIMIENTO · DECISIÓN.
Campos con procedencia A/B/C/D, vacíos como `NO DECLARADO`/`FALTA INFORMACION`, avisos PAPER_ONLY y sin verificación visual.
Generado con OpenCode (delegado) y verificado de forma independiente.

## 2. Contratos de datos

`daily_pilot/contracts/contrato_analista_manager.md` — procedencias A/B/C/D, 8 clasificaciones del Analyst, 6 veredictos del Manager, 7 estados de seguimiento, capital separado.

## 3. Código y pruebas

| Componente | Ruta |
|---|---|
| Modelo de escenario | `daily_pilot/core/model.py` |
| Clasificador de planes | `daily_pilot/core/plan_classifier.py` |
| Manager + capital | `daily_pilot/core/manager.py` |
| Constructor de escenarios reales | `daily_pilot/scripts/build_escenarios_s_GjovZxQqY.py` |

| Suite | Resultado |
|---|---|
| `tests/test_core.py` (clasificador + Manager) | **13/13** |
| `test_signal_classifier.py` (clasificador legado) | **10/10** |
| `risk_manager/test_risk_manager.py` | **14/14** |

## 4. Ejemplo real del vídeo `s_GjovZxQqY`

8 escenarios construidos **solo** con lo dicho por CreceTrader (procedencia A). Ninguno se convierte en operación:

| Escenario | Clasificación | Manager |
|---|---|---|
| Weekly 71.509/69.000 | PLAN_OPERATIVO | ESPERAR_CONFIRMACION (stop no declarado) |
| 4H sin reversión → 56.750 | ESCENARIO_CONDICIONAL | ESPERAR_CONFIRMACION |
| Intradía 66.617–64.004 | ZONA_DE_INTERES | FALTA_INFORMACION |
| Vigilar 65.520 | ZONA_DE_INTERES | FALTA_INFORMACION |
| ETH 1.780–2.286 | PLAN_OPERATIVO | ESPERAR_CONFIRMACION |
| Oro 3.906→3.623 | PLAN_OPERATIVO | ESPERAR_CONFIRMACION |
| SPX 7.592→6.612 | NIVEL_REFERENCIADO | FALTA_INFORMACION |
| NQ 28.400→25.479 | ZONA_DE_INTERES | FALTA_INFORMACION |

**0 señales activas.** Todo lo que falta está declarado en `info_faltante` (principalmente stops no declarados por el analista).

## 5. Limitaciones conocidas

1. **Sin verificación visual**: los niveles son lo **dicho** por CreceTrader, no contrastados con el gráfico. B4 sigue pendiente (faltan anotadores humanos).
2. **Sin feed de precios**: el "precio de referencia" es el citado en el vídeo; no hay cotización en tiempo real (Kraken no integrado).
3. **Datos DEMO**: no se usaron datos inventados; los campos desconocidos quedan como `NO_DETERMINADO`.
4. **El clasificador legado** (`signal_classifier.py`, 6 tipos) quedó como versión anterior; el vigente es `core/plan_classifier.py` (8 tipos).
5. **Estimaciones de visión en CPU** (sin GPU): 60-180 s/frame → no operativo por ahora.

## 6. Próximos pasos concretos

1. Anotación humana de B4 → validar la lectura visual.
2. Autorizar infraestructura de visión (Kaggle sin GPU / Colab).
3. Integrar OHLCV de Kraken para BTC y contrastar niveles.
4. Añadir el video `bCc--rvyHpY` y `Vm7nUxLCMZQ` al flujo y comparar escenarios entre vídeos.
5. Definir las reglas de paso de `PLAN_OPERATIVO` a `OPORTUNIDAD_VALIDABLE` cuando exista verificación visual.

## Confirmaciones

- Producción intacta: no se modificaron scripts de pipeline, prompts, modelos, skills ni configuración.
- Scheduler con `--no-vision` (ya corregido y probado).
- LaunchAgent de Harness sin tocar.
- Sin inferencia audiovisual en el Mac; sin frames enviados a servicios externos.
- Sin operaciones de trading.
