"""Secchielli CRUD (Stories 3.1/3.2/3.3, FR-9/10/11), per-Utente scoped.

Quota and Saldo are never stored — they are derived on read by the pure engine
(``app.calc.secchiello``) from the stored inputs and the linked Spese. Every
access goes through the ``UserScopedRepository`` (authZ choke point): another
Utente's Secchiello is indistinguishable from a missing one (404).
"""

import uuid
from collections.abc import Sequence
from datetime import date

from fastapi import APIRouter, HTTPException

from app.api.deps import CurrentUtente, SessionDep
from app.calc.secchiello import compute_saldo_quota
from app.models import (
    CategoriaTipo,
    Message,
    Movimento,
    Periodicita,
    Secchiello,
    SecchielloCreate,
    SecchielloPublic,
    SecchielloUpdate,
    get_datetime_utc,
)
from app.services.repository import UserScopedRepository

router = APIRouter(prefix="/secchielli", tags=["secchielli"])


def _repo(
    session: SessionDep, current_utente: CurrentUtente
) -> UserScopedRepository[Secchiello]:
    return UserScopedRepository(
        session=session, model=Secchiello, utente_id=current_utente.id
    )


def _movimenti(
    session: SessionDep, current_utente: CurrentUtente
) -> Sequence[Movimento]:
    return UserScopedRepository(
        session=session, model=Movimento, utente_id=current_utente.id
    ).list()


def _linked_spese(
    movimenti: Sequence[Movimento], secchiello_id: uuid.UUID
) -> list[tuple[date, int]]:
    return [
        (m.data, m.amount_cents)
        for m in movimenti
        if m.secchiello_id == secchiello_id and m.tipo == CategoriaTipo.spesa.value
    ]


def _public(
    s: Secchiello, movimenti: Sequence[Movimento], today: date
) -> SecchielloPublic:
    saldo, quota = compute_saldo_quota(
        data_inizio=s.data_inizio,
        importo_previsto_cents=s.importo_previsto_cents,
        prossima_scadenza=s.prossima_scadenza,
        spese=_linked_spese(movimenti, s.id),
        today=today,
    )
    return SecchielloPublic(
        id=s.id,
        nome=s.nome,
        importo_previsto_cents=s.importo_previsto_cents,
        periodicita=s.periodicita,
        intervallo_mesi=s.intervallo_mesi,
        prossima_scadenza=s.prossima_scadenza,
        data_inizio=s.data_inizio,
        saldo_cents=saldo,
        quota_cents=quota,
        created_at=s.created_at,
    )


def _resolve_intervallo(periodicita: Periodicita, intervallo: int | None) -> int | None:
    """Custom needs a positive interval; named periodicità ignore it (→ None)."""
    if periodicita == Periodicita.custom:
        if intervallo is None:
            raise HTTPException(
                status_code=422,
                detail="La periodicità 'custom' richiede un intervallo in mesi (≥ 1).",
            )
        return intervallo
    return None


@router.post("/", status_code=201)
def create_secchiello(
    body: SecchielloCreate, session: SessionDep, current_utente: CurrentUtente
) -> SecchielloPublic:
    intervallo = _resolve_intervallo(body.periodicita, body.intervallo_mesi)
    today = date.today()
    repo = _repo(session, current_utente)
    secchiello = repo.add(
        Secchiello(
            utente_id=current_utente.id,
            nome=body.nome,
            importo_previsto_cents=body.importo_previsto_cents,
            periodicita=body.periodicita.value,
            intervallo_mesi=intervallo,
            prossima_scadenza=body.prossima_scadenza,
            data_inizio=today,
        )
    )
    return _public(secchiello, _movimenti(session, current_utente), today)


@router.get("/")
def list_secchielli(
    session: SessionDep, current_utente: CurrentUtente
) -> list[SecchielloPublic]:
    today = date.today()
    movimenti = _movimenti(session, current_utente)
    secchielli = sorted(_repo(session, current_utente).list(), key=lambda s: s.nome)
    return [_public(s, movimenti, today) for s in secchielli]


@router.get("/{secchiello_id}")
def get_secchiello(
    secchiello_id: uuid.UUID, session: SessionDep, current_utente: CurrentUtente
) -> SecchielloPublic:
    s = _repo(session, current_utente).get(secchiello_id)
    if s is None:
        raise HTTPException(status_code=404, detail="Secchiello non trovato.")
    return _public(s, _movimenti(session, current_utente), date.today())


@router.patch("/{secchiello_id}")
def update_secchiello(
    secchiello_id: uuid.UUID,
    body: SecchielloUpdate,
    session: SessionDep,
    current_utente: CurrentUtente,
) -> SecchielloPublic:
    repo = _repo(session, current_utente)
    s = repo.get(secchiello_id)
    if s is None:
        raise HTTPException(status_code=404, detail="Secchiello non trovato.")

    changes = body.model_dump(exclude_unset=True)
    if "periodicita" in changes and changes["periodicita"] is not None:
        per = changes["periodicita"]
        per_enum = per if isinstance(per, Periodicita) else Periodicita(per)
        intervallo = changes.get("intervallo_mesi", s.intervallo_mesi)
        changes["periodicita"] = per_enum.value
        changes["intervallo_mesi"] = _resolve_intervallo(per_enum, intervallo)
    for key in ("nome", "importo_previsto_cents", "prossima_scadenza", "periodicita"):
        if key in changes and changes[key] is None:
            changes.pop(key)
    changes["updated_at"] = get_datetime_utc()

    updated = repo.update(secchiello_id, **changes)
    if updated is None:  # pragma: no cover - just fetched above
        raise HTTPException(status_code=404, detail="Secchiello non trovato.")
    return _public(updated, _movimenti(session, current_utente), date.today())


@router.delete("/{secchiello_id}")
def delete_secchiello(
    secchiello_id: uuid.UUID, session: SessionDep, current_utente: CurrentUtente
) -> Message:
    if not _repo(session, current_utente).delete(secchiello_id):
        raise HTTPException(status_code=404, detail="Secchiello non trovato.")
    return Message(message="Secchiello eliminato.")
