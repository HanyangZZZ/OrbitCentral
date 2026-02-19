#!/bin/sh
set -e

# ── Wait for PostgreSQL to be ready ──────────────────────────────────────────
echo "Waiting for PostgreSQL..."
while ! python -c "
import psycopg2
import os
dsn = os.environ.get('DATABASE_URL')
if dsn:
    psycopg2.connect(dsn, connect_timeout=3)
else:
    psycopg2.connect(
        host=os.environ.get('PG_HOST', '127.0.0.1'),
        port=int(os.environ.get('PG_PORT', '5432')),
        user=os.environ.get('PG_USER', 'fblc'),
        password=os.environ.get('PG_PASSWORD', 'fblc_password'),
        dbname=os.environ.get('PG_DATABASE', 'fblc'),
        connect_timeout=3,
    )
" 2>/dev/null; do
    echo "  PostgreSQL not ready — retrying in 2s..."
    sleep 2
done
echo "PostgreSQL is ready!"

# ── Run migrations ────────────────────────────────────────────────────────────
echo "Running database migrations..."
python manage.py migrate --noinput

# ── Seed categories (idempotent) ──────────────────────────────────────────────
echo "Seeding categories..."
python manage.py seed_categories

# ── Collect static files ──────────────────────────────────────────────────────
echo "Collecting static files..."
python manage.py collectstatic --noinput

# ── Start Gunicorn (default) or custom command ────────────────────────────────
# If a custom command is passed (e.g., celery worker), run that instead.
# This allows the same image to run as Django, Celery worker, or Flower.
if [ "$#" -gt 0 ]; then
    echo "Starting custom command: $@"
    exec "$@"
else
    echo "Starting Gunicorn..."
    exec gunicorn server.wsgi:application \
        --bind 0.0.0.0:8000 \
        --workers "${GUNICORN_WORKERS:-3}" \
        --threads "${GUNICORN_THREADS:-2}" \
        --timeout 120 \
        --graceful-timeout 30 \
        --max-requests 1000 \
        --max-requests-jitter 50 \
        --access-logfile - \
        --error-logfile -
fi
