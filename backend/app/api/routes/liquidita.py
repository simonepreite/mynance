"""Liquidità iniziale baseline (Story 2.2, FR-12), per-Utente.

The baseline is a property of the authenticated Utente — there is no id in the
path, so a request can only ever read or change the caller's own value (FR-4).
The derived Liquidità read endpoint (Story 2.4) lands on this same router.
"""

from collections.abc import Sequence
from datetime import date

from fastapi import APIRouter, Query

from app import crud_liquidita, crud_ricorrenza
from app.api.deps import CurrentUtente, SessionDep
from app.calc.allocazione import (
    cuscinetto,
    liquidita_allocata,
    risparmio_libero,
    spesa_media_mensile,
)
from app.calc.periodo import period_bounds
from app.calc.secchiello import compute_saldo_quota
from app.models import (
    AllocazionePublic,
    CategoriaTipo,
    LiquiditaInizialePublic,
    LiquiditaInizialeSet,
    LiquiditaInizialeSetResponse,
    LiquiditaPublic,
    Movimento,
    Secchiello,
)
from app.services.repository import UserScopedRepository

router = APIRouter(prefix="/liquidita", tags=["liquidita"])


@router.get("/")
def read_liquidita(
    session: SessionDep, current_utente: CurrentUtente
) -> LiquiditaPublic:
    """Current Liquidità, derived server-side (API-3: client never recomputes).

    Loads the Utente's stored inputs — baseline + Movimenti (Entrate/Spese),
    scoped via the repository — and feeds them to the pure calc engine (Story
    2.3). Capitale versato (Investimenti) arrives in Epic 5; empty for now.
    Negative values are returned with sign, never clamped.
    """
    # Lazy generation on access (Epic 6) before deriving the value.
    crud_ricorrenza.run_generation(session=session, utente=current_utente)
    value = crud_liquidita.compute_current_liquidita(
        session=session, utente=current_utente
    )
    return LiquiditaPublic(
        value_cents=value,
        iniziale_is_set=current_utente.liquidita_iniziale_cents is not None,
    )


@router.get("/iniziale")
def read_liquidita_iniziale(
    current_utente: CurrentUtente,
) -> LiquiditaInizialePublic:
    value = current_utente.liquidita_iniziale_cents
    return LiquiditaInizialePublic(value_cents=value, is_set=value is not None)


@router.put("/iniziale")
def set_liquidita_iniziale(
    body: LiquiditaInizialeSet,
    session: SessionDep,
    current_utente: CurrentUtente,
) -> LiquiditaInizialeSetResponse:
    rebaselined = crud_liquidita.set_liquidita_iniziale(
        session=session, utente=current_utente, value_cents=body.value_cents
    )
    return LiquiditaInizialeSetResponse(
        value_cents=body.value_cents, rebaselined=rebaselined
    )


def _first_of_month(d: date) -> date:
    return d.replace(day=1)


def _prev_month(first_of_month: date) -> date:
    if first_of_month.month == 1:
        return date(first_of_month.year - 1, 12, 1)
    return date(first_of_month.year, first_of_month.month - 1, 1)


def _monthly_spese_totals(
    spese: Sequence[Movimento], today: date, mesi: int
) -> list[int]:
    """Spese totals for the last ``mesi`` COMPLETE calendar months (current month
    excluded), restricted to months at/after the first recorded Spesa — so a new
    account averages over the months actually available (Story 3.6)."""
    if not spese:
        return []
    earliest = _first_of_month(min(m.data for m in spese))
    cursor = _prev_month(_first_of_month(today))  # latest complete month
    totals: list[int] = []
    for _ in range(mesi):
        if cursor < earliest:
            break
        start, end = period_bounds("month", cursor)
        totals.append(sum(m.amount_cents for m in spese if start <= m.data < end))
        cursor = _prev_month(cursor)
    return totals


@router.get("/allocazione")
def allocazione(
    session: SessionDep,
    current_utente: CurrentUtente,
    mesi: int = Query(6, ge=1, le=60),
) -> AllocazionePublic:
    """Allocation split + safety buffer, computed server-side (FR-14/FR-15)."""
    today = date.today()
    movimenti = UserScopedRepository(
        session=session, model=Movimento, utente_id=current_utente.id
    ).list()
    spese_mov = [m for m in movimenti if m.tipo == CategoriaTipo.spesa.value]
    liquidita = crud_liquidita.compute_current_liquidita(
        session=session, utente=current_utente
    )

    secchielli = UserScopedRepository(
        session=session, model=Secchiello, utente_id=current_utente.id
    ).list()
    saldi: list[int] = []
    for s in secchielli:
        linked = [
            (m.data, m.amount_cents) for m in spese_mov if m.secchiello_id == s.id
        ]
        saldo, _ = compute_saldo_quota(
            data_inizio=s.data_inizio,
            importo_previsto_cents=s.importo_previsto_cents,
            prossima_scadenza=s.prossima_scadenza,
            spese=linked,
            today=today,
        )
        saldi.append(saldo)

    allocata = liquidita_allocata(saldi)
    libero = risparmio_libero(liquidita, allocata)
    media = spesa_media_mensile(_monthly_spese_totals(spese_mov, today, mesi))
    target = cuscinetto(media, mesi)

    return AllocazionePublic(
        liquidita_cents=liquidita,
        liquidita_allocata_cents=allocata,
        risparmio_libero_cents=libero,
        spesa_media_mensile_cents=media,
        mesi_cuscinetto=mesi,
        cuscinetto_cents=target,
        sotto_cuscinetto=libero < target,
    )
