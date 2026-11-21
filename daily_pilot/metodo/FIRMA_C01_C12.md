# FIRMA — Reglas C01–C12 del método CreceTrader

**Firmante:** Francisco («Tata») — Chief del proyecto.

## Firmas

| # | Fecha | Canal | Declaración textual |
|---|---|---|---|
| 1ª | 2026-11-19 · 12:13 UTC | Hermes (`local-337a3a96…`) | «te digo yo ahora francisco firmo todo! lo aseguro y acredito!» |
| **2ª (re-firma)** | **2026-11-20** | Hermes (misma sesión) | **«hace todo!»** — autoriza la re-firma con los anexos C05-A/C05-B y los arreglos de la auditoría |

## Artefacto firmado

Archivo: `daily_pilot/metodo/playbook_v0.1.md`

| Versión | sha256 | Cuándo |
|---|---|---|
| dictada (1ª firma) | `b4db713f392f9a17f1a60d97346ad5c3f02dda3a28bcfb20caecf2415562568a` | 2026-11-19 |
| con 1ª firma incrustada | `7be1dd686be51c058c887b3aa032b40268bca1cd20fb1778b1294c1f1e99aeed` | 2026-11-19 |
| **actual (2ª firma)** | `c676021f1581e7d85609f5c1e50b47f369d0f99edf78a4cfcf744665d9c3603b` | 2026-11-20 |

**Cómo se ancla:** el hash se registra **antes** de escribir la firma; al quedar
incrustada, el hash cambia solo por eso. **Si cambia una regla, hay que re-firmar.**

## Reglas firmadas — las 12

| # | Regla | Estado |
|---|---|---|
| C01 | Tendencia **W > D > 4H** (el semanal manda; diario y 4h confirman) | **aprobado_por_francisco** |
| C02 | 30% oferta / 70% confirmación; 5 pares en oferta; BTC 30–45% | **aprobado_por_francisco** |
| C03 | 4H: fase 3 = corrección; 4H + diario → long | **aprobado_por_francisco** |
| C04 | Abanico intradía: cierre 21:00 ± **fibo × 1.000 puntos** (0,236/0,382/0,618/0,929/1,238) | **aprobado_por_francisco** — re-firmado 20/11 |
| C05 | Fibo **0 = mínimo, 1 = máximo**; retrocesos 0,382/0,5/**0,61**/0,786; extensiones 1/1,25/1,5/1,75/2/3 | **aprobado_por_francisco** — re-firmado 20/11 |
| C06 | Confluencia de 4 componentes + secuencia 4H | **aprobado_por_francisco** — agregado en la 2ª firma |
| C07 | Regímenes: tendencia / **corrección (dentro de la tendencia)** / rango / no determinado | **aprobado_por_francisco** |
| C08 | Invalidación = no ocurrió el cambio de tendencia → cerrar | **aprobado_por_francisco** |
| C09 | Objetivos = extensiones C05; el 100% repartido; stop break-even | **aprobado_por_francisco** |
| C10 | Niveles de impulso 50/61,8/100/125/150% (**de CreceTrader**) + riesgo (**de Francisco**); la confianza la asigna el trader | **aprobado_por_francisco** |
| C11 | Riesgo = confianza × tope (5% tendencia / 2% corrección) | **aprobado_por_francisco** |
| C12 | OB = zona de liquidez **por timeframe** | **aprobado_por_francisco** |

## Anexos que son parte del método firmado

- **C05-A** — nomenclatura del indicador de CreceTrader: `0 = mínimo`, `1 = máximo`;
  las extensiones quedan **arriba**. Validado con **12 niveles exactos** en las 3
  capturas BNB del 2026-11-20.
- **C05-B** — el tramo del ciclo: **cada TF tiene su swing** (macro = semanal,
  micro = diario y 4h); el tramo va del **máximo más alto** al **piso más bajo
  posterior**. Validado en 1W / 1D / 4H.

## Verificación (read-only)

```bash
cd /Users/franciscootamendi/YouTubeTradingAgent
shasum -a 256 daily_pilot/metodo/playbook_v0.1.md
```

## Límites que el firmante conoce

- **PAPER_ONLY=true** en todo el código. Nada de esto ejecuta órdenes.
- Los **precios** salen de la transcripción; **no hay feed en vivo**.
- La **decisión** es del trader; el sistema describe y calcula, no ordena.
