"""Regole ricorrenti CRUD (Story 6.1, FR-8), per-Utente scoped.

A Regola describes recurring money; the generation service (``crud_ricorrenza``)
materializes the Entrate / Versamenti PAC it owes. ``kind=entrata`` requires an
owned Entrata-type Categoria; ``kind=versamento_pac`` requires an owned
Investimento. Previously generated items are never rewritten by a Regola edit.
"""

import uuid

from fastapi import APIRouter, HTTPException, Query
from sqlmodel import SQLModel

from app.api.deps import CurrentUtente, SessionDep
from app.models import (
    Categoria,
    CategoriaTipo,
    Investimento,
    Message,
    Periodicita,
    RegolaKind,
    RegolaRicorrente,
    RegolaRicorrenteCreate,
    RegolaRicorrentePublic,
    RegolaRicorrenteUpdate,
    get_datetime_utc,
)
from app.services.repository import UserScopedRepository

router = APIRouter(prefix="/regole-ricorrenti", tags=["regole-ricorrenti"])


class RegoleRicorrentiList(SQLModel):
    items: list[RegolaRicorrentePublic]
    total: int
    limit: int
    offset: int


def _repo(
    session: SessionDep, current_utente: CurrentUtente
) -> UserScopedRepository[RegolaRicorrente]:
    return UserScopedRepository(
        session=session, model=RegolaRicorrente, utente_id=current_utente.id
    )


def _public(r: RegolaRicorrente) -> RegolaRicorrentePublic:
    return RegolaRicorrentePublic(
        id=r.id,
        importo_cents=r.importo_cents,
        periodicita=r.periodicita,
        intervallo_mesi=r.intervallo_mesi,
        day_of_period=r.day_of_period,
        kind=r.kind,
        categoria_id=r.categoria_id,
        investimento_id=r.investimento_id,
        start_date=r.start_date,
        note=r.note,
        created_at=r.created_at,
    )


def _resolve_intervallo(periodicita: Periodicita, intervallo: int | None) -> int | None:
    if periodicita == Periodicita.custom:
        if intervallo is None:
            raise HTTPException(
                status_code=422,
                detail="La periodicità 'custom' richiede un intervallo in mesi (≥ 1).",
            )
        return intervallo
    return None


def _validate_target(
    session: SessionDep,
    current_utente: CurrentUtente,
    body: RegolaRicorrenteCreate,
) -> None:
    if body.kind == RegolaKind.entrata:
        if body.categoria_id is None:
            raise HTTPException(
                status_code=422, detail="Una regola di entrata richiede una categoria."
            )
        cat = UserScopedRepository(
            session=session, model=Categoria, utente_id=current_utente.id
        ).get(body.categoria_id)
        if cat is None:
            raise HTTPException(status_code=404, detail="Categoria non trovata.")
        if cat.tipo != CategoriaTipo.entrata.value:
            raise HTTPException(
                status_code=422,
                detail="La categoria deve essere di tipo entrata.",
            )
    else:  # versamento_pac
        if body.investimento_id is None:
            raise HTTPException(
                status_code=422,
                detail="Una regola PAC richiede un investimento.",
            )
        inv = UserScopedRepository(
            session=session, model=Investimento, utente_id=current_utente.id
        ).get(body.investimento_id)
        if inv is None:
            raise HTTPException(status_code=404, detail="Investimento non trovato.")


@router.post("/", status_code=201)
def create_regola(
    body: RegolaRicorrenteCreate,
    session: SessionDep,
    current_utente: CurrentUtente,
) -> RegolaRicorrentePublic:
    _validate_target(session, current_utente, body)
    intervallo = _resolve_intervallo(body.periodicita, body.intervallo_mesi)
    regola = _repo(session, current_utente).add(
        RegolaRicorrente(
            utente_id=current_utente.id,
            importo_cents=body.importo_cents,
            periodicita=body.periodicita.value,
            intervallo_mesi=intervallo,
            day_of_period=body.day_of_period,
            kind=body.kind.value,
            categoria_id=body.categoria_id,
            investimento_id=body.investimento_id,
            start_date=body.start_date,
            note=body.note,
        )
    )
    return _public(regola)


@router.get("/")
def list_regole(
    session: SessionDep,
    current_utente: CurrentUtente,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> RegoleRicorrentiList:
    rows = sorted(
        _repo(session, current_utente).list(),
        key=lambda r: r.created_at or r.start_date,
        reverse=True,
    )
    page = rows[offset : offset + limit]
    return RegoleRicorrentiList(
        items=[_public(r) for r in page],
        total=len(rows),
        limit=limit,
        offset=offset,
    )


@router.get("/{regola_id}")
def get_regola(
    regola_id: uuid.UUID, session: SessionDep, current_utente: CurrentUtente
) -> RegolaRicorrentePublic:
    r = _repo(session, current_utente).get(regola_id)
    if r is None:
        raise HTTPException(status_code=404, detail="Regola non trovata.")
    return _public(r)


@router.patch("/{regola_id}")
def update_regola(
    regola_id: uuid.UUID,
    body: RegolaRicorrenteUpdate,
    session: SessionDep,
    current_utente: CurrentUtente,
) -> RegolaRicorrentePublic:
    repo = _repo(session, current_utente)
    regola = repo.get(regola_id)
    if regola is None:
        raise HTTPException(status_code=404, detail="Regola non trovata.")
    changes = body.model_dump(exclude_unset=True)
    if changes.get("periodicita") is not None:
        per = changes["periodicita"]
        per_enum = per if isinstance(per, Periodicita) else Periodicita(per)
        intervallo = changes.get("intervallo_mesi", regola.intervallo_mesi)
        changes["periodicita"] = per_enum.value
        changes["intervallo_mesi"] = _resolve_intervallo(per_enum, intervallo)
    for key in ("importo_cents", "periodicita", "day_of_period"):
        if key in changes and changes[key] is None:
            changes.pop(key)
    changes["updated_at"] = get_datetime_utc()
    updated = repo.update(regola_id, **changes)
    assert updated is not None
    return _public(updated)


@router.delete("/{regola_id}")
def delete_regola(
    regola_id: uuid.UUID, session: SessionDep, current_utente: CurrentUtente
) -> Message:
    if not _repo(session, current_utente).delete(regola_id):
        raise HTTPException(status_code=404, detail="Regola non trovata.")
    return Message(message="Regola eliminata.")
