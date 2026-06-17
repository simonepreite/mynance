"""User-scoped repository — the single per-Utente authorization choke point.

Every read/write is filtered by ``utente_id`` (FR-4, AR-AuthZ). Cross-Utente
access and a truly-missing row are indistinguishable (both → ``None``), so the
existence of another Utente's data is never leaked through differing responses.
Routers must go through this repository and never query owned models directly;
a query missing the ``utente_id`` scope is a defect (architecture anti-pattern).

Owned models are expected to carry ``utente_id`` and (optionally) ``deleted_at``
for soft-delete; the rest of the entity tables arrive in Epic 2.
"""

import uuid
from collections.abc import Sequence
from datetime import datetime, timezone
from typing import Generic, TypeVar

from sqlmodel import Session, SQLModel, select

ModelT = TypeVar("ModelT", bound=SQLModel)


class UserScopedRepository(Generic[ModelT]):
    def __init__(
        self, *, session: Session, model: type[ModelT], utente_id: uuid.UUID
    ) -> None:
        self.session = session
        self.model = model
        self.utente_id = utente_id

    def _owned(self, obj: ModelT | None) -> bool:
        return (
            obj is not None
            and getattr(obj, "utente_id", None) == self.utente_id
            and getattr(obj, "deleted_at", None) is None
        )

    def get(self, entity_id: uuid.UUID) -> ModelT | None:
        """Return the entity iff it belongs to this Utente, else ``None``."""
        obj = self.session.get(self.model, entity_id)
        return obj if self._owned(obj) else None

    def list(self) -> Sequence[ModelT]:
        utente_col = getattr(self.model, "utente_id")  # noqa: B009
        statement = select(self.model).where(utente_col == self.utente_id)
        rows = self.session.exec(statement).all()
        return [r for r in rows if getattr(r, "deleted_at", None) is None]

    def add(self, obj: ModelT) -> ModelT:
        # Force ownership — never trust a caller-supplied utente_id.
        setattr(obj, "utente_id", self.utente_id)  # noqa: B010
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def update(self, entity_id: uuid.UUID, **changes: object) -> ModelT | None:
        obj = self.get(entity_id)
        if obj is None:
            return None
        for key, value in changes.items():
            setattr(obj, key, value)
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def delete(self, entity_id: uuid.UUID) -> bool:
        obj = self.get(entity_id)
        if obj is None:
            return False
        if hasattr(obj, "deleted_at"):
            setattr(obj, "deleted_at", datetime.now(timezone.utc))  # noqa: B010
            self.session.add(obj)
        else:
            self.session.delete(obj)
        self.session.commit()
        return True
