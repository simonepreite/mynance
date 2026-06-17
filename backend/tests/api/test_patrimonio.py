"""Patrimonio: Investimenti/PAC, Beni, net worth, reallocation offset (Epic 5)."""

import uuid

from fastapi.testclient import TestClient

from app.core.config import settings

PW = "una-password-robusta"
PROBLEM_JSON = "application/problem+json"
INV = f"{settings.API_V1_STR}/investimenti"
IMMOBILI = f"{settings.API_V1_STR}/beni-immobili"
MOBILI = f"{settings.API_V1_STR}/beni-mobili"
PAT = f"{settings.API_V1_STR}/patrimonio"
INIZIALE = f"{settings.API_V1_STR}/liquidita/iniziale"
LIQ = f"{settings.API_V1_STR}/liquidita/"


def _auth(client: TestClient) -> dict[str, str]:
    username = f"pat_{uuid.uuid4().hex[:12]}"
    client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={"username": username, "password": PW},
    )
    token = client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"username": username, "password": PW},
    ).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_versamento_pac_increases_capitale_and_lowers_liquidita(
    client: TestClient,
) -> None:
    headers = _auth(client)
    client.put(INIZIALE, headers=headers, json={"value_cents": 100000})
    inv = client.post(INV, headers=headers, json={"nome": "ETF World"}).json()
    assert inv["capitale_versato_cents"] == 0

    client.post(
        f"{INV}/{inv['id']}/versamenti",
        headers=headers,
        json={"importo_cents": 30000, "data": "2026-06-10"},
    )
    invs = client.get(INV, headers=headers).json()
    assert invs[0]["capitale_versato_cents"] == 30000
    # Liquidità falls by the Versamento (FR-19).
    assert client.get(LIQ, headers=headers).json()["value_cents"] == 70000


def test_versamento_non_positive_is_422(client: TestClient) -> None:
    headers = _auth(client)
    inv = client.post(INV, headers=headers, json={"nome": "X"}).json()
    r = client.post(
        f"{INV}/{inv['id']}/versamenti",
        headers=headers,
        json={"importo_cents": 0, "data": "2026-06-10"},
    )
    assert r.status_code == 422
    assert r.headers["content-type"].startswith(PROBLEM_JSON)


def test_no_market_value_field(client: TestClient) -> None:
    headers = _auth(client)
    inv = client.post(INV, headers=headers, json={"nome": "ETF"}).json()
    assert "market" not in str(inv).lower()
    assert "capitale_versato_cents" in inv


def test_bene_immobile_static_and_no_cash_deduction(client: TestClient) -> None:
    headers = _auth(client)
    client.put(INIZIALE, headers=headers, json={"value_cents": 100000})
    client.post(
        IMMOBILI, headers=headers, json={"nome": "Casa", "prezzo_cents": 20000000}
    )
    # Liquidità unchanged by registration (FR-22).
    assert client.get(LIQ, headers=headers).json()["value_cents"] == 100000
    p = client.get(PAT, headers=headers).json()
    assert p["beni_immobili_cents"] == 20000000


def test_bene_mobile_depreciates(client: TestClient) -> None:
    headers = _auth(client)
    b = client.post(
        MOBILI,
        headers=headers,
        json={
            "nome": "Auto",
            "prezzo_cents": 2000000,
            "data_acquisto": "2024-01-01",
            "svalutazione_percentuale": 20.0,
        },
    ).json()
    assert 0 <= b["valore_cents"] < 2000000  # depreciated below price


def test_patrimonio_total_and_reallocation_offset(client: TestClient) -> None:
    headers = _auth(client)
    client.put(INIZIALE, headers=headers, json={"value_cents": 100000})
    inv = client.post(INV, headers=headers, json={"nome": "ETF"}).json()
    client.post(
        f"{INV}/{inv['id']}/versamenti",
        headers=headers,
        json={"importo_cents": 30000, "data": "2026-06-10"},
    )
    p = client.get(PAT, headers=headers).json()
    # Reallocation: Liquidità −30000, Capitale +30000 → total unchanged (FR-22).
    assert p["liquidita_cents"] == 70000
    assert p["capitale_versato_cents"] == 30000
    assert p["totale_cents"] == 100000
    assert p["totale_cents"] == (
        p["liquidita_cents"]
        + p["capitale_versato_cents"]
        + p["beni_immobili_cents"]
        + p["beni_mobili_cents"]
    )


def test_isolation_and_auth(client: TestClient) -> None:
    headers_a = _auth(client)
    inv_a = client.post(INV, headers=headers_a, json={"nome": "A"}).json()["id"]
    headers_b = _auth(client)
    assert (
        client.patch(
            f"{INV}/{inv_a}", headers=headers_b, json={"nome": "x"}
        ).status_code
        == 404
    )
    assert client.delete(f"{INV}/{inv_a}", headers=headers_b).status_code == 404
    assert client.get(PAT).status_code == 401
