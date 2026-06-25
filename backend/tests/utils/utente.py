"""Shared helpers for the mynance Utente domain in tests.

Registration now requires an email and login is gated by verification, so most
tests need a *verified* account. ``auth_headers`` registers one, flips it
verified directly in the DB (bypassing the email step the tests don't care
about), logs in, and returns the bearer header.
"""

import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.config import settings
from app.core.db import engine
from app.models import Utente

PW = "una-password-robusta"


def register(
    client: TestClient,
    *,
    username: str | None = None,
    email: str | None = None,
    password: str = PW,
):
    username = username or f"u_{uuid.uuid4().hex[:12]}"
    email = email or f"{username}@example.com"
    r = client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={"username": username, "email": email, "password": password},
    )
    return username, email, r


def verify_in_db(username: str) -> None:
    with Session(engine) as s:
        u = s.exec(select(Utente).where(Utente.username == username)).one()
        u.email_verified = True
        s.add(u)
        s.commit()


def register_verified(client: TestClient, *, password: str = PW) -> tuple[str, str]:
    username, email, r = register(client, password=password)
    assert r.status_code == 201, r.text
    verify_in_db(username)
    return username, email


def auth_headers(client: TestClient, *, password: str = PW) -> dict[str, str]:
    username, _ = register_verified(client, password=password)
    token = client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"username": username, "password": password},
    ).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
