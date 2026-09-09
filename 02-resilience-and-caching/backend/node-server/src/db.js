import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { DatabaseSync } from 'node:sqlite';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DB_PATH = process.env.DB_PATH || path.join(__dirname, '..', '..', 'data', 'db.sqlite');

const db = new DatabaseSync(DB_PATH);
db.exec('PRAGMA busy_timeout = 3000;');

try {
  db.exec('SELECT 1 FROM productos LIMIT 1;');
} catch {
  console.error('[db] ERROR: data/db.sqlite no existe o está vacío.');
  console.error('[db] Carga la base primero:   node database/load.js');
  console.error('[db]   o con sqlite3:         sqlite3 data/db.sqlite < database/schema.sql');
  console.error('[db]                           sqlite3 data/db.sqlite < database/seed.sql');
  process.exit(1);
}

// "Cálculo pesado": recorre los 1M de productos y los agrupa por categoría.
function reportePesado() {
  return db.prepare(`
    SELECT categoria,
           COUNT(*)              AS cantidad,
           ROUND(AVG(precio), 2) AS precio_promedio,
           SUM(precio)           AS ingresos_totales
    FROM productos
    GROUP BY categoria
    ORDER BY ingresos_totales DESC
  `).all();
}

export { reportePesado };