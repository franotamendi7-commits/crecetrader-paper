# SNAPSHOT CONGELADO — R4 (102 videos)

> **Congelado el 2026-11-18.** No debe moverse durante la auditoría.
> Si `git rev-parse HEAD` ≠ `e7890db…`, la auditoría es inválida.

```
commit            e7890db077a5bce18516d8397dd82ad1c963bc65
rama              crecetrader-limpio
store.db          6055bfe62625cea976bc156fdc5383770770c98cc9128e525012d5aa855026a9
dashboard/index   89e9af609df1d9895e1f7424dafad6b5ded9a1d7dd6649972e0c6e59125c7be8
playbook          c98e710ce48526582905d05b9de54c690c5ea0c66ccfbcb2a58d07083d1c6b50
```

## Verificación

```bash
cd /Users/franciscootamendi/YouTubeTradingAgent
git rev-parse HEAD
shasum -a 256 daily_pilot/knowledge/store.db daily_pilot/dashboard/index.html \
              daily_pilot/metodo/playbook_v0.1.md
python3 -B daily_pilot/knowledge/verify_integrity.py
python3 -B daily_pilot/tests/run_all.py
```

## E1 — 102 vídeos

| | |
|---|---|
| vídeos | **102** |
| cues | **105.275** |
| claims | **18.562** |
| análisis | **102/102** |
| integridad | **OK** · `.control` re-sellado |

## Suite
**14 read-only OK** · 0 fallos · FUENTES INTACTAS.

## Reglas de negocio en este snapshot

- **Corpus** = aprendizaje del método (102 vídeos, históricos).
- **Dash** = **solo el último video** (`cH2KY5vnsVQ`). Nunca se mezcla histórico.
- **Sin feed real**: el precio es el del video; Fundamental/Sentimiento → NO DISPONIBLE.
- **Sensor visual**: VLM local `qwen3-vl:8b-instruct`; ground truth de 19 frames
  (`daily_pilot/vision_mission/TU_ANOTACION.csv`); dedup + prompt C04.
- **PAPER_ONLY=true** en `risk_manager` y `allocacion`.
