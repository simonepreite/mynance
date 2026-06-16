"""RFC 9457 (Problem Details for HTTP APIs) error responses.

Every domain/HTTP error and every request-validation failure is rendered as
``application/problem+json`` with the canonical members
``{type, title, status, detail, instance}``. Validation failures additionally
carry an ``errors`` extension member and return HTTP 422.
"""

from http import HTTPStatus
from typing import Any

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

PROBLEM_JSON_CONTENT_TYPE = "application/problem+json"


def problem_response(
    *,
    status: int,
    detail: str | None,
    instance: str,
    title: str | None = None,
    type_: str = "about:blank",
    headers: dict[str, str] | None = None,
    **extensions: Any,
) -> JSONResponse:
    """Build an ``application/problem+json`` response (RFC 9457)."""
    content: dict[str, Any] = {
        "type": type_,
        "title": title or HTTPStatus(status).phrase,
        "status": status,
        "detail": detail,
        "instance": instance,
        **extensions,
    }
    return JSONResponse(
        status_code=status,
        content=content,
        media_type=PROBLEM_JSON_CONTENT_TYPE,
        headers=headers,
    )


async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    # RFC 9457 `detail` is a human-readable string. FastAPI allows a structured
    # (dict/list) HTTPException detail; rather than silently dropping it, surface
    # it under the `errors` extension so no information is lost.
    detail = exc.detail if isinstance(exc.detail, str) else None
    extensions: dict[str, Any] = {}
    if detail is None and exc.detail is not None:
        extensions["errors"] = jsonable_encoder(exc.detail)
    return problem_response(
        status=exc.status_code,
        detail=detail,
        instance=request.url.path,
        headers=getattr(exc, "headers", None),
        **extensions,
    )


async def unhandled_exception_handler(
    request: Request,
    exc: Exception,  # noqa: ARG001 — required by the handler signature, body must not leak it
) -> JSONResponse:
    # Catch-all so unhandled exceptions surface as problem+json instead of
    # Starlette's default text/plain "Internal Server Error". The detail is
    # deliberately generic — never leak internals/tracebacks to the client.
    # Starlette re-raises after this handler runs, so the error is still logged.
    return problem_response(
        status=int(HTTPStatus.INTERNAL_SERVER_ERROR),  # 500
        detail="An unexpected error occurred.",
        instance=request.url.path,
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return problem_response(
        status=int(HTTPStatus.UNPROCESSABLE_ENTITY),  # 422
        title=HTTPStatus.UNPROCESSABLE_ENTITY.phrase,
        detail="Request validation failed",
        instance=request.url.path,
        errors=jsonable_encoder(exc.errors()),
    )


def register_problem_handlers(app: FastAPI) -> None:
    """Wire the problem+json handlers onto the FastAPI app.

    Overrides FastAPI's default HTTPException and RequestValidationError
    handlers, plus a catch-all Exception handler, so every error — including
    unhandled 500s — surfaces as RFC 9457 problem+json.
    """
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, unhandled_exception_handler)
