import os

PORT = int(os.environ.get("PORT", "6001"))
REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/0")
STOCK_INICIAL = int(os.environ.get("STOCK_INICIAL", "5"))
STOCK_PRODUCTOS = [p.strip() for p in os.environ.get("STOCK_PRODUCTOS", "1,2,3").split(",") if p.strip()]
STOCK_AUTOSEED = os.environ.get("STOCK_AUTOSEED", "1") == "1"
MODO = os.environ.get("MODO_ESTADO", "redis")
ES_MEMORIA = MODO == "memoria"
NODO = f"stock_{PORT}"
