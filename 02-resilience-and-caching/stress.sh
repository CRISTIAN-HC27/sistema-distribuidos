#!/usr/bin/env bash
set -euo pipefail
URL="${1:-http://localhost:8000/api}"
TOTAL="${2:-60}"

ok=0; cnt429=0; acc=0; msgs=()
echo "== Stress a $URL (${TOTAL} peticiones) =="
for i in $(seq 1 "$TOTAL"); do
  t0=$(date +%s%N)
  code=$(curl -s -o /tmp/resp_taller2.json -w '%{http_code}' "$URL")
  ms=$(( ($(date +%s%N) - t0) / 1000000 ))
  acc=$((acc + ms))
  origen=$(grep -o '"origen":"[a-z]*"' /tmp/resp_taller2.json | cut -d'"' -f4 || echo "-")
  if [ "$code" = "429" ]; then cnt429=$((cnt429 + 1)); else ok=$((ok + 1)); fi
  msgs+=("$(printf '%3d  HTTP %s  %5d ms  %s' "$i" "$code" "$ms" "$origen")")
done
printf '%s\n' "${msgs[@]}"
echo "== Resumen =="
echo "OK: $ok  |  429: $cnt429  |  latencia promedio: $((acc / TOTAL)) ms"