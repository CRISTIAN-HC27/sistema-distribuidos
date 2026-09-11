import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

import uvicorn  # noqa: E402
from fastapi import FastAPI  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402

from routers.products_routers import router  # noqa: E402
from config import NODO, PORT  # noqa: E402

app = FastAPI(title="Backend Python — Resiliencia y Caché")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(router)


def main():
    print(f"[{NODO}] Backend UP, conectado a Redis y SQLite")
    print(f"[{NODO}] Escuchando en :{PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)


if __name__ == "__main__":
    main()