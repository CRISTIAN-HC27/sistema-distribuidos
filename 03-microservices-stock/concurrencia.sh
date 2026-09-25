#!/usr/bin/env bash
# Prueba de concurrencia del taller 3: envia N compras en paralelo alternando
# entre las dos instancias del servicio de Stock y cuenta cuantas tienen exito.
#   bash concurrencia.sh [producto_id] [intentos] [paralelo]
set -euo pipefail

PRODUCTO="${1:-1}"
INTENTOS="${2:-40}"
PARALELO="${3:-8}"
PUERTO_A="${STOCK_PORT_A:-6001}"
PUERTO_B="${STOCK_PORT_B:-6002}"
INICIAL="${STOCK_INICIAL:-5}"

if ! curl -sf "http://localhost:$PUERTO_A/stock/$PRODUCTO" >/dev/null 2>&1; then
  echo "El servicio de stock no responde en el puerto $PUERTO_A. Levantalo con: docker compose up -d --build"
  exit 1
fi

docker compose exec -T redis redis-cli DEL "stock:$PRODUCTO" >/dev/null
curl -s "http://localhost:$PUERTO_A/stock/$PRODUCTO" >/dev/null

antes=$(curl -s "http://localhost:$PUERTO_A/stock/$PRODUCTO" | sed 's/.*"stock":\([0-9-]*\).*/\1/')
echo "== Concurrencia: $INTENTOS compras al producto $PRODUCTO alternando :$PUERTO_A / :$PUERTO_B =="
echo "Stock inicial: $antes (configurado: $INICIAL)"

codigos=$(mktemp)
trap 'rm -f "$codigos"' EXIT

export codigos
seq 1 "$INTENTOS" \
  | awk -v a="$PUERTO_A" -v b="$PUERTO_B" -v p="$PRODUCTO" \
      '{ print (NR % 2 == 0 ? a : b), p, NR }' \
  | xargs -P "$PARALELO" -n 3 bash -c '
        curl -s -o /dev/null -w "%{http_code}\n" -X POST "http://localhost:$1/stock/$2/comprar" >> "$codigos"
    ' _

ok=$(grep -c '^200$' "$codigos" || true)
sin_stock=$(grep -c '^409$' "$codigos" || true)
otros=$(grep -vc -e '^200$' -e '^409$' "$codigos" || true)
final=$(curl -s "http://localhost:$PUERTO_B/stock/$PRODUCTO" | sed 's/.*"stock":\([0-9-]*\).*/\1/')

echo "== Resumen =="
echo "Compras exitosas (200): $ok"
echo "Sin stock (409):        $sin_stock"
echo "Otros estados:          $otros"
echo "Stock final (leido desde la otra instancia): $final"
echo

if [ "$ok" -eq "$INICIAL" ] && [ "$final" -eq 0 ]; then
  echo "OK: exactamente $INICIAL compras exitosas, sin sobreventa."
else
  echo "FALLO: se esperaban $INICIAL compras exitosas y stock final 0, hubo $ok y $final."
  if [ "$ok" -gt "$INICIAL" ]; then
    echo "Sobreventa detectada: el estado no se esta compartiendo correctamente."
  fi
  exit 1
fi
