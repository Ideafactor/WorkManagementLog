FROM oven/bun:1.3.14-slim AS web-build
WORKDIR /build/apps/web
COPY apps/web/package.json apps/web/bun.lock ./
RUN bun install --frozen-lockfile
COPY apps/web/ ./
RUN bun run build

FROM python:3.13-slim-bookworm AS api-build
COPY --from=ghcr.io/astral-sh/uv:0.12.3 /uv /uvx /bin/
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv
WORKDIR /build/apps/api
COPY apps/api/pyproject.toml apps/api/uv.lock ./
RUN uv sync --locked --no-dev --no-install-project

FROM python:3.13-slim-bookworm AS runtime
ARG VCS_REF=unknown
LABEL org.opencontainers.image.title="Company Web Boilerplate" \
      org.opencontainers.image.revision="$VCS_REF"
ENV APP_ENV=production \
    APP_TIMEZONE=Asia/Seoul \
    FORWARDED_ALLOW_IPS=127.0.0.1 \
    PATH=/opt/venv/bin:$PATH \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_STATIC_DIR=/app/static
WORKDIR /app/api
COPY --from=api-build /opt/venv /opt/venv
COPY apps/api/app ./app
COPY apps/api/alembic ./alembic
COPY apps/api/alembic.ini ./alembic.ini
COPY --from=web-build /build/apps/web/dist /app/static
COPY --chmod=755 scripts/container-entrypoint.sh /usr/local/bin/appctl
RUN addgroup --system app && adduser --system --ingroup app app \
    && chown -R app:app /app
USER app
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2).read()"]
ENTRYPOINT ["appctl"]
CMD ["serve"]
