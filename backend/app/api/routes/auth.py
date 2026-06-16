"""mynance auth: registration, one-time recovery code, login/logout (FR-1/2/3).

Errors surface as application/problem+json (see app.core.problem). Messages are
plain Italian and never reveal whether an account exists. Login and recovery are
rate-limited; logout revokes the session token (in-memory denylist).
"""

import uuid
from datetime import timedelta

import jwt
from fastapi import APIRouter, HTTPException, Request
from jwt.exceptions import InvalidTokenError

from app import crud_categoria, crud_utente
from app.api.deps import CurrentUtente, SessionDep, UtenteTokenDep
from app.core import security
from app.core.auth_state import revoke_token, too_many_attempts
from app.core.config import settings
from app.models import (
    Message,
    Token,
    Utente,
    UtenteLogin,
    UtentePublic,
    UtenteRecover,
    UtenteRegister,
    UtenteRegisterResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def _client_host(request: Request) -> str:
    return request.client.host if request.client else "unknown"


def _public(utente: Utente) -> UtentePublic:
    return UtentePublic(
        id=utente.id,
        username=utente.username,
        session_timeout_days=utente.session_timeout_days,
        created_at=utente.created_at,
    )


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
    # Provision the per-tipo starter Categorie for the new account (Story 2.1).
    crud_categoria.provision_starter_categorie(session=session, utente_id=utente.id)
    return UtenteRegisterResponse(utente=_public(utente), recovery_code=recovery_code)


@router.post("/login")
def login(body: UtenteLogin, request: Request, session: SessionDep) -> Token:
    """Authenticate and issue a JWT valid for the Utente's session window."""
    if too_many_attempts(f"login:{_client_host(request)}:{body.username}"):
        raise HTTPException(
            status_code=429,
            detail="Troppi tentativi di accesso. Riprova tra poco.",
        )
    utente = crud_utente.authenticate(
        session=session, username=body.username, password=body.password
    )
    if utente is None:
        raise HTTPException(status_code=400, detail="Username o password non validi.")
    jti = uuid.uuid4().hex
    expires = timedelta(days=utente.session_timeout_days)
    token = security.create_access_token(utente.id, expires_delta=expires, jti=jti)
    return Token(access_token=token)


@router.get("/me")
def read_me(current_utente: CurrentUtente) -> UtentePublic:
    """The authenticated Utente (protected — proves a valid session)."""
    return _public(current_utente)


@router.post("/logout")
def logout(token: UtenteTokenDep) -> Message:
    """End the session immediately by revoking the token (denylist)."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Sessione non valida.")
    jti = payload.get("jti")
    if jti:
        revoke_token(jti)
    return Message(message="Sessione terminata.")


@router.post("/recover")
def recover(body: UtenteRecover, request: Request, session: SessionDep) -> Message:
    """Regain access with username + recovery code, setting a new password."""
    if too_many_attempts(f"recover:{_client_host(request)}:{body.username}"):
        raise HTTPException(
            status_code=429,
            detail="Troppi tentativi di recupero. Riprova tra poco.",
        )
    utente = crud_utente.recover_utente(
        session=session,
        username=body.username,
        recovery_code=body.recovery_code,
        new_password=body.new_password,
    )
    if utente is None:
        raise HTTPException(
            status_code=400, detail="Username o codice di recupero non validi."
        )
    return Message(
        message="Password aggiornata. Ora puoi accedere con la nuova password."
    )
