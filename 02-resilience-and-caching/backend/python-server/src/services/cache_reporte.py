import json

from db import reporte_pesado
from redis_client import get_redis

CACHE_KEY = "cache:reporte_pesado"
CACHE_TTL = 10  # segundos antes de expirar


# Caché con TTL: HIT -> devuelve guardado; MISS -> calcula, guarda y devuelve.
def get_or_calculated():
    r = get_redis()
    cached = r.get(CACHE_KEY)
    if cached is not None:
        return {"origen": "cache", "datos": json.loads(cached)}   # HIT

    datos = reporte_pesado()                                       # MISS
    r.set(CACHE_KEY, json.dumps(datos), ex=CACHE_TTL)
    return {"origen": "calculo", "datos": datos}