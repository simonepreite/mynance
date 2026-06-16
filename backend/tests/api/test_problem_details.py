"""RFC 9457 problem+json error contract (Story 1.1, AC3)."""

from fastapi.testclient import TestClient

from app.core.config import settings

PROBLEM_JSON = "application/problem+json"
REQUIRED_FIELDS = {"type", "title", "status", "detail", "instance"}


def test_http_error_renders_problem_json(client: TestClient) -> None:
    # No auth -> 401 HTTPException -> problem+json
    r = client.get(f"{settings.API_V1_STR}/users/me")
    assert r.status_code == 401
    assert r.headers["content-type"].startswith(PROBLEM_JSON)
    body = r.json()
    assert REQUIRED_FIELDS <= set(body)
    assert body["status"] == 401
    assert body["instance"] == f"{settings.API_V1_STR}/users/me"


def test_unknown_route_renders_problem_json(client: TestClient) -> None:
    r = client.get(f"{settings.API_V1_STR}/does-not-exist")
    assert r.status_code == 404
    assert r.headers["content-type"].startswith(PROBLEM_JSON)
    assert REQUIRED_FIELDS <= set(r.json())


def test_validation_error_is_422_problem_json(client: TestClient) -> None:
    # Missing form fields -> RequestValidationError -> 422 problem+json
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data={})
    assert r.status_code == 422
    assert r.headers["content-type"].startswith(PROBLEM_JSON)
    body = r.json()
    assert REQUIRED_FIELDS <= set(body)
    assert body["status"] == 422
    assert "errors" in body
