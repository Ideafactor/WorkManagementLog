"""Credential primitive tests."""

from app.auth.security import digest_token, hash_password, verify_password


def test_password_hash_does_not_store_plaintext() -> None:
    """Passwords round-trip only through Argon2 verification."""
    password_hash = hash_password("a-long-local-test-password")

    assert "a-long-local-test-password" not in password_hash
    assert verify_password(password_hash, "a-long-local-test-password") is True
    assert verify_password(password_hash, "wrong-password") is False


def test_token_digest_is_keyed() -> None:
    """The same opaque token has distinct digests under different trust roots."""
    assert digest_token("token", "a" * 32) != digest_token("token", "b" * 32)
