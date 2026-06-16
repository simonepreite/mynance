"""Typed Categorie CRUD (Story 2.1, FR-7), per-Utente scoped via the repository.

Every access goes through ``UserScopedRepository`` (the authZ choke point), so
another Utente's Categoria is indistinguishable from a missing one (404).
"""

import uuid

from fastapi import APIRouter, HTTPException

from app.api.deps import CurrentUtente, SessionDep
from app.models import (
    Categoria,
    CategoriaCreate,
    CategoriaPublic,
    CategoriaTipo,
    CategoriaUpdate,
    CategorieList,
    Message,
    get_datetime_utc,
)
from app.services.repository import UserScopedRepository

router = APIRouter(prefix="/categorie", tags=["categorie"])


def _repo(
    session: SessionDep, current_utente: CurrentUtente
) -> UserScopedRepository[Categoria]:
    return UserScopedRepository(
        session=session, model=Categoria, utente_id=current_utente.id
    )


def _public(categoria: Categoria) -> CategoriaPublic:
    return CategoriaPublic(
        id=categoria.id,
        nome=categoria.nome,
        tipo=categoria.tipo,
        created_at=categoria.created_at,
    )


@router.post("/", status_code=201)
def create_categoria(
    body: CategoriaCreate, session: SessionDep, current_utente: CurrentUtente
) -> CategoriaPublic:
    repo = _repo(session, current_utente)
    categoria = repo.add(
        Categoria(utente_id=current_utente.id, nome=body.nome, tipo=body.tipo.value)
    )
    return _public(categoria)


@router.get("/")
def list_categorie(session: SessionDep, current_utente: CurrentUtente) -> CategorieList:
    repo = _repo(session, current_utente)
    items = repo.list()
    return CategorieList(
        spesa=[_public(c) for c in items if c.tipo == CategoriaTipo.spesa.value],
        entrata=[_public(c) for c in items if c.tipo == CategoriaTipo.entrata.value],
    )


@router.patch("/{categoria_id}")
def rename_categoria(
    categoria_id: uuid.UUID,
    body: CategoriaUpdate,
    session: SessionDep,
    current_utente: CurrentUtente,
) -> CategoriaPublic:
    repo = _repo(session, current_utente)
    categoria = repo.update(categoria_id, nome=body.nome, updated_at=get_datetime_utc())
    if categoria is None:
        raise HTTPException(status_code=404, detail="Categoria non trovata.")
    return _public(categoria)


@router.delete("/{categoria_id}")
def delete_categoria(
    categoria_id: uuid.UUID, session: SessionDep, current_utente: CurrentUtente
) -> Message:
    # NOTE (Story 2.5): when Movimenti exist, deleting a Categoria in use must
    # prompt reassignment rather than soft-delete silently. No Movimenti yet.
    repo = _repo(session, current_utente)
    if not repo.delete(categoria_id):
        raise HTTPException(status_code=404, detail="Categoria non trovata.")
    return Message(message="Categoria eliminata.")
