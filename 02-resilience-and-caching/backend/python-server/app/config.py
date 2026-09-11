import os
from pathlib import Path

PORT = int(os.getenv("PORT", "5003"))
NODO = f"nodo_{PORT}"
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
DB_PATH = os.getenv("DB_PATH", str(Path(__file__).parent.parent / "data" / "db.json"))


# Constants variable configuration for Redis
RATE_KEY = "ratelimit:global"
TIME_WINDOW = 10
LIMIT_REQUEST = 30

METRICAS_KEY = "metricas:nodo"

CACHE_KEY = "cache:heavy_report"
CACHE_TTL = 10 # seconds before expires