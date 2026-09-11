import time

from fastapi import APIRouter
from fatsapi.responses import JSONResponse

from config import NODO, METRICAS_KEY, RATE_KEY
from redis_client import get_redis
from services.cache_report import get_data
from services.metricas import register
from services.rate_limiter import check


router = APIRouter()

@router.get("/api")
def api():
    inicio = time.time()
    try:
        rl = check()                                # A
        if not rl["permitted"]:
            return JSONResponse(
                status_code=429, 
                content={
                    "error": "Too Many Requests",
                    "nodo": NODO,
                    "peticiones_ventana": rl["n"],
                    "limite": rl["limited"],
                    "ventana_s": rl["window"],
                })

        register(NODO)                              # C

        res = get_data()                   # B
        res.update({
            "nodo": NODO,
            "latencia_ms": round((time.time() - inicio) * 1000, 2),
            "peticiones_ventana": rl["n"],
        })
        return res
    except Exception as err:                        # noqa: BLE001
        print(f"[{NODO}] Error en /api:", err)
        return JSONResponse(
            status_code=500, 
            content={"error": "Error interno", "nodo": NODO}
            )


@router.get("/status")
def status():
    try:
        r = get_redis()
        metricas = r.hgetall(METRICAS_KEY)
        ventana = int(r.get(RATE_KEY) or 0)
        return {
            "nodo": NODO,
            "estado": "UP",
            "peticiones_nodo": int(metricas.get(NODO, 0)),
            "peticiones_ventana": ventana,
        }
    except Exception as err:                        # noqa: BLE001
        print(f"[{NODO}] Error en /status:", err)
        return JSONResponse(status_code=500, content={"nodo": NODO, "estado": "ERROR"})