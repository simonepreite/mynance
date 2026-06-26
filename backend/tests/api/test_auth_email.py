"""mynance auth: email at registration, verification gate, password reset.

Tokens are single-use hashed DB rows; only the hash is stored, so the verify /
reset endpoint tests mint a raw token via ``crud_token.issue`` (the same seam
the email flow uses) and post it.
"""

import logging
import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app import crud_token
from app.core.config import settings
from app.core.db import engine
from app.models import (
    TOKEN_PURPOSE_EMAIL_VERIFY,
    TOKEN_PURPOSE_PASSWORD_RESET,
    UtenteToken,
)
from tests.utils.utente import PW, register, register_verified, verify_in_db

PROBLEM_JSON = "application/problem+json"
AUTH = f"{settings.API_V1_STR}/auth"


def _login(client: TestClient, identifier: str, password: str = PW):
    return client.post(
        f"{AUTH}/login", json={"username": identifier, "password": password}
    )


def _mint(uid: str, purpose: str, expires_hours: int = 24) -> str:
    with Session(engine) as s:
        return crud_token.issue(
            session=s,
            utente_id=uuid.UUID(uid),
            purpose=purpose,
            expires_hours=expires_hours,
        )


def _token_count(uid: str, purpose: str) -> int:
    with Session(engine) as s:
        rows = s.exec(
            select(UtenteToken).where(
                UtenteToken.utente_id == uuid.UUID(uid),
                UtenteToken.purpose == purpose,
            )
        ).all()
    return len(rows)


# --- registration -----------------------------------------------------------


def test_register_requires_email(client: TestClient) -> None:
    username = f"noemail_{uuid.uuid4().hex[:8]}"
    r = client.post(f"{AUTH}/register", json={"username": username, "password": PW})
    assert r.status_code == 422


def test_register_duplicate_email_is_conflict(client: TestClient) -> None:
    email = f"dup_{uuid.uuid4().hex[:8]}@example.com"
    _, _, first = register(client, email=email)
    assert first.status_code == 201
    _, _, second = register(client, email=email)
    assert second.status_code == 409
    assert second.headers["content-type"].startswith(PROBLEM_JSON)
    assert "email" in second.json()["detail"].lower()


def test_register_creates_unverified_account_with_verify_token(
    client: TestClient,
) -> None:
    _, _, r = register(client)
    assert r.status_code == 201
    body = r.json()
    assert body["utente"]["email_verified"] is False
    assert body["utente"]["email"]
    assert _token_count(body["utente"]["id"], TOKEN_PURPOSE_EMAIL_VERIFY) == 1


def test_register_logs_verification_link_in_dev(client: TestClient, caplog) -> None:
    with caplog.at_level(logging.INFO):
        register(client)
    assert "/verify-email?token=" in caplog.text


# --- login gate -------------------------------------------------------------


def test_login_blocked_until_verified(client: TestClient) -> None:
    username, _, r = register(client)
    assert r.status_code == 201
    blocked = _login(client, username)
    assert blocked.status_code == 403
    assert blocked.headers["content-type"].startswith(PROBLEM_JSON)
    assert "Verifica" in blocked.json()["detail"]


def test_login_succeeds_after_verification_by_username_and_email(
    client: TestClient,
) -> None:
    username, email, r = register(client)
    verify_in_db(username)
    by_username = _login(client, username)
    assert by_username.status_code == 200
    assert by_username.json()["access_token"]
    by_email = _login(client, email)
    assert by_email.status_code == 200
    assert by_email.json()["access_token"]


# --- verify-email -----------------------------------------------------------


def test_verify_email_with_valid_token_then_login(client: TestClient) -> None:
    username, _, r = register(client)
    token = _mint(r.json()["utente"]["id"], TOKEN_PURPOSE_EMAIL_VERIFY)
    ok = client.post(f"{AUTH}/verify-email", json={"token": token})
    assert ok.status_code == 200
    assert _login(client, username).status_code == 200


