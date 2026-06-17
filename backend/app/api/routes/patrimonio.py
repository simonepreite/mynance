"""Patrimonio: Investimenti (Capitale versato), Beni immobili/mobili, net worth.

Epic 5 (FR-19/20/21/22). Investimenti are valued at Σ Versamenti PAC (never
market value); each Versamento PAC lowers derived Liquidità. Beni immobili are
static at price paid; Beni mobili depreciate linearly (floored at 0). Asset
registration never moves cash. All per-Utente scoped (FR-4), money integer cents.
"""

import uuid
from collections.abc import Sequence
from datetime import date
from typing import TypeVar

from fastapi import APIRouter, HTTPException
from sqlmodel import Session, SQLModel

from app import crud_liquidita, crud_ricorrenza
from app.api.deps import CurrentUtente, SessionDep
from app.calc.patrimonio import patrimonio_totale, valore_bene_mobile
from app.models import (
    BeneImmobile,
    BeneImmobileCreate,
    BeneImmobilePublic,
    BeneImmobileUpdate,
    BeneMobile,
    BeneMobileCreate,
    BeneMobilePublic,
    BeneMobileUpdate,
    Investimento,
    InvestimentoCreate,
    InvestimentoPublic,
    InvestimentoUpdate,
    Message,
    PatrimonioComponente,
    PatrimonioPublic,
    Utente,
    VersamentoPac,
    VersamentoPacCreate,
    VersamentoPacPublic,
    VersamentoPacUpdate,
    get_datetime_utc,
)
from app.services.repository import UserScopedRepository

router = APIRouter(tags=["patrimonio"])

ModelT = TypeVar("ModelT", bound=SQLModel)


def _repo(
    session: Session, current_utente: Utente, model: type[ModelT]
) -> UserScopedRepository[ModelT]:
    return UserScopedRepository(
        session=session, model=model, utente_id=current_utente.id
    )


def _drop_none(changes: dict[str, object], keys: tuple[str, ...]) -> None:
    for k in keys:
        if k in changes and changes[k] is None:
            changes.pop(k)


# --- Investimenti + Versamenti PAC (Story 5.1) ----------------------------


def _versamenti(
    session: SessionDep, current_utente: CurrentUtente
) -> Sequence[VersamentoPac]:
    return _repo(session, current_utente, VersamentoPac).list()


def _investimento_public(
    inv: Investimento, versamenti: Sequence[VersamentoPac]
) -> InvestimentoPublic:
    capitale = sum(v.importo_cents for v in versamenti if v.investimento_id == inv.id)
    return InvestimentoPublic(
        id=inv.id,
        nome=inv.nome,
        capitale_versato_cents=capitale,
        created_at=inv.created_at,
    )


@router.post("/investimenti", status_code=201)
def create_investimento(
    body: InvestimentoCreate, session: SessionDep, current_utente: CurrentUtente
) -> InvestimentoPublic:
    inv = _repo(session, current_utente, Investimento).add(
        Investimento(utente_id=current_utente.id, nome=body.nome)
    )
    return _investimento_public(inv, _versamenti(session, current_utente))


@router.get("/investimenti")
def list_investimenti(
    session: SessionDep, current_utente: CurrentUtente
) -> list[InvestimentoPublic]:
    versamenti = _versamenti(session, current_utente)
    invs = sorted(
        _repo(session, current_utente, Investimento).list(), key=lambda i: i.nome
    )
    return [_investimento_public(i, versamenti) for i in invs]


@router.patch("/investimenti/{investimento_id}")
def update_investimento(
    investimento_id: uuid.UUID,
    body: InvestimentoUpdate,
    session: SessionDep,
    current_utente: CurrentUtente,
) -> InvestimentoPublic:
    repo = _repo(session, current_utente, Investimento)
    if repo.get(investimento_id) is None:
        raise HTTPException(status_code=404, detail="Investimento non trovato.")
    changes = body.model_dump(exclude_unset=True)
    _drop_none(changes, ("nome",))
    changes["updated_at"] = get_datetime_utc()
    inv = repo.update(investimento_id, **changes)
    assert inv is not None
    return _investimento_public(inv, _versamenti(session, current_utente))


@router.delete("/investimenti/{investimento_id}")
def delete_investimento(
    investimento_id: uuid.UUID, session: SessionDep, current_utente: CurrentUtente
) -> Message:
    if not _repo(session, current_utente, Investimento).delete(investimento_id):
        raise HTTPException(status_code=404, detail="Investimento non trovato.")
    return Message(message="Investimento eliminato.")


def _require_investimento(
    session: SessionDep, current_utente: CurrentUtente, investimento_id: uuid.UUID
) -> None:
    if _repo(session, current_utente, Investimento).get(investimento_id) is None:
        raise HTTPException(status_code=404, detail="Investimento non trovato.")


