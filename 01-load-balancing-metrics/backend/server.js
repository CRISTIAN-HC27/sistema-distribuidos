const express = require('express');
const { createClient } = require('redis');

const app = express();
const PORT = parseInt(process.env.PORT) || 3000;

// Permitir CORS para que el dashboard (8080) pueda leer los /status de estos backends
app.use((req, res, next) => {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    if (req.method === 'OPTIONS') return res.sendStatus(204);
    next();
});

const redisClient = createClient({
  url: process.env.REDIS_URL || 'redis://localhost:6379',
});

redisClient.on('error', (err) => console.error(`[${PORT}] Redis Client Error`, err));

async function startServer() {
    await redisClient.connect();
    console.log(`[${PORT}] Backend UP y conectado a Redis`);

    // GET / -> incrementa contadores y devuelve el global
    app.get('/', async (req, res) => {
        try {
            let total = await redisClient.incr('total_peticiones');
            let nodo = await redisClient.incr(`peticiones_nodo_${PORT}`);
            res.json({
                nodo: PORT,
                total_peticiones: total,
            })
        } catch (err) {
            res.status(500).json({ error: 'Error fetching value from Redis' });
        }
    })

    // GET /status -> para el dashboard (heartbeat + contadores)
    app.get('/status', async (req, res) => {
        try {
            let total = parseInt(await redisClient.get('total_peticiones')) || 0;
            let node = parseInt(await redisClient.get(`peticiones_nodo_${PORT}`)) || 0;
            res.json({
                nodo: PORT,
                estado: 'UP',
                peticiones_nodo: node,
                peticiones_totales: total,
            })
        } catch (err) {
            res.status(500).json({ nodo: PORT, estado: 'ERROR' });
        }
    })

    const server = app.listen(PORT, () => {
        console.log(`[${PORT}] Escuchando en http://localhost:${PORT}`);
    });

    // Graceful shutdown: al recibir SIGTERM/SIGINT cierra Redis y el server
    const shutdown = async () => {
        console.log(`[${PORT}] Apagando graceful shutdown...`);
        server.close(async () => {
            await redisClient.quit();
            process.exit(0);
        });
        // Fuerza salida si algo no cierra en 3s
        setTimeout(() => process.exit(1), 3000).unref();
    };
    process.on('SIGTERM', shutdown);
    process.on('SIGINT', shutdown);
}

startServer();
