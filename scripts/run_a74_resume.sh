#!/bin/bash
# A.7.4: reanudacion secuencial de los 3 videos priorizados (vision + validacion)
cd ~/YouTubeTradingAgent
PY=.venv/bin/python
for V in 5KtjJ8kefQ4 DnwM-2nuS4s j06_M-fADjM; do
  echo "=== $(date '+%H:%M:%S') INICIO $V ==="
  $PY run_video.py --video "$V" --vision-model qwen2.5vl:3b
  echo "=== $(date '+%H:%M:%S') FIN $V ==="
done
echo "=== $(date '+%H:%M:%S') SECUENCIA COMPLETA ==="
