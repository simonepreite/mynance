"""Secchielli CRUD + Categoria→Secchiello link + Spesa default link (Story 3.1)."""

import uuid

from fastapi.testclient import TestClient

from app.core.config import settings
from tests.utils.utente import verify_in_db

PW = "una-password-robusta"
PROBLEM_JSON = "application/problem+json"
SEC = f"{settings.API_V1_STR}/secchielli/"
CAT = f"{settings.API_V1_STR}/categorie/"
MOV = f"{settings.API_V1_STR}/movimenti/"


def _auth(client: TestClient) -> dict[str, str]:
    username = f"sec_{uuid.uuid4().hex[:12]}"
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


def _cat_id(
    client: TestClient, headers: dict[str, str], tipo: str, idx: int = 0
) -> str:
    return client.get(CAT, headers=headers).json()[tipo][idx]["id"]


def _make(client, headers, **over):  # type: ignore[no-untyped-def]
    body = {
        "nome": "Assicurazione auto",
        "importo_previsto_cents": 62000,
        "periodicita": "annual",
        "prossima_scadenza": "2027-02-01",
    }
    body.update(over)
    return client.post(SEC, headers=headers, json=body)


def test_create_returns_derived_quota_saldo(client: TestClient) -> None:
    headers = _auth(client)
    r = _make(client, headers)
    assert r.status_code == 201
    body = r.json()
    assert body["nome"] == "Assicurazione auto"
    assert body["importo_previsto_cents"] == 62000
    assert "saldo_cents" in body and "quota_cents" in body
    assert body["quota_cents"] >= 0


def test_custom_requires_interval(client: TestClient) -> None:
    headers = _auth(client)
    r = _make(client, headers, periodicita="custom")
    assert r.status_code == 422
    assert r.headers["content-type"].startswith(PROBLEM_JSON)
    ok = _make(client, headers, periodicita="custom", intervallo_mesi=2)
    assert ok.status_code == 201
    assert ok.json()["intervallo_mesi"] == 2


def test_invalid_inputs_are_422(client: TestClient) -> None:
    headers = _auth(client)
    assert _make(client, headers, importo_previsto_cents=0).status_code == 422
    assert _make(client, headers, nome="").status_code == 422


def test_list_get_patch_delete(client: TestClient) -> None:
    headers = _auth(client)
    sid = _make(client, headers).json()["id"]
    assert any(s["id"] == sid for s in client.get(SEC, headers=headers).json())
    assert client.get(f"{SEC}{sid}", headers=headers).status_code == 200
    patched = client.patch(f"{SEC}{sid}", headers=headers, json={"nome": "RC auto"})
    assert patched.status_code == 200
    assert patched.json()["nome"] == "RC auto"
    assert client.delete(f"{SEC}{sid}", headers=headers).status_code == 200
    assert all(s["id"] != sid for s in client.get(SEC, headers=headers).json())


def test_isolation(client: TestClient) -> None:
    headers_a = _auth(client)
    headers_b = _auth(client)
    sid_a = _make(client, headers_a).json()["id"]
    assert client.get(f"{SEC}{sid_a}", headers=headers_b).status_code == 404
    assert (
        client.patch(f"{SEC}{sid_a}", headers=headers_b, json={"nome": "x"}).status_code
        == 404
    )
    assert client.delete(f"{SEC}{sid_a}", headers=headers_b).status_code == 404


def test_categoria_link_spesa_only(client: TestClient) -> None:
    headers = _auth(client)
    sid = _make(client, headers).json()["id"]
    spesa_cat = _cat_id(client, headers, "spesa")
    entrata_cat = _cat_id(client, headers, "entrata")

    linked = client.patch(
        f"{CAT}{spesa_cat}", headers=headers, json={"secchiello_id": sid}
    )
    assert linked.status_code == 200
    assert linked.json()["secchiello_id"] == sid

    # Entrata-type Categoria cannot be linked.
    bad = client.patch(
        f"{CAT}{entrata_cat}", headers=headers, json={"secchiello_id": sid}
    )
    assert bad.status_code == 422


def test_spesa_defaults_secchiello_from_categoria_and_affects_saldo(
    client: TestClient,
) -> None:
    headers = _auth(client)
    sid = _make(client, headers).json()["id"]
    spesa_cat = _cat_id(client, headers, "spesa")
    client.patch(f"{CAT}{spesa_cat}", headers=headers, json={"secchiello_id": sid})

    saldo0 = client.get(f"{SEC}{sid}", headers=headers).json()["saldo_cents"]

    # Spesa without an explicit secchiello → defaults from the Categoria link.
    mov = client.post(
        MOV,
        headers=headers,
        json={
            "tipo": "spesa",
            "amount_cents": 10000,
            "data": "2026-06-17",
            "categoria_id": spesa_cat,
        },
    ).json()
    assert mov["secchiello_id"] == sid

    # Same-month replay → the linked Spesa lowers the Saldo by exactly its amount.
    saldo1 = client.get(f"{SEC}{sid}", headers=headers).json()["saldo_cents"]
    assert saldo1 == saldo0 - 10000


def test_spesa_explicit_null_secchiello(client: TestClient) -> None:
    headers = _auth(client)
    sid = _make(client, headers).json()["id"]
    spesa_cat = _cat_id(client, headers, "spesa")
    client.patch(f"{CAT}{spesa_cat}", headers=headers, json={"secchiello_id": sid})
    mov = client.post(
        MOV,
        headers=headers,
        json={
            "tipo": "spesa",
            "amount_cents": 5000,
            "data": "2026-06-17",
            "categoria_id": spesa_cat,
            "secchiello_id": None,
        },
    ).json()
    assert mov["secchiello_id"] is None


def test_registra_pagamento_advances_cycle(client: TestClient) -> None:
    headers = _auth(client)
    sid = _make(client, headers, prossima_scadenza="2027-02-01").json()["id"]
    spesa_cat = _cat_id(client, headers, "spesa")
    r = client.post(
        f"{SEC}{sid}/pagamento",
        headers=headers,
        json={"amount_cents": 60000, "data": "2026-06-17", "categoria_id": spesa_cat},
    )
    assert r.status_code == 200
    body = r.json()
    # Importo previsto updated to the actual paid amount; scadenza +12 months.
    assert body["importo_previsto_cents"] == 60000
    assert body["prossima_scadenza"] == "2028-02-01"


def test_registra_pagamento_requires_spesa_categoria(client: TestClient) -> None:
    headers = _auth(client)
    sid = _make(client, headers).json()["id"]
    entrata_cat = _cat_id(client, headers, "entrata")
    r = client.post(
        f"{SEC}{sid}/pagamento",
        headers=headers,
        json={"amount_cents": 60000, "data": "2026-06-17", "categoria_id": entrata_cat},
    )
    assert r.status_code == 422
