from redis_client import get_redis
from config import RATE_KEY, TIME_WINDOW, LIMIT_REQUEST

def check():
    redis = get_redis()
    n = redis.incr(RATE_KEY)

    if n == 1:
        # First request open window
        redis.expire(RATE_KEY, TIME_WINDOW)
    return {
        "permitted": n <= LIMIT_REQUEST,
        "number_request": n,
        "limited" : LIMIT_REQUEST,
        "time_window": TIME_WINDOW
    }