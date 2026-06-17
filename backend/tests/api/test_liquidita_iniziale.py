"""Liquidità iniziale baseline + audited re-baselining (Story 2.2, FR-12/FR-4)."""

import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.config import settings
from app.models import RebaselineAudit

PW = "una-password-robusta"
PROBLEM_JSON = "application/problem+json"
BASE = f"{settings.API_V1_STR}/liquidita/iniziale"


def _register_and_auth(client: TestClient) -> tuple[dict[str, str], uuid.UUID]:
    username = f"liq_{uuid.uuid4().hex[:12]}"
    reg = client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={"username": username, "password": PW},
    ).json()
    token = client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"username": username, "password": PW},
    ).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}, uuid.UUID(reg["utente"]["id"])


def test_unset_on_new_account(client: TestClient) -> None:
    headers, _ = _register_and_auth(client)
    r = client.get(BASE, headers=headers)
    assert r.status_code == 200
    body = r.json()
    assert body["is_set"] is False
    assert body["value_cents"] is None


def test_set_when_unset_persists_without_audit(client: TestClient) -> None:
    headers, _ = _register_and_auth(client)
    r = client.put(BASE, headers=headers, json={"value_cents": 100000})
    assert r.status_code == 200
    body = r.json()
    assert body["value_cents"] == 100000
    assert body["is_set"] is True
    assert body["rebaselined"] is False

    got = client.get(BASE, headers=headers).json()
    assert got["value_cents"] == 100000
    assert got["is_set"] is True


def test_zero_is_permitted(client: TestClient) -> None:
    headers, _ = _register_and_auth(client)
    r = client.put(BASE, headers=headers, json={"value_cents": 0})
    assert r.status_code == 200
    assert client.get(BASE, headers=headers).json()["value_cents"] == 0


def test_negative_is_422(client: TestClient) -> None:
    headers, _ = _register_and_auth(client)
    r = client.put(BASE, headers=headers, json={"value_cents": -1})
    assert r.status_code == 422
    assert r.headers["content-type"].startswith(PROBLEM_JSON)


def test_non_integer_cents_is_422(client: TestClient) -> None:
    headers, _ = _register_and_auth(client)
    r = client.put(BASE, headers=headers, json={"value_cents": 100.5})
    assert r.status_code == 422
    assert r.headers["content-type"].startswith(PROBLEM_JSON)


def test_change_records_rebaseline_audit(client: TestClient, db: Session) -> None:
    headers, utente_id = _register_and_auth(client)
    client.put(BASE, headers=headers, json={"value_cents": 100000})

    r = client.put(BASE, headers=headers, json={"value_cents": 250000})
    assert r.status_code == 200
    assert r.json()["rebaselined"] is True
    assert client.get(BASE, headers=headers).json()["value_cents"] == 250000

    rows = db.exec(
        select(RebaselineAudit).where(RebaselineAudit.utente_id == utente_id)
    ).all()
    assert len(rows) == 1
    assert rows[0].old_value_cents == 100000
    assert rows[0].new_value_cents == 250000


def test_same_value_is_not_a_rebaseline(client: TestClient, db: Session) -> None:
    headers, utente_id = _register_and_auth(client)
    client.put(BASE, headers=headers, json={"value_cents": 5000})
    r = client.put(BASE, headers=headers, json={"value_cents": 5000})
    assert r.json()["rebaselined"] is False
    rows = db.exec(
        select(RebaselineAudit).where(RebaselineAudit.utente_id == utente_id)
    ).all()
    assert len(rows) == 0


def test_isolation_baseline_is_per_utente(client: TestClient) -> None:
    headers_a, _ = _register_and_auth(client)
    headers_b, _ = _register_and_auth(client)
    client.put(BASE, headers=headers_a, json={"value_cents": 999999})

    # B never sees A's baseline — B's own value stays unset.
    b = client.get(BASE, headers=headers_b).json()
    assert b["is_set"] is False
    assert b["value_cents"] is None


def test_unauthenticated_is_401(client: TestClient) -> None:
    assert client.get(BASE).status_code == 401
    assert client.put(BASE, json={"value_cents": 1000}).status_code == 401
