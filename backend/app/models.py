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
    # Reconciliation cadence in days (Story 4.1, FR-16); default weekly.
    intervallo_riconciliazione_giorni: int = Field(default=7)
    mesi_cuscinetto: int = Field(default=6)
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
    parent_id: uuid.UUID | None = None


class CategoriaUpdate(SQLModel):
    # tipo is fixed; a rename and/or the Secchiello link may change (Story 3.1).
    nome: str | None = Field(default=None, min_length=1, max_length=255)
    # Categoria→Secchiello link (Spesa-type only): null clears it.
    secchiello_id: uuid.UUID | None = None


class Categoria(SQLModel, table=True):
    __tablename__ = "categorie"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    utente_id: uuid.UUID = Field(foreign_key="utenti.id", nullable=False, index=True)
    nome: str = Field(max_length=255)
    tipo: str = Field(max_length=16, index=True)  # "spesa" | "entrata"
    # Optional default Secchiello for Spese in this Categoria (Story 3.1, FR-7).
    secchiello_id: uuid.UUID | None = Field(
        default=None, foreign_key="secchielli.id", nullable=True
    )
    parent_id: uuid.UUID | None = Field(
        default=None, foreign_key="categorie.id", nullable=True, index=True
    )
    # System "non identificato" Categorie (Story 4.1) — cannot be renamed/deleted.
    is_system: bool = Field(default=False)
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
    secchiello_id: uuid.UUID | None = None
    parent_id: uuid.UUID | None = None
    is_system: bool = False
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


# Allocation + safety buffer (Stories 3.5/3.6, FR-14/FR-15) — all integer cents.
class AllocazionePublic(SQLModel):
    liquidita_cents: int
    liquidita_allocata_cents: int
    risparmio_libero_cents: int
    spesa_media_mensile_cents: int
    mesi_cuscinetto: int
    cuscinetto_cents: int
    sotto_cuscinetto: bool


class CuscinettoMesi(SQLModel):
    mesi_cuscinetto: int = Field(ge=1)


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
    # Per-Spesa Secchiello link (Story 3.1). If omitted, it defaults from the
    # Categoria's linked Secchiello; pass null to force "no Secchiello".
    secchiello_id: uuid.UUID | None = None


class MovimentoUpdate(SQLModel):
    # tipo is immutable (a Spesa never becomes an Entrata); only these change.
    amount_cents: int | None = Field(default=None, gt=0)
    data: date | None = None
    categoria_id: uuid.UUID | None = None
    note: str | None = Field(default=None, max_length=255)
    secchiello_id: uuid.UUID | None = None


class Movimento(SQLModel, table=True):
    __tablename__ = "movimenti"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    utente_id: uuid.UUID = Field(foreign_key="utenti.id", nullable=False, index=True)
    tipo: str = Field(max_length=16, index=True)  # "spesa" | "entrata"
    amount_cents: int = Field(sa_type=BigInteger)
    data: date
    categoria_id: uuid.UUID = Field(foreign_key="categorie.id", nullable=False)
    secchiello_id: uuid.UUID | None = Field(
        default=None, foreign_key="secchielli.id", nullable=True
    )
    # Back-reference to the originating Regola ricorrente (Epic 6), if generated.
    regola_id: uuid.UUID | None = Field(
        default=None, foreign_key="regole_ricorrenti.id", nullable=True
    )
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
    secchiello_id: uuid.UUID | None = None
    note: str | None = None
    created_at: datetime | None = None


# ---------------------------------------------------------------------------
# mynance — Period aggregation (Story 2.8 Home "Mese", Story 2.9 Statistiche).
# All monetary aggregates are integer cents, computed server-side (API-3).
# ---------------------------------------------------------------------------


class CategoriaSpesa(SQLModel):
    categoria_id: uuid.UUID
    nome: str
    total_cents: int
    sottocategorie: list["CategoriaSpesa"] | None = None


class BilancioPeriodo(SQLModel):
    period: str
    start: date
    end: date
    netto_cents: int
    entrate_cents: int
    spese_cents: int
    # Spese grouped by Categoria, sorted largest → smallest (decision #14).
    spese_per_categoria: list[CategoriaSpesa]


