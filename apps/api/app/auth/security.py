"""Password and opaque-token primitives."""

import hashlib
import hmac
import secrets

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

_PASSWORD_HASHER = PasswordHasher()


def hash_password(password: str) -> str:
    """Hash a password with Argon2id."""
    return _PASSWORD_HASHER.hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    """Verify a password without leaking the failure reason."""
    try:
        return _PASSWORD_HASHER.verify(password_hash, password)
    except (VerificationError, InvalidHashError):
        return False


def new_token() -> str:
    """Return an unpredictable browser credential."""
    return secrets.token_urlsafe(32)


def digest_token(token: str, secret: str) -> str:
    """Create a keyed token digest suitable for persistence."""
    return hmac.new(secret.encode(), token.encode(), hashlib.sha256).hexdigest()
