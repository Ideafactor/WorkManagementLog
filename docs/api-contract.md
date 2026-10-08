# API Contract

Base URL: `/api/v1`

Dates and timestamps are ISO 8601. Existing mutable resources carry an integer `version`; updates use
quoted `If-Match: "<version>"` and return `409 VERSION_CONFLICT` when stale.

## Error envelope

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "VALIDATION_ERROR",
    "field": null
  }
}
```

## System

- `GET /health` and `GET /api/v1/health`: process liveness
- `GET /ready` and `GET /api/v1/ready`: runtime database readiness

## Authentication

- `POST /auth/login`
  - body: `{ "email": "admin@example.com", "password": "..." }`
  - creates `app_session` HttpOnly cookie and `app_csrf` cookie
- `GET /auth/me`
  - returns the current user and absolute session expiry
- `POST /auth/logout`
  - requires `X-CSRF-Token`
- `POST /auth/password`
  - body: `{ "currentPassword": "...", "newPassword": "..." }`
  - requires `X-CSRF-Token`; new passwords are at least 12 characters

Authentication failures return one `401 LOGIN_FAILED` response regardless of whether the email or
password was wrong.

## Administration

All routes require an active `ADMIN` session.

- `GET /admin/users`: list accounts without credential fields
- `POST /admin/users`: create an account with an initial password that is immediately hashed
- `PATCH /admin/users/{id}`: replace role and lifecycle status; requires `If-Match`

## Adding a domain API

1. Create an isolated package under `apps/api/app/<feature>`.
2. Define strict Pydantic request and response models with `extra="forbid"`.
3. Put authorization and transaction boundaries in the service layer.
4. Add an Alembic migration rather than creating tables at application startup.
5. Cover success, validation, permission, not-found and concurrency paths.
6. Register the router in `app/main.py` under `/api/v1`.

