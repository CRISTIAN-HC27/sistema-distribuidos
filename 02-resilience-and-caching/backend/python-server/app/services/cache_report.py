import json

from db import heavy_report
from redis_client import get_redis
from config import CACHE_KEY, CACHE_TTL


def get_data():
    redis = get_redis()
    cached = redis.get(CACHE_KEY)

    if cached is not None:
        # HIT : devuelve guardado
        return {
            "origen" : "CACHED",
            "data" : json.loads(cached)
        }

    # MISS : calcula, guarda y devuelve
    data = heavy_report()
    redis.set(CACHE_KEY, json.dumps(data), ex=CACHE_TTL)

    return {
        "origen" : "CALCULATED",
        "data" : data
    }