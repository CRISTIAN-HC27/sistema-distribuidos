from contextlib import contextmanager

from psycopg_pool import ConnectionPool # type: ignore

from config import DATABASE_URL

pool = ConnectionPool(DATABASE_URL, min_size=1, max_size=5)


@contextmanager
def get_conn():
    with pool.connection() as conn:
        yield conn
