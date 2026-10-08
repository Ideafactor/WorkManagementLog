"""Idempotent initial administrator bootstrap command."""

import asyncio

from sqlalchemy import select

from app.auth.security import hash_password
from app.config import get_settings
from app.database.models import User, UserRole
from app.database.session import get_engine, get_session_factory


async def bootstrap() -> None:
    """Create the configured administrator only when it does not exist."""
    settings = get_settings()
    if (
        settings.bootstrap_admin_email is None
        or settings.bootstrap_admin_name is None
        or settings.bootstrap_admin_password is None
    ):
        print("bootstrap skipped: administrator settings are not configured")
        return
    async with get_session_factory()() as database:
        email = str(settings.bootstrap_admin_email).lower()
        existing = (
            await database.execute(select(User.id).where(User.email == email))
        ).scalar_one_or_none()
        if existing is not None:
            print("bootstrap unchanged: administrator already exists")
            return
        database.add(
            User(
                email=email,
                name=settings.bootstrap_admin_name,
                password_hash=hash_password(settings.bootstrap_admin_password.get_secret_value()),
                role=UserRole.ADMIN,
            )
        )
        await database.commit()
        print("bootstrap complete: administrator created")
    await get_engine().dispose()


if __name__ == "__main__":
    asyncio.run(bootstrap())
