"""mynance auth: registration + one-time recovery code (Story 1.3, FR-1/FR-3)."""

import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session

from app import crud_utente
from app.core.config import settings
from app.core.security import verify_password

PROBLEM_JSON = "application/problem+json"


def _unique_username() -> str:
    return f"mario_{uuid.uuid4().hex[:12]}"


def test_register_returns_one_time_recovery_code_and_stores_only_hashes(
    client: TestClient, db: Session
) -> None:
    username = _unique_username()
    password = "una-password-robusta"
    r = client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={"username": username, "password": password},
    )
    assert r.status_code == 201
    body = r.json()
    assert body["utente"]["username"] == username
    assert body["utente"]["session_timeout_days"] == 30
    assert "id" in body["utente"]
    recovery_code = body["recovery_code"]
    assert recovery_code and "-" in recovery_code

    # Neither secret is persisted in plaintext.
    utente = crud_utente.get_utente_by_username(session=db, username=username)
    assert utente is not None
    assert utente.password_hash != password
    assert utente.recovery_code_hash != recovery_code
    verified, _ = verify_password(password, utente.password_hash)
    assert verified


def test_register_duplicate_username_is_conflict_problem_json(
    client: TestClient,
) -> None:
    username = _unique_username()
    payload = {"username": username, "password": "una-password-robusta"}
    first = client.post(f"{settings.API_V1_STR}/auth/register", json=payload)
    assert first.status_code == 201
    second = client.post(f"{settings.API_V1_STR}/auth/register", json=payload)
    assert second.status_code == 409
    assert second.headers["content-type"].startswith(PROBLEM_JSON)
    assert "già in uso" in second.json()["detail"]


def test_recover_with_correct_code_sets_new_password(client: TestClient) -> None:
    username = _unique_username()
    reg = client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={"username": username, "password": "vecchia-password"},
    )
    recovery_code = reg.json()["recovery_code"]
    r = client.post(
        f"{settings.API_V1_STR}/auth/recover",
        json={
            "username": username,
            "recovery_code": recovery_code,
            "new_password": "nuova-password-robusta",
        },
    )
    assert r.status_code == 200
    assert "Password aggiornata" in r.json()["message"]


def test_recover_with_wrong_code_is_generic_problem_json(client: TestClient) -> None:
    username = _unique_username()
    client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={"username": username, "password": "una-password-robusta"},
    )
    r = client.post(
        f"{settings.API_V1_STR}/auth/recover",
        json={
            "username": username,
            "recovery_code": "WRON-GCOD-EWRO-NGCO",
            "new_password": "nuova-password-robusta",
        },
    )
    assert r.status_code == 400
    assert r.headers["content-type"].startswith(PROBLEM_JSON)
    assert r.json()["detail"] == "Username o codice di recupero non validi."


def test_recover_unknown_username_is_generic(client: TestClient) -> None:
    r = client.post(
        f"{settings.API_V1_STR}/auth/recover",
        json={
            "username": _unique_username(),
            "recovery_code": "ABCD-EFGH-JKLM-NPQR",
            "new_password": "nuova-password-robusta",
        },
    )
    assert r.status_code == 400
    # Same message as a wrong code — does not reveal whether the account exists.
    assert r.json()["detail"] == "Username o codice di recupero non validi."
