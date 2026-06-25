"""Allocation split + Cuscinetto endpoint (Stories 3.5/3.6, FR-14/FR-15/FR-4)."""

import uuid

from fastapi.testclient import TestClient

from app.core.config import settings
from tests.utils.utente import verify_in_db

PW = "una-password-robusta"
ALLOC = f"{settings.API_V1_STR}/liquidita/allocazione"
INIZIALE = f"{settings.API_V1_STR}/liquidita/iniziale"
SEC = f"{settings.API_V1_STR}/secchielli/"
CAT = f"{settings.API_V1_STR}/categorie/"
MOV = f"{settings.API_V1_STR}/movimenti/"
CUSC = f"{settings.API_V1_STR}/liquidita/cuscinetto-mesi"


def _auth(client: TestClient) -> dict[str, str]:
    username = f"alloc_{uuid.uuid4().hex[:12]}"
    client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={"username": username, "email": f"{username}@example.com", "password": PW},
    )
    verify_in_db(username)
    token = client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"username": username, "password": PW},
    ).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _spesa_cat(client: TestClient, headers: dict[str, str]) -> str:
    return client.get(CAT, headers=headers).json()["spesa"][0]["id"]


def test_empty_account_is_calm_zeroes(client: TestClient) -> None:
    headers = _auth(client)
    a = client.get(ALLOC, headers=headers).json()
    assert a["liquidita_cents"] == 0
    assert a["liquidita_allocata_cents"] == 0
    assert a["risparmio_libero_cents"] == 0
    assert a["spesa_media_mensile_cents"] == 0
    assert a["cuscinetto_cents"] == 0
    assert a["sotto_cuscinetto"] is False


def test_allocata_matches_positive_secchiello_saldo(client: TestClient) -> None:
    headers = _auth(client)
    client.put(INIZIALE, headers=headers, json={"value_cents": 500000})
    sid = client.post(
        SEC,
        headers=headers,
        json={
            "nome": "Bollo",
            "importo_previsto_cents": 30000,
            "periodicita": "annual",
            "prossima_scadenza": "2027-02-01",
        },
    ).json()["id"]

    saldo = next(s for s in client.get(SEC, headers=headers).json() if s["id"] == sid)[
        "saldo_cents"
    ]
    liquidita = client.get(f"{settings.API_V1_STR}/liquidita/", headers=headers).json()[
        "value_cents"
    ]

    a = client.get(ALLOC, headers=headers).json()
    assert a["liquidita_cents"] == liquidita
    assert a["liquidita_allocata_cents"] == max(0, saldo)
    assert a["risparmio_libero_cents"] == liquidita - max(0, saldo)


def test_cuscinetto_from_complete_months_and_below_flag(client: TestClient) -> None:
    headers = _auth(client)
    cat = _spesa_cat(client, headers)
    # Two complete prior months (current month excluded), 100000 each.
    for data in ("2026-04-10", "2026-05-12"):
        client.post(
            MOV,
            headers=headers,
            json={
                "tipo": "spesa",
                "amount_cents": 100000,
                "data": data,
                "categoria_id": cat,
            },
        )
    a = client.get(ALLOC, headers=headers, params={"mesi": 6}).json()
    assert a["spesa_media_mensile_cents"] == 100000  # mean over the 2 available
    assert a["cuscinetto_cents"] == 600000  # 6 × media
    # Liquidità is negative (only spese) → far below the buffer.
    assert a["sotto_cuscinetto"] is True


def test_isolation_and_auth(client: TestClient) -> None:
    headers_a = _auth(client)
    client.put(INIZIALE, headers=headers_a, json={"value_cents": 777000})
    headers_b = _auth(client)
    b = client.get(ALLOC, headers=headers_b).json()
    assert b["liquidita_cents"] == 0  # never sees A's liquidità
    assert client.get(ALLOC).status_code == 401


def test_cuscinetto_mesi_default_and_update(client: TestClient) -> None:
    headers = _auth(client)
    assert client.get(CUSC, headers=headers).json()["mesi_cuscinetto"] == 6
    ok = client.put(CUSC, headers=headers, json={"mesi_cuscinetto": 3})
    assert ok.status_code == 200 and ok.json()["mesi_cuscinetto"] == 3
    bad = client.put(CUSC, headers=headers, json={"mesi_cuscinetto": 0})
    assert bad.status_code == 422


def test_allocazione_uses_stored_mesi(client: TestClient) -> None:
    headers = _auth(client)
    cat = _spesa_cat(client, headers)
    for data in ("2026-04-10", "2026-05-12"):
        client.post(
            MOV,
            headers=headers,
            json={
                "tipo": "spesa",
                "amount_cents": 100000,
                "data": data,
                "categoria_id": cat,
            },
        )
    client.put(CUSC, headers=headers, json={"mesi_cuscinetto": 3})
    a = client.get(ALLOC, headers=headers).json()  # no mesi override
    assert a["mesi_cuscinetto"] == 3
    assert a["cuscinetto_cents"] == 300000  # 3 × media(100000)
