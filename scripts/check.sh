#!/bin/sh
set -eu

(cd apps/api && uv run ruff check app tests && uv run ruff format --check app tests)
(cd apps/api && uv run basedpyright && uv run pytest)
(cd apps/web && bun run lint && bun run typecheck && bun run test && bun run build)

