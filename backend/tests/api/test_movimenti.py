"""Record Spesa/Entrata + derived-Liquidità recompute + isolation (2.5/2.6)."""

import uuid

from fastapi.testclient import TestClient

from app.core.config import settings

PW = "una-password-robusta"
PROBLEM_JSON = "application/problem+json"
MOV = f"{settings.API_V1_STR}/movimenti/"
CAT = f"{settings.API_V1_STR}/categorie/"
INIZIALE = f"{settings.API_V1_STR}/liquidita/iniziale"
LIQUIDITA = f"{settings.API_V1_STR}/liquidita/"


def _auth(client: TestClient) -> dict[str, str]:
    username = f"mov_{uuid.uuid4().hex[:12]}"
    client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={"username": username, "password": PW},
    )
    token = client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"username": username, "password": PW},
    ).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _categoria_id(client: TestClient, headers: dict[str, str], tipo: str) -> str:
    listed = client.get(CAT, headers=headers).json()
    return listed[tipo][0]["id"]


def test_create_spesa_persists_in_cents(client: TestClient) -> None:
    headers = _auth(client)
    cat = _categoria_id(client, headers, "spesa")
    r = client.post(
        MOV,
        headers=headers,
        json={
            "tipo": "spesa",
            "amount_cents": 4599,
            "data": "2026-06-17",
            "categoria_id": cat,
            "note": "Pranzo",
        },
    )
    assert r.status_code == 201
    body = r.json()
    assert body["tipo"] == "spesa"
    assert body["amount_cents"] == 4599
    assert body["categoria_id"] == cat
    assert body["note"] == "Pranzo"
    assert "id" in body


def test_create_entrata_persists(client: TestClient) -> None:
    headers = _auth(client)
    cat = _categoria_id(client, headers, "entrata")
    r = client.post(
        MOV,
        headers=headers,
        json={
            "tipo": "entrata",
            "amount_cents": 250000,
            "data": "2026-06-01",
            "categoria_id": cat,
        },
    )
    assert r.status_code == 201
    assert r.json()["tipo"] == "entrata"


def test_tipo_mismatch_is_422(client: TestClient) -> None:
    headers = _auth(client)
    spesa_cat = _categoria_id(client, headers, "spesa")
    entrata_cat = _categoria_id(client, headers, "entrata")
    # Spesa with an Entrata-type Categoria.
    r1 = client.post(
        MOV,
        headers=headers,
        json={
            "tipo": "spesa",
            "amount_cents": 100,
            "data": "2026-06-17",
            "categoria_id": entrata_cat,
        },
    )
    assert r1.status_code == 422
    assert r1.headers["content-type"].startswith(PROBLEM_JSON)
    # Entrata with a Spesa-type Categoria.
    r2 = client.post(
        MOV,
        headers=headers,
        json={
            "tipo": "entrata",
            "amount_cents": 100,
            "data": "2026-06-17",
            "categoria_id": spesa_cat,
        },
    )
    assert r2.status_code == 422


def test_zero_or_negative_amount_is_422(client: TestClient) -> None:
    headers = _auth(client)
    cat = _categoria_id(client, headers, "spesa")
    for amount in (0, -100):
        r = client.post(
            MOV,
            headers=headers,
            json={
                "tipo": "spesa",
                "amount_cents": amount,
                "data": "2026-06-17",
                "categoria_id": cat,
            },
        )
        assert r.status_code == 422


def test_liquidita_recomputes_with_movimenti(client: TestClient) -> None:
    headers = _auth(client)
    spesa_cat = _categoria_id(client, headers, "spesa")
    entrata_cat = _categoria_id(client, headers, "entrata")
    client.put(INIZIALE, headers=headers, json={"value_cents": 100000})

    client.post(
        MOV,
        headers=headers,
        json={
            "tipo": "spesa",
            "amount_cents": 30000,
            "data": "2026-06-17",
            "categoria_id": spesa_cat,
        },
    )
    assert client.get(LIQUIDITA, headers=headers).json()["value_cents"] == 70000

    client.post(
        MOV,
        headers=headers,
        json={
            "tipo": "entrata",
            "amount_cents": 50000,
            "data": "2026-06-17",
            "categoria_id": entrata_cat,
        },
    )
    assert client.get(LIQUIDITA, headers=headers).json()["value_cents"] == 120000


