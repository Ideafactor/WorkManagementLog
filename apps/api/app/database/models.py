"""Minimal identity and session persistence models."""

from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Identity,
    Index,
    String,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.schema import SchemaItem

from app.database.base import Base


class UserRole(StrEnum):
    """Application authorization roles."""

    MEMBER = "MEMBER"
    ADMIN = "ADMIN"


class UserStatus(StrEnum):
    """Account lifecycle states."""

    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"


class User(Base):
    """Authenticated application user."""

    __tablename__: str = "app_user"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    password_hash: Mapped[str] = mapped_column(String(512))
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role"), server_default=text("'MEMBER'")
    )
    status: Mapped[UserStatus] = mapped_column(
        Enum(UserStatus, name="user_status"), server_default=text("'ACTIVE'")
    )
    must_change_password: Mapped[bool] = mapped_column(Boolean, server_default=text("false"))
    version: Mapped[int] = mapped_column(server_default=text("1"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )


class LoginSession(Base):
    """Hashed, revocable, absolute-expiry browser session."""

    __tablename__: str = "login_session"
    __table_args__: tuple[SchemaItem, ...] = (
        Index(
            "ix_login_session_active_user",
            "user_id",
            "expires_at",
            postgresql_where=text("revoked_at IS NULL"),
        ),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[int] = mapped_column(ForeignKey("app_user.id"), index=True)
    session_token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    csrf_token_hash: Mapped[str] = mapped_column(String(64))
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
