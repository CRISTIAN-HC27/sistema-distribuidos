# Taller 2 - Resiliencia y Caché (Redis + Nginx + Node)

Cluster con 3 patrones avanzados: Rate Limiting, Caché con TTL y Métricas con Hashes.

## Arquitectura
Nginx LB (:80 y :8000) -> backend-node-1 (:5001) + backend-node-2 (:5002) + backend-python (:5003)
Backends leen: Redis (patrones) y data/db.sqlite (1.000.000 de productos).

## Puesta en marcha
1) Liberar puertos del taller 1:   sudo systemctl stop nginx && pm2 kill
2) Cargar la BD (una vez):          node database/load.js
3) Levantar:                        docker compose up --build -d
4) Verificar:                       bash stress.sh http://localhost:8000/api 60

## Auditar los patrones (entregas del taller)
docker compose exec redis redis-cli HGETALL metricas:nodos   # métricas por nodo
docker compose exec redis redis-cli TTL cache:reporte_pesado # segundos restantes
docker compose exec redis redis-cli GET ratelimit:global     # contador de la ventana

## Carga manual de la BD con sqlite3 (opcional, en vez de node database/load.js)
sudo apt install sqlite3
mkdir -p data
sqlite3 data/db.sqlite < database/schema.sql
sqlite3 data/db.sqlite < database/seed.sql

## Detener
docker compose down      # conserva data/ y redes
docker compose down -v   # además borra volúmenes/redes