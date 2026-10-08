"""Minimal administrator account management routes."""

from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import Principal, parse_if_match, require_admin, require_csrf
from app.auth.router import user_view
from app.auth.schemas import UserCreateRequest, UserPatchRequest, UserView
from app.auth.security import hash_password
from app.database.models import User, UserRole
from app.database.session import get_database

router = APIRouter(prefix="/admin/users", tags=["admin"])


async def require_admin_csrf(
    principal: Annotated[Principal, Depends(require_csrf)],
) -> Principal:
    """Combine CSRF verification with administrator authorization."""
    if principal.user.must_change_password:
        raise HTTPException(status_code=403, detail="PASSWORD_CHANGE_REQUIRED")
    if principal.user.role is not UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="ADMIN_REQUIRED")
    return principal


@router.get("")
async def list_users(
    _principal: Annotated[Principal, Depends(require_admin)],
    database: Annotated[AsyncSession, Depends(get_database)],
) -> list[UserView]:
    """List accounts without credential fields."""
    users = (await database.execute(select(User).order_by(User.id))).scalars().all()
    return [user_view(user) for user in users]


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_user(
    body: UserCreateRequest,
    _principal: Annotated[Principal, Depends(require_admin_csrf)],
    database: Annotated[AsyncSession, Depends(get_database)],
) -> UserView:
    """Create an account with an immediately hashed initial password."""
    user = User(
        email=str(body.email).lower(),
        name=body.name.strip(),
        password_hash=hash_password(body.initial_password),
        role=body.role,
    )
    database.add(user)
    try:
        await database.commit()
    except IntegrityError as error:
        await database.rollback()
        raise HTTPException(status_code=409, detail="USER_CONFLICT") from error
    await database.refresh(user)
    return user_view(user)


@router.patch("/{user_id}")
async def patch_user(
    user_id: int,
    body: UserPatchRequest,
    _principal: Annotated[Principal, Depends(require_admin_csrf)],
    database: Annotated[AsyncSession, Depends(get_database)],
    if_match: Annotated[str | None, Header(alias="If-Match")] = None,
) -> UserView:
    """Change role and lifecycle state with optimistic concurrency."""
    expected_version = parse_if_match(if_match)
    user = (
        await database.execute(select(User).where(User.id == user_id).with_for_update())
    ).scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="USER_NOT_FOUND")
    if user.version != expected_version:
        raise HTTPException(status_code=409, detail="VERSION_CONFLICT")
    user.role = body.role
    user.status = body.status
    user.version += 1
    user.updated_at = datetime.now(UTC)
    await database.commit()
    return user_view(user)
