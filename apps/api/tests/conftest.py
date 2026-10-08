"""Safe configuration for tests that do not open a database connection."""

import os

_ = os.environ.setdefault("APP_ENV", "test")
_ = os.environ.setdefault("APP_TIMEZONE", "Asia/Seoul")
_ = os.environ.setdefault(
    "DATABASE_URL_POOLED", "postgresql+asyncpg://template:template@127.0.0.1:55432/template_test"
)
_ = os.environ.setdefault(
    "DATABASE_URL_DIRECT", "postgresql+asyncpg://template:template@127.0.0.1:55432/template_test"
)
_ = os.environ.setdefault("SESSION_SECRET", "test-session-secret-that-is-at-least-32-characters")
_ = os.environ.setdefault("CSRF_SECRET", "test-csrf-secret-that-is-different-and-long")
