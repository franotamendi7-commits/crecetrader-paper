#!/usr/bin/env bash
# Preparar el proyecto para migrar a un VPS Linux (Ubuntu/Debian ARM o x86).
# NO instala nada, NO conecta a ningún servidor. Solo genera el paquete.
set -euo pipefail
SRC="$HOME/YouTubeTradingAgent"
OUT="$HOME/YouTubeTradingAgent/daily_pilot/datos/vps_paquete"
mkdir -p "$OUT"

# 1) Codigo + datos operativos (sin historial pesado ni secretos)
mkdir -p "$OUT/proyecto"
cp -R "$SRC/daily_pilot/scripts" "$OUT/proyecto/"
# Solo las velas 1h/4h de los 13 pares operativos (~125 MB), no todo el historial
mkdir -p "$OUT/proyecto/datos_velas"
for par in BTC XRP HBAR LINK AVAX FIL NEAR THETA ETC ARB INJ DOGE DOT; do
  cp "$SRC/daily_pilot/datos/velas/${par}USDT_1h.json" "$OUT/proyecto/datos_velas/" 2>/dev/null || true
  cp "$SRC/daily_pilot/datos/velas/${par}USDT_4h.json" "$OUT/proyecto/datos_velas/" 2>/dev/null || true
done
cp "$SRC/daily_pilot/datos"/*.json "$OUT/proyecto/" 2>/dev/null || true
cp -R "$SRC/daily_pilot/analisis" "$OUT/proyecto/"
cp -R "$SRC/daily_pilot/dashboard" "$OUT/proyecto/"
mkdir -p "$OUT/proyecto/datos"
cp "$SRC/daily_pilot/datos"/*.json "$OUT/proyecto/datos/" 2>/dev/null || true

# 2) Excluir secretos y archivos prohibidos
find "$OUT" -type f \( -name '*.env' -o -name '*token*' -o -name '*secret*' \) -delete 2>/dev/null || true
cat > "$OUT/NO_MIGRAR.txt" <<'EOF'
NO copiar al VPS:
- store.db
- daily_pilot/metodo/
- la FIRMA
- ~/.hermes/.env (el webhook de Discord se carga aparte en el VPS)
EOF

# 3) systemd units con la MISMA cadencia que el Mac
mkdir -p "$OUT/systemd"
gen_timer() {
  local name="$1" every="$2"
  cat > "$OUT/systemd/${name}.timer" <<EOF
[Unit]
Description=CreceTrader ${name}
[Timer]
OnCalendar=${every}
Persistent=true
[Install]
WantedBy=timers.target
EOF
}
gen_service() {
  local name="$1" script="$2"
  cat > "$OUT/systemd/${name}.service" <<EOF
[Unit]
Description=CreceTrader ${name}
[Service]
Type=oneshot
WorkingDirectory=/opt/crecetrader
ExecStart=/usr/bin/python3 /opt/crecetrader/daily_pilot/scripts/${script}
EOF
}

# velas cada 15 min
gen_service actualizar-velas actualizar_velas.py
cat > "$OUT/systemd/actualizar-velas.timer" <<'EOF'
[Unit]
Description=CreceTrader actualizar velas
[Timer]
OnCalendar=*:0/15
Persistent=true
[Install]
WantedBy=timers.target
EOF
# trackers justo tras el cierre de hora
for s in "scalein:1:tracker_scalein.py" "paper:2:tracker_paper.py" "bos:3:tracker_bos.py"; do
  IFS=: read n m sc <<< "$s"
  gen_service "tracker-$n" "$sc"
  cat > "$OUT/systemd/tracker-$n.timer" <<EOF
[Unit]
Description=CreceTrader tracker $n
[Timer]
OnCalendar=*:0${m}
Persistent=true
[Install]
WantedBy=timers.target
EOF
done
# alertas a las :05
gen_service alertas-senales alertas_senales.py
cat > "$OUT/systemd/alertas-senales.timer" <<'EOF'
[Unit]
Description=CreceTrader alertas Discord
[Timer]
OnCalendar=*:05
Persistent=true
[Install]
WantedBy=timers.target
EOF
# dash refresh cada 5 min
gen_service dash-refresh generar_dashboard_v6.py
cat > "$OUT/systemd/dash-refresh.timer" <<'EOF'
[Unit]
Description=CreceTrader refrescar dash
[Timer]
OnCalendar=*:0/5
Persistent=true
[Install]
WantedBy=timers.target
EOF
# servidor HTTP permanente
cat > "$OUT/systemd/dash-server.service" <<'EOF'
[Unit]
Description=CreceTrader dash HTTP
After=network.target
[Service]
Type=simple
WorkingDirectory=/opt/crecetrader/daily_pilot/dashboard
ExecStart=/usr/bin/python3 -m http.server 8765
Restart=always
RestartSec=3
[Install]
WantedBy=multi-user.target
EOF

# 4) healthcheck anti-reclaim (Oracle)
cat > "$OUT/healthcheck.sh" <<'EOF'
#!/usr/bin/env bash
curl -fsS -o /dev/null http://127.0.0.1:8765/index.html && date -u '+%Y-%m-%dT%H:%M:%SZ' >> /opt/crecetrader/health.log
EOF
chmod +x "$OUT/healthcheck.sh"

# 5) Instrucciones
cat > "$OUT/INSTALL.md" <<'EOF'
# Instalación en VPS (Ubuntu/Debian)
1. apt update && apt install -y python3 python3-pip git curl
2. pip3 install yt-dlp   (solo si se quiere analizar videos en el VPS)
3. mkdir -p /opt/crecetrader && copiar proyecto/ ahí
4. exportar DISCORD_WEBHOOK_URL en /etc/environment o en un EnvironmentFile de systemd
5. copiar systemd/*.service y *.timer a /etc/systemd/system/
6. systemctl daemon-reload
7. systemctl enable --now dash-server.service
8. systemctl enable --now actualizar-velas.timer tracker-scalein.timer tracker-paper.timer tracker-bos.timer alertas-senales.timer dash-refresh.timer
9. verificar: systemctl list-timers | grep crecetrader
10. healthcheck: crontab -e → */10 * * * * /opt/crecetrader/healthcheck.sh
EOF

echo "PAQUETE LISTO: $OUT"
du -sh "$OUT"
ls "$OUT"
