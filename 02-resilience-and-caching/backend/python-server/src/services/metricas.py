from redis_client import get_redis

METRICAS_KEY = "metricas:nodos"


# Métricas por nodo dentro de la tabla Hash compartida.
def register(nodo):
    r = get_redis()
    r.hincrby(METRICAS_KEY, nodo, 1)