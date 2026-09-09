-- PRAGMAs de velocidad para la carga masiva
PRAGMA journal_mode = WAL;
PRAGMA synchronous  = OFF;
PRAGMA temp_store   = MEMORY;

-- Genera 1.000.000 de productos (100 x 100 x 100 = 1M).
-- SQLite limita la profundidad de un CTE recursivo a 1000,
-- por eso usamos 3 tablas de 100 filas en producto cartesiano.
INSERT INTO productos (nombre, categoria, precio)
WITH RECURSIVE cnt(x) AS (
    SELECT 1
    UNION ALL
    SELECT x + 1 FROM cnt WHERE x < 100
)
SELECT
    'Producto ' || printf('%07d',
        (c1.x - 1) * 10000 + (c2.x - 1) * 100 + c3.x) AS nombre,
    CASE ((c1.x - 1) * 10000 + (c2.x - 1) * 100 + c3.x) % 10
        WHEN 0 THEN 'Electronica'
        WHEN 1 THEN 'Hogar'
        WHEN 2 THEN 'Ropa'
        WHEN 3 THEN 'Deportes'
        WHEN 4 THEN 'Juguetes'
        WHEN 5 THEN 'Alimentos'
        WHEN 6 THEN 'Belleza'
        WHEN 7 THEN 'Libros'
        WHEN 8 THEN 'Herramientas'
        ELSE 'Automotriz'
    END AS categoria,
    ABS(RANDOM() % 500001) + 100 AS precio   -- 100 .. 500.100 pesos
FROM cnt c1, cnt c2, cnt c3;

-- Índices DESPUÉS de la carga (mucho más rápido)
CREATE INDEX IF NOT EXISTS idx_categoria ON productos(categoria);
CREATE INDEX IF NOT EXISTS idx_precio    ON productos(precio);