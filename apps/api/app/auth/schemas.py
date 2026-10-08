"""Authentication and user HTTP contracts."""

from datetime import datetime
from typing import Annotated, ClassVar

from pydantic import BaseModel, ConfigDict, EmailStr, Field, StringConstraints

from app.database.models import UserRole, UserStatus

Password = Annotated[str, StringConstraints(min_length=12, max_length=1024)]


class ApiModel(BaseModel):
    """Strict camel-case response and request base model."""

    model_config: ClassVar[ConfigDict] = ConfigDict(
        frozen=True,
        populate_by_name=True,
        extra="forbid",
    )


class LoginRequest(ApiModel):
    """Password login input."""

    email: EmailStr
    password: str = Field(min_length=1, max_length=1024)


class UserView(ApiModel):
    """Public user representation."""

    id: int
    email: EmailStr
    name: str
    role: UserRole
    status: UserStatus
    must_change_password: bool = Field(alias="mustChangePassword")
    version: int


class SessionView(ApiModel):
    """Authenticated session response."""

    user: UserView
    expires_at: datetime = Field(alias="expiresAt")
    csrf_token: str | None = Field(default=None, alias="csrfToken")


class PasswordChangeRequest(ApiModel):
    """Current and replacement password input."""

    current_password: str = Field(alias="currentPassword", min_length=1, max_length=1024)
    new_password: Password = Field(alias="newPassword")


class UserCreateRequest(ApiModel):
    """Administrator-created account input."""

    email: EmailStr
    name: str = Field(min_length=1, max_length=100)
    initial_password: Password = Field(alias="initialPassword")
    role: UserRole = UserRole.MEMBER


class UserPatchRequest(ApiModel):
    """Administrator-controlled account lifecycle fields."""

    role: UserRole
    status: UserStatus
