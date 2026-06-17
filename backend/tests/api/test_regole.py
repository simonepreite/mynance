"""Regole ricorrenti CRUD + lazy generation + skip (Epic 6, FR-8)."""

import uuid

from fastapi.testclient import TestClient

from app.core.config import settings

PW = "una-password-robusta"
PROBLEM_JSON = "application/problem+json"
REG = f"{settings.API_V1_STR}/regole-ricorrenti/"
CAT = f"{settings.API_V1_STR}/categorie/"
MOV = f"{settings.API_V1_STR}/movimenti/"
LIQ = f"{settings.API_V1_STR}/liquidita/"
INIZIALE = f"{settings.API_V1_STR}/liquidita/iniziale"
INV = f"{settings.API_V1_STR}/investimenti"


def _auth(client: TestClient) -> dict[str, str]:
    username = f"reg_{uuid.uuid4().hex[:12]}"
    client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={"username": username, "password": PW},
    )
    token = client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"username": username, "password": PW},
    ).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _entrata_cat(client: TestClient, headers: dict[str, str]) -> str:
    return client.get(CAT, headers=headers).json()["entrata"][0]["id"]


def _spesa_cat(client: TestClient, headers: dict[str, str]) -> str:
    return client.get(CAT, headers=headers).json()["spesa"][0]["id"]


def test_create_entrata_regola(client: TestClient) -> None:
    headers = _auth(client)
    r = client.post(
        REG,
        headers=headers,
        json={
            "importo_cents": 200000,
            "periodicita": "monthly",
            "day_of_period": 1,
            "kind": "entrata",
            "categoria_id": _entrata_cat(client, headers),
            "start_date": "2026-06-01",
        },
    )
    assert r.status_code == 201
    assert r.json()["kind"] == "entrata"


def test_entrata_regola_rejects_spesa_categoria_and_missing(client: TestClient) -> None:
    headers = _auth(client)
    bad = client.post(
        REG,
        headers=headers,
        json={
            "importo_cents": 1000,
            "periodicita": "monthly",
            "day_of_period": 1,
            "kind": "entrata",
            "categoria_id": _spesa_cat(client, headers),
            "start_date": "2026-06-01",
        },
    )
    assert bad.status_code == 422
    assert bad.headers["content-type"].startswith(PROBLEM_JSON)
    missing = client.post(
        REG,
        headers=headers,
        json={
            "importo_cents": 1000,
            "periodicita": "monthly",
            "day_of_period": 1,
            "kind": "entrata",
            "start_date": "2026-06-01",
        },
    )
    assert missing.status_code == 422


def test_invalid_day_of_period(client: TestClient) -> None:
    headers = _auth(client)
    for day in (0, 32):
        r = client.post(
            REG,
            headers=headers,
            json={
                "importo_cents": 1000,
                "periodicita": "monthly",
                "day_of_period": day,
                "kind": "entrata",
                "categoria_id": _entrata_cat(client, headers),
                "start_date": "2026-06-01",
            },
        )
        assert r.status_code == 422


def test_lazy_generation_idempotent_and_liquidita(client: TestClient) -> None:
    headers = _auth(client)
    client.put(INIZIALE, headers=headers, json={"value_cents": 0})
    client.post(
        REG,
        headers=headers,
        json={
            "importo_cents": 100000,
            "periodicita": "monthly",
            "day_of_period": 1,
            "kind": "entrata",
            "categoria_id": _entrata_cat(client, headers),
            "start_date": "2026-03-01",
        },
    )
    # Access triggers generation: Mar/Apr/May/Jun 1 ≤ 2026-06-17 → 4 Entrate.
    movs = client.get(MOV, headers=headers).json()
    entrate = [m for m in movs if m["tipo"] == "entrata"]
    assert len(entrate) == 4
    # Idempotent: a second access does not duplicate.
    movs2 = client.get(MOV, headers=headers).json()
    assert len([m for m in movs2 if m["tipo"] == "entrata"]) == 4
    # Liquidità reflects the generated income.
    assert client.get(LIQ, headers=headers).json()["value_cents"] == 400000


def test_skip_generated_item_not_recreated(client: TestClient) -> None:
    headers = _auth(client)
    client.post(
        REG,
        headers=headers,
        json={
            "importo_cents": 100000,
            "periodicita": "monthly",
            "day_of_period": 1,
            "kind": "entrata",
            "categoria_id": _entrata_cat(client, headers),
            "start_date": "2026-03-01",
        },
    )
    entrate = [
        m for m in client.get(MOV, headers=headers).json() if m["tipo"] == "entrata"
    ]
    assert len(entrate) == 4
    # Skip one by deleting it; re-generation must NOT recreate it.
    client.delete(f"{MOV}{entrate[0]['id']}", headers=headers)
    after = [
        m for m in client.get(MOV, headers=headers).json() if m["tipo"] == "entrata"
    ]
    assert len(after) == 3


def test_pac_regola_generates_versamenti(client: TestClient) -> None:
    headers = _auth(client)
    client.put(INIZIALE, headers=headers, json={"value_cents": 500000})
    inv = client.post(INV, headers=headers, json={"nome": "ETF"}).json()
    client.post(
        REG,
        headers=headers,
        json={
            "importo_cents": 50000,
            "periodicita": "monthly",
            "day_of_period": 1,
            "kind": "versamento_pac",
            "investimento_id": inv["id"],
            "start_date": "2026-05-01",
        },
    )
    # Access triggers generation (May/Jun → 2 versamenti × 50000 = 100000).
    liq = client.get(LIQ, headers=headers).json()["value_cents"]
    assert liq == 500000 - 100000
    invs = client.get(INV, headers=headers).json()
    assert invs[0]["capitale_versato_cents"] == 100000


def test_pac_regola_missing_investimento_is_422(client: TestClient) -> None:
    headers = _auth(client)
    r = client.post(
        REG,
        headers=headers,
        json={
            "importo_cents": 1000,
            "periodicita": "monthly",
            "day_of_period": 1,
            "kind": "versamento_pac",
            "start_date": "2026-06-01",
        },
    )
    assert r.status_code == 422


def test_isolation(client: TestClient) -> None:
    headers_a = _auth(client)
    rid = client.post(
        REG,
        headers=headers_a,
        json={
            "importo_cents": 1000,
            "periodicita": "monthly",
            "day_of_period": 1,
            "kind": "entrata",
            "categoria_id": _entrata_cat(client, headers_a),
            "start_date": "2026-06-01",
        },
    ).json()["id"]
    headers_b = _auth(client)
    assert client.get(f"{REG}{rid}", headers=headers_b).status_code == 404
    assert client.delete(f"{REG}{rid}", headers=headers_b).status_code == 404
