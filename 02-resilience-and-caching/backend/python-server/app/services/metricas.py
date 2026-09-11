from redis_client import get_redis
from config import METRICAS_KEY


def register(nodo):
    redis = get_redis()
    redis.hincrby(METRICAS_KEY, nodo, 1)