"""Per-Utente isolation at the repository choke point (Story 1.5, FR-4)."""

import uuid
from collections.abc import Generator
from datetime import datetime

import pytest
from sqlmodel import Field, Session, SQLModel

from app.core.db import engine
from app.services.repository import UserScopedRepository


# A throwaway owned model + table, created only for these tests (not part of the
# app migrations). Stands in for the owned entities arriving in Epic 2.
class _DemoOwned(SQLModel, table=True):
    __tablename__ = "_demo_owned_isolation"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    utente_id: uuid.UUID = Field(index=True)
    label: str = ""
    deleted_at: datetime | None = None


@pytest.fixture(autouse=True)
def demo_table() -> Generator[None, None, None]:
    _DemoOwned.__table__.create(engine, checkfirst=True)
    yield
    _DemoOwned.__table__.drop(engine, checkfirst=True)


def test_cross_utente_and_missing_are_indistinguishable(db: Session) -> None:
    utente_a = uuid.uuid4()
    utente_b = uuid.uuid4()
    repo_a = UserScopedRepository(session=db, model=_DemoOwned, utente_id=utente_a)
    repo_b = UserScopedRepository(session=db, model=_DemoOwned, utente_id=utente_b)

    row_a = repo_a.add(_DemoOwned(utente_id=utente_a, label="a-data"))
    row_b = repo_b.add(_DemoOwned(utente_id=utente_b, label="b-data"))

    # A reads only its own; cross-Utente and non-existent are both None.
    assert repo_a.get(row_a.id) is not None
    assert repo_a.get(row_b.id) is None
    assert repo_a.get(uuid.uuid4()) is None
    assert [r.id for r in repo_a.list()] == [row_a.id]

    # A cannot mutate or delete B's row (same not-found result).
    assert repo_a.update(row_b.id, label="hacked") is None
    assert repo_a.delete(row_b.id) is False

    # B's data is untouched.
    got_b = repo_b.get(row_b.id)
    assert got_b is not None
    assert got_b.label == "b-data"


def test_add_forces_ownership(db: Session) -> None:
    owner = uuid.uuid4()
    attacker = uuid.uuid4()
    repo = UserScopedRepository(session=db, model=_DemoOwned, utente_id=owner)
    # Caller tries to plant a row owned by someone else; the repo overrides it.
    row = repo.add(_DemoOwned(utente_id=attacker, label="x"))
    assert row.utente_id == owner


def test_soft_delete_hides_row_from_reads(db: Session) -> None:
    owner = uuid.uuid4()
    repo = UserScopedRepository(session=db, model=_DemoOwned, utente_id=owner)
    row = repo.add(_DemoOwned(utente_id=owner, label="y"))
    assert repo.delete(row.id) is True
    assert repo.get(row.id) is None
    assert list(repo.list()) == []
