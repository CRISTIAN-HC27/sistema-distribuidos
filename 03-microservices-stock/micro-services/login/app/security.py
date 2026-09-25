import hashlib
import hmac
import re

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

HASH_ALGORITHM = "sha256"
HASH_PREFIX = "pbkdf2_sha256"


def normalizar_email(email: str) -> str:
    return (email or "").strip().lower()


def email_valido(email: str) -> bool:
    return len(email) <= 254 and bool(EMAIL_RE.match(email))


def verificar_contrasena(contrasena: str, almacenado: str) -> bool:
    try:
        prefijo, iteraciones, salt_hex, digest_hex = (almacenado or "").split("$")
        if prefijo != HASH_PREFIX:
            return False
        esperado = bytes.fromhex(digest_hex)
        calculado = hashlib.pbkdf2_hmac(
            HASH_ALGORITHM,
            contrasena.encode("utf-8"),
            bytes.fromhex(salt_hex),
            int(iteraciones),
        )
    except (AttributeError, ValueError):
        return False
    return hmac.compare_digest(calculado, esperado)