class TrendPunto(SQLModel):
    mese: str  # "YYYY-MM"
    entrate_cents: int
    spese_cents: int
    netto_cents: int


class Statistiche(SQLModel):
    period: str
    start: date
    end: date
    trend: list[TrendPunto]  # month-over-month
    pie: list[CategoriaSpesa]  # selected period's Spese share by Categoria
    has_trend: bool  # enough history (≥2 months with data) to chart a trend
    has_pie: bool  # the selected period has Spese


# ---------------------------------------------------------------------------
# mynance — Secchiello (FR-9/10/11). A predictive amortization bucket: set aside
# money in advance for a known recurring expense. Quota and Saldo are derived
# on read (Stories 3.2/3.3); only the inputs below are stored.
# ---------------------------------------------------------------------------


class Periodicita(str, enum.Enum):
    monthly = "monthly"
    quarterly = "quarterly"
    semiannual = "semiannual"
    annual = "annual"
    custom = "custom"


def periodicita_mesi(periodicita: str, intervallo_mesi: int | None) -> int:
    """Interval length in months for a Periodicità."""
    fixed = {"monthly": 1, "quarterly": 3, "semiannual": 6, "annual": 12}
    if periodicita in fixed:
        return fixed[periodicita]
    if periodicita == "custom" and intervallo_mesi is not None:
        return intervallo_mesi
    raise ValueError("custom periodicità requires a positive integer interval")


class SecchielloBase(SQLModel):
    nome: str = Field(min_length=1, max_length=255)
    importo_previsto_cents: int = Field(gt=0)
    periodicita: Periodicita
    intervallo_mesi: int | None = Field(default=None, ge=1)
    prossima_scadenza: date


class SecchielloCreate(SecchielloBase):
    pass


class SecchielloUpdate(SQLModel):
    nome: str | None = Field(default=None, min_length=1, max_length=255)
    importo_previsto_cents: int | None = Field(default=None, gt=0)
    periodicita: Periodicita | None = None
    intervallo_mesi: int | None = Field(default=None, ge=1)
    prossima_scadenza: date | None = None


# Registering the actual payment for a Secchiello (Story 3.3 cycle advance):
# creates the linked Spesa and advances the cycle.
class SecchielloPagamento(SQLModel):
    amount_cents: int = Field(gt=0)
    data: date
    categoria_id: uuid.UUID


class Secchiello(SQLModel, table=True):
    __tablename__ = "secchielli"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    utente_id: uuid.UUID = Field(foreign_key="utenti.id", nullable=False, index=True)
    nome: str = Field(max_length=255)
    importo_previsto_cents: int = Field(sa_type=BigInteger)
    periodicita: str = Field(max_length=16)
    intervallo_mesi: int | None = Field(default=None)
    prossima_scadenza: date
    data_inizio: date  # when accumulation started (chronological replay anchor)
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


# Public projection — Quota & Saldo are derived-on-read (read-only, Story 3.2).
class SecchielloPublic(SQLModel):
    id: uuid.UUID
    nome: str
    importo_previsto_cents: int
    periodicita: str
    intervallo_mesi: int | None
    prossima_scadenza: date
    data_inizio: date
    saldo_cents: int
    quota_cents: int
    created_at: datetime | None = None


# ---------------------------------------------------------------------------
# mynance — Riconciliazione (FR-16/17/18, Epic 4). Honest, manual reconciliation
# of computed vs real Liquidità: the Drift, and two ways to resolve it.
# ---------------------------------------------------------------------------


class RiconciliazioneEsito(str, enum.Enum):
    chiusa = "chiusa"  # gap closed via a "non identificato" plug Movimento
    acknowledged_open = "acknowledged_open"  # confirmed but left open


class Riconciliazione(SQLModel, table=True):
    __tablename__ = "riconciliazioni"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    utente_id: uuid.UUID = Field(foreign_key="utenti.id", nullable=False, index=True)
    liquidita_reale_cents: int = Field(sa_type=BigInteger)
    liquidita_calcolata_cents: int = Field(sa_type=BigInteger)
    drift_cents: int = Field(sa_type=BigInteger)  # signed: reale − calcolata
    data_riconciliazione: date
    esito: str = Field(max_length=20)
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


class RiconciliazionePublic(SQLModel):
    id: uuid.UUID
    liquidita_reale_cents: int
    liquidita_calcolata_cents: int
    drift_cents: int
    drift_percent: float | None
    data_riconciliazione: date
    esito: str
    created_at: datetime | None = None


class DriftPreview(SQLModel):
    liquidita_calcolata_cents: int
    drift_cents: int
    drift_percent: float | None


class RiconciliazioneRealeInput(SQLModel):
    liquidita_reale_cents: int = Field(ge=0)


class RiconciliazioneCreate(SQLModel):
    liquidita_reale_cents: int = Field(ge=0)
    esito: RiconciliazioneEsito


class PromemoriaPublic(SQLModel):
    due: bool
    giorni_dall_ultima: int
    data_ultima_riconciliazione: date | None
    intervallo_giorni: int
    # Standing quiet indicator: the snapshot Drift of the latest acknowledged-open
    # Riconciliazione (null when none is open).
    drift_aperto_cents: int | None = None


class IntervalloUpdate(SQLModel):
    intervallo_riconciliazione_giorni: int = Field(ge=1)


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


# ---------------------------------------------------------------------------
# mynance — Patrimonio (Epic 5, FR-19/20/21/22). Net worth on the Utente's own
# valuation terms: Investimenti at Capitale versato (never market value), Beni
# immobili at price paid (static), Beni mobili with linear Svalutazione.
# All money integer cents; component values derived on read.
# ---------------------------------------------------------------------------


class InvestimentoCreate(SQLModel):
    nome: str = Field(min_length=1, max_length=255)


class InvestimentoUpdate(SQLModel):
    nome: str | None = Field(default=None, min_length=1, max_length=255)


class Investimento(SQLModel, table=True):
    __tablename__ = "investimenti"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    utente_id: uuid.UUID = Field(foreign_key="utenti.id", nullable=False, index=True)
    nome: str = Field(max_length=255)
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


class InvestimentoPublic(SQLModel):
    id: uuid.UUID
    nome: str
    # Derived: Σ Versamenti PAC (Capitale versato) — never market value.
    capitale_versato_cents: int
    created_at: datetime | None = None


class VersamentoPacCreate(SQLModel):
    importo_cents: int = Field(gt=0)
    data: date


class VersamentoPacUpdate(SQLModel):
    importo_cents: int | None = Field(default=None, gt=0)
    data: date | None = None


