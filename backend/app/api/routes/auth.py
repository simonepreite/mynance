"""mynance auth: self-service registration + one-time recovery code (FR-1/FR-3).

Errors surface as application/problem+json (see app.core.problem). Messages are
plain Italian and never reveal whether an account exists.
"""

from fastapi import APIRouter, HTTPException

from app import crud_utente
from app.api.deps import SessionDep
from app.models import (
    Message,
    UtentePublic,
    UtenteRecover,
    UtenteRegister,
    UtenteRegisterResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=201)
def register(body: UtenteRegister, session: SessionDep) -> UtenteRegisterResponse:
    """Create an Utente and return the one-time recovery code (shown once)."""
    existing = crud_utente.get_utente_by_username(
        session=session, username=body.username
    )
    if existing is not None:
        raise HTTPException(
            status_code=409,
            detail="Questo username è già in uso. Scegline un altro.",
        )
    utente, recovery_code = crud_utente.create_utente(
        session=session, username=body.username, password=body.password
    )
    return UtenteRegisterResponse(
        utente=UtentePublic(
            id=utente.id,
            username=utente.username,
            session_timeout_days=utente.session_timeout_days,
            created_at=utente.created_at,
        ),
        recovery_code=recovery_code,
    )


@router.post("/recover")
def recover(body: UtenteRecover, session: SessionDep) -> Message:
    """Regain access with username + recovery code, setting a new password."""
    utente = crud_utente.recover_utente(
        session=session,
        username=body.username,
        recovery_code=body.recovery_code,
        new_password=body.new_password,
    )
    if utente is None:
        # Single non-revealing message for wrong username OR wrong code.
        raise HTTPException(
            status_code=400,
            detail="Username o codice di recupero non validi.",
        )
    return Message(
        message="Password aggiornata. Ora puoi accedere con la nuova password."
    )
