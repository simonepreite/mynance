"""Single-use, hashed, expiring tokens for email verification + password reset.

Only the sha256 hash of each token is stored; the plaintext lives only in the
emailed link. Tokens are single-use (``used_at``) and expiring (``expires_at``).
"""

import uuid
from datetime import timedelta

from sqlmodel import Session, col, select

from app.core.security import generate_url_token, hash_url_token
from app.models import Utente, UtenteToken, get_datetime_utc


def issue(
    *, session: Session, utente_id: uuid.UUID, purpose: str, expires_hours: int
) -> str:
    """Mint a token for (utente, purpose); return the plaintext (emailed once).

    Any prior unused token of the same (utente, purpose) is invalidated, so a
    resend disables the previous links.
    """
    now = get_datetime_utc()
    outstanding = session.exec(
        select(UtenteToken).where(
            UtenteToken.utente_id == utente_id,
            UtenteToken.purpose == purpose,
            col(UtenteToken.used_at).is_(None),
        )
    ).all()
    for tok in outstanding:
        tok.used_at = now
        session.add(tok)

    token = generate_url_token()
    row = UtenteToken(
        utente_id=utente_id,
        token_hash=hash_url_token(token),
        purpose=purpose,
        expires_at=now + timedelta(hours=expires_hours),
    )
    session.add(row)
    session.commit()
    return token


def consume(*, session: Session, token: str, purpose: str) -> Utente | None:
    """Validate and single-use-consume a token; return its Utente, else None."""
    now = get_datetime_utc()
    row = session.exec(
        select(UtenteToken).where(
            UtenteToken.token_hash == hash_url_token(token),
            UtenteToken.purpose == purpose,
        )
    ).first()
    if row is None or row.used_at is not None or row.expires_at <= now:
        return None
    utente = session.get(Utente, row.utente_id)
    if utente is None or utente.deleted_at is not None:
        return None
    row.used_at = now
    session.add(row)
    session.commit()
    return utente
