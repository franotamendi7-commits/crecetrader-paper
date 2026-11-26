# AUDITORÍA VPS — dónde correr el dash cuando el Mac no está

Fecha: 2026-11-26 · PAPER_ONLY · **auditoría de lectura, nada modificado.**

## 1. Lo que el proyecto really necesita

Del análisis del código (`generar_dashboard_v6.py`, paneles y trackers):

```
Python 3.11+ · SOLO librería estándar (json, pathlib, datetime, html, urllib, re)
Sin Flask, sin pandas, sin numpy, sin Base de datos
Genera un HTML estático → se sirve con `python3 -m http.server`
Actualiza velas con urllib a api.binance.com (solo lectura)
```

**Conclusión: corre en cualquier VPS mínimo.** No hay dependencias pesadas. El workspace completo sin velas es liviano; las velas 1h/4h de 13 pares son lo único voluminoso (~125,2 MB; 294 MB el directorio completo con 1d/1w/caches).

## 2. Opciones reales (datos de fuentes públicas, 2026)

| Proveedor | Siempre gratis | Specs | Riesgo principal |
|---|---|---|---|
| **Oracle Always Free Ampere A1** | Sí, sin vencimiento | 2 OCPU / 12 GB RAM (recortado en jun-2026 de 4/24), 200 GB disco, 10 TB egress | **Falta de capacidad** en regiones populares; Oracle reclama instancias inactivas |
| **Google Cloud e2-micro** | Sí, sin vencimiento | 2 vCPU compartidas (burst) / 1 GB RAM, 30 GB disco, **1 GB egress/mes** | 1 GB de salida es poquísimo; sin SLA; IPv4 ~$3,65/mes |
| Oracle AMD micro ×2 | Sí | 1/8 OCPU / 1 GB c/u | Muy chico para el caso |
| Render / Koyeb / Railway / HF Spaces | Sí pero duermen | scale-to-zero | **Duermen** al inactivarse → no sirve para "siempre arriba" |
| AWS / Azure / DigitalOcean | Solo créditos temporales | — | Se vencen (6-12 meses) → no son "para siempre" |

## 3. Recomendación

**Oracle Always Free Ampere A1 (2 OCPU / 12 GB), región con cupo disponible.**

Razones:
- Es la única con especificaciones holgadas **y** permanente (10 TB de salida vs 1 GB de GCP).
- 12 GB de RAM de sobra para Python + 13 pares de velas.
- Con `curl` periódico al dash se evita que Oracle la reclame por inactividad.

Plan B: **GCP e2-micro** si Oracle no tiene capacidad en la región. Pero vigilar el egress: regenerar el HTML cada 5 min con 13 pares consume varios MB/día; 1 GB/mes podría quedar corto. En GCP subir el refresh a 15 min.

## 4. Qué hay que migrar (y qué NO)

**Sí migrar:**
```
daily_pilot/scripts/        (generador, paneles, trackers, alertas, actualizar_velas)
daily_pilot/datos/velas/    (13 pares × 1h+4h, ~50 MB)
daily_pilot/datos/*.json    (journals, cartera, resumen_video)
daily_pilot/analisis/       (resúmenes)
```

**NO migrar:**
```
store.db · FIRMA · daily_pilot/metodo/ · ~/.hermes/.env (webhook)
```
El webhook va en el VPS aparte, nunca en el repo.

## 5. Arquitectura propuesta en el VPS

```
systemd timers (no launchd):
  actualizar_velas.service → cada 15 min
  tracker_scalein/paper/bos.service → :01/:02/:03 cada hora
  alertas_senales.service → :05 cada hora
  dash-refresh.service → cada 5 min (o 15 en GCP)
python3 -m http.server 8765 → sirve el HTML

Healthcheck: cron que hace curl localhost:8765 y escribe timestamp
→ también evita reclaim de Oracle por inactividad
```

## 6. Lo que NO resuelve el VPS

- **Discord**: funciona igual (webhook saliente), pero hay que cargar la URL en el VPS.
- **El Mac**: si el Mac se apaga, el VPS sigue — pero las velas se descargan en el VPS, no en el Mac. No duplicar jobs en ambos o se pisarán los journals.
- **PAPER_ONLY**: las decisiones siguen siendo locales; el VPS nunca ejecuta órdenes reales.

## 7. Costo

```
Oracle: $0/mes (dentro de Always Free)
GCP:    $0/mes compute, ~$3,65/mes IPv4; ojo con 1 GB egress
```

## 8. Veredicto

**Viable y barato.** El proyecto es ideal para un VPS: sin dependencias, sin DB, HTML estático. Recomiendo Oracle Ampere A1 2/12. Antes de migrar, decidir cuáles paneles se quedan en el dash (según dijiste, vamos a limpiar lo de backtesting).

**No se hizo ningún cambio. Auditoría de lectura.**
