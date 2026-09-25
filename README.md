# Sistemas Distribuidos

Actividades y posibles soluciones a los talleres de la materia **Sistemas Distribuidos**.

## Contenido

| # | Taller | Temas |
|---|--------|-------|
| 01 | [Load Balancing y Métricas](01-load-balancing-metrics/) | Nginx Load Balancer, Round Robin, Least Connections, IP Hash, Failover, Redis como store compartido, Dashboard de métricas |
| 02 | [Resiliencia y Caché](02-resilience-and-caching/) | Rate Limiting, Caché con TTL, Métricas con Redis Hashes, Nginx + Node.js + Python, Docker Compose |
| 03 | [Microservicios y Estado Compartido](03-microservices-stock/) | Registro, Login, Stock con Redis, dos instancias del mismo servicio, compra atomica, prueba de concurrencia |

## Requisitos

- Node.js 18+
- Redis
- Nginx
- Docker y Docker Compose (para los Talleres 2 y 3)
- PM2 (`npm install -g pm2`)

## Inicio rápido

Cada taller tiene su propio README con instrucciones detalladas. En general:

```bash
# Taller 1
cd 01-load-balancing-metrics
./start.sh

# Taller 2
cd 02-resilience-and-caching
docker compose up --build -d

# Taller 3
cd 03-microservices-stock
docker compose up --build -d
bash concurrencia.sh
```

## Autor

**Cristian Huanca** - [CRISTIAN-HC27](https://github.com/CRISTIAN-HC27)
