import db # type: ignore
import security # type: ignore


class CredencialesInvalidas(Exception):
    pass


def autenticar(email: str, contrasena: str) -> dict:
    email = security.normalizar_email(email)

    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT email, password FROM usuarios WHERE email = %s",
            (email,),
        )
        cuenta = cur.fetchone()

    if cuenta is None or not security.verificar_contrasena(contrasena, cuenta[1]):
        raise CredencialesInvalidas(email)

    return {"email": cuenta[0]}
