# SNAPSHOT CONGELADO — auditoría R3

> **Congelado el 2026-11-18 antes de entregar el prompt a DeepSeek.**
> No debe moverse durante la auditoría. Si `git rev-parse HEAD` cambia, la auditoría es inválida.

```
commit            939440c4431f6568b96bcec0753a9a063d0a9017
rama              crecetrader-limpio
store.db          6826b7e148fe13da9ecf58841d6a0f30627b2bc191541252d7411cdcedc76976
dashboard/index   4c73f494b46682c2f92b7d004a120b4eb94337b8c8c97d20224d2e90a611d9a6
estado_hoy.json   e530689e5b9e8eb70e1dbce92cacd88c08cfa56096bad55212eb901d4cba9475
dashboard_data    d92faf246999b87635ad7114b53ead7fbf8ab8cce7eb6f88e7f639b7a17b5f7e
prompt R2         d5fc292f0e808aaae53108793f5cc146cd3ff2f5d894f38adaa8a720992e5bbc
playbook          7286185e1daecfb6e71f418f50a4bfd5e0fec5e1394b6afc3c8f090c7602391c
run_all.py        47acdc446dca85e5c684f7d66eafd2e34e2d25216db05adc21d38e85ccdf88c7
```

## Verificación de los hashes

```bash
cd /Users/franciscootamendi/YouTubeTradingAgent
git rev-parse HEAD
shasum -a 256 daily_pilot/investigacion/PROMPT_AUDITORIA_DEEPSEEK_R2.md \
              daily_pilot/metodo/playbook_v0.1.md daily_pilot/tests/run_all.py \
              daily_pilot/knowledge/store.db daily_pilot/dashboard/index.html \
              daily_pilot/estado/estado_hoy.json daily_pilot/datos/dashboard_data.json
```

## E1

42 vídeos · 34.061 cues · 6.831 claims · `verify_integrity.py` OK · `.control.json` cierra.

## Suite

**14 read-only OK** (12 suites + `test_c11_cruzado` + `test_signal_classifier`) · 0 fallos ·
2 suites de integración (**no correr en vivo; usan `--integracion` en copia**).

## Aislamiento (R2-01, verificado)

`BASE` y `STORE_PATH` son **relativos al archivo**. Desde una copia del árbol:

```
BASE en copia -> /var/folders/.../tmp.XXXX
STORE en copia -> /var/folders/.../tmp.XXXX/daily_pilot/knowledge/store.db
```

**La copia escribe en la copia.** Verificá corriendo el mismo `git archive` + `rsync` y
comprobando que `run_all.BASE` apunte a la copia.
