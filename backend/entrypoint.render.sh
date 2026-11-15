#!/bin/sh
set -eu

if [ -z "${DATABASE_URL:-}" ]; then
  echo "DATABASE_URL is required. Add the pooled Neon connection string in Render."
  exit 1
fi

python manage.py migrate --noinput
python manage.py import_pdd /app/data/pdd_official_ru.jsonl

exec gunicorn config.wsgi:application \
  --bind "0.0.0.0:${PORT:-10000}" \
  --workers "${WEB_CONCURRENCY:-2}" \
  --timeout 60 \
  --access-logfile - \
  --error-logfile -
