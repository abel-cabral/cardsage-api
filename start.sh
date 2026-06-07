#!/bin/bash
set -e

cleanup() {
  trap - TERM INT
  kill -TERM "$WORKER_PID" "$GUNICORN_PID" 2>/dev/null
  wait
}
trap cleanup TERM INT

# Worker dedicado: consome a fila de processamento de itens um por vez
python3 queue_worker.py &
WORKER_PID=$!

gunicorn \
  --bind "0.0.0.0:${PORT:-8021}" \
  --workers "${GUNICORN_WORKERS:-4}" \
  --timeout "${GUNICORN_TIMEOUT:-120}" \
  run:app &
GUNICORN_PID=$!

# Se qualquer um dos dois cair, encerra o outro — o restart policy do
# container sobe os dois de novo. (`wait -n` não existe no bash 3.2 do macOS,
# por isso o polling abaixo, compatível com qualquer versão do bash)
while kill -0 "$WORKER_PID" 2>/dev/null && kill -0 "$GUNICORN_PID" 2>/dev/null; do
  sleep 2
done
cleanup
