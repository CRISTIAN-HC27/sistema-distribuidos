import os

PORT = int(os.environ.get("PORT", "6003"))
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://tiendanorte:tiendanorte@postgres:5432/tiendanorte",
)
NODO = f"registro_{PORT}"