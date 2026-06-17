"""Calc tests are PURE — they must not touch the database.

The architecture mandates that ``app/calc/`` has no DB/IO and is unit-tested in
isolation. The top-level ``tests/conftest.py`` defines a session-scoped autouse
``db`` fixture that opens a real Postgres session; override it here with a no-op
so calc tests run without a database.
"""

from collections.abc import Generator

import pytest


@pytest.fixture(scope="session", autouse=True)
def db() -> Generator[None, None, None]:
    yield None