def _versamento_public(v: VersamentoPac) -> VersamentoPacPublic:
    return VersamentoPacPublic(
        id=v.id,
        investimento_id=v.investimento_id,
        importo_cents=v.importo_cents,
        data=v.data,
        created_at=v.created_at,
    )


@router.post("/investimenti/{investimento_id}/versamenti", status_code=201)
def create_versamento(
    investimento_id: uuid.UUID,
    body: VersamentoPacCreate,
    session: SessionDep,
    current_utente: CurrentUtente,
) -> VersamentoPacPublic:
    _require_investimento(session, current_utente, investimento_id)
    v = _repo(session, current_utente, VersamentoPac).add(
        VersamentoPac(
            utente_id=current_utente.id,
            investimento_id=investimento_id,
            importo_cents=body.importo_cents,
            data=body.data,
        )
    )
    return _versamento_public(v)


@router.get("/investimenti/{investimento_id}/versamenti")
def list_versamenti(
    investimento_id: uuid.UUID, session: SessionDep, current_utente: CurrentUtente
) -> list[VersamentoPacPublic]:
    _require_investimento(session, current_utente, investimento_id)
    rows = [
        v
        for v in _repo(session, current_utente, VersamentoPac).list()
        if v.investimento_id == investimento_id
    ]
    rows.sort(key=lambda v: v.data, reverse=True)
    return [_versamento_public(v) for v in rows]


@router.patch("/versamenti/{versamento_id}")
def update_versamento(
    versamento_id: uuid.UUID,
    body: VersamentoPacUpdate,
    session: SessionDep,
    current_utente: CurrentUtente,
) -> VersamentoPacPublic:
    repo = _repo(session, current_utente, VersamentoPac)
    if repo.get(versamento_id) is None:
        raise HTTPException(status_code=404, detail="Versamento non trovato.")
    changes = body.model_dump(exclude_unset=True)
    _drop_none(changes, ("importo_cents", "data"))
    changes["updated_at"] = get_datetime_utc()
    v = repo.update(versamento_id, **changes)
    assert v is not None
    return _versamento_public(v)


@router.delete("/versamenti/{versamento_id}")
def delete_versamento(
    versamento_id: uuid.UUID, session: SessionDep, current_utente: CurrentUtente
) -> Message:
    repo = _repo(session, current_utente, VersamentoPac)
    v = repo.get(versamento_id)
    if v is None:
        raise HTTPException(status_code=404, detail="Versamento non trovato.")
    # A generated Versamento PAC: deleting it skips that occurrence (Story 6.4).
    if v.regola_id is not None:
        crud_ricorrenza.mark_skipped(
            session=session,
            utente=current_utente,
            regola_id=v.regola_id,
            data=v.data,
        )
    repo.delete(versamento_id)
    return Message(message="Versamento eliminato.")


# --- Beni immobili (Story 5.2) --------------------------------------------


def _immobile_public(b: BeneImmobile) -> BeneImmobilePublic:
    return BeneImmobilePublic(
        id=b.id, nome=b.nome, prezzo_cents=b.prezzo_cents, created_at=b.created_at
    )


@router.post("/beni-immobili", status_code=201)
def create_immobile(
    body: BeneImmobileCreate, session: SessionDep, current_utente: CurrentUtente
) -> BeneImmobilePublic:
    b = _repo(session, current_utente, BeneImmobile).add(
        BeneImmobile(
            utente_id=current_utente.id, nome=body.nome, prezzo_cents=body.prezzo_cents
        )
    )
    return _immobile_public(b)


@router.get("/beni-immobili")
def list_immobili(
    session: SessionDep, current_utente: CurrentUtente
) -> list[BeneImmobilePublic]:
    rows = sorted(
        _repo(session, current_utente, BeneImmobile).list(), key=lambda b: b.nome
    )
    return [_immobile_public(b) for b in rows]


@router.patch("/beni-immobili/{bene_id}")
def update_immobile(
    bene_id: uuid.UUID,
    body: BeneImmobileUpdate,
    session: SessionDep,
    current_utente: CurrentUtente,
) -> BeneImmobilePublic:
    repo = _repo(session, current_utente, BeneImmobile)
    if repo.get(bene_id) is None:
        raise HTTPException(status_code=404, detail="Bene immobile non trovato.")
    changes = body.model_dump(exclude_unset=True)
    _drop_none(changes, ("nome", "prezzo_cents"))
    changes["updated_at"] = get_datetime_utc()
    b = repo.update(bene_id, **changes)
    assert b is not None
    return _immobile_public(b)


