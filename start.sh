#!/bin/bash
set -e

echo "🚀 Iniciando API Flask e Worker RQ..."

# Inicia o Gunicorn em background
gunicorn -b 0.0.0.0:8021 run:app &

# Inicia o worker do RQ
if [ -z "$REDIS_URL" ]; then
  echo "⚠️  Variável REDIS_URL não definida. Usando valor padrão redis://localhost:6379/0"
  REDIS_URL="redis://localhost:6379/0"
fi

rq worker -u "$REDIS_URL" processar_fila