"""Derived Liquidità read endpoint (Story 2.4, FR-13/FR-4)."""

import uuid

from fastapi.testclient import TestClient

from app.core.config import settings

PW = "una-password-robusta"
READ = f"{settings.API_V1_STR}/liquidita/"
INIZIALE = f"{settings.API_V1_STR}/liquidita/iniziale"


def _auth(client: TestClient) -> dict[str, str]:
    username = f"liqr_{uuid.uuid4().hex[:12]}"
    client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={"username": username, "password": PW},
    )
    token = client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"username": username, "password": PW},
    ).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_unset_baseline_returns_zero_deterministically(client: TestClient) -> None:
    headers = _auth(client)
    r = client.get(READ, headers=headers)
    assert r.status_code == 200
    body = r.json()
    assert body["value_cents"] == 0
    assert body["iniziale_is_set"] is False


def test_reflects_set_baseline(client: TestClient) -> None:
    headers = _auth(client)
    client.put(INIZIALE, headers=headers, json={"value_cents": 100000})
    r = client.get(READ, headers=headers)
    assert r.status_code == 200
    body = r.json()
    # No Movimenti yet → Liquidità equals the baseline.
    assert body["value_cents"] == 100000
    assert body["iniziale_is_set"] is True


def test_unauthenticated_is_401(client: TestClient) -> None:
    assert client.get(READ).status_code == 401


def test_isolation_never_returns_another_utentes_liquidita(
    client: TestClient,
) -> None:
    headers_a = _auth(client)
    headers_b = _auth(client)
    client.put(INIZIALE, headers=headers_a, json={"value_cents": 999999})

    # B sees only its own derived value (unset → 0), never A's baseline.
    b = client.get(READ, headers=headers_b).json()
    assert b["value_cents"] == 0
    assert b["iniziale_is_set"] is False
