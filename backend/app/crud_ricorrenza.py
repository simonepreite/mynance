"""Lazy idempotent generation for Regole ricorrenti (Epic 6, FR-8/AR-Regole-Lazy).

Triggered on access (no scheduler). For each Regola it materializes the Entrate
or Versamenti PAC due up to today only, skipping occurrences already generated or
skipped (the ``regole_occorrenze`` ledger is the idempotency + skip memory).
"""

import uuid
from datetime import date

from sqlmodel import Session

from app.calc.ricorrenza import occorrenze_due
from app.models import (
    Investimento,
    Movimento,
    RegolaKind,
    RegolaOccorrenza,
    RegolaRicorrente,
    Utente,
    VersamentoPac,
    periodicita_mesi,
)
from app.services.repository import UserScopedRepository


def run_generation(*, session: Session, utente: Utente) -> None:
    """Materialize all due (≤ today) Entrate / Versamenti PAC for the Utente."""
    regole = UserScopedRepository(
        session=session, model=RegolaRicorrente, utente_id=utente.id
    ).list()
    if not regole:
        return

    today = date.today()
    occ_repo = UserScopedRepository(
        session=session, model=RegolaOccorrenza, utente_id=utente.id
    )
    # Already materialized OR skipped → never (re)generate (idempotent).
    seen = {(o.regola_id, o.data) for o in occ_repo.list()}
    inv_repo = UserScopedRepository(
        session=session, model=Investimento, utente_id=utente.id
    )

    created = False
    for r in regole:
        if r.kind == RegolaKind.versamento_pac.value:
            # Orphaned (Investimento soft-deleted) → skip this Regola, not others.
            if r.investimento_id is None or inv_repo.get(r.investimento_id) is None:
                continue

        intervallo = periodicita_mesi(r.periodicita, r.intervallo_mesi)
        for d in occorrenze_due(
            start_date=r.start_date,
            intervallo_mesi=intervallo,
            day_of_period=r.day_of_period,
            today=today,
        ):
            if (r.id, d) in seen:
                continue
            if r.kind == RegolaKind.entrata.value:
                session.add(
                    Movimento(
                        utente_id=utente.id,
                        tipo="entrata",
                        amount_cents=r.importo_cents,
                        data=d,
                        categoria_id=r.categoria_id,
                        regola_id=r.id,
                    )
                )
            else:
                session.add(
                    VersamentoPac(
                        utente_id=utente.id,
                        investimento_id=r.investimento_id,
                        importo_cents=r.importo_cents,
                        data=d,
                        regola_id=r.id,
                    )
                )
            session.add(
                RegolaOccorrenza(
                    utente_id=utente.id, regola_id=r.id, data=d, skipped=False
                )
            )
            seen.add((r.id, d))
            created = True

    if created:
        session.commit()


def mark_skipped(
    *,
    session: Session,
    utente: Utente,
    regola_id: uuid.UUID,
    data: date,
) -> None:
    """Remember a skipped occurrence so generation never re-materializes it."""
    rows = UserScopedRepository(
        session=session, model=RegolaOccorrenza, utente_id=utente.id
    ).list()
    for o in rows:
        if o.regola_id == regola_id and o.data == data:
            o.skipped = True
            session.add(o)
            session.commit()
            return
    # No ledger row yet (defensive): record the skip so it stays skipped.
    session.add(
        RegolaOccorrenza(
            utente_id=utente.id, regola_id=regola_id, data=data, skipped=True
        )
    )
    session.commit()
