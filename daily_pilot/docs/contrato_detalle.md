# CONTRATO — Detalle del dashboard (Fase 0 de coherencia)

Fecha: 2026-11-18 · Estado: **vigente** · `PAPER_ONLY=true`

## Problema que resuelve
El dashboard mostraba el **estado** de un video y el **detalle** de otro (estado `cH2KY5vnsVQ` del 18/11 con mercado de `s_GjovZxQqY` del 16/11). Peor que no actualizar: **parece actualizado**.

## Regla
1. El **detalle** (mercado, escenarios, niveles) sale del **último análisis real**:
   `daily_pilot/analisis/<video_id>_analisis.json`.
2. `daily_pilot/datos/dashboard_data.json` es **fallback únicamente**, y cuando se use debe mostrarse un **banner visible**: `DETALLE DE OTRO VIDEO · <video_id> · <fecha>`.
3. Todo bloque de datos lleva: `fuente`, `video_id`, `published`, `generado_el`.
4. El **estado** (`estado_hoy.json`) y el **detalle** deben poder leerse por separado; nunca se asume que son el mismo video.
5. `ultimo_analizado` es **campo canónico único** = `ultimo_analisis_completo`.

## Campos del detalle
| Campo | Obligatorio | Descripción |
|---|---|---|
| `fuente` | sí | ruta o identificador de la fuente |
| `video_id` | sí | video del que proviene |
| `published` | sí | fecha de publicación (RFC3339) |
| `generado_el` | sí | cuándo se generó el bloque |
| `niveles` | sí | cada nivel con procedencia A/B/C/D |

## Generación
```bash
python3 daily_pilot/scripts/control_diario.py     # escribe ultimo_analisis_completo
python3 daily_pilot/scripts/generar_dashboard.py  # incrusta detalle + banner
```

## Aceptación
- El dashboard del 18/11 muestra el análisis del 18/11.
- Si el detalle es más viejo que el estado, hay banner.
- Ninguna tarjeta sin `fuente` y `fecha`.
- `verify_integrity.py` OK y `run_all.py` en verde.
