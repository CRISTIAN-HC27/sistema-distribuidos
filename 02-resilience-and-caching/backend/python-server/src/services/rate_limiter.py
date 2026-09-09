from redis_client import get_redis

RATE_KEY = "ratelimit:global"
VENTANA = 10  # segundos por ventana
LIMITE = 30   # peticiones máximas por ventana


# Rate limiting por ventana fija: INCR + EXPIRE en la 1ª petición.
def check():
    r = get_redis()
    n = r.incr(RATE_KEY)
    if n == 1:
        r.expire(RATE_KEY, VENTANA)  # 1ª petición abre la ventana
    return {"permitted": n <= LIMITE, "n": n, "limited": LIMITE, "window": VENTANA}