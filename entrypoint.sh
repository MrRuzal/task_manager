#!/bin/sh
set -e

alembic upgrade head || echo "Alembic migration failed or not configured, skipping"
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload