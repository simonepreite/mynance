---
baseline_commit: e3ac5e8
---

# Story 2.2: Set Liquidità iniziale once with re-baseline audit (FR-12)

Status: done

## Story

As an Utente, I want to set my Liquidità iniziale a single time and have any later change recorded as an audited re-baselining, so that all derived figures start from an honest baseline and any shift of that baseline is traceable.

## Acceptance Criteria

- **AC1 — unset on a new account:** reading Liquidità iniziale on a fresh account reports as unset (no baseline, per FR-1).
- **AC2 — set in cents, validated:** setting an integer-cents value stores it in cents (BIGINT, `*_cents`) scoped to `utente_id`; zero is permitted, a negative or non-integer-cents value is rejected with 422 problem+json.
- **AC3 — re-baseline audit:** changing an already-set value is allowed but recorded as a re-baselining event (old value, new value, timestamp, `utente_id`); the response flags it (`rebaselined: true`) because it shifts all derived figures.
- **AC4 — isolation:** another Utente's baseline can never be read or changed (no id in the path → only the caller's own value is addressable; FR-4).

## Tasks / Subtasks

- [x] **Model + migration (AC1, AC2, AC3):** nullable `liquidita_iniziale_cents` (BIGINT) on `utenti` (NULL = unset) + append-only `RebaselineAudit` (`rebaseline_audit` table: old/new value cents, `utente_id`, `created_at`); migration `e3f4a5b6c7d8`. [backend/app/models.py, backend/app/alembic/versions/e3f4a5b6c7d8_add_liquidita_iniziale_and_rebaseline_audit.py]
- [x] **Service (AC2, AC3):** `crud_liquidita.set_liquidita_iniziale` — first set is not audited; changing an already-set value to a different one writes an audit row and returns `rebaselined=True`. [backend/app/crud_liquidita.py]
- [x] **Endpoints (AC1–AC4):** `GET /api/v1/liquidita/iniziale` (value + `is_set`) and `PUT /api/v1/liquidita/iniziale` (`value_cents` ≥ 0; 422 on negative/non-integer); both keyed to `current_utente` only (no id → isolation). [backend/app/api/routes/liquidita.py, backend/app/api/main.py]
- [x] **Tests:** unset, set-without-audit, zero permitted, negative→422, non-integer→422, change→audit row written + `rebaselined`, same-value→no audit, per-Utente isolation, unauthenticated→401. [backend/tests/api/test_liquidita_iniziale.py]
- [x] **Frontend wiring:** Impostazioni section reads the current baseline and sets/updates it (euro→cents parse with no float drift), surfacing the re-baselining toast; the Home first-run onboarding prompt ("Imposta ora") routes here. [frontend/src/routes/_layout/settings.tsx, frontend/src/lib/money.ts]

## Dev Notes

- The baseline is a single value per Utente, so it lives on the `utenti` row (NULL = unset) rather than a child table; with no id in the path, a request can only ever touch the caller's own value (AC4 holds without an explicit choke-point lookup).
- `value_cents: int = Field(ge=0)` gives free 422 validation: negatives fail `ge=0`, and a non-integer JSON number (e.g. `100.5`) fails int parsing — both surface as problem+json via the Story 1.1 handlers.
- The re-baseline audit is append-only and not yet surfaced via an endpoint (none required by the ACs); it exists for traceability and a future history view.
- Frontend money entry is parsed to integer cents client-side only for the request (`lib/money.ts`); money is never derived on the client (the derived Liquidità read lands in Story 2.4).

### Completion Notes List

_Backend + frontend implemented and verified locally. Backend (Docker Postgres + uv): ruff check + `ruff format --check` clean, mypy clean, `alembic upgrade head` applies `e3f4a5b6c7d8`, **pytest 98 passed / 1 skipped** (9 new). Frontend (Node 22 + npm): `biome ci .` clean, `tsc` + `vite build` green. Live smoke test confirmed: unset → set (`rebaselined:false`) → change (`rebaselined:true`, persisted) → negative/non-integer → 422._

### Change Log

| Date | Change |
|---|---|
| 2026-06-17 | Backend: `liquidita_iniziale_cents` on `utenti` + `rebaseline_audit` table + migration + `crud_liquidita` + GET/PUT `/liquidita/iniziale` + tests. Frontend: Impostazioni setter (euro→cents) + re-baseline toast + onboarding link. Story done. |

### File List

**Added:** `backend/app/crud_liquidita.py`, `backend/app/api/routes/liquidita.py`, `backend/app/alembic/versions/e3f4a5b6c7d8_add_liquidita_iniziale_and_rebaseline_audit.py`, `backend/tests/api/test_liquidita_iniziale.py`, `frontend/src/lib/money.ts`
**Modified:** `backend/app/models.py` (Utente baseline + RebaselineAudit + request/response models), `backend/app/api/main.py` (liquidita router), `frontend/src/routes/_layout/settings.tsx` (Liquidità iniziale section), `frontend/src/lib/api/*` (regenerated client), `_bmad-output/implementation-artifacts/sprint-status.yaml`
