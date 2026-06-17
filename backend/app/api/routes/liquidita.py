"""Liquidità iniziale baseline (Story 2.2, FR-12), per-Utente.

The baseline is a property of the authenticated Utente — there is no id in the
path, so a request can only ever read or change the caller's own value (FR-4).
The derived Liquidità read endpoint (Story 2.4) lands on this same router.
"""

from fastapi import APIRouter

from app import crud_liquidita
from app.api.deps import CurrentUtente, SessionDep
from app.calc.liquidita import compute_liquidita
from app.models import (
    CategoriaTipo,
    LiquiditaInizialePublic,
    LiquiditaInizialeSet,
    LiquiditaInizialeSetResponse,
    LiquiditaPublic,
    Movimento,
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
    iniziale = current_utente.liquidita_iniziale_cents
    repo = UserScopedRepository(
        session=session, model=Movimento, utente_id=current_utente.id
    )
    movimenti = repo.list()
    entrate = [
        m.amount_cents for m in movimenti if m.tipo == CategoriaTipo.entrata.value
    ]
    spese = [m.amount_cents for m in movimenti if m.tipo == CategoriaTipo.spesa.value]
    value = compute_liquidita(
        iniziale_cents=iniziale,
        entrate_cents=entrate,
        spese_cents=spese,
    )
    return LiquiditaPublic(value_cents=value, iniziale_is_set=iniziale is not None)


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
