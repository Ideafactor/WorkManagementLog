"""Authentication, CSRF, and authorization dependencies."""

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import Cookie, Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.security import digest_token
from app.config import get_settings
from app.database.models import LoginSession, User, UserRole, UserStatus
from app.database.session import get_database

SESSION_COOKIE = "app_session"
CSRF_COOKIE = "app_csrf"
MIN_QUOTED_VERSION_LENGTH = 3


@dataclass(frozen=True, slots=True)
class Principal:
    """Verified request identity and session."""

    user: User
    session: LoginSession


async def get_principal(
    database: Annotated[AsyncSession, Depends(get_database)],
    raw_token: Annotated[str | None, Cookie(alias=SESSION_COOKIE)] = None,
) -> Principal:
    """Resolve an active user from a hashed absolute-expiry session."""
    if raw_token is None:
        raise HTTPException(status_code=401, detail="SESSION_REQUIRED")
    settings = get_settings()
    token_hash = digest_token(raw_token, settings.session_secret.get_secret_value())
    row = (
        (
            await database.execute(
                select(LoginSession, User)
                .join(User, User.id == LoginSession.user_id)
                .where(LoginSession.session_token_hash == token_hash)
            )
        )
        .tuples()
        .one_or_none()
    )
    if row is None:
        raise HTTPException(status_code=401, detail="SESSION_REQUIRED")
    login_session, user = row
    if (
        login_session.revoked_at is not None
        or login_session.expires_at <= datetime.now(UTC)
        or user.status is not UserStatus.ACTIVE
    ):
        raise HTTPException(status_code=401, detail="SESSION_REQUIRED")
    return Principal(user=user, session=login_session)


async def require_ready_principal(
    principal: Annotated[Principal, Depends(get_principal)],
) -> Principal:
    """Block ordinary APIs until a forced password change is complete."""
    if principal.user.must_change_password:
        raise HTTPException(status_code=403, detail="PASSWORD_CHANGE_REQUIRED")
    return principal


async def require_csrf(
    principal: Annotated[Principal, Depends(get_principal)],
    header_token: Annotated[str | None, Header(alias="X-CSRF-Token")] = None,
    cookie_token: Annotated[str | None, Cookie(alias=CSRF_COOKIE)] = None,
) -> Principal:
    """Validate double-submit and server-side CSRF token state."""
    if header_token is None or cookie_token is None or header_token != cookie_token:
        raise HTTPException(status_code=403, detail="CSRF_FAILED")
    expected = digest_token(header_token, get_settings().csrf_secret.get_secret_value())
    if expected != principal.session.csrf_token_hash:
        raise HTTPException(status_code=403, detail="CSRF_FAILED")
    return principal


async def require_admin(
    principal: Annotated[Principal, Depends(require_ready_principal)],
) -> Principal:
    """Restrict an endpoint to administrators."""
    if principal.user.role is not UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="ADMIN_REQUIRED")
    return principal


def parse_if_match(raw_value: str | None) -> int:
    """Parse a quoted integer entity version."""
    if raw_value is None:
        raise HTTPException(status_code=400, detail="IF_MATCH_REQUIRED")
    normalized = raw_value.strip()
    if len(normalized) < MIN_QUOTED_VERSION_LENGTH or normalized[0] != '"' or normalized[-1] != '"':
        raise HTTPException(status_code=400, detail="IF_MATCH_INVALID")
    try:
        version = int(normalized[1:-1])
    except ValueError as error:
        raise HTTPException(status_code=400, detail="IF_MATCH_INVALID") from error
    if version < 1:
        raise HTTPException(status_code=400, detail="IF_MATCH_INVALID")
    return version


def session_uuid(principal: Principal) -> UUID:
    """Expose the typed session identifier for mutations."""
    return principal.session.id
