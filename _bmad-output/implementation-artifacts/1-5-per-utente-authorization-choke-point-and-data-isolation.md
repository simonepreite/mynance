---
baseline_commit: 2238780
---

# Story 1.5: Per-Utente authorization choke point and data isolation (FR-4, AR-AuthZ)

Status: in-progress

## Story

As an authenticated Utente, I want every read and write to be automatically scoped to my own data, so that no other Utente can ever read or write my financial information and I can never see theirs.

## Acceptance Criteria

- **AC1 — choke point:** all owned-data access goes through a user-scoped base repository (`services/repository.py`) that always filters by `utente_id`; routers never query owned models directly.
- **AC2 — identity from JWT:** the current Utente is resolved from the validated JWT via `current_utente`, scoping every downstream query.
- **AC3 — cross-Utente blocked:** A accessing/editing/deleting B's entity → 404 (problem+json), never B's data.
- **AC4 — no existence leak:** a non-existent id returns the same not-found shape as cross-Utente access.
- **AC5 — isolation tests:** at least one test asserting cross-Utente access returns not-found and never the data, covering the choke point for each entity type introduced.
- **AC6 — future endpoints:** any later endpoint must query through the user-scoped repository; a query missing the `utente_id` scope is a defect (review/CI per architecture anti-patterns).

## Tasks / Subtasks

- [x] **`UserScopedRepository` (AC1, AC3, AC4):** generic repo (`get`/`list`/`add`/`update`/`delete`) that always filters by `utente_id`; cross-Utente and missing rows are indistinguishable (both → `None`/`False`); `add` forces ownership; soft-delete honored when the model has `deleted_at`. [backend/app/services/repository.py]
- [x] **Identity dependency (AC2):** `current_utente` (from Story 1.4) supplies the `utente_id` that scopes a repository instance.
- [x] **Isolation tests (AC5):** cross-Utente + non-existent indistinguishable, `add` forces ownership, soft-delete hides rows — via a throwaway owned model (stand-in until Epic 2 entities). [backend/tests/services/test_repository_isolation.py]
- [x] **AC6:** documented as an architecture anti-pattern (queries missing `utente_id` scope) — enforced in review/CI; Epic-2 routers will instantiate `UserScopedRepository` per entity.

## Dev Notes

- The repository is the single authZ choke point: routers in later epics MUST go through it and never query owned models directly. Cross-Utente access and truly-missing rows both return the not-found shape → no existence leak (AC3/AC4).
- No owned entity tables exist yet (they arrive in Epic 2); the isolation tests use an in-test throwaway model + table so the mechanism is proven now. Each Epic-2 entity adds its own isolation test per AC5.

### Completion Notes List

_Repository + isolation tests implemented; ruff check + `ruff format --check` clean locally; mypy/pytest in CI. Backend-only story (no UI); fully delivered here._

### Change Log

| Date | Change |
|---|---|
| 2026-06-16 | UserScopedRepository choke point + per-Utente isolation tests (cross-Utente/missing parity, forced ownership, soft-delete). |

### File List

**Added:** `backend/app/services/__init__.py`, `backend/app/services/repository.py`, `backend/tests/services/__init__.py`, `backend/tests/services/test_repository_isolation.py`
**Modified:** `_bmad-output/implementation-artifacts/sprint-status.yaml`
