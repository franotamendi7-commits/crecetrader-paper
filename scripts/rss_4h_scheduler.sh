#!/bin/bash
# ======================================================================
# RSS 4-HOUR SCHEDULER — rss_priority_processor.py con protección de concurrencia
# ======================================================================
# Ejecuta el procesador RSS una vez cada 4 horas.
# Con protección contra ejecuciones simultáneas mediante lock file.
# ======================================================================

set -uo pipefail

export HOME="/Users/franciscootamendi"
export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin"
export PYTHONUNBUFFERED=1

# Directorios
BASE_DIR="/Users/franciscootamendi/YouTubeTradingAgent"
LOG_DIR="/Users/franciscootamendi/.hermes/cron/output"
mkdir -p "$LOG_DIR"

LOG_FILE="$LOG_DIR/rss_4h_scheduler.log"
LOCK_FILE="$BASE_DIR/experimental/rss_scheduler.lock"
PROGRESS_FILE="$BASE_DIR/experimental/results/historical_progress.json"

# Timestamp log
echo "============================================================" >> "$LOG_FILE"
echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] ┌─────────────────────────────────────┐" >> "$LOG_FILE"
echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] │ RSS 4h Scheduler — Crecetrader Daily Check │" >> "$LOG_FILE"
echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] └─────────────────────────────────────┘" >> "$LOG_FILE"

# 1. Verificar y adquirir bloqueo (lock file)
if [ -f "$LOCK_FILE" ]; then
    EXISTING_PID=$(cat "$LOCK_FILE" 2>/dev/null)
    if [ -n "$EXISTING_PID" ] && kill -0 "$EXISTING_PID" 2>/dev/null; then
        echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] [LOCK] OMITIDO: otro proceso activo (PID $EXISTING_PID), ciclo pospuesto" >> "$LOG_FILE"
        echo "🔒 Ciclo omitido: otro proceso de RSS está ejecutándose (PID $EXISTING_PID)" >&2
        exit 0
    else
        # PID inválido o zombie — eliminarlo
        rm -f "$LOCK_FILE"
        echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] [LOCK] Bloqueo obsoleto eliminado (PID inválido)" >> "$LOG_FILE"
    fi
fi

# 2. Crear nuevo bloqueo
echo $$ > "$LOCK_FILE"
echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] [LOCK] Bloqueo adquirido (PID $$)" >> "$LOG_FILE"

# 3. Ejecutar el procesador
cd "$BASE_DIR" || exit 1
python3 scripts/rss_priority_processor.py \
    --once \
    --no-vision \
    --progress-file "$BASE_DIR/experimental/results/historical_progress.json" \
    --log-file "$LOG_DIR/rss_priority_processor.log" \
    --lock-file "$LOCK_FILE" \
    >> "$LOG_FILE" 2>&1

LOCK_EXIT_CODE=$?

# 4. Liberar bloqueo
rm -f "$LOCK_FILE"
echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] [LOCK] Bloqueo liberado." >> "$LOG_FILE"

# 5. Aviso de resultado
if [ $LOCK_EXIT_CODE -eq 0 ]; then
    echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] ✅ RSS 4h check completado exitosamente." >> "$LOG_FILE"
else
    echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] ❌ RSS 4h check falló (código $LOCK_EXIT_CODE)" >> "$LOG_FILE"
fi

exit $LOCK_EXIT_CODE
