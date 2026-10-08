"""Validated environment configuration."""

from functools import lru_cache
from pathlib import Path
from typing import ClassVar, Literal, Self

from pydantic import EmailStr, Field, PostgresDsn, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Immutable application settings loaded from environment variables."""

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=(".env.local", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        frozen=True,
        hide_input_in_errors=True,
    )

    app_env: Literal["development", "test", "production"] = "development"
    app_timezone: Literal["Asia/Seoul"] = "Asia/Seoul"
    database_url_pooled: PostgresDsn
    database_url_direct: PostgresDsn
    session_secret: SecretStr = Field(min_length=32)
    csrf_secret: SecretStr = Field(min_length=32)
    static_dir: Path = Field(default=Path("/app/static"), validation_alias="APP_STATIC_DIR")
    forwarded_allow_ips: str = "127.0.0.1"
    bootstrap_admin_email: EmailStr | None = None
    bootstrap_admin_name: str | None = Field(default=None, min_length=1, max_length=100)
    bootstrap_admin_password: SecretStr | None = Field(default=None, min_length=12)

    @property
    def secure_cookies(self) -> bool:
        """Require HTTPS cookies outside local development and tests."""
        return self.app_env == "production"

    @model_validator(mode="after")
    def validate_boundaries(self) -> Self:
        """Reject weak or incomplete deployment configuration."""
        if self.session_secret == self.csrf_secret:
            msg = "SESSION_SECRET and CSRF_SECRET must differ"
            raise ValueError(msg)
        bootstrap_values = (
            self.bootstrap_admin_email,
            self.bootstrap_admin_name,
            self.bootstrap_admin_password,
        )
        if any(value is not None for value in bootstrap_values) and any(
            value is None for value in bootstrap_values
        ):
            msg = "bootstrap admin settings must be supplied together"
            raise ValueError(msg)
        if self.app_env == "production" and self.database_url_pooled == self.database_url_direct:
            msg = "production pooled and direct database URLs must differ"
            raise ValueError(msg)
        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the process-wide validated settings object."""
    return Settings()  # pyright: ignore[reportCallIssue]


if __name__ == "__main__":
    _ = get_settings()
    print("configuration valid")
