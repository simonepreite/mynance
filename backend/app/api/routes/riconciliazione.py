"""Riconciliazione: reminder, Drift, and honest resolution (Epic 4, FR-16/17/18).

The reminder is computed on read (``today − last Riconciliazione``, no scheduler).
The Drift (real − computed Liquidità) is computed server-side; the gap is closed
with a "non identificato" plug Movimento or acknowledged-and-left-open. All reads
are per-Utente scoped (FR-4).
"""

from collections.abc import Sequence
from datetime import date

from fastapi import APIRouter, HTTPException

from app import crud_categoria, crud_liquidita
from app.api.deps import CurrentUtente, SessionDep
from app.models import (
    CategoriaTipo,
    DriftPreview,
    IntervalloUpdate,
    Movimento,
    PromemoriaPublic,
    Riconciliazione,
    RiconciliazioneCreate,
    RiconciliazioneEsito,
    RiconciliazionePublic,
    RiconciliazioneRealeInput,
)
from app.services.repository import UserScopedRepository

router = APIRouter(prefix="/riconciliazione", tags=["riconciliazione"])


def _liquidita_calcolata(session: SessionDep, current_utente: CurrentUtente) -> int:
    return crud_liquidita.compute_current_liquidita(
        session=session, utente=current_utente
    )


def _drift_percent(reale: int, calcolata: int) -> float | None:
    if calcolata == 0:
        return None  # no divide-by-zero; € Drift is still shown
    return round((reale - calcolata) / calcolata * 100, 1)


def _to_public(r: Riconciliazione) -> RiconciliazionePublic:
    return RiconciliazionePublic(
        id=r.id,
        liquidita_reale_cents=r.liquidita_reale_cents,
        liquidita_calcolata_cents=r.liquidita_calcolata_cents,
        drift_cents=r.drift_cents,
        drift_percent=_drift_percent(
            r.liquidita_reale_cents, r.liquidita_calcolata_cents
        ),
        data_riconciliazione=r.data_riconciliazione,
        esito=r.esito,
        created_at=r.created_at,
    )


def _sorted_history(rows: Sequence[Riconciliazione]) -> list[Riconciliazione]:
    return sorted(
        rows,
        key=lambda r: (r.data_riconciliazione, r.created_at or r.data_riconciliazione),
        reverse=True,
    )


@router.get("/intervallo")
def get_intervallo(current_utente: CurrentUtente) -> IntervalloUpdate:
    return IntervalloUpdate(
        intervallo_riconciliazione_giorni=current_utente.intervallo_riconciliazione_giorni
    )


@router.put("/intervallo")
def set_intervallo(
    body: IntervalloUpdate, session: SessionDep, current_utente: CurrentUtente
) -> IntervalloUpdate:
    current_utente.intervallo_riconciliazione_giorni = (
        body.intervallo_riconciliazione_giorni
    )
    session.add(current_utente)
    session.commit()
    return IntervalloUpdate(
        intervallo_riconciliazione_giorni=current_utente.intervallo_riconciliazione_giorni
    )


@router.get("/promemoria")
def promemoria(session: SessionDep, current_utente: CurrentUtente) -> PromemoriaPublic:
    today = date.today()
    interval = current_utente.intervallo_riconciliazione_giorni
    rows = UserScopedRepository(
        session=session, model=Riconciliazione, utente_id=current_utente.id
    ).list()
    history = _sorted_history(rows)
    last = history[0] if history else None

    if last is not None:
        baseline = last.data_riconciliazione
        data_ultima: date | None = last.data_riconciliazione
    else:
        created = current_utente.created_at
        baseline = created.date() if created is not None else today
        data_ultima = None

    giorni = max(0, (today - baseline).days)
    drift_aperto = (
        last.drift_cents
        if last is not None
        and last.esito == RiconciliazioneEsito.acknowledged_open.value
        else None
    )
    # A never-reconciled account is honestly flagged as due (FR-16); otherwise
    # the interval gates it (SM-C2 over-prompting respected).
    return PromemoriaPublic(
        due=last is None or giorni >= interval,
        giorni_dall_ultima=giorni,
        data_ultima_riconciliazione=data_ultima,
        intervallo_giorni=interval,
        drift_aperto_cents=drift_aperto,
    )


@router.post("/anteprima")
def anteprima(
    body: RiconciliazioneRealeInput,
    session: SessionDep,
    current_utente: CurrentUtente,
) -> DriftPreview:
    calcolata = _liquidita_calcolata(session, current_utente)
    drift = body.liquidita_reale_cents - calcolata
    return DriftPreview(
        liquidita_calcolata_cents=calcolata,
        drift_cents=drift,
        drift_percent=_drift_percent(body.liquidita_reale_cents, calcolata),
    )


@router.post("/", status_code=201)
def confirm(
    body: RiconciliazioneCreate, session: SessionDep, current_utente: CurrentUtente
) -> RiconciliazionePublic:
    today = date.today()
    calcolata = _liquidita_calcolata(session, current_utente)
    drift = body.liquidita_reale_cents - calcolata

    if body.esito == RiconciliazioneEsito.chiusa and drift != 0:
        # Close the gap: a plug Movimento for |drift| on the matching system
        # "non identificato" Categoria. R>C → Entrata (real higher), R<C → Spesa.
        tipo = CategoriaTipo.entrata if drift > 0 else CategoriaTipo.spesa
        system_cat = crud_categoria.get_system_categoria(
            session=session, utente_id=current_utente.id, tipo=tipo
        )
        if system_cat is None:  # pragma: no cover - provisioned at registration
            raise HTTPException(
                status_code=500, detail="Categoria di sistema mancante."
            )
        UserScopedRepository(
            session=session, model=Movimento, utente_id=current_utente.id
        ).add(
            Movimento(
                utente_id=current_utente.id,
                tipo=tipo.value,
                amount_cents=abs(drift),
                data=today,
                categoria_id=system_cat.id,
                note="Riconciliazione — non identificato",
            )
        )

    repo = UserScopedRepository(
        session=session, model=Riconciliazione, utente_id=current_utente.id
    )
    riconc = repo.add(
        Riconciliazione(
            utente_id=current_utente.id,
            liquidita_reale_cents=body.liquidita_reale_cents,
            liquidita_calcolata_cents=calcolata,
            drift_cents=drift,
            data_riconciliazione=today,
            esito=body.esito.value,
        )
    )
    return _to_public(riconc)


@router.get("/")
def history(
    session: SessionDep, current_utente: CurrentUtente
) -> list[RiconciliazionePublic]:
    rows = UserScopedRepository(
        session=session, model=Riconciliazione, utente_id=current_utente.id
    ).list()
    return [_to_public(r) for r in _sorted_history(rows)]
