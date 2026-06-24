"""Movimenti CRUD (Story 2.5 Spesa / 2.6 Entrata, FR-5/FR-6), per-Utente scoped.

A Movimento's ``tipo`` must match its Categoria's ``tipo`` (FR-7): a Categoria
only applies to Movimenti of its own tipo. Every access goes through the
``UserScopedRepository`` (authZ choke point), so another Utente's Categoria or
Movimento is indistinguishable from a missing one (404).
"""

import uuid
from datetime import date

from fastapi import APIRouter, HTTPException, Query

from app import crud_ricorrenza
from app.api.deps import CurrentUtente, SessionDep
from app.models import (
    Categoria,
    Message,
    Movimento,
    MovimentoCreate,
    MovimentoPublic,
    MovimentoUpdate,
    Secchiello,
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
        secchiello_id=m.secchiello_id,
        note=m.note,
        created_at=m.created_at,
    )


def _require_categoria_of_tipo(
    cat_repo: UserScopedRepository[Categoria], categoria_id: uuid.UUID, tipo: str
) -> Categoria:
    """Owned Categoria of the matching tipo, else 404 (missing/foreign) or 422 (tipo)."""
    cat = cat_repo.get(categoria_id)
    if cat is None:
        raise HTTPException(status_code=404, detail="Categoria non trovata.")
    if cat.tipo != tipo:
        raise HTTPException(
            status_code=422,
            detail="La Categoria non è del tipo del movimento.",
        )
    return cat


def _require_owned_secchiello(
    session: SessionDep, current_utente: CurrentUtente, secchiello_id: uuid.UUID
) -> None:
    owned = UserScopedRepository(
        session=session, model=Secchiello, utente_id=current_utente.id
    ).get(secchiello_id)
    if owned is None:
        raise HTTPException(status_code=404, detail="Secchiello non trovato.")


@router.post("/", status_code=201)
def create_movimento(
    body: MovimentoCreate, session: SessionDep, current_utente: CurrentUtente
) -> MovimentoPublic:
    categoria = _require_categoria_of_tipo(
        _cat_repo(session, current_utente), body.categoria_id, body.tipo.value
    )
    # Secchiello link (Story 3.1): Entrate never link; for a Spesa, default from
    # the Categoria's linked Secchiello unless the caller set one explicitly
    # (passing null forces "no Secchiello").
    secchiello_id: uuid.UUID | None
    if body.tipo.value != "spesa":
        secchiello_id = None
    elif "secchiello_id" in body.model_fields_set:
        secchiello_id = body.secchiello_id
    else:
        secchiello_id = categoria.secchiello_id
    if secchiello_id is not None:
        _require_owned_secchiello(session, current_utente, secchiello_id)

    repo = _mov_repo(session, current_utente)
    movimento = repo.add(
        Movimento(
            utente_id=current_utente.id,
            tipo=body.tipo.value,
            amount_cents=body.amount_cents,
            data=body.data,
            categoria_id=body.categoria_id,
            secchiello_id=secchiello_id,
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
    # Lazy generation on access (Epic 6): materialize due recurring items first.
    crud_ricorrenza.run_generation(session=session, utente=current_utente)
    repo = _mov_repo(session, current_utente)
    items = list(repo.list())
    if categoria_id is not None:
        cat_ids = {categoria_id}
        for c in _cat_repo(session, current_utente).list():
            if c.parent_id == categoria_id:
                cat_ids.add(c.id)
        items = [m for m in items if m.categoria_id in cat_ids]
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
    movimento = repo.get(movimento_id)
    if movimento is None:
        raise HTTPException(status_code=404, detail="Movimento non trovato.")
    # A generated Entrata: deleting it skips that occurrence so generation never
    # re-materializes it (Story 6.4 — skip leaves no Drift).
    if movimento.regola_id is not None:
        crud_ricorrenza.mark_skipped(
            session=session,
            utente=current_utente,
            regola_id=movimento.regola_id,
            data=movimento.data,
        )
    repo.delete(movimento_id)
    return Message(message="Movimento eliminato.")
