#!/bin/bash
set -e

echo "Running database migrations..."
alembic upgrade head

echo "Starting Uvicorn server..."
# Use WEB_CONCURRENCY if set by platform (Render), otherwise default to 1
# Free tiers typically set WEB_CONCURRENCY=1 due to resource limits
WORKERS="${WEB_CONCURRENCY:-1}"
echo "Using $WORKERS worker(s) on port ${PORT:-8000}"
exec uvicorn src.main:app --host 0.0.0.0 --port "${PORT:-8000}" --workers "$WORKERS"
