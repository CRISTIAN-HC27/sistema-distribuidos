import redis from '../redis.js';

// Métricas por nodo dentro de la tabla Hash compartida.
async function register(node) {
  await redis.hIncrBy('metricas:nodos', node, 1);
}

export default { register };