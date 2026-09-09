import redis from '../redis.js';
import { reportePesado } from '../db.js';

// Caché con TTL: HIT -> devuelve guardado; MISS -> calcula, guarda y devuelve.
async function getOrCalculated() {
  const cached = await redis.get('cache:reporte_pesado');
  if (cached != null) {
    return { origen: 'cache', datos: JSON.parse(cached) };   // HIT
  }

  const datos = reportePesado();                             // MISS
  await redis.set('cache:reporte_pesado', JSON.stringify(datos), { EX: 10 });
  return { origen: 'calculo', datos };
}

export default { getOrCalculated };