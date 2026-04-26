#!/bin/bash
set -e

case "${1:-web}" in
  web)
    echo "==> Running Alembic migrations..."
    alembic upgrade head
    echo "==> Starting Gunicorn (workers=${GUNICORN_WORKERS:-2}, port=${APP_PORT:-2000})..."
    exec gunicorn app.main:application \
      -k uvicorn.workers.UvicornWorker \
      -b "0.0.0.0:${APP_PORT:-2000}" \
      --workers "${GUNICORN_WORKERS:-2}" \
      --timeout 120 \
      --access-logfile - \
      --error-logfile -
    ;;
  *)
    exec "$@"
    ;;
esac
