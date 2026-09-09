import { Router } from 'express';
import redis from '../redis.js';

const router = Router();
const PORT = parseInt(process.env.PORT) || 5001;
const NODO = `nodo_${PORT}`;

router.get('/', async (_req, res) => {
  try {
    const metricas = await redis.hGetAll('metricas:nodos');
    const ventana  = parseInt(await redis.get('ratelimit:global')) || 0;
    res.json({
      nodo: NODO,
      estado: 'UP',
      peticiones_nodo: parseInt(metricas[NODO]) || 0,
      peticiones_ventana: ventana,
    });
  } catch {
    res.status(500).json({ nodo: NODO, estado: 'ERROR' });
  }
});

export default router;