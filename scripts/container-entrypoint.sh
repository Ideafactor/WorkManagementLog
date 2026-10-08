#!/bin/sh
set -eu

python -m app.config

serve() {
  exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port "${PORT:-8000}" \
    --proxy-headers \
    --forwarded-allow-ips "$FORWARDED_ALLOW_IPS" \
    --log-config app/logging.json
}

case "${1:-serve}" in
  serve)
    serve
    ;;
  migrate)
    exec alembic upgrade head
    ;;
  bootstrap)
    exec python -m app.bootstrap
    ;;
  release)
    alembic upgrade head
    alembic current --check-heads
    exec python -m app.bootstrap
    ;;
  release-and-serve)
    alembic upgrade head
    alembic current --check-heads
    python -m app.bootstrap
    serve
    ;;
  *)
    echo "USAGE_ERROR: expected serve|migrate|bootstrap|release|release-and-serve" >&2
    exit 64
    ;;
esac

