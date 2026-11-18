# Risk Manager — Interfaz

Componente **aislado** del YouTube Analyst. `PAPER_ONLY=true`. Sin ejecución automática, sin conexión con permisos de trading, no envía órdenes.

## API

```python
from risk_manager import RiskManager, Config, Signal

cfg = Config(account_balance=10000.0, max_risk_pct=0.01, max_exposure_pct=0.05,
             max_senales_por_instrumento=2, min_confianza=0.5, requerir_evidencia=True)
rm = RiskManager(cfg)
resultado = rm.evaluar(lista_de_senales)   # Signal(...) o dict
```

## Campos de una señal (entrada)

| Campo | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `id` | str | sí | identificador único |
| `instrument` | str | sí | BTCUSD, ETHUSD, XAUUSD, ES, NQ… |
| `direction` | str | sí | `compra`, `venta`, `sin_operacion` |
| `entry_low` / `entry_high` | float | sí (si opera) | zona de entrada |
| `invalidation` | float | sí (si opera) | nivel de invalidación |
| `targets` | list[float] | sí (si opera) | objetivos |
| `evidence` | list[str] | sí | evidencia (timestamps, fuentes) |
| `confidence` | float | no (0-1) | confianza |
| `status` | str | no | EXPERIMENTAL / NO VERIFICADO |

## Salida

```json
{
  "paper_only": true,
  "decision": "ACEPTAR | RECHAZAR | REVISION MANUAL",
  "razones": ["..."],
  "exposicion_total": 500.0,
  "senales": [{"id": "...", "decision": "...", "razones": ["..."],
               "risk": {"risk_per_unit":..., "position_size":...,
                        "perdida_potencial":..., "r_multiples":[...]}}]
}
```

## Reglas de decisión

1. **RECHAZAR**: campo obligatorio ausente; contradicción (compra con entrada ≤ invalidación, venta con entrada ≥ invalidación, objetivo en contra).
2. **REVISION MANUAL**: confianza < mínimo; más de `max_senales_por_instrumento` por instrumento; exposición agregada > `max_exposure_pct`.
3. **ACEPTAR**: todo lo anterior superado.
4. Toda decisión incluye **razones** y el detalle de riesgo por señal.

## CLI

```bash
.venv/bin/python3 -c "import sys;sys.path.insert(0,'daily_pilot/risk_manager');\
from risk_manager import evaluar_json;import json;print(json.dumps(evaluar_json('senales.json'),ensure_ascii=False,indent=2))"
```

## Pruebas

`test_risk_manager.py` — 14/14 OK (señal completa, campos faltantes, contradicciones compra/venta, exposición, duplicidad por instrumento, confianza, sin operación, sin evidencia, paper-only, R múltiplos, dirección inválida, lista vacía).
