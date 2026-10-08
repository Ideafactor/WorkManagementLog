# Project development instructions

This repository is a reusable internal web-service foundation.

Before changing behavior, read:

1. `docs/architecture.md`
2. `docs/api-contract.md`

Rules:

- Do not add product-specific domains to the core modules.
- Update `docs/api-contract.md` whenever an API contract changes.
- Use Alembic for schema changes; never create production tables at startup.
- Store no plaintext passwords, session tokens, CSRF tokens, or deployment secrets.
- Existing mutable resources use `version` and quoted `If-Match`.
- Write success, validation, permission, not-found and concurrency tests for each feature.
- Run lint, typecheck, test and build before completion.
- Keep `.env` files outside Git and Docker images.

