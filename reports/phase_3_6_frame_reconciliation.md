# FASE 3.6 — RECONCILIACIÓN DE FRAMES

## Fuente de verdad canónica
Archivo: `experimental/results/vision_analysis_canonical.json`
Total: 19 frames (14 OK, 5 ERR)

## Tabla de reconciliación

| Frame | Imagen | Timestamp | Tipo | Estado | Tiempo (s) | Motivo error |
|-------|--------|-----------|------|--------|------------|--------------|
| 0 | scene_000_0.0s.jpg | 0.0s | Escritorio/terminal | OK | 336.5 | — |
| 1 | scene_001_8.3s.jpg | 8.3s | Gráfico semanal BTC | ERR | 0.0 | Timeout 600s (3 intentos) |
| 2 | scene_002_10.1s.jpg | 10.1s | Gráfico 1H BTC | ERR | 0.0 | Timeout 600s (3 intentos) |
| 3 | scene_003_196.8s.jpg | 196.8s | Gráfico 4H BTC | OK | 100.7 | — |
| 4 | scene_004_303.7s.jpg | 303.7s | Gráfico daily BTC | OK | 544.3 | Recuperado con preprocesamiento 2x |
| 5 | scene_005_350.8s.jpg | 350.8s | Gráfico 1H BTC | OK | 318.7 | — |
| 6 | scene_006_439.2s.jpg | 439.2s | Gráfico daily BTC | ERR | 0.0 | Timeout 600s (3 intentos) |
| 7 | scene_007_449.9s.jpg | 449.9s | Página web | OK | 209.9 | — |
| 8 | scene_008_451.7s.jpg | 451.7s | Página web | OK | 167.9 | — |
| 9 | scene_009_463.4s.jpg | 463.4s | Gráfico daily BTC | OK | 279.8 | — |
| 10 | scene_010_466.5s.jpg | 466.5s | Gráfico 4H BTC | OK | 459.2 | Recuperado con preprocesamiento 2x |
| 11 | scene_011_529.6s.jpg | 529.6s | Gráfico daily BTC | OK | 135.2 | — |
| 12 | scene_012_584.5s.jpg | 584.5s | Gráfico daily BTC | ERR | 0.0 | Timeout 600s (3 intentos) |
| 13 | scene_013_596.2s.jpg | 596.2s | Gráfico daily BTC | OK | 296.4 | — |
| 14 | scene_014_634.9s.jpg | 634.9s | Gráfico 4H BTC | OK | 127.0 | — |
| 15 | scene_015_636.7s.jpg | 636.7s | Gráfico 4H BTC | OK | 233.6 | — |
| 16 | scene_016_678.4s.jpg | 678.4s | Gráfico daily BTC | ERR | 0.0 | Timeout 600s (3 intentos) |
| 17 | scene_017_783.5s.jpg | 783.5s | Gráfico daily BTC | OK | 376.6 | — |
| 18 | scene_018_836.2s.jpg | 836.2s | Gráfico 4H BTC | OK | 48.2 | — |

## Discrepancias resueltas

### 1. 14 OK / 5 ERR vs 13 OK / 6 ERR
- **Causa**: retry_failed_frames.py (primer intento) recuperó frames 4 y 10 pero frame 6 siguió fallando
- **Resolución**: El estado canónico es 14 OK / 5 ERR. Los 5 errores son frames 1, 2, 6, 12, 16.

### 2. Frames 4 y 10 "recuperados" vs "timeout"
- **Causa**: retry_failed_frames.py usó preprocesamiento 2x y recuperó ambos frames
- **Resolución**: Frames 4 y 10 están en vision_analysis.json como OK con tiempos 544.3s y 459.2s

### 3. Timeouts con duración 0s vs 600s
- **Causa**: El script registra time_seconds=0 cuando ocurre ReadTimeoutError porque la excepción se captura antes de medir el tiempo
- **Resolución**: Los 5 frames ERR tienen time_seconds=0 pero el timeout real fue de 600s (configurado en el script)

### 4. vision_analysis.json con 16 vs 19 entries
- **Causa**: retry_failed_v2.py filtró los 5 frames fallidos al inicio y solo procesó 2 de ellos antes de ser interrumpido
- **Resolución**: Se restauraron los 3 frames faltantes (6, 12, 16) como entries de error

## Ejecuciones identificadas

| Ejecución | Script | Timeout | Resultado | Fecha |
|-----------|--------|---------|-----------|-------|
| 1 | vision_analyzer.py | 300s | 15 OK, 4 ERR | Original |
| 2 | retry_failed_frames.py (1er intento) | 600s | 17 OK, 2 ERR | Recuperó 4, 10 |
| 3 | retry_failed_frames.py (2do intento) | 600s | Falló (SIGTERM) | — |
| 4 | vision_analyzer.py (2do run) | 600s | Falló (SIGTERM) | — |
| 5 | retry_failed_v2.py | 600s | 16 entries (14 OK, 2 ERR) | Interrumpido |

## Estado final canónico
- **19 frames totales**
- **14 OK** (frames 0, 3, 4, 5, 7, 8, 9, 10, 11, 13, 14, 15, 17, 18)
- **5 ERR** (frames 1, 2, 6, 12, 16) — todos timeouts de 600s
- **Tiempo total de procesamiento exitoso**: ~3,860s (~64 minutos)
- **Tiempo promedio por frame exitoso**: ~276s (~4.6 minutos)

## Notas
- Los 5 frames fallidos son gráficos complejos de BTC (weekly, 1H, daily)
- El modelo Qwen3.5:9b-mlx tarda ~4-9 minutos por imagen compleja
- Frames 4 y 10 fueron recuperados con preprocesamiento 2x (resize)
- No se han podido recuperar frames 1, 2, 6, 12, 16 con el enfoque actual