import psycopg.errors # type: ignore

import db # type: ignore
import security # type: ignore


class EmailYaExiste(Exception):
    pass


def registrar(email: str, contrasena: str) -> dict:
    email = security.normalizar_email(email)

    try:
        with db.get_conn() as conn, conn.cursor() as cur:
            cur.execute(
                "INSERT INTO usuarios (email, password) VALUES (%s, %s)",
                (email, security.hashear_contrasena(contrasena)),
            )
            conn.commit()
    except psycopg.errors.UniqueViolation:
        raise EmailYaExiste(email)

    return {"email": email}