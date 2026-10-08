# Architecture

## Runtime

The production image serves the React SPA and FastAPI API from one origin.

```text
Browser
  ├─ /api/v1/** → FastAPI
  └─ other paths → built React SPA

FastAPI → PostgreSQL
```

- Python 3.13, FastAPI, Pydantic v2
- SQLAlchemy 2 async with asyncpg
- React 19, TypeScript, Vite
- PostgreSQL pooled URL for runtime and direct URL for migrations
- Asia/Seoul application time zone

## Modules

```text
apps/api/app/
  auth/       session, password, CSRF and authorization boundaries
  database/   engine and identity models
  admin.py    example role-protected account management

apps/web/src/
  app/        router composition
  components/ reusable shell
  features/   feature-owned UI and state
  lib/        API transport and runtime validation
  pages/      route entry points
```

Domain features must own their router, service, schema, model, tests and migration. Avoid adding
unrelated feature logic to `main.py`, `admin.py`, or the shared web API client.

## Security boundaries

- Passwords are Argon2id hashes and are never returned or logged.
- Browser sessions use an opaque HttpOnly cookie and seven-day absolute expiry.
- Session and CSRF token digests are persisted instead of raw credentials.
- Mutations require a CSRF header matching the readable CSRF cookie and stored digest.
- Disabled accounts and revoked or expired sessions are rejected server-side.
- API errors do not distinguish an unknown login from a wrong password.
- Secrets are supplied only through runtime environment variables.

## Deployment

The Docker build compiles the SPA with Bun and installs the API with uv. The final Python image runs
as a non-root user, listens on `0.0.0.0:${PORT:-8000}`, and writes logs to stdout. `/health` is a
database-independent liveness check; `/ready` verifies the runtime database path.

The sample deploy workflow uses GitHub OIDC, ECR and EC2 SSM. It contains no account-specific ARN or
repository name and is manual until repository variables and the target deployment script exist.

