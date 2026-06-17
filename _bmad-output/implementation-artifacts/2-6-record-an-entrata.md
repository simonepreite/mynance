---
baseline_commit: bdb9fbe
---

# Story 2.6: Record an Entrata (FR-6)

Status: done

## Story

As an Utente, I want to record an Entrata with amount, date, an Entrata-type Categoria, and optional note, so that my inflows immediately increase my derived Liquidità.

## Acceptance Criteria

- **AC1 — create:** POST an Entrata with integer-cents amount, date, and an Entrata-type Categoria persists it as a Movimento scoped to `utente_id`, amount in `*_cents` (never float).
- **AC2 — tipo guard:** attaching a Spesa-type Categoria to an Entrata is rejected with 422 problem+json (tipo mismatch, FR-7).
- **AC3 — increases Liquidità:** after recording an Entrata, `GET /api/v1/liquidita` has increased by exactly that Entrata's cents (FR-13 recompute).
- **AC4 — edit/delete recompute:** editing or soft-deleting an Entrata persists with no silent loss, and derived Liquidità recomputes on next read.
- **AC5 — isolation:** another Utente's Entrata id → 404/403, never their data (FR-4).

## Tasks / Subtasks

- [x] **Shared Movimento model (AC1):** Entrata is the `tipo="entrata"` Movimento on the same `movimenti` table created in Story 2.5; `amount_cents` positive, added (not subtracted) by the calc engine. [backend/app/models.py]
- [x] **Create/edit/delete + tipo guard (AC1, AC2, AC4, AC5):** the shared `/api/v1/movimenti` endpoints; an Entrata requires an Entrata-type Categoria (422 on Spesa-type), per-Utente scoped (404 cross-Utente). [backend/app/api/routes/movimenti.py]
- [x] **Increases derived Liquidità (AC3):** `GET /liquidita` sums Entrate into the baseline via the pure engine; verified by a worked test (100000 + Entrata 50000 → 150000-class assertion in the combined recompute test). [backend/app/api/routes/liquidita.py]
- [x] **Tests:** create Entrata, tipo mismatch→422, Liquidità increases by the exact cents (combined recompute test), isolation, 401. [backend/tests/api/test_movimenti.py]

## Dev Notes

- Entrata and Spesa share one table/endpoint (see Story 2.5 notes); only the tipo and the engine's add-vs-subtract differ. This keeps the quick-add (2.7) a single toggle.
- Secchiello concepts do not apply to Entrate.

### Completion Notes List

_Backend implemented and verified with Story 2.5 in the same pass: ruff/format/mypy clean, pytest 119 passed / 1 skipped. Live smoke test: after Entrata 50000 on a 70000 Liquidità, GET returned 120000 (increase == exact cents). Quick-add UI is Story 2.7._

### Change Log

| Date | Change |
|---|---|
| 2026-06-17 | Backend: Entrata via the shared Movimento endpoints + tipo guard + Entrata sums into derived Liquidità + tests. Story done (delivered alongside 2.5). |

### File List

(Shared with Story 2.5 — same `movimenti` table, router, and tests.)
**Modified:** `backend/app/api/routes/movimenti.py`, `backend/app/api/routes/liquidita.py`, `backend/app/models.py`, `backend/tests/api/test_movimenti.py`