class VersamentoPac(SQLModel, table=True):
    __tablename__ = "versamenti_pac"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    utente_id: uuid.UUID = Field(foreign_key="utenti.id", nullable=False, index=True)
    investimento_id: uuid.UUID = Field(
        foreign_key="investimenti.id", nullable=False, index=True
    )
    importo_cents: int = Field(sa_type=BigInteger)
    data: date
    regola_id: uuid.UUID | None = Field(
        default=None, foreign_key="regole_ricorrenti.id", nullable=True
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


class VersamentoPacPublic(SQLModel):
    id: uuid.UUID
    investimento_id: uuid.UUID
    importo_cents: int
    data: date
    created_at: datetime | None = None


class BeneImmobileCreate(SQLModel):
    nome: str = Field(min_length=1, max_length=255)
    prezzo_cents: int = Field(gt=0)


class BeneImmobileUpdate(SQLModel):
    nome: str | None = Field(default=None, min_length=1, max_length=255)
    prezzo_cents: int | None = Field(default=None, gt=0)


class BeneImmobile(SQLModel, table=True):
    __tablename__ = "beni_immobili"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    utente_id: uuid.UUID = Field(foreign_key="utenti.id", nullable=False, index=True)
    nome: str = Field(max_length=255)
    prezzo_cents: int = Field(sa_type=BigInteger)
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


class BeneImmobilePublic(SQLModel):
    id: uuid.UUID
    nome: str
    prezzo_cents: int  # Valore = price paid (static)
    created_at: datetime | None = None


class BeneMobileCreate(SQLModel):
    nome: str = Field(min_length=1, max_length=255)
    prezzo_cents: int = Field(gt=0)
    data_acquisto: date
    svalutazione_percentuale: float = Field(ge=0, le=100)


class BeneMobileUpdate(SQLModel):
    nome: str | None = Field(default=None, min_length=1, max_length=255)
    prezzo_cents: int | None = Field(default=None, gt=0)
    data_acquisto: date | None = None
    svalutazione_percentuale: float | None = Field(default=None, ge=0, le=100)


class BeneMobile(SQLModel, table=True):
    __tablename__ = "beni_mobili"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    utente_id: uuid.UUID = Field(foreign_key="utenti.id", nullable=False, index=True)
    nome: str = Field(max_length=255)
    prezzo_cents: int = Field(sa_type=BigInteger)
    data_acquisto: date
    svalutazione_percentuale: float
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


class BeneMobilePublic(SQLModel):
    id: uuid.UUID
    nome: str
    prezzo_cents: int
    data_acquisto: date
    svalutazione_percentuale: float
    valore_cents: int  # derived linear depreciation, floored at 0
    created_at: datetime | None = None


class PatrimonioComponente(SQLModel):
    chiave: str  # "liquidita" | "investimenti" | "beni_immobili" | "beni_mobili"
    valore_cents: int


class PatrimonioPublic(SQLModel):
    totale_cents: int
    liquidita_cents: int
    capitale_versato_cents: int
    beni_immobili_cents: int
    beni_mobili_cents: int
    componenti: list[PatrimonioComponente]


# ---------------------------------------------------------------------------
# mynance — Regole ricorrenti (Epic 6, FR-8). Describe recurring money; the
# generation engine materializes Entrate / Versamenti PAC up to today only,
# lazily and idempotently. Generated items carry a regola_id back-reference and
# are independently editable/skippable (skip recorded in regole_occorrenze).
# ---------------------------------------------------------------------------


class RegolaKind(str, enum.Enum):
    entrata = "entrata"
    versamento_pac = "versamento_pac"


class RegolaRicorrenteBase(SQLModel):
    importo_cents: int = Field(gt=0)
    periodicita: Periodicita
    intervallo_mesi: int | None = Field(default=None, ge=1)
    day_of_period: int = Field(ge=1, le=31)
    kind: RegolaKind
    categoria_id: uuid.UUID | None = None  # required when kind == entrata
    investimento_id: uuid.UUID | None = None  # required when kind == versamento_pac
    start_date: date
    note: str | None = Field(default=None, max_length=255)


class RegolaRicorrenteCreate(RegolaRicorrenteBase):
    pass


class RegolaRicorrenteUpdate(SQLModel):
    importo_cents: int | None = Field(default=None, gt=0)
    periodicita: Periodicita | None = None
    intervallo_mesi: int | None = Field(default=None, ge=1)
    day_of_period: int | None = Field(default=None, ge=1, le=31)
    note: str | None = Field(default=None, max_length=255)


class RegolaRicorrente(SQLModel, table=True):
    __tablename__ = "regole_ricorrenti"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    utente_id: uuid.UUID = Field(foreign_key="utenti.id", nullable=False, index=True)
    importo_cents: int = Field(sa_type=BigInteger)
    periodicita: str = Field(max_length=16)
    intervallo_mesi: int | None = Field(default=None)
    day_of_period: int
    kind: str = Field(max_length=20)
    categoria_id: uuid.UUID | None = Field(
        default=None, foreign_key="categorie.id", nullable=True
    )
    investimento_id: uuid.UUID | None = Field(
        default=None, foreign_key="investimenti.id", nullable=True
    )
    start_date: date
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


class RegolaRicorrentePublic(SQLModel):
    id: uuid.UUID
    importo_cents: int
    periodicita: str
    intervallo_mesi: int | None
    day_of_period: int
    kind: str
    categoria_id: uuid.UUID | None
    investimento_id: uuid.UUID | None
    start_date: date
    note: str | None = None
    created_at: datetime | None = None


# Ledger of materialized/skipped occurrences — the idempotency + skip memory.
class RegolaOccorrenza(SQLModel, table=True):
    __tablename__ = "regole_occorrenze"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    utente_id: uuid.UUID = Field(foreign_key="utenti.id", nullable=False, index=True)
    regola_id: uuid.UUID = Field(
        foreign_key="regole_ricorrenti.id", nullable=False, index=True
    )
    data: date
    skipped: bool = Field(default=False)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
