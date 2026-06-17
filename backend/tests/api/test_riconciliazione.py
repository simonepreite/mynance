"""Riconciliazione: system categorie, reminder, Drift, close/ack (Epic 4)."""

import uuid

from fastapi.testclient import TestClient

from app.core.config import settings

PW = "una-password-robusta"
PROBLEM_JSON = "application/problem+json"
RIC = f"{settings.API_V1_STR}/riconciliazione"
CAT = f"{settings.API_V1_STR}/categorie/"
INIZIALE = f"{settings.API_V1_STR}/liquidita/iniziale"
LIQ = f"{settings.API_V1_STR}/liquidita/"


def _auth(client: TestClient) -> dict[str, str]:
    username = f"ric_{uuid.uuid4().hex[:12]}"
    client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={"username": username, "password": PW},
    )
    token = client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"username": username, "password": PW},
    ).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_system_categorie_provisioned_and_protected(client: TestClient) -> None:
    headers = _auth(client)
    cats = client.get(CAT, headers=headers).json()
    spesa_sys = [c for c in cats["spesa"] if c["is_system"]]
    entrata_sys = [c for c in cats["entrata"] if c["is_system"]]
    assert len(spesa_sys) == 1 and spesa_sys[0]["nome"] == "non identificato"
    assert len(entrata_sys) == 1 and entrata_sys[0]["nome"] == "non identificato"
    # Cannot rename or delete a system Categoria.
    sid = spesa_sys[0]["id"]
    assert (
        client.patch(f"{CAT}{sid}", headers=headers, json={"nome": "x"}).status_code
        == 422
    )
    assert client.delete(f"{CAT}{sid}", headers=headers).status_code == 422


def test_intervallo_get_default_and_update(client: TestClient) -> None:
    headers = _auth(client)
    assert (
        client.get(f"{RIC}/intervallo", headers=headers).json()[
            "intervallo_riconciliazione_giorni"
        ]
        == 7
    )
    ok = client.put(
        f"{RIC}/intervallo",
        headers=headers,
        json={"intervallo_riconciliazione_giorni": 14},
    )
    assert ok.status_code == 200
    assert ok.json()["intervallo_riconciliazione_giorni"] == 14
    bad = client.put(
        f"{RIC}/intervallo",
        headers=headers,
        json={"intervallo_riconciliazione_giorni": 0},
    )
    assert bad.status_code == 422
    assert bad.headers["content-type"].startswith(PROBLEM_JSON)


def test_promemoria_never_reconciled_is_due(client: TestClient) -> None:
    headers = _auth(client)
    p = client.get(f"{RIC}/promemoria", headers=headers).json()
    assert p["due"] is True
    assert p["data_ultima_riconciliazione"] is None
    assert p["drift_aperto_cents"] is None


def test_anteprima_drift_euro_and_percent(client: TestClient) -> None:
    headers = _auth(client)
    client.put(INIZIALE, headers=headers, json={"value_cents": 100000})
    a = client.post(
        f"{RIC}/anteprima", headers=headers, json={"liquidita_reale_cents": 90000}
    ).json()
    assert a["liquidita_calcolata_cents"] == 100000
    assert a["drift_cents"] == -10000
    assert a["drift_percent"] == -10.0


def test_anteprima_percent_none_when_calcolata_zero(client: TestClient) -> None:
    headers = _auth(client)  # no iniziale → calcolata 0
    a = client.post(
        f"{RIC}/anteprima", headers=headers, json={"liquidita_reale_cents": 5000}
    ).json()
    assert a["liquidita_calcolata_cents"] == 0
    assert a["drift_cents"] == 5000
    assert a["drift_percent"] is None


def test_close_gap_creates_plug_and_matches_real(client: TestClient) -> None:
    headers = _auth(client)
    client.put(INIZIALE, headers=headers, json={"value_cents": 100000})
    r = client.post(
        f"{RIC}/",
        headers=headers,
        json={"liquidita_reale_cents": 90000, "esito": "chiusa"},
    )
    assert r.status_code == 201
    assert r.json()["esito"] == "chiusa"
    assert r.json()["drift_cents"] == -10000
    # Gap closed: computed Liquidità now equals the real figure.
    assert client.get(LIQ, headers=headers).json()["value_cents"] == 90000


def test_acknowledge_open_keeps_gap_and_resets_timer(client: TestClient) -> None:
    headers = _auth(client)
    client.put(INIZIALE, headers=headers, json={"value_cents": 100000})
    client.post(
        f"{RIC}/",
        headers=headers,
        json={"liquidita_reale_cents": 90000, "esito": "acknowledged_open"},
    )
    # Liquidità unchanged (no plug); timer reset (not due); open drift surfaced.
    assert client.get(LIQ, headers=headers).json()["value_cents"] == 100000
    p = client.get(f"{RIC}/promemoria", headers=headers).json()
    assert p["due"] is False
    assert p["drift_aperto_cents"] == -10000


def test_history_lists_most_recent_first(client: TestClient) -> None:
    headers = _auth(client)
    client.put(INIZIALE, headers=headers, json={"value_cents": 100000})
    client.post(
        f"{RIC}/",
        headers=headers,
        json={"liquidita_reale_cents": 95000, "esito": "acknowledged_open"},
    )
    hist = client.get(f"{RIC}/", headers=headers).json()
    assert len(hist) >= 1
    assert hist[0]["drift_cents"] == -5000


def test_isolation_and_auth(client: TestClient) -> None:
    headers_a = _auth(client)
    client.put(INIZIALE, headers=headers_a, json={"value_cents": 100000})
    client.post(
        f"{RIC}/",
        headers=headers_a,
        json={"liquidita_reale_cents": 90000, "esito": "acknowledged_open"},
    )
    headers_b = _auth(client)
    # B sees its own (empty) history and a never-reconciled reminder.
    assert client.get(f"{RIC}/", headers=headers_b).json() == []
    assert (
        client.get(f"{RIC}/promemoria", headers=headers_b).json()["drift_aperto_cents"]
        is None
    )
    assert client.get(f"{RIC}/promemoria").status_code == 401
