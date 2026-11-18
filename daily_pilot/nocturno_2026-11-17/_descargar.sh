#!/bin/bash
# Descarga de subtitulos (solo es) de los 20 videos nocturnos. No descarga video.
set -u
BASE="/Users/franciscootamendi/YouTubeTradingAgent/daily_pilot/nocturno_2026-11-17"
IDS="cjUwyMHygEs xHR9d-0ToXU lwb4Qxy8D9w 3OZ2vJPj92o CmbG9QntQ10 G3GPk1mxPcQ D6XrdvQVTgk ac6-r7g8pao TT07djUkfhE B4Vf3bSk5GY lkMTbT7tK8c NVZfPTaeuLc 0JHYwOCzCKI avNOZfXdyX8 2QjLmPdDKlk nqzn3DsZzKU MgTOoUWEq-M y9gsOU6_Bzw FkPGRd7kXnE _Lxz34x7eGg"
mkdir -p "$BASE"
for id in $IDS; do
  d="$BASE/$id"
  mkdir -p "$d"
  if ls "$d"/*.vtt >/dev/null 2>&1; then echo "SKIP $id"; continue; fi
  ok=0
  for intento in 1 2 3; do
    yt-dlp --skip-download --write-auto-subs --sub-langs es --sub-format vtt \
      --no-warnings --quiet --no-progress \
      -o "$d/$id" "https://www.youtube.com/watch?v=$id" >/dev/null 2>&1
    if ls "$d"/*.vtt >/dev/null 2>&1; then ok=1; break; fi
    sleep 15
  done
  if [ "$ok" = "1" ]; then echo "OK $id"; else echo "FAIL $id"; fi
done
echo "RESUMEN: $(find "$BASE" -name '*.vtt' | wc -l) vtt"
