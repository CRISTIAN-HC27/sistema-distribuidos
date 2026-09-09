import { Router } from 'express';
import rateLimiter  from '../services/rateLimiter.js';
import metricas     from '../services/metricas.js';
import cacheReporte from '../services/cacheReporte.js';

const router = Router();
const PORT = parseInt(process.env.PORT) || 5001;
const NODO = `nodo_${PORT}`;

router.get('/', async (_req, res) => {
  const inicio = Date.now();

  try {
    const rl = await rateLimiter.check();                      // A
    if (!rl.permitted) {
      return res.status(429).json({
        error: 'Too Many Requests',
        nodo: NODO,
        peticiones_ventana: rl.n,
        limite: rl.limited,
        ventana_s: rl.window,
      });
    }

    await metricas.register(NODO);                             // C

    const { origen, datos } = await cacheReporte.getOrCalculated(); // B

    res.json({
      nodo: NODO,
      origen,
      latencia_ms: Date.now() - inicio,
      peticiones_ventana: rl.n,
      datos,
    });
  } catch (err) {
    console.error(`[${NODO}] Error en /api`, err);
    res.status(500).json({ error: 'Error interno', nodo: NODO });
  }
});

export default router;