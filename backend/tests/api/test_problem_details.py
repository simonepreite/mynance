"""RFC 9457 problem+json error contract (Story 1.1, AC3)."""

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.problem import register_problem_handlers

PROBLEM_JSON = "application/problem+json"
REQUIRED_FIELDS = {"type", "title", "status", "detail", "instance"}


@pytest.fixture
def problem_app() -> TestClient:
    """A minimal app with the problem+json handlers wired, plus routes that
    raise an unexpected error and a structured-detail HTTPException."""
    app = FastAPI()
    register_problem_handlers(app)

    @app.get("/boom")
    def boom() -> None:
        raise RuntimeError("internal detail that must not leak")

    @app.get("/structured")
    def structured() -> None:
        raise HTTPException(status_code=409, detail={"code": "conflict"})

    # raise_server_exceptions=False so the 500 handler's response is returned
    # instead of Starlette re-raising the original exception into the test.
    return TestClient(app, raise_server_exceptions=False)


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


def test_unhandled_exception_renders_problem_json_without_leak(
    problem_app: TestClient,
) -> None:
    # An unexpected exception surfaces as 500 problem+json with a generic
    # detail — internals/tracebacks must never reach the client.
    r = problem_app.get("/boom")
    assert r.status_code == 500
    assert r.headers["content-type"].startswith(PROBLEM_JSON)
    body = r.json()
    assert REQUIRED_FIELDS <= set(body)
    assert body["status"] == 500
    assert body["detail"] == "An unexpected error occurred."
    assert "internal detail that must not leak" not in r.text


def test_structured_http_detail_preserved_under_errors(
    problem_app: TestClient,
) -> None:
    # A non-string HTTPException detail is preserved under the `errors`
    # extension rather than silently dropped.
    r = problem_app.get("/structured")
    assert r.status_code == 409
    assert r.headers["content-type"].startswith(PROBLEM_JSON)
    body = r.json()
    assert REQUIRED_FIELDS <= set(body)
    assert body["detail"] is None
    assert body["errors"] == {"code": "conflict"}
