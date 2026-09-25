import uvicorn  # type: ignore
from fastapi import FastAPI  # type: ignore

import config  # type: ignore
from routers.stock_router import router
from services import stock_service  # type: ignore

app = FastAPI(title="Stock - TiendaNorte")
app.include_router(router)


def main():
    stock_service.inicializar()
    print(f"[{config.NODO}] Stock UP | estado={config.MODO} | redis={config.REDIS_URL}")
    uvicorn.run(app, host="0.0.0.0", port=config.PORT)


if __name__ == "__main__":
    main()
