import redis  # type: ignore

import config

rds = redis.Redis.from_url(config.REDIS_URL, decode_responses=True)

SCRIPT_COMPRAR = """
local actual = redis.call('GET', KEYS[1])
if not actual then
    return {'inexistente', '0'}
end
if tonumber(actual) <= 0 then
    return {'sin_stock', '0'}
end
return {'vendido', tostring(redis.call('DECR', KEYS[1]))}
"""

comprar_atomico = rds.register_script(SCRIPT_COMPRAR)

INEXISTENTE = "inexistente"
SIN_STOCK = "sin_stock"
VENDIDO = "vendido"

stock_local: dict[str, int] = {}


def _clave(producto_id: str) -> str:
    return f"stock:{producto_id}"


def _sembrar_redis(producto_id: str) -> int:
    creado = rds.set(_clave(producto_id), config.STOCK_INICIAL, nx=True)
    if creado:
        print(f"[{config.NODO}] producto {producto_id} inicializado con {config.STOCK_INICIAL} unidades")
    return int(rds.get(_clave(producto_id)))


def _consultar_redis(producto_id: str) -> int | None:
    if rds.get(_clave(producto_id)) is None and not config.STOCK_AUTOSEED:
        return None
    return _sembrar_redis(producto_id)


def _comprar_redis(producto_id: str) -> tuple[str, int]:
    _sembrar_redis(producto_id)
    estado, restante = comprar_atomico(keys=[_clave(producto_id)])
    return estado, int(restante)


def _sembrar_memoria(producto_id: str) -> int:
    stock_local.setdefault(producto_id, config.STOCK_INICIAL)
    return stock_local[producto_id]


def _consultar_memoria(producto_id: str) -> int | None:
    return stock_local.get(producto_id)


def _comprar_memoria(producto_id: str) -> tuple[str, int]:
    _sembrar_memoria(producto_id)
    if stock_local[producto_id] > 0:
        stock_local[producto_id] -= 1
        return VENDIDO, stock_local[producto_id]
    return SIN_STOCK, stock_local[producto_id]


def inicializar() -> None:
    for producto_id in config.STOCK_PRODUCTOS:
        _sembrar_memoria(producto_id) if config.ES_MEMORIA else _sembrar_redis(producto_id)


consultar = _consultar_memoria if config.ES_MEMORIA else _consultar_redis
comprar = _comprar_memoria if config.ES_MEMORIA else _comprar_redis
