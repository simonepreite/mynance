import enum
import uuid
from datetime import date, datetime, timezone

from pydantic import EmailStr
from sqlalchemy import BigInteger, DateTime
from sqlmodel import Field, Relationship, SQLModel


def get_datetime_utc() -> datetime:
    return datetime.now(timezone.utc)


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore[assignment]
    password: str | None = Field(default=None, min_length=8, max_length=128)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID
    created_at: datetime | None = None


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Shared properties
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Properties to receive on item creation
class ItemCreate(ItemBase):
    pass


# Properties to receive on item update
class ItemUpdate(ItemBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore[assignment]


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime | None = None


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None
    jti: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)


# ---------------------------------------------------------------------------
# mynance — Utente domain (FR-1 registration, FR-3 one-time recovery code).
# Distinct from the template's email-based ``User`` (reused only for the seeded
# superuser / template tests). Italian domain noun + plural table per
# architecture.md. Money is not involved here; later stories add the rest.
# ---------------------------------------------------------------------------


# Properties received on registration
class UtenteRegister(SQLModel):
    username: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=8, max_length=128)


# Properties received on login
class UtenteLogin(SQLModel):
    username: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=8, max_length=128)


# Properties received on recovery (regain access via the one-time code)
class UtenteRecover(SQLModel):
    username: str = Field(min_length=3, max_length=255)
    recovery_code: str = Field(min_length=1, max_length=255)
    new_password: str = Field(min_length=8, max_length=128)


# Database model — table ``utenti``
class Utente(SQLModel, table=True):
    __tablename__ = "utenti"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    username: str = Field(unique=True, index=True, max_length=255)
    # argon2 salted hashes — plaintext is never persisted or logged
    password_hash: str
    recovery_code_hash: str
    session_timeout_days: int = Field(default=30)
    # Liquidità iniziale baseline in integer cents (Story 2.2, FR-12).
    # NULL = unset: a new account starts with no baseline (FR-1).
    liquidita_iniziale_cents: int | None = Field(
        default=None,
        sa_type=BigInteger,
    )
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    updated_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    deleted_at: datetime | None = Field(
        default=None,
        sa_type=DateTime(timezone=True),  # type: ignore
    )


# Safe public projection — never includes either hash
class UtentePublic(SQLModel):
    id: uuid.UUID
    username: str
    session_timeout_days: int
    created_at: datetime | None = None


# Registration response — carries the one-time recovery code, shown EXACTLY
# once. The plaintext lives only in this response; it is never retrievable.
class UtenteRegisterResponse(SQLModel):
    utente: UtentePublic
    recovery_code: str


# ---------------------------------------------------------------------------
# mynance — Categoria (FR-7). Typed (Spesa/Entrata) and per-Utente scoped.
# ---------------------------------------------------------------------------


class CategoriaTipo(str, enum.Enum):
    spesa = "spesa"
    entrata = "entrata"


class CategoriaCreate(SQLModel):
    nome: str = Field(min_length=1, max_length=255)
    tipo: CategoriaTipo


class CategoriaUpdate(SQLModel):
    # Only a rename is allowed; tipo is a fixed, distinct space.
    nome: str = Field(min_length=1, max_length=255)


class Categoria(SQLModel, table=True):
    __tablename__ = "categorie"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    utente_id: uuid.UUID = Field(foreign_key="utenti.id", nullable=False, index=True)
    nome: str = Field(max_length=255)
    tipo: str = Field(max_length=16, index=True)  # "spesa" | "entrata"
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    updated_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    deleted_at: datetime | None = Field(
        default=None,
        sa_type=DateTime(timezone=True),  # type: ignore
    )


class CategoriaPublic(SQLModel):
    id: uuid.UUID
    nome: str
    tipo: str
    created_at: datetime | None = None


# Categorie split by tipo (Spesa and Entrata are distinct spaces, not a filter)
class CategorieList(SQLModel):
    spesa: list[CategoriaPublic]
    entrata: list[CategoriaPublic]


# ---------------------------------------------------------------------------
# mynance — Liquidità iniziale (FR-12). A single per-Utente baseline in integer
# cents; changing an already-set value is an audited re-baselining event.
# ---------------------------------------------------------------------------


class LiquiditaInizialeSet(SQLModel):
    # Integer cents; zero is permitted, negative is rejected. A non-integer
    # (e.g. a float) is not valid cents and is rejected as 422 problem+json.
    value_cents: int = Field(ge=0)


class LiquiditaInizialePublic(SQLModel):
    value_cents: int | None = None  # None = unset
    is_set: bool


class LiquiditaInizialeSetResponse(SQLModel):
    value_cents: int
    is_set: bool = True
    # True iff this call changed an already-set baseline (re-baselining): it
    # shifts every derived figure, so the client surfaces it explicitly.
    rebaselined: bool


# Derived-on-read current Liquidità (Story 2.4, FR-13) — computed server-side.
class LiquiditaPublic(SQLModel):
    value_cents: int
    iniziale_is_set: bool


# ---------------------------------------------------------------------------
# mynance — Movimento (FR-5 Spesa, FR-6 Entrata). A typed cash movement in
# integer cents; ``tipo`` matches the referenced Categoria's tipo. The sign is
# implied by tipo (Spesa subtracts, Entrata adds) — ``amount_cents`` is the
# positive magnitude. Per-Utente scoped, soft-deleted.
# ---------------------------------------------------------------------------


class MovimentoCreate(SQLModel):
    tipo: CategoriaTipo
    amount_cents: int = Field(gt=0)
    data: date
    categoria_id: uuid.UUID
    note: str | None = Field(default=None, max_length=255)


class MovimentoUpdate(SQLModel):
    # tipo is immutable (a Spesa never becomes an Entrata); only these change.
    amount_cents: int | None = Field(default=None, gt=0)
    data: date | None = None
    categoria_id: uuid.UUID | None = None
    note: str | None = Field(default=None, max_length=255)


class Movimento(SQLModel, table=True):
    __tablename__ = "movimenti"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    utente_id: uuid.UUID = Field(foreign_key="utenti.id", nullable=False, index=True)
    tipo: str = Field(max_length=16, index=True)  # "spesa" | "entrata"
    amount_cents: int = Field(sa_type=BigInteger)
    data: date
    categoria_id: uuid.UUID = Field(foreign_key="categorie.id", nullable=False)
    note: str | None = Field(default=None, max_length=255)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    updated_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    deleted_at: datetime | None = Field(
        default=None,
        sa_type=DateTime(timezone=True),  # type: ignore
    )


class MovimentoPublic(SQLModel):
    id: uuid.UUID
    tipo: str
    amount_cents: int
    data: date
    categoria_id: uuid.UUID
    note: str | None = None
    created_at: datetime | None = None


# Append-only audit of re-baselining events (old value, new value, when, whose)
class RebaselineAudit(SQLModel, table=True):
    __tablename__ = "rebaseline_audit"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    utente_id: uuid.UUID = Field(foreign_key="utenti.id", nullable=False, index=True)
    old_value_cents: int = Field(sa_type=BigInteger)
    new_value_cents: int = Field(sa_type=BigInteger)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
