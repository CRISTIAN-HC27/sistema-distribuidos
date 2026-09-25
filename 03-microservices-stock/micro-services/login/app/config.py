import os

PORT = int(os.environ.get("PORT", "6004"))
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://tiendanorte:tiendanorte@postgres:5432/tiendanorte",
)
NODO = f"login_{PORT}"
