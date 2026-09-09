-- Esquema del catálogo: 1.000.000 de productos
CREATE TABLE IF NOT EXISTS productos (
    id        INTEGER PRIMARY KEY,
    nombre    TEXT    NOT NULL,
    categoria TEXT    NOT NULL,
    precio    INTEGER NOT NULL CHECK (precio >= 0)
);