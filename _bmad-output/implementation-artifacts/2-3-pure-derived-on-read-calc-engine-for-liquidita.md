---
baseline_commit: e343a2a
---

# Story 2.3: Pure derived-on-read calc engine for Liquidità (AR-Calc) with worked-example tests (FR-13, NFR-1)

Status: done

## Story

As a developer, I want a pure, framework-independent calculation module that derives Liquidità from stored inputs in integer cents, so that the core financial figure is deterministic, reproducible, isolated from DB/IO, and covered by worked-example tests before any endpoint depends on it.

## Acceptance Criteria

- **AC1 — pure module:** the calc code lives in `backend/app/calc/` with no DB access, no FastAPI imports, no IO — pure functions over plain inputs, unit-testable in isolation.
- **AC2 — formula in integer cents:** `Liquidità = Liquidità iniziale + Σ Entrate − Σ Spese − Σ Capitale versato`, all arithmetic in integer cents (never float); Capitale versato may be empty (sums to 0).
- **AC3 — unset baseline:** an unset Liquidità iniziale is treated as 0 cents, deterministically, without throwing.
- **AC4 — worked examples:** the reference example (iniziale 100000; Entrate 250000+50000; Spese 45000+1299+90000) computes to the exact hand-value (263701); unit tests in `backend/tests/calc/` cover it plus a negative-result case (surfaced, never clamped).
- **AC5 — order-independent + deterministic:** the same inputs in different orderings yield an identical result, reproducible across runs (NFR-1).
- **AC6 — rounding centralized:** rounding/conversion is centralized in `money.py`; all values stay exact integer cents with no float drift.

## Tasks / Subtasks

- [x] **Pure engine (AC1, AC2, AC3):** `compute_liquidita(iniziale_cents, entrate_cents, spese_cents, capitale_versato_cents)` — unset baseline → 0, negatives surfaced, integer-cents only via `money.add`; imports nothing but stdlib + `app.calc.money`. [backend/app/calc/liquidita.py]
- [x] **Money convention reuse (AC6):** builds on the Story 1.1 `app/calc/money.py` (`euros_to_cents` HALF_UP, `add`, float-rejecting) — the single home for the cents convention and any rounding. [backend/app/calc/money.py]
- [x] **Worked-example + determinism tests (AC4, AC5):** reference example == 263701, negative-result cases, unset baseline, empty collections, Capitale versato subtraction, order-independence, float-input rejection. [backend/tests/calc/test_liquidita.py]
- [x] **Purity guard (AC1):** meta-test fails the build if `app/calc/` ever imports sqlmodel/sqlalchemy/fastapi/app.core.db/app.api/app.models/requests/httpx. [backend/tests/calc/test_purity.py]

## Dev Notes

- The engine is consumed by the derived read endpoint in Story 2.4; Movimenti (Entrate/Spese) arrive in 2.5/2.6 and Capitale versato (Investimenti) in Epic 5 — until then the caller passes empty collections and the formula still holds.
- `tests/calc/conftest.py` (from 1.1) overrides the session DB fixture with a no-op, so calc tests run with no database — reinforcing AC1.
- Honesty principle: negative Liquidità is returned with sign, never clamped to zero.

### Completion Notes List

_Backend-only, pure module. Verified locally: ruff check + `ruff format --check` clean, mypy clean, `pytest tests/calc` → 14 passed (worked example, negatives, unset, order-independence, float rejection, purity guard)._

### Change Log

| Date | Change |
|---|---|
| 2026-06-17 | Pure `compute_liquidita` engine + worked-example/determinism tests + calc-purity guard. Story done. |

### File List

**Added:** `backend/app/calc/liquidita.py`, `backend/tests/calc/test_liquidita.py`, `backend/tests/calc/test_purity.py`
**Modified:** `_bmad-output/implementation-artifacts/sprint-status.yaml`
