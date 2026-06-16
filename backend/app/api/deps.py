import uuid
from collections.abc import Generator
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import Session

from app.core import security
from app.core.auth_state import is_token_revoked
from app.core.config import settings
from app.core.db import engine
from app.models import TokenPayload, User, Utente

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]


def get_current_user(session: SessionDep, token: TokenDep) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = session.get(User, token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_active_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user


# --- mynance Utente session (Story 1.4) -----------------------------------
reusable_oauth2_utente = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)
UtenteTokenDep = Annotated[str, Depends(reusable_oauth2_utente)]


def _decode_utente_token(token: str) -> TokenPayload:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(status_code=401, detail="Sessione non valida.")
    if data.jti is not None and is_token_revoked(data.jti):
        raise HTTPException(status_code=401, detail="Sessione terminata.")
    return data


def get_current_utente(session: SessionDep, token: UtenteTokenDep) -> Utente:
    data = _decode_utente_token(token)
    try:
        utente_id = uuid.UUID(str(data.sub))
    except (ValueError, TypeError):
        raise HTTPException(status_code=401, detail="Sessione non valida.")
    utente = session.get(Utente, utente_id)
    if utente is None or utente.deleted_at is not None:
        raise HTTPException(status_code=401, detail="Sessione non valida.")
    return utente


CurrentUtente = Annotated[Utente, Depends(get_current_utente)]