@router.delete("/beni-immobili/{bene_id}")
def delete_immobile(
    bene_id: uuid.UUID, session: SessionDep, current_utente: CurrentUtente
) -> Message:
    if not _repo(session, current_utente, BeneImmobile).delete(bene_id):
        raise HTTPException(status_code=404, detail="Bene immobile non trovato.")
    return Message(message="Bene immobile eliminato.")


# --- Beni mobili (Story 5.3) ----------------------------------------------


def _mobile_public(b: BeneMobile, today: date) -> BeneMobilePublic:
    return BeneMobilePublic(
        id=b.id,
        nome=b.nome,
        prezzo_cents=b.prezzo_cents,
        data_acquisto=b.data_acquisto,
        svalutazione_percentuale=b.svalutazione_percentuale,
        valore_cents=valore_bene_mobile(
            prezzo_cents=b.prezzo_cents,
            svalutazione_percentuale=b.svalutazione_percentuale,
            data_acquisto=b.data_acquisto,
            today=today,
        ),
        created_at=b.created_at,
    )


@router.post("/beni-mobili", status_code=201)
def create_mobile(
    body: BeneMobileCreate, session: SessionDep, current_utente: CurrentUtente
) -> BeneMobilePublic:
    b = _repo(session, current_utente, BeneMobile).add(
        BeneMobile(
            utente_id=current_utente.id,
            nome=body.nome,
            prezzo_cents=body.prezzo_cents,
            data_acquisto=body.data_acquisto,
            svalutazione_percentuale=body.svalutazione_percentuale,
        )
    )
    return _mobile_public(b, date.today())


@router.get("/beni-mobili")
def list_mobili(
    session: SessionDep, current_utente: CurrentUtente
) -> list[BeneMobilePublic]:
    today = date.today()
    rows = sorted(
        _repo(session, current_utente, BeneMobile).list(), key=lambda b: b.nome
    )
    return [_mobile_public(b, today) for b in rows]


@router.patch("/beni-mobili/{bene_id}")
def update_mobile(
    bene_id: uuid.UUID,
    body: BeneMobileUpdate,
    session: SessionDep,
    current_utente: CurrentUtente,
) -> BeneMobilePublic:
    repo = _repo(session, current_utente, BeneMobile)
    if repo.get(bene_id) is None:
        raise HTTPException(status_code=404, detail="Bene mobile non trovato.")
    changes = body.model_dump(exclude_unset=True)
    _drop_none(
        changes, ("nome", "prezzo_cents", "data_acquisto", "svalutazione_percentuale")
    )
    changes["updated_at"] = get_datetime_utc()
    b = repo.update(bene_id, **changes)
    assert b is not None
    return _mobile_public(b, date.today())


@router.delete("/beni-mobili/{bene_id}")
def delete_mobile(
    bene_id: uuid.UUID, session: SessionDep, current_utente: CurrentUtente
) -> Message:
    if not _repo(session, current_utente, BeneMobile).delete(bene_id):
        raise HTTPException(status_code=404, detail="Bene mobile non trovato.")
    return Message(message="Bene mobile eliminato.")


# --- Patrimonio total (Story 5.4) -----------------------------------------


@router.get("/patrimonio")
def patrimonio(session: SessionDep, current_utente: CurrentUtente) -> PatrimonioPublic:
    today = date.today()
    liquidita = crud_liquidita.compute_current_liquidita(
        session=session, utente=current_utente
    )
    capitale = sum(v.importo_cents for v in _versamenti(session, current_utente))
    immobili = sum(
        b.prezzo_cents for b in _repo(session, current_utente, BeneImmobile).list()
    )
    mobili = sum(
        valore_bene_mobile(
            prezzo_cents=b.prezzo_cents,
            svalutazione_percentuale=b.svalutazione_percentuale,
            data_acquisto=b.data_acquisto,
            today=today,
        )
        for b in _repo(session, current_utente, BeneMobile).list()
    )
    totale = patrimonio_totale(
        liquidita_cents=liquidita,
        capitale_versato_cents=capitale,
        beni_immobili_cents=immobili,
        beni_mobili_cents=mobili,
    )
    return PatrimonioPublic(
        totale_cents=totale,
        liquidita_cents=liquidita,
        capitale_versato_cents=capitale,
        beni_immobili_cents=immobili,
        beni_mobili_cents=mobili,
        componenti=[
            PatrimonioComponente(chiave="liquidita", valore_cents=liquidita),
            PatrimonioComponente(chiave="investimenti", valore_cents=capitale),
            PatrimonioComponente(chiave="beni_immobili", valore_cents=immobili),
            PatrimonioComponente(chiave="beni_mobili", valore_cents=mobili),
        ],
    )
