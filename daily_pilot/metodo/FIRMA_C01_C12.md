# FIRMA — Reglas C01–C12 del método CreceTrader

**Firmante:** Francisco («Tata») — Chief del proyecto.
**Fecha y hora:** 2026-11-19 · 12:13 UTC (09:13 −03, Argentina).
**Canal:** chat de Hermes Agent (sesión `local-337a3a967c76923daf810150298934942df2272d099ab20c0b8d3042e4a08d48`).
**Declaración textual del firmante:**

> «te digo yo ahora francisco firmo todo! lo aseguro y acredito!»

## Artefacto firmado

Archivo: `daily_pilot/metodo/playbook_v0.1.md`
**sha256 (versión firmada):** `b4db713f392f9a17f1a60d97346ad5c3f02dda3a28bcfb20caecf2415562568a`

## Reglas firmadas — las 12

| # | Regla | Estado |
|---|---|---|
| C01 | Tendencia W > D > 4H | **aprobado_por_francisco** |
| C02 | 30% oferta / 70% confirmación; 5 pares en oferta; BTC 30–45% | **aprobado_por_francisco** |
| C03 | 4H: fase 3 = corrección; 4H + diario → long | **aprobado_por_francisco** |
| C04 | Abanico intradía de 9 niveles en **%** (0,25 = 0,25%), punto cero 21:00 | **aprobado_por_francisco** |
| C05 | Fibo por TF; retrocesos 50/61/78; extensiones 50/100/150/200; bajista inverso | **aprobado_por_francisco** |
| C07 | Regímenes: tendencia / **corrección** / rango / no determinado | **aprobado_por_francisco** |
| C08 | Invalidación = no ocurrió el cambio de tendencia → cerrar | **aprobado_por_francisco** |
| C09 | Objetivos = extensiones C05; 4 tramos 25%; stop break-even | **aprobado_por_francisco** |
| C10 | Niveles de impulso 50/61,8/100/125/150% (**de CreceTrader**) + riesgo (**de Francisco**) | **aprobado_por_francisco** |
| C11 | Riesgo = confianza × tope (5% tendencia / 2% corrección) | **aprobado_por_francisco** |
| C12 | OB = zona de liquidez por TF | **aprobado_por_francisco** |

## Verificación (read-only)

```bash
cd /Users/franciscootamendi/YouTubeTradingAgent
shasum -a 256 daily_pilot/metodo/playbook_v0.1.md
# debe dar b4db713f392f9a17f1a60d97346ad5c3f02dda3a28bcfb20caecf2415562568a
```

**Hash del playbook ya firmado (con la firma incrustada):** `7be1dd686be51c058c887b3aa032b40268bca1cd20fb1778b1294c1f1e99aeed`

**Nota de integridad:** la firma se ancló a `b4db713f…` (la versión dictada). El hash cambió
**solo** porque el encabezado ahora declara la firma. Si cambia **alguna regla C01–C12**,
este hash deja de servir y hay que **re-firmar**. Por eso el hash se registra antes de editar
el encabezado del playbook (ver commit siguiente).

## Límites que el firmante conoce
- **PAPER_ONLY=true** en todo el código. Nada de esto ejecuta órdenes.
- Los **precios** salen de la transcripción; **no hay feed en vivo**.
- La **decisión** es del trader; el sistema describe y calcula, no ordena.
