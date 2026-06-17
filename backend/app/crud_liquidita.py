"""Liquidità iniziale baseline + audited re-baselining (Story 2.2, FR-12).

The baseline lives on the Utente row (a single per-Utente value, integer cents).
A first set (currently unset) is not a re-baselining and is not audited; changing
an already-set value to a different one writes a ``RebaselineAudit`` row.
"""

from sqlmodel import Session

from app.models import RebaselineAudit, Utente, get_datetime_utc


def set_liquidita_iniziale(
    *, session: Session, utente: Utente, value_cents: int
) -> bool:
    """Set the baseline; return True iff this re-baselined an existing value."""
    old = utente.liquidita_iniziale_cents
    rebaselined = old is not None and old != value_cents
    if old is not None and old != value_cents:
        session.add(
            RebaselineAudit(
                utente_id=utente.id,
                old_value_cents=old,
                new_value_cents=value_cents,
            )
        )
    utente.liquidita_iniziale_cents = value_cents
    utente.updated_at = get_datetime_utc()
    session.add(utente)
    session.commit()
    session.refresh(utente)
    return rebaselined
