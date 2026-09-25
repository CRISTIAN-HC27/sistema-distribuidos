from fastapi import APIRouter  # type: ignore
from fastapi.responses import JSONResponse  # type: ignore

import config  # type: ignore
from services import stock_service  # type: ignore

router = APIRouter()


@router.get("/stock/{producto_id}")
def ver_stock(producto_id: str):
    stock = stock_service.consultar(producto_id)

    if stock is None:
        return JSONResponse(
            status_code=404,
            content={"error": f"el producto {producto_id} no existe", "nodo": config.NODO},
        )

    return JSONResponse(
        status_code=200,
        content={"producto_id": producto_id, "stock": stock, "nodo": config.NODO},
    )


@router.post("/stock/{producto_id}/comprar")
def comprar(producto_id: str):
    estado, restante = stock_service.comprar(producto_id)

    if estado == stock_service.VENDIDO:
        return JSONResponse(
            status_code=200,
            content={
                "ok": True,
                "producto_id": producto_id,
                "stock_restante": restante,
                "nodo": config.NODO,
            },
        )

    if estado == stock_service.INEXISTENTE:
        status_code, error = 404, f"el producto {producto_id} no existe"
    else:
        status_code, error = 409, "sin stock"
    return JSONResponse(
        status_code=status_code,
        content={
            "ok": False,
            "error": error,
            "producto_id": producto_id,
            "stock": restante,
            "nodo": config.NODO,
        },
    )
