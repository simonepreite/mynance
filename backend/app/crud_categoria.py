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
