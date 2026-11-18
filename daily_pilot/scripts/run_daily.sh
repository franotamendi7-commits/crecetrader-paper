#!/bin/bash
# YouTube Analyst — piloto diario (LISTO, NO INSTALADO).
# Detecta videos nuevos, transcribe con timestamps y registra. SIN vision.
# Para programarlo: crontab -e  ->  0 9 * * * /Users/franciscootamendi/YouTubeTradingAgent/daily_pilot/scripts/run_daily.sh
set -uo pipefail
export HOME="/Users/franciscootamendi"
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
BASE="/Users/franciscootamendi/YouTubeTradingAgent"
LOG="$HOME/.hermes/cron/output/youtube-analyst-pilot.log"
mkdir -p "$(dirname "$LOG")"
echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] INICIO piloto diario" >> "$LOG"
cd "$BASE" || exit 1
.venv/bin/python3 daily_pilot/scripts/daily_pilot.py >> "$LOG" 2>&1
code=$?
echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] FIN piloto diario (exit=$code)" >> "$LOG"
exit $code
