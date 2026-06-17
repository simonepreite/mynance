"""Server-side period aggregation (Story 2.8 Bilancio, Story 2.9 Statistiche).

Every monetary aggregate is computed here in integer cents (API-3: the client
renders but never sums money). All reads are scoped to the current Utente via
the repository, so cross-Utente data is never aggregated (FR-4).
"""

import uuid
from collections.abc import Sequence
from datetime import date

from fastapi import APIRouter, HTTPException, Query

from app.api.deps import CurrentUtente, SessionDep
from app.calc.money import add
from app.calc.periodo import VALID_PERIODS, month_anchors_back, period_bounds
from app.models import (
    BilancioPeriodo,
    Categoria,
    CategoriaSpesa,
    CategoriaTipo,
    Movimento,
    Statistiche,
    TrendPunto,
)
from app.services.repository import UserScopedRepository

router = APIRouter(tags=["riepilogo"])


def _load(
    session: SessionDep, current_utente: CurrentUtente
) -> tuple[Sequence[Movimento], dict[uuid.UUID, str]]:
    mov_repo = UserScopedRepository(
        session=session, model=Movimento, utente_id=current_utente.id
    )
    cat_repo = UserScopedRepository(
        session=session, model=Categoria, utente_id=current_utente.id
    )
    nomi = {c.id: c.nome for c in cat_repo.list()}
    return mov_repo.list(), nomi


def _in_range(m: Movimento, start: date, end: date) -> bool:
    return start <= m.data < end


def _sum_tipo(movimenti: Sequence[Movimento], tipo: CategoriaTipo) -> int:
    return add(*[m.amount_cents for m in movimenti if m.tipo == tipo.value])


def _spese_per_categoria(
    movimenti: Sequence[Movimento], nomi: dict[uuid.UUID, str]
) -> list[CategoriaSpesa]:
    totals: dict[uuid.UUID, int] = {}
    for m in movimenti:
        if m.tipo == CategoriaTipo.spesa.value:
            totals[m.categoria_id] = totals.get(m.categoria_id, 0) + m.amount_cents
    items = [
        CategoriaSpesa(categoria_id=cid, nome=nomi.get(cid, "—"), total_cents=tot)
        for cid, tot in totals.items()
    ]
    items.sort(key=lambda x: x.total_cents, reverse=True)
    return items


def _validate_period(period: str) -> None:
    if period not in VALID_PERIODS:
        raise HTTPException(status_code=422, detail="Periodo non valido.")


@router.get("/bilancio")
def bilancio(
    session: SessionDep,
    current_utente: CurrentUtente,
    anchor: date = Query(...),
    period: str = Query("month"),
) -> BilancioPeriodo:
    _validate_period(period)
    start, end = period_bounds(period, anchor)
    movimenti, nomi = _load(session, current_utente)
    in_period = [m for m in movimenti if _in_range(m, start, end)]
    entrate = _sum_tipo(in_period, CategoriaTipo.entrata)
    spese = _sum_tipo(in_period, CategoriaTipo.spesa)
    return BilancioPeriodo(
        period=period,
        start=start,
        end=end,
        netto_cents=entrate - spese,
        entrate_cents=entrate,
        spese_cents=spese,
        spese_per_categoria=_spese_per_categoria(in_period, nomi),
    )


@router.get("/statistiche")
def statistiche(
    session: SessionDep,
    current_utente: CurrentUtente,
    anchor: date = Query(...),
    period: str = Query("month"),
) -> Statistiche:
    _validate_period(period)
    start, end = period_bounds(period, anchor)
    movimenti, nomi = _load(session, current_utente)

    in_period = [m for m in movimenti if _in_range(m, start, end)]
    pie = _spese_per_categoria(in_period, nomi)

    trend: list[TrendPunto] = []
    months_with_data = 0
    for mstart in month_anchors_back(anchor, 6):
        ms, me = period_bounds("month", mstart)
        month_mov = [m for m in movimenti if _in_range(m, ms, me)]
        if month_mov:
            months_with_data += 1
        e = _sum_tipo(month_mov, CategoriaTipo.entrata)
        s = _sum_tipo(month_mov, CategoriaTipo.spesa)
        trend.append(
            TrendPunto(
                mese=f"{mstart.year:04d}-{mstart.month:02d}",
                entrate_cents=e,
                spese_cents=s,
                netto_cents=e - s,
            )
        )

    return Statistiche(
        period=period,
        start=start,
        end=end,
        trend=trend,
        pie=pie,
        has_trend=months_with_data >= 2,
        has_pie=any(p.total_cents > 0 for p in pie),
    )
