import json
import os
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from services.cache_reporte import get_or_calculated
from services.metricas import register
from services.rate_limiter import check
from redis_client import get_redis

PORT = int(os.getenv("PORT", "5003"))
NODO = f"nodo_{PORT}"


class Handler(BaseHTTPRequestHandler):
    # Silenciar el log por defecto de http.server
    def log_message(self, fmt, *args):
        pass

    def _json(self, status, data):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/api":
            self._api()
        elif path == "/status":
            self._status()
        else:
            self._json(404, {"error": "Not Found"})

    def _api(self):
        inicio = time.time()
        try:
            rl = check()                               # A
            if not rl["permitted"]:
                return self._json(429, {
                    "error": "Too Many Requests",
                    "nodo": NODO,
                    "peticiones_ventana": rl["n"],
                    "limite": rl["limited"],
                    "ventana_s": rl["window"],
                })

            register(NODO)                             # C

            res = get_or_calculated()                  # B
            res.update({
                "nodo": NODO,
                "latencia_ms": round((time.time() - inicio) * 1000, 2),
                "peticiones_ventana": rl["n"],
            })
            self._json(200, res)
        except Exception as err:                        # noqa: BLE001
            print(f"[{NODO}] Error en /api:", err)
            self._json(500, {"error": "Error interno", "nodo": NODO})

    def _status(self):
        try:
            r = get_redis()
            metricas = r.hgetall("metricas:nodos")
            ventana = int(r.get("ratelimit:global") or 0)
            self._json(200, {
                "nodo": NODO,
                "estado": "UP",
                "peticiones_nodo": int(metricas.get(NODO, 0)),
                "peticiones_ventana": ventana,
            })
        except Exception as err:                        # noqa: BLE001
            print(f"[{NODO}] Error en /status:", err)
            self._json(500, {"nodo": NODO, "estado": "ERROR"})


def crear_servidor():
    return ThreadingHTTPServer(("0.0.0.0", PORT), Handler)