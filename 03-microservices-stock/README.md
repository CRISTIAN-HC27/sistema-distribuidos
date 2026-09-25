# Taller 3 - Microservicios y Estado Compartido con Redis

TiendaNorte: microservicios independientes (Registro, Login) y un servicio de Stock
con **dos instancias** que comparten el estado en Redis mediante una operacion atomica.

## Arquitectura

```
cliente
  |-- POST /registro        -> registro  :6003 ─┐
  |                                           ├─> PostgreSQL :5435 (tabla usuarios)
  |-- POST /login           -> login     :6004 ─┘
  |
  |-- GET  /stock/{id}        ┐
  |                           ├─> redis :6379
  |-- POST /stock/{id}/comprar┘   stock-a :6001
                                stock-b :6002
```

`registro` y `login` son servicios de una sola instancia con estado propio (PostgreSQL).
`stock-a` y `stock-b` son el **mismo** microservicio en dos procesos: ninguna guarda stock
en su memoria, las dos leen y escriben en la misma clave de Redis (`stock:{id}`).

## Puesta en marcha

```bash
docker compose up -d --build
docker compose ps
```

| Servicio    | Host                   | Endpoint                       |
|-------------|------------------------|--------------------------------|
| Registro    | http://localhost:6003  | `POST /registro`               |
| Login       | http://localhost:6004  | `POST /login`                  |
| Stock A     | http://localhost:6001  | `GET /stock/{id}` · `POST /stock/{id}/comprar` |
| Stock B     | http://localhost:6002  | `GET /stock/{id}` · `POST /stock/{id}/comprar` |

Docs interactivas: `http://localhost:6001/docs`, `http://localhost:6002/docs`,
`http://localhost:6003/docs`, `http://localhost:6004/docs`.

## Probar a mano

```bash
# Registro y Login
curl -i -X POST http://localhost:6003/registro \
  -H 'Content-Type: application/json' \
  -d '{"email":"ana@tiendanorte.com","contrasena":"clave12345"}'

curl -i -X POST http://localhost:6004/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"ana@tiendanorte.com","contrasena":"clave12345"}'

# Stock: consultar y comprar, alternando entre las dos instancias
curl -s http://localhost:6001/stock/1
curl -s -X POST http://localhost:6002/stock/1/comprar
curl -s http://localhost:6001/stock/1
```

`comprar` responde `200` si descontó, `409` si no queda stock y `404` si el producto
no existe. El cuerpo trae `nodo` para ver qué instancia atendió la petición.

## Prueba de concurrencia

```bash
bash concurrencia.sh                 # producto 1, 40 intentos, 8 en paralelo
bash concurrencia.sh 7 100 16       # producto 7, 100 intentos, 16 en paralelo
```

Reinicia el stock del producto, lanza las compras en paralelo alternando entre
`:6001` y `:6002`, y verifica que las compras exitosas sean exactamente las del stock
inicial. Con Redis el resultado es siempre `5` de `5` y el script termina en `OK`.

### El "antes": el Incidente 1

Con el stock guardado en la memoria de cada instancia, cada una vende su propio stock
y el resultado es el del Incidente 1: el doble de ventas sobre un producto agotado.

```bash
MODO_ESTADO=memoria docker compose up -d
bash concurrencia.sh
# Compras exitosas (200): 10   <-- sobreventa, el script marca FALLO

docker compose up -d              # volver al estado compartido
```

## Configuracion (.env)

| Variable            | Default        | Para que sirve                                            |
|---------------------|----------------|-----------------------------------------------------------|
| `MODO_ESTADO`       | `redis`        | `redis` = estado compartido, `memoria` = estado por instancia |
| `STOCK_INICIAL`     | `5`            | Unidades con las que se siembra cada producto             |
| `STOCK_PRODUCTOS`   | `1,2,3`        | Productos que se siembran al arrancar                     |
| `STOCK_AUTOSEED`    | `1`            | `1` = un producto desconocido se inicializa solo, `0` = 404 |

## Auditar el estado compartido

```bash
docker compose exec redis redis-cli KEYS 'stock:*'   # claves de stock
docker compose exec redis redis-cli GET stock:1      # unidades restantes
docker compose logs -f stock-a stock-b               # quien atendio cada compra
```

El `comprar` es un script de Lua ejecutado por Redis (`EVALSHA`): Redis procesa los
comandos de a uno, asi que el `DECR` no puede quedar a medio hacer entre dos peticiones
concurrentes. Por eso el stock nunca baja de cero ni se venden mas unidades de las que hay.

## Detener

```bash
docker compose down      # conserva data/ (PostgreSQL)
docker compose down -v   # ademas borra volumenes y redes
```
