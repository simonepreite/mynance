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


def get_utente_by_email(*, session: Session, email: str) -> Utente | None:
    statement = select(Utente).where(Utente.email == email)
    return session.exec(statement).first()


def get_utente_by_identifier(*, session: Session, identifier: str) -> Utente | None:
    """Resolve an Utente by username, falling back to email."""
    utente = get_utente_by_username(session=session, username=identifier)
    if utente is None:
        utente = get_utente_by_email(session=session, email=identifier)
    return utente


def authenticate(*, session: Session, username: str, password: str) -> Utente | None:
    """Return the Utente iff identifier+password match; constant-time on miss.

    ``username`` accepts a username *or* an email.
    """
    utente = get_utente_by_identifier(session=session, identifier=username)
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
    *, session: Session, username: str, password: str, email: str
) -> tuple[Utente, str]:
    """Create an unverified Utente; return it with the one-time recovery code.

    The recovery-code plaintext is returned exactly once (for the registration
    response) and never persisted — only its salted hash is stored. The account
    starts ``email_verified=False`` (verification gates login).
    """
    recovery_code = generate_recovery_code()
    utente = Utente(
        username=username,
        email=email,
        email_verified=False,
        password_hash=get_password_hash(password),
        recovery_code_hash=hash_recovery_code(recovery_code),
    )
    session.add(utente)
    session.commit()
    session.refresh(utente)
    return utente, recovery_code


def set_password(*, session: Session, utente: Utente, new_password: str) -> None:
    """Replace the password hash (used by the email-based reset flow)."""
    utente.password_hash = get_password_hash(new_password)
    utente.updated_at = get_datetime_utc()
    session.add(utente)
    session.commit()


def mark_email_verified(*, session: Session, utente: Utente) -> None:
    utente.email_verified = True
    utente.updated_at = get_datetime_utc()
    session.add(utente)
    session.commit()


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