def test_edit_amount_recomputes_liquidita(client: TestClient) -> None:
    headers = _auth(client)
    cat = _categoria_id(client, headers, "spesa")
    client.put(INIZIALE, headers=headers, json={"value_cents": 100000})
    mid = client.post(
        MOV,
        headers=headers,
        json={
            "tipo": "spesa",
            "amount_cents": 30000,
            "data": "2026-06-17",
            "categoria_id": cat,
        },
    ).json()["id"]
    assert client.get(LIQUIDITA, headers=headers).json()["value_cents"] == 70000

    r = client.patch(f"{MOV}{mid}", headers=headers, json={"amount_cents": 10000})
    assert r.status_code == 200
    assert r.json()["amount_cents"] == 10000
    assert client.get(LIQUIDITA, headers=headers).json()["value_cents"] == 90000


def test_soft_delete_recomputes_and_drops_from_list(client: TestClient) -> None:
    headers = _auth(client)
    cat = _categoria_id(client, headers, "spesa")
    client.put(INIZIALE, headers=headers, json={"value_cents": 100000})
    mid = client.post(
        MOV,
        headers=headers,
        json={
            "tipo": "spesa",
            "amount_cents": 30000,
            "data": "2026-06-17",
            "categoria_id": cat,
        },
    ).json()["id"]

    assert client.delete(f"{MOV}{mid}", headers=headers).status_code == 200
    assert client.get(LIQUIDITA, headers=headers).json()["value_cents"] == 100000
    ids = [m["id"] for m in client.get(MOV, headers=headers).json()]
    assert mid not in ids


def test_cross_utente_isolation(client: TestClient) -> None:
    headers_a = _auth(client)
    headers_b = _auth(client)
    cat_a = _categoria_id(client, headers_a, "spesa")
    mid_a = client.post(
        MOV,
        headers=headers_a,
        json={
            "tipo": "spesa",
            "amount_cents": 12345,
            "data": "2026-06-17",
            "categoria_id": cat_a,
        },
    ).json()["id"]

    # B cannot use A's Categoria on create (foreign id → 404).
    assert (
        client.post(
            MOV,
            headers=headers_b,
            json={
                "tipo": "spesa",
                "amount_cents": 100,
                "data": "2026-06-17",
                "categoria_id": cat_a,
            },
        ).status_code
        == 404
    )
    # B cannot edit or delete A's Movimento, and never sees it.
    assert (
        client.patch(
            f"{MOV}{mid_a}", headers=headers_b, json={"amount_cents": 1}
        ).status_code
        == 404
    )
    assert client.delete(f"{MOV}{mid_a}", headers=headers_b).status_code == 404
    assert mid_a not in [m["id"] for m in client.get(MOV, headers=headers_b).json()]


def test_unauthenticated_is_401(client: TestClient) -> None:
    assert client.get(MOV).status_code == 401
    assert (
        client.post(
            MOV,
            json={
                "tipo": "spesa",
                "amount_cents": 100,
                "data": "2026-06-17",
                "categoria_id": str(uuid.uuid4()),
            },
        ).status_code
        == 401
    )


def test_list_filter_includes_children(client: TestClient) -> None:
    headers = _auth(client)
    casa = client.post(
        CAT, headers=headers, json={"nome": "Casa", "tipo": "spesa"}
    ).json()
    mutuo = client.post(
        CAT,
        headers=headers,
        json={"nome": "Mutuo", "tipo": "spesa", "parent_id": casa["id"]},
    ).json()
    client.post(
        MOV,
        headers=headers,
        json={
            "tipo": "spesa",
            "amount_cents": 10000,
            "data": "2026-06-05",
            "categoria_id": casa["id"],
        },
    )
    client.post(
        MOV,
        headers=headers,
        json={
            "tipo": "spesa",
            "amount_cents": 40000,
            "data": "2026-06-06",
            "categoria_id": mutuo["id"],
        },
    )
    # Parent filter → parent + child movimenti.
    rows = client.get(MOV, headers=headers, params={"categoria_id": casa["id"]}).json()
    assert len(rows) == 2
    # Child filter → only the child's.
    rows_child = client.get(
        MOV, headers=headers, params={"categoria_id": mutuo["id"]}
    ).json()
    assert len(rows_child) == 1 and rows_child[0]["amount_cents"] == 40000
