#!/bin/ash

set -e

# Checks that Postgres is available before starting.
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_SERVER" -U "$POSTGRES_USER" postgres -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - executing command"


source /app_dir/venv/bin/activate

python /app_dir/bootstrap.py

python /app_dir/venv/bin/gunicorn -b :8000 app.main:app --log-level INFO --enable-stdio-inheritance --workers 1 -k uvicorn.workers.UvicornWorker -t 600