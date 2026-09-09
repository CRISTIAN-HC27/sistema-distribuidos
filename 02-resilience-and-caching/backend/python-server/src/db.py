import os
import sqlite3
import sys
import threading
from pathlib import Path

DB_PATH = os.getenv("DB_PATH", str(Path(__file__).resolve().parent.parent.parent / "data" / "db.sqlite"))

_conexion = None
_lock = threading.Lock()


def _conectar():
    global _conexion
    if _conexion is None:
        _conexion = sqlite3.connect(DB_PATH, check_same_thread=False)
        _conexion.row_factory = sqlite3.Row
    return _conexion


# Guarda: si la tabla no existe, la BD no fue cargada -> error claro
try:
    _conectar().execute("SELECT 1 FROM productos LIMIT 1").fetchone()
except sqlite3.Error:
    print("[db] ERROR: data/db.sqlite no existe o está vacío.")
    print("[db] Carga la base primero:   node database/load.js")
    print("[db]   o con sqlite3:         sqlite3 data/db.sqlite < database/schema.sql")
    print("[db]                           sqlite3 data/db.sqlite < database/seed.sql")
    sys.exit(1)


# "Cálculo pesado": recorre los 1M de productos y los agrupa por categoría.
def reporte_pesado():
    with _lock:
        cur = _conexion.execute(
            """
            SELECT categoria,
                   COUNT(*)                    AS cantidad,
                   ROUND(AVG(precio), 2)       AS precio_promedio,
                   SUM(precio)                 AS ingresos_totales
            FROM productos
            GROUP BY categoria
            ORDER BY ingresos_totales DESC
            """
        )
        filas = cur.fetchall()
    return [dict(fila) for fila in filas]