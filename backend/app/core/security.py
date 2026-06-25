import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher
from pwdlib.hashers.bcrypt import BcryptHasher

from app.core.config import settings

# Unambiguous alphabet (no 0/O/1/I) for a human-transcribable recovery code.
_RECOVERY_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
_RECOVERY_LENGTH = 20  # ~100 bits of entropy

password_hash = PasswordHash(
    (
        Argon2Hasher(),
        BcryptHasher(),
    )
)


ALGORITHM = "HS256"


def create_access_token(
    subject: str | Any, expires_delta: timedelta, jti: str | None = None
) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode: dict[str, Any] = {"exp": expire, "sub": str(subject)}
    if jti is not None:
        to_encode["jti"] = jti
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(
    plain_password: str, hashed_password: str
) -> tuple[bool, str | None]:
    return password_hash.verify_and_update(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return password_hash.hash(password)


def generate_recovery_code() -> str:
    """A one-time recovery code, grouped for human transcription (FR-3)."""
    raw = "".join(secrets.choice(_RECOVERY_ALPHABET) for _ in range(_RECOVERY_LENGTH))
    return "-".join(raw[i : i + 5] for i in range(0, _RECOVERY_LENGTH, 5))


def hash_recovery_code(code: str) -> str:
    """Salted hash of a recovery code — plaintext is never persisted."""
    return password_hash.hash(code)


def verify_recovery_code(code: str, code_hash: str) -> bool:
    valid, _ = password_hash.verify_and_update(code, code_hash)
    return valid


def generate_url_token() -> str:
    """A high-entropy URL-safe token for email-verification / reset links."""
    return secrets.token_urlsafe(32)


def hash_url_token(token: str) -> str:
    """Deterministic sha256 of a URL token, so it can be looked up by hash.

    The token is already ~256 bits of randomness, so a fast hash is sufficient
    (no need for a slow password hash) and lets us query by ``token_hash``.
    """
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
