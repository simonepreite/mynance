"""Movimenti CRUD (Story 2.5 Spesa / 2.6 Entrata, FR-5/FR-6), per-Utente scoped.

A Movimento's ``tipo`` must match its Categoria's ``tipo`` (FR-7): a Categoria
only applies to Movimenti of its own tipo. Every access goes through the
``UserScopedRepository`` (authZ choke point), so another Utente's Categoria or
Movimento is indistinguishable from a missing one (404).
"""

import uuid
from datetime import date

from fastapi import APIRouter, HTTPException, Query

from app.api.deps import CurrentUtente, SessionDep
from app.models import (
    Categoria,
    Message,
    Movimento,
    MovimentoCreate,
    MovimentoPublic,
    MovimentoUpdate,
    get_datetime_utc,
)
from app.services.repository import UserScopedRepository

router = APIRouter(prefix="/movimenti", tags=["movimenti"])


def _mov_repo(
    session: SessionDep, current_utente: CurrentUtente
) -> UserScopedRepository[Movimento]:
    return UserScopedRepository(
        session=session, model=Movimento, utente_id=current_utente.id
    )


def _cat_repo(
    session: SessionDep, current_utente: CurrentUtente
) -> UserScopedRepository[Categoria]:
    return UserScopedRepository(
        session=session, model=Categoria, utente_id=current_utente.id
    )


def _public(m: Movimento) -> MovimentoPublic:
    return MovimentoPublic(
        id=m.id,
        tipo=m.tipo,
        amount_cents=m.amount_cents,
        data=m.data,
        categoria_id=m.categoria_id,
        note=m.note,
        created_at=m.created_at,
    )


def _require_categoria_of_tipo(
    cat_repo: UserScopedRepository[Categoria], categoria_id: uuid.UUID, tipo: str
) -> None:
    """Owned Categoria of the matching tipo, else 404 (missing/foreign) or 422 (tipo)."""
    cat = cat_repo.get(categoria_id)
    if cat is None:
        raise HTTPException(status_code=404, detail="Categoria non trovata.")
    if cat.tipo != tipo:
        raise HTTPException(
            status_code=422,
            detail="La Categoria non è del tipo del movimento.",
        )


@router.post("/", status_code=201)
def create_movimento(
    body: MovimentoCreate, session: SessionDep, current_utente: CurrentUtente
) -> MovimentoPublic:
    _require_categoria_of_tipo(
        _cat_repo(session, current_utente), body.categoria_id, body.tipo.value
    )
    repo = _mov_repo(session, current_utente)
    movimento = repo.add(
        Movimento(
            utente_id=current_utente.id,
            tipo=body.tipo.value,
            amount_cents=body.amount_cents,
            data=body.data,
            categoria_id=body.categoria_id,
            note=body.note,
        )
    )
    return _public(movimento)


@router.get("/")
def list_movimenti(
    session: SessionDep,
    current_utente: CurrentUtente,
    categoria_id: uuid.UUID | None = Query(None),
    start: date | None = Query(None),
    end: date | None = Query(None),
) -> list[MovimentoPublic]:
    """List my Movimenti, newest first. Optional filters power the Home
    per-Categoria drill-down (Story 2.8): a Categoria and a half-open
    ``[start, end)`` date range."""
    repo = _mov_repo(session, current_utente)
    items = list(repo.list())
    if categoria_id is not None:
        items = [m for m in items if m.categoria_id == categoria_id]
    if start is not None:
        items = [m for m in items if m.data >= start]
    if end is not None:
        items = [m for m in items if m.data < end]
    items.sort(key=lambda m: m.data, reverse=True)
    return [_public(m) for m in items]


@router.patch("/{movimento_id}")
def update_movimento(
    movimento_id: uuid.UUID,
    body: MovimentoUpdate,
    session: SessionDep,
    current_utente: CurrentUtente,
) -> MovimentoPublic:
    repo = _mov_repo(session, current_utente)
    movimento = repo.get(movimento_id)
    if movimento is None:
        raise HTTPException(status_code=404, detail="Movimento non trovato.")

    changes = body.model_dump(exclude_unset=True)
    # Never null out a required column; only `note` is nullable.
    for key in ("amount_cents", "data", "categoria_id"):
        if key in changes and changes[key] is None:
            changes.pop(key)
    if changes.get("categoria_id") is not None:
        _require_categoria_of_tipo(
            _cat_repo(session, current_utente),
            changes["categoria_id"],
            movimento.tipo,
        )

    changes["updated_at"] = get_datetime_utc()
    updated = repo.update(movimento_id, **changes)
    if updated is None:  # pragma: no cover - just fetched above
        raise HTTPException(status_code=404, detail="Movimento non trovato.")
    return _public(updated)


@router.delete("/{movimento_id}")
def delete_movimento(
    movimento_id: uuid.UUID, session: SessionDep, current_utente: CurrentUtente
) -> Message:
    repo = _mov_repo(session, current_utente)
    if not repo.delete(movimento_id):
        raise HTTPException(status_code=404, detail="Movimento non trovato.")
    return Message(message="Movimento eliminato.")
