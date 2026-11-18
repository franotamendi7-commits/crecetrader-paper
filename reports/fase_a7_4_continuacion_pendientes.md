# FASE A.7.4 — Continuación de videos pendientes

Fecha: 2026-11-15
Ejecutor: Hermes Agent (modelo LLM `meituan/longcat-2.5:free`, provider Nous)
Visión: `qwen2.5vl:3b` vía Ollama local (`localhost:11434`), prompt `VISION_PROMPT_TEMPLATE`
Muestreo de frames: `fps=1/30`, `max_frames=20` (recorte a los últimos 20 si el video es largo)

## Videos procesados en esta sesión

| video | título | duración | frames | instrumentos detectados | estado |
|---|---|---|---|---|---|
| LzPTdClLo_w | Bitcoin rebota tras la apertura de Wall Street… 78.241 manda | 524 s | 17 | BTCUSD, ETHUSD, XAUUSD, ES | completed |
| XLgPycsN0ls | QUÉ HARÁ BITCOIN HOY 30.10.26 — BTC-ETH-ORO-SP500-NASDAQ | 1216 s | 20 | BTCUSD, ETHUSD, XAUUSD, ES, VX1!, UNKNOWN×2 | completed |
| dPHvRw1wzYQ | (análisis BTC) | — | 20 | BTCUSD | completed |
| jeOFS1TZYQA | Bitcoin no recupera los 78.241: plan 71.000–69.000 | 774 s | 20 | BTCUSD, ETHUSD, XAUUSD, ES, NQ, AMD, MDT | completed |
| s3KxjqkzwKM | Bitcoin el día de las elecciones: 76.852 clave | 993 s | 20 | BTCUSD, ETHUSD, ES, NQ, UNKNOWN | completed |
| scJ-ai2FRiE | Bitcoin recupera los 78.241 tras las elecciones… | 884 s | 20 | BTCUSD, ETHUSD, XAUUSD, ES, NQ, AMD | completed |

No se reprocesaron: `EJoLhxbwYxo` (ya completed) ni las etapas completadas de `LFHkc5dUoLw`.

## Verificación state ↔ disco (RECOMPUTADA)

| video | status | dl/fr/tr/vi/va | mp4 | frames | vtt | transcript json | analysis | visión no vacía |
|---|---|---|---|---|---|---|---|---|
| EJoLhxbwYxo | completed | T/T/T/T/T | sí | 20 | sí | sí | sí | 20/20 |
| LFHkc5dUoLw | processing | T/T/T/T/**F** | sí | 20 | sí | sí | sí | 20/20 |
| LzPTdClLo_w | completed | T/T/T/T/T | sí | 17 | sí | sí | sí | 17/17 |
| XLgPycsN0ls | completed | T/T/T/T/T | sí | 20 | sí | sí | sí | 20/20 |
| dPHvRw1wzYQ | completed | T/T/T/T/T | sí | 20 | sí | sí | sí | 20/20 |
| jeOFS1TZYQA | completed | T/T/T/T/T | sí | 20 | sí | sí | sí | 20/20 |
| s3KxjqkzwKM | completed | T/T/T/T/T | sí | 20 | sí | sí | sí | 20/20 |
| scJ-ai2FRiE | completed | T/T/T/T/T | sí | 20 | sí | sí | sí | 20/20 |

## Incidencias y correcciones

1. **YouTube HTTP 429 en subtítulos `en`** (todos los videos nuevos): `extract_transcript` cae porque intenta `es,en`. Workaround: descargar solo `.es.vtt` y dejar que el parser cue-wise genere el JSON. No se modificó el repositorio.
2. **`artifacts.analysis_file = null`** (defecto documentado): el pipeline crashea con `AttributeError: 'NoneType' object has no attribute 'parent'`. Resuelto asignando `experimental/results/historical/{video}_analysis.json` antes de la visión.
3. **`scJ-ai2FRiE` tenía `transcript=true` sin archivo**: flag falso reconciliado a `false` y reprocesado.
4. **Visión lenta intermitente**: algunos frames tardaron 110–195 s (frente a ~10–20 s habituales). No hubo timeouts (límite 300 s).

## Validación de LFHkc5dUoLw — NO satisfactoria

`validation` permanece `false`. Defectos: D1 precios de visión no corresponden a niveles reales; D2 `MA` falso positivo y Fibonacci no reportado; D3 sin mapeo frame↔timestamp; D4 transcripción triplicada; D5 cobertura solo BTCUSD; D6 `frame_4013` no inspeccionado (429 auxiliar).
Detalle completo: `reports/fase_a7_4_validacion_LFHkc5dUoLw.md`.

## Pendiente

- Validación visual/temporal sustantiva de los 6 videos nuevos (la validación automática solo verifica artefactos).
- Re-inspección de `frame_4013` de LFHkc5dUoLw.
- Corrección del prompt de visión (transcribir niveles reales, `null` si no hay indicador) — requiere autorización.
