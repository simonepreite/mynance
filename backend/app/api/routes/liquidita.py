"""Liquidità iniziale baseline (Story 2.2, FR-12), per-Utente.

The baseline is a property of the authenticated Utente — there is no id in the
path, so a request can only ever read or change the caller's own value (FR-4).
The derived Liquidità read endpoint (Story 2.4) lands on this same router.
"""

from fastapi import APIRouter

from app import crud_liquidita
from app.api.deps import CurrentUtente, SessionDep
from app.models import (
    LiquiditaInizialePublic,
    LiquiditaInizialeSet,
    LiquiditaInizialeSetResponse,
)

router = APIRouter(prefix="/liquidita", tags=["liquidita"])


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
