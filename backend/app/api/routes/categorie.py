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
    Secchiello,
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
        parent_id=categoria.parent_id,
        secchiello_id=categoria.secchiello_id,
        is_system=categoria.is_system,
        created_at=categoria.created_at,
    )


@router.post("/", status_code=201)
def create_categoria(
    body: CategoriaCreate, session: SessionDep, current_utente: CurrentUtente
) -> CategoriaPublic:
    repo = _repo(session, current_utente)
    if body.parent_id is not None:
        parent = repo.get(body.parent_id)
        if parent is None:
            raise HTTPException(status_code=404, detail="Categoria padre non trovata.")
        if parent.parent_id is not None:
            raise HTTPException(
                status_code=422,
                detail="Le sottocategorie possono avere un solo livello.",
            )
        if parent.tipo != body.tipo.value:
            raise HTTPException(
                status_code=422,
                detail="La sottocategoria deve essere dello stesso tipo della categoria padre.",
            )
        if parent.is_system:
            raise HTTPException(
                status_code=422,
                detail="Le categorie di sistema non possono avere sottocategorie.",
            )
    categoria = repo.add(
        Categoria(
            utente_id=current_utente.id,
            nome=body.nome,
            tipo=body.tipo.value,
            parent_id=body.parent_id,
        )
    )
    return _public(categoria)


@router.get("/")
def list_categorie(session: SessionDep, current_utente: CurrentUtente) -> CategorieList:
    repo = _repo(session, current_utente)
    # Deterministic order: user Categorie first (alphabetical), system "non
    # identificato" plugs last. Without this the underlying query has no ORDER
    # BY, so the heap order is unstable as the table grows.
    items = sorted(repo.list(), key=lambda c: (c.is_system, c.nome.lower()))
    return CategorieList(
        spesa=[_public(c) for c in items if c.tipo == CategoriaTipo.spesa.value],
        entrata=[_public(c) for c in items if c.tipo == CategoriaTipo.entrata.value],
    )


@router.patch("/{categoria_id}")
def update_categoria(
    categoria_id: uuid.UUID,
    body: CategoriaUpdate,
    session: SessionDep,
    current_utente: CurrentUtente,
) -> CategoriaPublic:
    """Rename and/or set the Categoria→Secchiello link (Story 3.1).

    Only Spesa-type Categorie can link to a Secchiello (Entrata → 422); the
    Secchiello must be owned (else 404); `secchiello_id: null` clears the link.
    """
    repo = _repo(session, current_utente)
    categoria = repo.get(categoria_id)
    if categoria is None:
        raise HTTPException(status_code=404, detail="Categoria non trovata.")
    if categoria.is_system:
        raise HTTPException(
            status_code=422,
            detail="Le categorie di sistema non possono essere modificate.",
        )

    changes = body.model_dump(exclude_unset=True)
    if "secchiello_id" in changes:
        if categoria.tipo != CategoriaTipo.spesa.value:
            raise HTTPException(
                status_code=422,
                detail="Solo le categorie di spesa possono avere un Secchiello.",
            )
        sid = changes["secchiello_id"]
        if sid is not None:
            owned = UserScopedRepository(
                session=session, model=Secchiello, utente_id=current_utente.id
            ).get(sid)
            if owned is None:
                raise HTTPException(status_code=404, detail="Secchiello non trovato.")
    if changes.get("nome") is None:
        changes.pop("nome", None)
    changes["updated_at"] = get_datetime_utc()

    updated = repo.update(categoria_id, **changes)
    if updated is None:  # pragma: no cover - just fetched above
        raise HTTPException(status_code=404, detail="Categoria non trovata.")
    return _public(updated)


@router.delete("/{categoria_id}")
def delete_categoria(
    categoria_id: uuid.UUID, session: SessionDep, current_utente: CurrentUtente
) -> Message:
    # NOTE (Story 2.5): when Movimenti exist, deleting a Categoria in use must
    # prompt reassignment rather than soft-delete silently. No Movimenti yet.
    repo = _repo(session, current_utente)
    existing = repo.get(categoria_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Categoria non trovata.")
    if existing.is_system:
        raise HTTPException(
            status_code=422,
            detail="Le categorie di sistema non possono essere eliminate.",
        )
    for child in repo.list():
        if child.parent_id == categoria_id:
            repo.delete(child.id)
    repo.delete(categoria_id)
    return Message(message="Categoria eliminata.")
