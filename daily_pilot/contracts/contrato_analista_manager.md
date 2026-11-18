# Contrato de datos — YouTube Analyst ↔ Manager

Versión: 1.0 · Fecha: 2026-11-16 · Estado: vigente
Alcance: componentes aislados en `daily_pilot/`. No modifica producción.

## 1. Principios

1. **No inventar**: el analista registra lo que CreceTrader dice o lo que el gráfico muestra.
2. **Procedencia obligatoria** en cada campo relevante:
   - `A` DATO EXPLÍCITO — dicho por CreceTrader.
   - `B` DATO OBSERVADO — visible en el gráfico, con evidencia.
   - `C` CÁLCULO DEL SISTEMA — derivado con metodología documentada.
   - `D` PROPUESTA DEL MANAGER — recomendación propia del Manager.
3. **No mezclar** categorías en un mismo campo. Si un stop no fue dado por CreceTrader, no puede llevar procedencia `A`.
4. Lo que falte se registra en `info_faltante`; no se completa por intuición.

## 2. Escenario (salida del Analyst)

```json
{
  "id": "ESC-<video_id>-<sec>",
  "video_id": "s_GjovZxQqY",
  "instrumento": "BTCUSD",
  "mercado": "Coinbase | NO_DETERMINADO",
  "timestamp_video": "2026-11-16T09:55:48+00:00",
  "timestamp_explicacion": "00:06:26",
  "temporalidades": ["Weekly", "Daily", "4H", "Intradia"],
  "direccion": "alcista | bajista | neutral",
  "nivel": {"valor": 69000, "procedencia": "A", "unidad": "precio"},
  "justificacion": "texto del analista",
  "evidencia": ["transcripcion 06:26-06:37"],
  "relacion_temporalidades": "Weekly 71.509 como objetivo; Daily 69.000 soporte",
  "condicion_activacion": {"texto": "...", "procedencia": "A|C"},
  "entrada": {"valor": 69000, "procedencia": "A"},
  "stop": {"valor": null, "procedencia": null},
  "objetivos": [{"valor": 72554, "procedencia": "A"}],
  "risk_reward": {"valor": null, "procedencia": null},
  "clasificacion": "ESCENARIO_CONDICIONAL",
  "info_faltante": ["stop no declarado"],
  "confianza": 0.0,
  "calidad_evidencia": "alta | media | baja",
  "fuente": "transcripcion | grafico | mixta"
}
```

## 3. Clasificación del Analyst (9 tipos)

`NIVEL_REFERENCIADO` · `ZONA_DE_INTERES` · `ESCENARIO_CONDICIONAL` · `PLAN_OPERATIVO_INCOMPLETO` · `PLAN_OPERATIVO_COMPLETO` · `OPORTUNIDAD_VALIDABLE` · `NO_OPERABLE` · `DESCARTADO` · `INDETERMINADO`

Reglas:
- `NIVEL_REFERENCIADO`: nivel sin información operativa.
- `ZONA_DE_INTERES`: el analista espera una reacción en la zona.
- `ESCENARIO_CONDICIONAL`: plan sujeto a condición de precio, sin entrada definida.
- `PLAN_OPERATIVO_INCOMPLETO`: con condición y entrada, pero falta invalidación y/o objetivos.
- `PLAN_OPERATIVO_COMPLETO`: **condición + entrada/método + invalidación + objetivos definidos**.
- `OPORTUNIDAD_VALIDABLE`: plan completo que supera el filtro del Manager (sin contradicciones y con R/B).
- `NO_OPERABLE` / `DESCARTADO`: los asigna el **Manager** o el seguimiento.
- `INDETERMINADO`: información insuficiente o ambigua.

**Regla:** un plan **no** es completo por tener solo un nivel y un posible objetivo. Los campos que falten quedan siempre visibles.

## 4. Veredicto del Manager (6)

`APTO_PARA_EVALUACION` · `ESPERAR_CONFIRMACION` · `FALTA_INFORMACION` · `RIESGO_INADECUADO` · `NO_OPERABLE` · `ESCENARIO_INVALIDADO`

## 5. Seguimiento (7 estados)

`EN_OBSERVACION` · `ESPERANDO_ACTIVACION` · `ACTIVADO` · `EN_SEGUIMIENTO` · `OBJETIVO_ALCANZADO` · `INVALIDADO` · `EXPIRADO`

**Regla:** que el precio toque un nivel **no** activa la operación; lo hace la condición definida en el plan.

## 6. Salida del Manager (hacia el Dashboard)

```json
{
  "escenario_id": "...",
  "veredicto": "APTO_PARA_EVALUACION",
  "motivos": ["..."],
  "condiciones_faltantes": ["..."],
  "risk_reward_propuesto": {"valor": 2.3, "procedencia": "D"},
  "stop_propuesto": {"valor": 68500, "procedencia": "D", "metodo": "minimo inferior 4H"},
  "capital": {"disponible": 10000.0, "riesgo_pct": 0.01, "tamano_propuesto": 0.0, "perdida_potencial": 0.0},
  "decision_usuario": "pendiente"
}
```

## 7. Gestión de capital

- Separada de la evaluación de escenarios.
- Capital simulado editable (`capital.json`), **no** se asume capital real.
- Sin conexión con exchanges. `PAPER_ONLY=true`.

## 8. Datos DEMO

Lo que no proceda de una fuente real se marca `"demo": true` y se identifica como DEMO en la interfaz.
