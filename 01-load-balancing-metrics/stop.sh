#!/bin/bash
# stop.sh - Detiene todo: backends + dashboard
echo "Deteniendo backends (pm2)..."
pm2 stop backend/ecosystem.config.js

echo "Deteniendo dashboard..."
pkill -f "http.server 8080" || echo "  (dashboard no estaba corriendo)"

echo "Todo detenido."
