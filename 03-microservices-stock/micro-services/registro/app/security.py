import hashlib
import re
import secrets

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

HASH_ALGORITHM = "sha256"
HASH_PREFIX = "pbkdf2_sha256"
PBKDF2_ITERATIONS = 100_000


def normalizar_email(email: str) -> str:
    return (email or "").strip().lower()


def email_valido(email: str) -> bool:
    return len(email) <= 254 and bool(EMAIL_RE.match(email))


def validar_contrasena(pw: str) -> str | None:
    if len(pw) < 8:
        return "la contraseña debe tener al menos 8 caracteres"
    if len(pw) > 128:
        return "la contraseña es demasiado larga"
    return None


def hashear_contrasena(contrasena: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        HASH_ALGORITHM, contrasena.encode("utf-8"), salt, PBKDF2_ITERATIONS
    )
    return f"{HASH_PREFIX}${PBKDF2_ITERATIONS}${salt.hex()}${digest.hex()}"
