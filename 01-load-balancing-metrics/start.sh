#!/bin/bash
# start.sh - Levanta todo: Redis + 2 backends + Nginx + Dashboard
set -e

echo "Iniciando Redis..."
redis-server --daemonize yes
sleep 1
redis-cli ping

echo "Iniciando backends con pm2 (5001 y 5002)..."
pm2 start backend/ecosystem.config.js
pm2 save

echo "Recargando Nginx..."
sudo nginx -t && sudo systemctl reload nginx

echo "Iniciando Dashboard en http://localhost:8080..."
python3 -m http.server 8080 --directory frontend &

echo ""
echo "Todo listo:"
echo "  Backend 1: http://localhost:5001"
echo "  Backend 2: http://localhost:5002"
echo "  Nginx LB:  http://localhost:80"
echo "  Dashboard: http://localhost:8080"
