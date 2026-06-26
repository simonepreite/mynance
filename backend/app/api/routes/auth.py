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

from app import crud_categoria, crud_token, crud_utente, utils
from app.api.deps import CurrentUtente, SessionDep, UtenteTokenDep
from app.core import security
from app.core.auth_state import revoke_token, too_many_attempts
from app.core.config import settings
from app.models import (
    TOKEN_PURPOSE_EMAIL_VERIFY,
    TOKEN_PURPOSE_PASSWORD_RESET,
    EmailVerifyRequest,
    ForgotPasswordRequest,
    Message,
    ResendVerificationRequest,
    ResetPasswordRequest,
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
        email=utente.email,
        email_verified=utente.email_verified,
        session_timeout_days=utente.session_timeout_days,
        created_at=utente.created_at,
    )


def _send_verification(session: SessionDep, utente: Utente) -> None:
    """Issue an email-verify token and deliver (or log, in dev) the link."""
    assert utente.email is not None
    token = crud_token.issue(
        session=session,
        utente_id=utente.id,
        purpose=TOKEN_PURPOSE_EMAIL_VERIFY,
        expires_hours=settings.EMAIL_VERIFY_TOKEN_EXPIRE_HOURS,
    )
    utils.deliver_email(
        email_to=utente.email,
        email_data=utils.generate_verify_email(utente.email, utente.username, token),
        dev_link=utils.verify_email_link(token),
    )


@router.post("/register", status_code=201)
def register(body: UtenteRegister, session: SessionDep) -> UtenteRegisterResponse:
    """Create an unverified Utente, send a verification email, and return the
    one-time recovery code (shown once). No session is issued — the user must
    verify their email before logging in."""
    if crud_utente.get_utente_by_username(session=session, username=body.username):
        raise HTTPException(
            status_code=409,
            detail="Questo username è già in uso. Scegline un altro.",
        )
    if crud_utente.get_utente_by_email(session=session, email=body.email):
        raise HTTPException(
            status_code=409,
            detail="Questa email è già in uso. Usane un'altra o recupera l'accesso.",
        )
    utente, recovery_code = crud_utente.create_utente(
        session=session,
        username=body.username,
        password=body.password,
        email=body.email,
    )
    # Provision the per-tipo starter Categorie for the new account (Story 2.1)
    # and the system "non identificato" Categorie for reconciliation (Story 4.1).
    crud_categoria.provision_starter_categorie(session=session, utente_id=utente.id)
    crud_categoria.provision_system_categorie(session=session, utente_id=utente.id)
    _send_verification(session, utente)
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
    if not utente.email_verified:
        raise HTTPException(
            status_code=403,
            detail="Verifica la tua email per accedere. Ti abbiamo inviato un link.",
        )
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


@router.post("/verify-email")
def verify_email(body: EmailVerifyRequest, session: SessionDep) -> Message:
    """Confirm an email address by consuming a single-use verify token."""
    utente = crud_token.consume(
        session=session, token=body.token, purpose=TOKEN_PURPOSE_EMAIL_VERIFY
    )
    if utente is None:
        raise HTTPException(
            status_code=400,
            detail="Link di verifica non valido o scaduto. Richiedine uno nuovo.",
        )
    crud_utente.mark_email_verified(session=session, utente=utente)
    return Message(message="Email verificata. Ora puoi accedere.")


@router.post("/resend-verification")
def resend_verification(
    body: ResendVerificationRequest, request: Request, session: SessionDep
) -> Message:
    """Re-send the verification link. Generic response (no account enumeration)."""
    if too_many_attempts(f"resend:{_client_host(request)}:{body.identifier}"):
        raise HTTPException(
            status_code=429, detail="Troppe richieste. Riprova tra poco."
        )
    utente = crud_utente.get_utente_by_identifier(
        session=session, identifier=body.identifier
    )
    if utente is not None and not utente.email_verified and utente.email is not None:
        _send_verification(session, utente)
    return Message(
        message="Se l'account esiste e non è verificato, ti abbiamo inviato un link."
    )


@router.post("/forgot-password")
def forgot_password(
    body: ForgotPasswordRequest, request: Request, session: SessionDep
) -> Message:
    """Start an email password reset. Generic response (no account enumeration)."""
    if too_many_attempts(f"forgot:{_client_host(request)}:{body.email}"):
        raise HTTPException(
            status_code=429, detail="Troppe richieste. Riprova tra poco."
        )
    utente = crud_utente.get_utente_by_email(session=session, email=body.email)
    if utente is not None and utente.deleted_at is None:
        token = crud_token.issue(
            session=session,
            utente_id=utente.id,
            purpose=TOKEN_PURPOSE_PASSWORD_RESET,
            expires_hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS,
        )
        utils.deliver_email(
            email_to=body.email,
            email_data=utils.generate_reset_password_email(
                email_to=body.email, email=body.email, token=token
            ),
            dev_link=utils.reset_password_link(token),
        )
    return Message(
        message="Se l'email è associata a un account, ti abbiamo inviato un link."
    )


@router.post("/reset-password")
def reset_password(body: ResetPasswordRequest, session: SessionDep) -> Message:
    """Set a new password by consuming a single-use reset token."""
    utente = crud_token.consume(
        session=session, token=body.token, purpose=TOKEN_PURPOSE_PASSWORD_RESET
    )
    if utente is None:
        raise HTTPException(
            status_code=400,
            detail="Link di reset non valido o scaduto. Richiedine uno nuovo.",
        )
    crud_utente.set_password(
        session=session, utente=utente, new_password=body.new_password
    )
    return Message(
        message="Password aggiornata. Ora puoi accedere con la nuova password."
    )
