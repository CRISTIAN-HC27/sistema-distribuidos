import redis # type:ignore[import-not-found]

from config import REDIS_URL

def get_redis() -> redis.Redis:
    return redis.Redis.from_url(REDIS_URL, decode_responses=True)

