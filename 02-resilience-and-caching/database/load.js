const fs = require('node:fs');
const path = require('node:path');
const { DatabaseSync } = require('node:sqlite');

const DATA_DIR = path.join(__dirname, '..', 'data');
const DB_PATH = path.join(DATA_DIR, 'db.sqlite');

fs.mkdirSync(DATA_DIR, { recursive: true });

const schema = fs.readFileSync(path.join(__dirname, 'schema.sql'), 'utf8');
const seed = fs.readFileSync(path.join(__dirname, 'seed.sql'), 'utf8');

const t0 = Date.now();
const db = new DatabaseSync(DB_PATH);

db.exec(schema);
console.log('Tabla creada, insertando 1.000.000 de productos...');
db.exec(seed);

const { n } = db.prepare('SELECT COUNT(*) AS n FROM productos').get();
console.log(`Listo: ${Number(n).toLocaleString()} productos en data/db.sqlite (${Date.now() - t0} ms)`);
db.close();