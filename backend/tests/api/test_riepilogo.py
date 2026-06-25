"""Period aggregation: Bilancio + Statistiche (Stories 2.8/2.9, FR-13/FR-4)."""

import uuid

from fastapi.testclient import TestClient

from app.core.config import settings
from tests.utils.utente import verify_in_db

PW = "una-password-robusta"
PROBLEM_JSON = "application/problem+json"
MOV = f"{settings.API_V1_STR}/movimenti/"
CAT = f"{settings.API_V1_STR}/categorie/"
BILANCIO = f"{settings.API_V1_STR}/bilancio"
STAT = f"{settings.API_V1_STR}/statistiche"


def _auth(client: TestClient) -> dict[str, str]:
    username = f"rie_{uuid.uuid4().hex[:12]}"
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


def _cat(client: TestClient, headers: dict[str, str], tipo: str, idx: int = 0) -> str:
    return client.get(CAT, headers=headers).json()[tipo][idx]["id"]


def _spesa(client, headers, cat, cents, data):  # type: ignore[no-untyped-def]
    return client.post(
        MOV,
        headers=headers,
        json={
            "tipo": "spesa",
            "amount_cents": cents,
            "data": data,
            "categoria_id": cat,
        },
    )


def test_empty_period_is_zero(client: TestClient) -> None:
    headers = _auth(client)
    r = client.get(
        BILANCIO, headers=headers, params={"period": "month", "anchor": "2026-06-15"}
    )
    assert r.status_code == 200
    body = r.json()
    assert body["netto_cents"] == 0
    assert body["entrate_cents"] == 0
    assert body["spese_cents"] == 0
    assert body["spese_per_categoria"] == []


def test_bilancio_aggregates_and_sorts_breakdown(client: TestClient) -> None:
    headers = _auth(client)
    casa = _cat(client, headers, "spesa", 0)
    svago = _cat(client, headers, "spesa", 1)
    stip = _cat(client, headers, "entrata", 0)

    _spesa(client, headers, casa, 20000, "2026-06-10")
    _spesa(client, headers, svago, 50000, "2026-06-12")
    client.post(
        MOV,
        headers=headers,
        json={
            "tipo": "entrata",
            "amount_cents": 300000,
            "data": "2026-06-01",
            "categoria_id": stip,
        },
    )
    # A spesa outside the period must be excluded.
    _spesa(client, headers, casa, 99999, "2026-05-31")

    body = client.get(
        BILANCIO, headers=headers, params={"period": "month", "anchor": "2026-06-15"}
    ).json()
    assert body["entrate_cents"] == 300000
    assert body["spese_cents"] == 70000
    assert body["netto_cents"] == 230000
    # Sorted largest → smallest: svago (50000) before casa (20000).
    breakdown = body["spese_per_categoria"]
    assert [c["total_cents"] for c in breakdown] == [50000, 20000]
    assert breakdown[0]["categoria_id"] == svago


def test_invalid_period_is_422(client: TestClient) -> None:
    headers = _auth(client)
    r = client.get(
        BILANCIO, headers=headers, params={"period": "decade", "anchor": "2026-06-15"}
    )
    assert r.status_code == 422
    assert r.headers["content-type"].startswith(PROBLEM_JSON)


def test_statistiche_pie_and_trend(client: TestClient) -> None:
    headers = _auth(client)
    casa = _cat(client, headers, "spesa", 0)
    _spesa(client, headers, casa, 20000, "2026-06-10")
    _spesa(client, headers, casa, 10000, "2026-05-10")

    body = client.get(
        STAT, headers=headers, params={"period": "month", "anchor": "2026-06-15"}
    ).json()
    assert len(body["trend"]) == 6
    assert body["trend"][-1]["mese"] == "2026-06"
    assert body["trend"][-1]["spese_cents"] == 20000
    # June pie has the casa spesa.
    assert body["has_pie"] is True
    assert body["pie"][0]["total_cents"] == 20000
    # Two months with data → trend chartable.
    assert body["has_trend"] is True


def test_statistiche_insufficient_data_flags(client: TestClient) -> None:
    headers = _auth(client)
    body = client.get(
        STAT, headers=headers, params={"period": "month", "anchor": "2026-06-15"}
    ).json()
    assert body["has_pie"] is False
    assert body["has_trend"] is False


def test_drilldown_filter_movimenti(client: TestClient) -> None:
    headers = _auth(client)
    casa = _cat(client, headers, "spesa", 0)
    svago = _cat(client, headers, "spesa", 1)
    _spesa(client, headers, casa, 20000, "2026-06-10")
    _spesa(client, headers, svago, 50000, "2026-06-12")
    _spesa(client, headers, casa, 99999, "2026-05-31")

    rows = client.get(
        MOV,
        headers=headers,
        params={"categoria_id": casa, "start": "2026-06-01", "end": "2026-07-01"},
    ).json()
    assert len(rows) == 1
    assert rows[0]["amount_cents"] == 20000


def test_isolation_and_auth(client: TestClient) -> None:
    headers_a = _auth(client)
    headers_b = _auth(client)
    casa_a = _cat(client, headers_a, "spesa", 0)
    _spesa(client, headers_a, casa_a, 12345, "2026-06-10")

    b = client.get(
        BILANCIO, headers=headers_b, params={"period": "month", "anchor": "2026-06-15"}
    ).json()
    assert b["spese_cents"] == 0  # never sees A's spesa
    assert (
        client.get(
            BILANCIO, params={"period": "month", "anchor": "2026-06-15"}
        ).status_code
        == 401
    )


def test_bilancio_aggregates_at_top_level_with_subsplit(client: TestClient) -> None:
    headers = _auth(client)
    casa = client.post(
        f"{CAT}", headers=headers, json={"nome": "Casa", "tipo": "spesa"}
    ).json()
    mutuo = client.post(
        f"{CAT}",
        headers=headers,
        json={"nome": "Mutuo", "tipo": "spesa", "parent_id": casa["id"]},
    ).json()
    _spesa(client, headers, casa["id"], 10000, "2026-06-05")  # direct on parent
    _spesa(client, headers, mutuo["id"], 40000, "2026-06-06")  # on child

    body = client.get(
        BILANCIO, headers=headers, params={"period": "month", "anchor": "2026-06-15"}
    ).json()
    casa_row = next(
        c for c in body["spese_per_categoria"] if c["categoria_id"] == casa["id"]
    )
    assert casa_row["total_cents"] == 50000  # parent + child
    subs = {s["nome"]: s["total_cents"] for s in casa_row["sottocategorie"]}
    assert subs["Mutuo"] == 40000
    assert subs["(diretto)"] == 10000
    # Child is not also a separate top-level row.
    assert all(c["categoria_id"] != mutuo["id"] for c in body["spese_per_categoria"])
