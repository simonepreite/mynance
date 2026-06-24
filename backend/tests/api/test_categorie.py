"""Typed Categorie CRUD + per-Utente isolation (Story 2.1, FR-7/FR-4)."""

import uuid

from fastapi.testclient import TestClient

from app.core.config import settings

PW = "una-password-robusta"
PROBLEM_JSON = "application/problem+json"
BASE = f"{settings.API_V1_STR}/categorie/"


def _auth_headers(client: TestClient) -> dict[str, str]:
    username = f"cat_{uuid.uuid4().hex[:12]}"
    client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={"username": username, "password": PW},
    )
    token = client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"username": username, "password": PW},
    ).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_starter_set_provisioned_per_tipo_on_register(client: TestClient) -> None:
    headers = _auth_headers(client)
    r = client.get(BASE, headers=headers)
    assert r.status_code == 200
    body = r.json()
    assert len(body["spesa"]) >= 1
    assert len(body["entrata"]) >= 1
    assert all(c["tipo"] == "spesa" for c in body["spesa"])
    assert all(c["tipo"] == "entrata" for c in body["entrata"])


def test_create_returns_object_and_lists_split_by_tipo(client: TestClient) -> None:
    headers = _auth_headers(client)
    created = client.post(
        BASE, headers=headers, json={"nome": "Bollette", "tipo": "spesa"}
    )
    assert created.status_code == 201
    obj = created.json()
    assert obj["nome"] == "Bollette"
    assert obj["tipo"] == "spesa"
    assert "id" in obj

    client.post(BASE, headers=headers, json={"nome": "Bonus", "tipo": "entrata"})
    listed = client.get(BASE, headers=headers).json()
    assert "Bollette" in [c["nome"] for c in listed["spesa"]]
    assert "Bonus" in [c["nome"] for c in listed["entrata"]]
    assert "Bollette" not in [c["nome"] for c in listed["entrata"]]


def test_invalid_tipo_is_422(client: TestClient) -> None:
    headers = _auth_headers(client)
    r = client.post(BASE, headers=headers, json={"nome": "X", "tipo": "altro"})
    assert r.status_code == 422
    assert r.headers["content-type"].startswith(PROBLEM_JSON)


def test_rename_persists(client: TestClient) -> None:
    headers = _auth_headers(client)
    cid = client.post(
        BASE, headers=headers, json={"nome": "Vecchio", "tipo": "spesa"}
    ).json()["id"]
    r = client.patch(f"{BASE}{cid}", headers=headers, json={"nome": "Nuovo"})
    assert r.status_code == 200
    assert r.json()["nome"] == "Nuovo"
    listed = client.get(BASE, headers=headers).json()
    assert "Nuovo" in [c["nome"] for c in listed["spesa"]]


def test_delete_removes_from_list(client: TestClient) -> None:
    headers = _auth_headers(client)
    cid = client.post(
        BASE, headers=headers, json={"nome": "Temp", "tipo": "spesa"}
    ).json()["id"]
    assert client.delete(f"{BASE}{cid}", headers=headers).status_code == 200
    listed = client.get(BASE, headers=headers).json()
    assert "Temp" not in [c["nome"] for c in listed["spesa"]]


def test_cross_utente_access_is_404(client: TestClient) -> None:
    headers_a = _auth_headers(client)
    headers_b = _auth_headers(client)
    cid_a = client.post(
        BASE, headers=headers_a, json={"nome": "Privata", "tipo": "spesa"}
    ).json()["id"]

    # B cannot rename or delete A's Categoria — same not-found as a missing id.
    assert (
        client.patch(
            f"{BASE}{cid_a}", headers=headers_b, json={"nome": "hack"}
        ).status_code
        == 404
    )
    assert client.delete(f"{BASE}{cid_a}", headers=headers_b).status_code == 404
    # ...and never sees it in their own list.
    listed_b = client.get(BASE, headers=headers_b).json()
    assert "Privata" not in [c["nome"] for c in listed_b["spesa"]]


def test_create_subcategoria(client: TestClient) -> None:
    headers = _auth_headers(client)
    parent = client.post(
        BASE, headers=headers, json={"nome": "Casa", "tipo": "spesa"}
    ).json()
    sub = client.post(
        BASE,
        headers=headers,
        json={"nome": "Mutuo", "tipo": "spesa", "parent_id": parent["id"]},
    )
    assert sub.status_code == 201
    assert sub.json()["parent_id"] == parent["id"]
    # GET carries parent_id on the child.
    listed = client.get(BASE, headers=headers).json()
    child = next(c for c in listed["spesa"] if c["nome"] == "Mutuo")
    assert child["parent_id"] == parent["id"]


def test_subcategoria_one_level_only(client: TestClient) -> None:
    headers = _auth_headers(client)
    parent = client.post(
        BASE, headers=headers, json={"nome": "Casa", "tipo": "spesa"}
    ).json()
    child = client.post(
        BASE,
        headers=headers,
        json={"nome": "Mutuo", "tipo": "spesa", "parent_id": parent["id"]},
    ).json()
    # A child cannot be a parent.
    r = client.post(
        BASE,
        headers=headers,
        json={"nome": "Rata", "tipo": "spesa", "parent_id": child["id"]},
    )
    assert r.status_code == 422
    assert r.headers["content-type"].startswith(PROBLEM_JSON)


def test_subcategoria_tipo_must_match_parent(client: TestClient) -> None:
    headers = _auth_headers(client)
    parent = client.post(
        BASE, headers=headers, json={"nome": "Casa", "tipo": "spesa"}
    ).json()
    r = client.post(
        BASE,
        headers=headers,
        json={"nome": "X", "tipo": "entrata", "parent_id": parent["id"]},
    )
    assert r.status_code == 422
    assert r.headers["content-type"].startswith(PROBLEM_JSON)


def test_subcategoria_parent_must_be_owned_and_non_system(client: TestClient) -> None:
    headers_a = _auth_headers(client)
    headers_b = _auth_headers(client)
    parent_a = client.post(
        BASE, headers=headers_a, json={"nome": "Casa", "tipo": "spesa"}
    ).json()
    # B cannot parent under A's categoria.
    assert (
        client.post(
            BASE,
            headers=headers_b,
            json={"nome": "x", "tipo": "spesa", "parent_id": parent_a["id"]},
        ).status_code
        == 404
    )
    # System "non identificato" cannot be a parent.
    sys_cat = next(
        c for c in client.get(BASE, headers=headers_a).json()["spesa"] if c["is_system"]
    )
    sys_resp = client.post(
        BASE,
        headers=headers_a,
        json={"nome": "x", "tipo": "spesa", "parent_id": sys_cat["id"]},
    )
    assert sys_resp.status_code == 422
    assert sys_resp.headers["content-type"].startswith(PROBLEM_JSON)
