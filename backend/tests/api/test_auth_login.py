"""mynance auth: login, session, logout, rate limiting (Story 1.4, FR-2)."""

from fastapi.testclient import TestClient

from app.core.config import settings
from tests.utils.utente import PW, register_verified

PROBLEM_JSON = "application/problem+json"


def _register(client: TestClient) -> str:
    """Register a verified Utente (login is gated by verification)."""
    username, _ = register_verified(client)
    return username


def _login(client: TestClient, username: str, password: str = PW):
    return client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"username": username, "password": password},
    )


def test_login_issues_token_and_me_returns_utente(client: TestClient) -> None:
    username = _register(client)
    r = _login(client, username)
    assert r.status_code == 200
    token = r.json()["access_token"]
    assert token

    me = client.get(
        f"{settings.API_V1_STR}/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me.status_code == 200
    assert me.json()["username"] == username


def test_login_wrong_password_is_generic_problem_json(client: TestClient) -> None:
    username = _register(client)
    r = _login(client, username, password="password-sbagliata")
    assert r.status_code == 400
    assert r.headers["content-type"].startswith(PROBLEM_JSON)
    assert r.json()["detail"] == "Username o password non validi."


def test_protected_route_without_token_is_401(client: TestClient) -> None:
    r = client.get(f"{settings.API_V1_STR}/auth/me")
    assert r.status_code == 401
    assert r.headers["content-type"].startswith(PROBLEM_JSON)


def test_logout_revokes_session(client: TestClient) -> None:
    username = _register(client)
    token = _login(client, username).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    assert (
        client.get(f"{settings.API_V1_STR}/auth/me", headers=headers).status_code == 200
    )
    logout = client.post(f"{settings.API_V1_STR}/auth/logout", headers=headers)
    assert logout.status_code == 200
    # The same token is now revoked → protected requests are rejected.
    after = client.get(f"{settings.API_V1_STR}/auth/me", headers=headers)
    assert after.status_code == 401


def test_login_is_rate_limited(client: TestClient) -> None:
    username = _register(client)
    statuses = [
        _login(client, username, password="sbagliata").status_code for _ in range(12)
    ]
    # The limiter (threshold 10/min, keyed by host+username) trips with 429.
    assert 429 in statuses