def test_verify_email_token_is_single_use(client: TestClient) -> None:
    _, _, r = register(client)
    token = _mint(r.json()["utente"]["id"], TOKEN_PURPOSE_EMAIL_VERIFY)
    assert client.post(f"{AUTH}/verify-email", json={"token": token}).status_code == 200
    reused = client.post(f"{AUTH}/verify-email", json={"token": token})
    assert reused.status_code == 400
    assert reused.headers["content-type"].startswith(PROBLEM_JSON)


def test_verify_email_expired_token_is_rejected(client: TestClient) -> None:
    _, _, r = register(client)
    token = _mint(
        r.json()["utente"]["id"], TOKEN_PURPOSE_EMAIL_VERIFY, expires_hours=-1
    )
    assert client.post(f"{AUTH}/verify-email", json={"token": token}).status_code == 400


def test_verify_email_rejects_wrong_purpose_token(client: TestClient) -> None:
    _, _, r = register(client)
    reset_token = _mint(r.json()["utente"]["id"], TOKEN_PURPOSE_PASSWORD_RESET)
    assert (
        client.post(f"{AUTH}/verify-email", json={"token": reset_token}).status_code
        == 400
    )


# --- resend-verification ----------------------------------------------------


def test_resend_verification_is_generic_and_invalidates_old_token(
    client: TestClient,
) -> None:
    username, _, r = register(client)
    uid = r.json()["utente"]["id"]
    old = _mint(uid, TOKEN_PURPOSE_EMAIL_VERIFY)

    resp = client.post(f"{AUTH}/resend-verification", json={"identifier": username})
    assert resp.status_code == 200
    assert "Se l'account" in resp.json()["message"]

    # The previously-minted token no longer works (a resend invalidates it).
    assert client.post(f"{AUTH}/verify-email", json={"token": old}).status_code == 400


def test_resend_for_unknown_account_is_generic_200(client: TestClient) -> None:
    resp = client.post(
        f"{AUTH}/resend-verification",
        json={"identifier": f"ghost_{uuid.uuid4().hex[:8]}"},
    )
    assert resp.status_code == 200


# --- forgot / reset password ------------------------------------------------


def test_forgot_password_is_generic_and_issues_reset_token(
    client: TestClient,
) -> None:
    username, email = register_verified(client)
    resp = client.post(f"{AUTH}/forgot-password", json={"email": email})
    assert resp.status_code == 200
    assert "Se l'email" in resp.json()["message"]
    with Session(engine) as s:
        from app import crud_utente

        u = crud_utente.get_utente_by_username(session=s, username=username)
        assert u is not None
        assert _token_count(str(u.id), TOKEN_PURPOSE_PASSWORD_RESET) == 1


def test_forgot_password_unknown_email_is_generic_200(client: TestClient) -> None:
    resp = client.post(
        f"{AUTH}/forgot-password",
        json={"email": f"ghost_{uuid.uuid4().hex[:8]}@example.com"},
    )
    assert resp.status_code == 200


def test_reset_password_with_valid_token_then_login_with_new_password(
    client: TestClient,
) -> None:
    username, _ = register_verified(client)
    with Session(engine) as s:
        from app import crud_utente

        uid = str(crud_utente.get_utente_by_username(session=s, username=username).id)
    token = _mint(uid, TOKEN_PURPOSE_PASSWORD_RESET, expires_hours=48)
    new_pw = "nuova-password-robusta"
    ok = client.post(
        f"{AUTH}/reset-password", json={"token": token, "new_password": new_pw}
    )
    assert ok.status_code == 200
    assert _login(client, username, password=new_pw).status_code == 200
    # Old password no longer works.
    assert _login(client, username, password=PW).status_code == 400


def test_reset_password_token_is_single_use(client: TestClient) -> None:
    username, _ = register_verified(client)
    with Session(engine) as s:
        from app import crud_utente

        uid = str(crud_utente.get_utente_by_username(session=s, username=username).id)
    token = _mint(uid, TOKEN_PURPOSE_PASSWORD_RESET, expires_hours=48)
    first = client.post(
        f"{AUTH}/reset-password",
        json={"token": token, "new_password": "pw-uno-robusta"},
    )
    assert first.status_code == 200
    reused = client.post(
        f"{AUTH}/reset-password",
        json={"token": token, "new_password": "pw-due-robusta"},
    )
    assert reused.status_code == 400
