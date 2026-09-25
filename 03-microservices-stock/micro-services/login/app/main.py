import uvicorn # type: ignore
from fastapi import FastAPI # type: ignore

from config import NODO, PORT
from routers.auth_router import router

app = FastAPI(title="Login - TiendaNorte")
app.include_router(router)


def main():
    print(f"[{NODO}] Login UP, conectado a PostgreSQL")
    uvicorn.run(app, host="0.0.0.0", port=PORT)


if __name__ == "__main__":
    main()
