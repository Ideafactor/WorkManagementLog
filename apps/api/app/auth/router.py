"""Session authentication HTTP routes."""

from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import (
    CSRF_COOKIE,
    SESSION_COOKIE,
    Principal,
    get_principal,
    require_csrf,
)
from app.auth.schemas import LoginRequest, PasswordChangeRequest, SessionView, UserView
from app.auth.security import digest_token, hash_password, new_token, verify_password
from app.config import get_settings
from app.database.models import LoginSession, User, UserStatus
from app.database.session import get_database

router = APIRouter(prefix="/auth", tags=["auth"])
SESSION_DURATION = timedelta(days=7)


def user_view(user: User) -> UserView:
    """Map an ORM user without exposing credentials."""
    return UserView(
        id=user.id,
        email=user.email,
        name=user.name,
        role=user.role,
        status=user.status,
        mustChangePassword=user.must_change_password,
        version=user.version,
    )


@router.post("/login")
async def login(
    body: LoginRequest,
    response: Response,
    database: Annotated[AsyncSession, Depends(get_database)],
) -> SessionView:
    """Create a seven-day absolute browser session."""
    user = (
        await database.execute(select(User).where(User.email == str(body.email).lower()))
    ).scalar_one_or_none()
    if (
        user is None
        or user.status is not UserStatus.ACTIVE
        or not verify_password(user.password_hash, body.password)
    ):
        raise HTTPException(status_code=401, detail="LOGIN_FAILED")

    settings = get_settings()
    raw_session = new_token()
    raw_csrf = new_token()
    issued_at = datetime.now(UTC)
    expires_at = issued_at + SESSION_DURATION
    database.add(
        LoginSession(
            user_id=user.id,
            session_token_hash=digest_token(
                raw_session, settings.session_secret.get_secret_value()
            ),
            csrf_token_hash=digest_token(raw_csrf, settings.csrf_secret.get_secret_value()),
            issued_at=issued_at,
            expires_at=expires_at,
        )
    )
    await database.commit()
    max_age = int(SESSION_DURATION.total_seconds())
    response.set_cookie(
        SESSION_COOKIE,
        raw_session,
        httponly=True,
        secure=settings.secure_cookies,
        samesite="lax",
        max_age=max_age,
        path="/",
    )
    response.set_cookie(
        CSRF_COOKIE,
        raw_csrf,
        httponly=False,
        secure=settings.secure_cookies,
        samesite="lax",
        max_age=max_age,
        path="/",
    )
    return SessionView(user=user_view(user), expiresAt=expires_at, csrfToken=raw_csrf)


@router.get("/me")
async def me(principal: Annotated[Principal, Depends(get_principal)]) -> SessionView:
    """Return the current session without exposing its tokens."""
    return SessionView(
        user=user_view(principal.user),
        expiresAt=principal.session.expires_at,
    )


@router.post("/logout", status_code=204)
async def logout(
    response: Response,
    principal: Annotated[Principal, Depends(require_csrf)],
    database: Annotated[AsyncSession, Depends(get_database)],
) -> None:
    """Revoke the current session and clear both cookies."""
    principal.session.revoked_at = datetime.now(UTC)
    await database.commit()
    response.delete_cookie(SESSION_COOKIE, path="/")
    response.delete_cookie(CSRF_COOKIE, path="/")


@router.post("/password")
async def change_password(
    body: PasswordChangeRequest,
    principal: Annotated[Principal, Depends(require_csrf)],
    database: Annotated[AsyncSession, Depends(get_database)],
) -> UserView:
    """Replace a password and revoke every other browser session."""
    user = (
        await database.execute(select(User).where(User.id == principal.user.id).with_for_update())
    ).scalar_one()
    if not verify_password(user.password_hash, body.current_password):
        raise HTTPException(status_code=400, detail="INVALID_CURRENT_PASSWORD")
    if verify_password(user.password_hash, body.new_password):
        raise HTTPException(status_code=400, detail="PASSWORD_REUSE")
    user.password_hash = hash_password(body.new_password)
    user.must_change_password = False
    user.version += 1
    user.updated_at = datetime.now(UTC)
    _ = await database.execute(
        update(LoginSession)
        .where(
            LoginSession.user_id == user.id,
            LoginSession.id != principal.session.id,
            LoginSession.revoked_at.is_(None),
        )
        .values(revoked_at=datetime.now(UTC))
    )
    await database.commit()
    return user_view(user)
