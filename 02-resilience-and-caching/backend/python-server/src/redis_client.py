import os

import redis  # type: ignore[import-not-found]

# En docker llega REDIS_URL=redis://redis:6379 (red interna del compose)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")


def get_redis():
    # decode_responses=True -> get() devuelve str en vez de bytes
    return redis.Redis.from_url(REDIS_URL, decode_responses=True)