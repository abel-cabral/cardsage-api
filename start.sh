#!/bin/bash
set -e

exec gunicorn \
  --bind "0.0.0.0:${PORT:-8021}" \
  --workers "${GUNICORN_WORKERS:-4}" \
  --timeout "${GUNICORN_TIMEOUT:-120}" \
  run:app
