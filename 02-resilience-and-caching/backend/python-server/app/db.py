import sqlite3
import sys
import threading

from config import DB_PATH

_connection = None
_lock = threading.Lock()

def _conection() -> sqlite3.Connection:
    global _connection

    if _connection is None:
        _connection = sqlite3.connect(DB_PATH, check_same_thread=False)
        _connection.row_factory = sqlite3.Row

    return _connection


try:
    _conection().execute("SELECT 1 FROM productos LIMIT 1").fetchone()
except sqlite3.Error:
    print("Error connecting to database.")
    sys.exit(1)


def heavy_report():
    with _lock:
        cur = _connection.execute(
            """
            SELECT categoria,
                COUNT(*)                AS cantidad,
                ROUND(AVG(precio),2)    AS precio_promedio,
                SUM(precio)             AS ingresos_totales
            FROM productos
            GROUP BY categoria
            ORDER BY ingresos_totales DESC
            """
        )

        rows = cur.fetchall()

    return [dict(row) for row in rows]

