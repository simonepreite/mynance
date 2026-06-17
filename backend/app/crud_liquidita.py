"""Liquidità iniziale baseline + audited re-baselining (Story 2.2, FR-12).

The baseline lives on the Utente row (a single per-Utente value, integer cents).
A first set (currently unset) is not a re-baselining and is not audited; changing
an already-set value to a different one writes a ``RebaselineAudit`` row.
"""

from sqlmodel import Session

from app.calc.liquidita import compute_liquidita
from app.models import (
    CategoriaTipo,
    Movimento,
    RebaselineAudit,
    Utente,
    VersamentoPac,
    get_datetime_utc,
)
from app.services.repository import UserScopedRepository


def compute_current_liquidita(*, session: Session, utente: Utente) -> int:
    """Current derived Liquidità in cents (FR-13), scoped to the Utente.

    ``Liquidità = iniziale + Σ Entrate − Σ Spese − Σ Capitale versato``. The
    single source used by the read endpoint, allocation, reconciliation, and
    Patrimonio so a Versamento PAC lowers Liquidità everywhere (FR-19/FR-22).
    """
    movimenti = UserScopedRepository(
        session=session, model=Movimento, utente_id=utente.id
    ).list()
    entrate = [
        m.amount_cents for m in movimenti if m.tipo == CategoriaTipo.entrata.value
    ]
    spese = [m.amount_cents for m in movimenti if m.tipo == CategoriaTipo.spesa.value]
    versamenti = UserScopedRepository(
        session=session, model=VersamentoPac, utente_id=utente.id
    ).list()
    capitale = [v.importo_cents for v in versamenti]
    return compute_liquidita(
        iniziale_cents=utente.liquidita_iniziale_cents,
        entrate_cents=entrate,
        spese_cents=spese,
        capitale_versato_cents=capitale,
    )


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
