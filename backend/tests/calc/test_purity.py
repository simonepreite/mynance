"""AR-Calc purity guard (Story 2.3, AC1): app/calc/ has no DB, FastAPI, or IO.

The calc package must operate only on plain values passed in, so it stays
deterministic and unit-testable in isolation. This meta-test fails the build if
a forbidden dependency ever creeps into the package.
"""

import pathlib

import app.calc as calc_pkg

FORBIDDEN = (
    "sqlmodel",
    "sqlalchemy",
    "fastapi",
    "app.core.db",
    "app.api",
    "app.models",
    "requests",
    "httpx",
)


def test_calc_package_has_no_db_or_io_imports() -> None:
    calc_dir = pathlib.Path(calc_pkg.__file__).parent
    for path in sorted(calc_dir.glob("*.py")):
        source = path.read_text(encoding="utf-8")
        for token in FORBIDDEN:
            assert f"import {token}" not in source, (
                f"{path.name} must not import {token} (calc is pure, AC1)"
            )
            assert f"from {token}" not in source, (
                f"{path.name} must not import from {token} (calc is pure, AC1)"
            )
