import { crearApp } from './app.js';
import redis from './redis.js';

const PORT = parseInt(process.env.PORT) || 5001;
const NODO = `nodo_${PORT}`;

async function main() {
  await redis.connect();
  console.log(`[${NODO}] Conectado a Redis`);

  const app = crearApp();
  app.listen(PORT, () => console.log(`[${NODO}] Escuchando en :${PORT}`));
}

main().catch((err) => {
  console.error('Fallo al iniciar:', err);
  process.exit(1);
});