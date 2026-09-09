import redis from '../redis.js';

// Rate limiting por ventana fija: INCR + EXPIRE en la 1ª petición.
async function check() {
  const n = await redis.incr('ratelimit:global');
  if (n === 1) {
    await redis.expire('ratelimit:global', 10);  // 1ª petición abre la ventana
  }
  return { permitted: n <= 30, n, limited: 30, window: 10 };
}

export default { check };