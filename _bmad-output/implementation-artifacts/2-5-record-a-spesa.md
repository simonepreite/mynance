---
baseline_commit: bdb9fbe
---

# Story 2.5: Record a Spesa (FR-5)

Status: done

## Story

As an Utente, I want to record a Spesa with amount, date, a Spesa-type Categoria, and optional note, so that I capture an outflow correctly and it immediately affects my derived Liquidità.

## Acceptance Criteria

- **AC1 — Movimento table + create:** the `movimenti` table is created here (money `*_cents` BIGINT, UUID PK, `utente_id`, soft-delete `deleted_at`); POST a Spesa with integer-cents amount, date, and a Spesa-type Categoria persists it scoped to `utente_id`, amount in cents (never float).
- **AC2 — tipo guard:** attaching an Entrata-type Categoria to a Spesa is rejected with 422 problem+json (a Categoria only applies to Movimenti of its own tipo, FR-7).
- **AC3 — edit/delete recompute:** editing amount/date/Categoria/note or soft-deleting a Spesa persists with no silent loss, and derived Liquidità (Story 2.4) recomputes on next read.
- **AC4 — isolation:** another Utente's Categoria id (on create) or Spesa id (read/edit/delete) → 404/403, never their data (FR-4).

## Tasks / Subtasks

- [x] **Model + migration (AC1):** `Movimento` (`movimenti` table; `tipo`, `amount_cents` BIGINT, `data`, FK `categoria_id`, `note`, per-Utente, soft-delete); migration `f4a5b6c7d8e9`. [backend/app/models.py, backend/app/alembic/versions/f4a5b6c7d8e9_add_movimenti_table.py]
- [x] **CRUD via the choke point (AC1, AC4):** `POST/GET/PATCH/DELETE /api/v1/movimenti` through `UserScopedRepository[Movimento]`; cross-Utente Categoria/Movimento → 404. [backend/app/api/routes/movimenti.py, backend/app/api/main.py]
- [x] **tipo guard (AC2):** create/edit validate the referenced Categoria is owned and of the Movimento's tipo → 404 (missing/foreign) or 422 (tipo mismatch) problem+json. [backend/app/api/routes/movimenti.py]
- [x] **Wire into derived Liquidità (AC3):** `GET /liquidita` loads Movimenti (split per tipo) and feeds the pure engine; create/edit/delete are reflected on next read. [backend/app/api/routes/liquidita.py]
- [x] **Tests:** create in cents, tipo mismatch→422, zero/negative amount→422, Liquidità recompute on add/edit/delete, isolation (foreign Categoria→404, foreign Movimento→404), 401. [backend/tests/api/test_movimenti.py]

## Dev Notes

- One `movimenti` table serves both Spesa and Entrata (Story 2.6); the `tipo` field selects the space and `amount_cents` is the positive magnitude (sign implied by tipo in the calc engine). The quick-add UI (2.7) toggles tipo on one endpoint.
- `tipo` is immutable on edit (a Spesa never becomes an Entrata); a Categoria change re-validates tipo. PATCH applies only provided fields and never nulls a required column.
- Secchiello link (FR-5/FR-7) is deferred to Epic 3 (Story 3.1).

### Completion Notes List

_Backend implemented and verified locally: ruff + `ruff format --check` clean, mypy clean, `alembic upgrade head` applies `f4a5b6c7d8e9`, pytest 119 passed / 1 skipped. Live smoke test: iniziale 100000 → Spesa 30000 → Liquidità 70000; tipo mismatch → 422. Quick-add UI is Story 2.7._

### Change Log

| Date | Change |
|---|---|
| 2026-06-17 | Backend: `movimenti` table + CRUD via UserScopedRepository + tipo guard + wired into derived Liquidità + tests. Story done. |

### File List

**Added:** `backend/app/api/routes/movimenti.py`, `backend/app/alembic/versions/f4a5b6c7d8e9_add_movimenti_table.py`, `backend/tests/api/test_movimenti.py`
**Modified:** `backend/app/models.py` (Movimento domain), `backend/app/api/main.py` (movimenti router), `backend/app/api/routes/liquidita.py` (load Movimenti into the derived read), `frontend/src/lib/api/*` (regenerated client), `_bmad-output/implementation-artifacts/sprint-status.yaml`
