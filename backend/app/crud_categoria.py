"""Categoria provisioning (Story 2.1, FR-7).

The starter set is suggested separately per tipo and created for a new Utente on
account creation. The system "non identificato" Categorie (one per tipo) are
provisioned later in Epic 4 (Story 4.1) — not here.
"""

import uuid

from sqlmodel import Session

from app.models import Categoria, CategoriaTipo

STARTER_SPESA: tuple[str, ...] = (
    "Spesa alimentare",
    "Casa",
    "Trasporti",
    "Salute",
    "Svago",
    "Abbonamenti",
    "Altro",
)
STARTER_ENTRATA: tuple[str, ...] = (
    "Stipendio",
    "Rimborsi",
    "Altro",
)


def provision_starter_categorie(*, session: Session, utente_id: uuid.UUID) -> None:
    """Create the per-tipo starter Categorie for a freshly-created Utente."""
    for nome in STARTER_SPESA:
        session.add(
            Categoria(utente_id=utente_id, nome=nome, tipo=CategoriaTipo.spesa.value)
        )
    for nome in STARTER_ENTRATA:
        session.add(
            Categoria(utente_id=utente_id, nome=nome, tipo=CategoriaTipo.entrata.value)
        )
    session.commit()


NON_IDENTIFICATO = "non identificato"


def provision_system_categorie(*, session: Session, utente_id: uuid.UUID) -> None:
    """Create the system "non identificato" Categorie, one per tipo (Story 4.1).

    Flagged ``is_system`` so they cannot be renamed/deleted; they appear in the
    typed lists like any other Categoria and host reconciliation plug Movimenti.
    """
    for tipo in (CategoriaTipo.spesa, CategoriaTipo.entrata):
        session.add(
            Categoria(
                utente_id=utente_id,
                nome=NON_IDENTIFICATO,
                tipo=tipo.value,
                is_system=True,
            )
        )
    session.commit()


def get_system_categoria(
    *, session: Session, utente_id: uuid.UUID, tipo: CategoriaTipo
) -> Categoria | None:
    """The Utente's "non identificato" Categoria for a tipo (reconciliation plug)."""
    from sqlmodel import select

    statement = select(Categoria).where(
        Categoria.utente_id == utente_id,
        Categoria.tipo == tipo.value,
        Categoria.is_system == True,  # noqa: E712
        Categoria.deleted_at == None,  # noqa: E711
    )
    return session.exec(statement).first()
