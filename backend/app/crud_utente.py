"""Persistence for the mynance Utente domain (FR-1 registration, FR-3 recovery).

Kept separate from the template's ``crud.py`` (email-based ``User``).
"""

from sqlmodel import Session, select

from app.core.security import (
    generate_recovery_code,
    get_password_hash,
    hash_recovery_code,
    verify_password,
    verify_recovery_code,
)
from app.models import Utente, get_datetime_utc

# Argon2 hash of a random value, used for constant-time password checks when the
# username does not exist (mirrors crud.authenticate; avoids existence leaks).
DUMMY_PASSWORD_HASH = (
    "$argon2id$v=19$m=65536,t=3,p=4$MjQyZWE1MzBjYjJlZTI0Yw$"
    "YTU4NGM5ZTZmYjE2NzZlZjY0ZWY3ZGRkY2U2OWFjNjk"
)

# Argon2 hash of a random value, used for constant-time recovery checks when the
# username does not exist (avoids revealing account existence via timing).
DUMMY_RECOVERY_HASH = (
    "$argon2id$v=19$m=65536,t=3,p=4$MjQyZWE1MzBjYjJlZTI0Yw$"
    "YTU4NGM5ZTZmYjE2NzZlZjY0ZWY3ZGRkY2U2OWFjNjk"
)


def get_utente_by_username(*, session: Session, username: str) -> Utente | None:
    statement = select(Utente).where(Utente.username == username)
    return session.exec(statement).first()


def authenticate(*, session: Session, username: str, password: str) -> Utente | None:
    """Return the Utente iff username+password match; constant-time on miss."""
    utente = get_utente_by_username(session=session, username=username)
    if utente is None or utente.deleted_at is not None:
        verify_password(password, DUMMY_PASSWORD_HASH)
        return None
    verified, updated_hash = verify_password(password, utente.password_hash)
    if not verified:
        return None
    if updated_hash:
        utente.password_hash = updated_hash
        session.add(utente)
        session.commit()
        session.refresh(utente)
    return utente


def create_utente(
    *, session: Session, username: str, password: str
) -> tuple[Utente, str]:
    """Create an Utente; return it with the one-time recovery code plaintext.

    The plaintext is returned exactly once (for the registration response) and
    never persisted — only its salted hash is stored.
    """
    recovery_code = generate_recovery_code()
    utente = Utente(
        username=username,
        password_hash=get_password_hash(password),
        recovery_code_hash=hash_recovery_code(recovery_code),
    )
    session.add(utente)
    session.commit()
    session.refresh(utente)
    return utente, recovery_code


def recover_utente(
    *, session: Session, username: str, recovery_code: str, new_password: str
) -> Utente | None:
    """Set a new password if the username + recovery code match.

    Returns ``None`` (without revealing why) on any mismatch.
    """
    utente = get_utente_by_username(session=session, username=username)
    if utente is None or utente.deleted_at is not None:
        # Constant-time work even when the account does not exist.
        verify_recovery_code(recovery_code, DUMMY_RECOVERY_HASH)
        return None
    if not verify_recovery_code(recovery_code, utente.recovery_code_hash):
        return None
    utente.password_hash = get_password_hash(new_password)
    utente.updated_at = get_datetime_utc()
    session.add(utente)
    session.commit()
    session.refresh(utente)
    return utente
