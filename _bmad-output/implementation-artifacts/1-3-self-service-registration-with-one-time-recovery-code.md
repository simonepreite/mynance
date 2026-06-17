---
baseline_commit: dcb3408
---

# Story 1.3: Self-service registration with one-time recovery code (FR-1, FR-3)

Status: done

## Story

As an anonymous visitor,
I want to create an account with a username and password and be shown a one-time recovery code to save,
So that I get an isolated, empty dataset and a way to regain access if I forget my password.

## Acceptance Criteria

- **AC1 — `utenti` migration:** Alembic migration creates `utenti` (UUID PK, unique `username`, `password_hash`, `recovery_code_hash`, `session_timeout_days` default 30, `created_at`/`updated_at`/`deleted_at`); no other entity tables.
- **AC2 — register:** unique username + password → new Utente, empty dataset, no Liquidità iniziale; password stored only as an argon2 salted hash; plaintext never persisted/logged.
- **AC3 — duplicate username:** rejected with a clear plain-Italian problem+json message; no Utente created.
- **AC4 — recovery code shown once:** a one-time recovery code generated, shown exactly once with "save now" framing; stored only as a salted hash; never retrievable afterward.
- **AC5 — recovery flow:** correct username + recovery code → regain access and set a new password; existing password never exposed.
- **AC6 — wrong username/code:** rejected with a message that does not reveal whether the account exists.
- **AC7 — lost code:** UI states plainly the account cannot be recovered without it (no false back-channel promise).

## Tasks / Subtasks

- [x] **Backend — model + migration (AC1, AC2):** `Utente` SQLModel (`utenti` table) + hand-written Alembic migration `c1d2e3f4a5b6` (down_revision = head `fe56fa70289e`). [backend/app/models.py, backend/app/alembic/versions/c1d2e3f4a5b6_add_utenti_table.py]
- [x] **Backend — security (AC2, AC4):** `generate_recovery_code` (unambiguous alphabet, grouped, ~100 bits), `hash_recovery_code`/`verify_recovery_code` (argon2 via pwdlib, reused). [backend/app/core/security.py]
- [x] **Backend — service + endpoints (AC2–AC6):** `crud_utente` (`get_utente_by_username`, `create_utente` → returns one-time code, `recover_utente` with constant-time miss); `POST /api/v1/auth/register` (201, returns code once), `POST /api/v1/auth/recover` (generic non-revealing error); wired into `api/main.py`. Errors as problem+json (Italian). [backend/app/crud_utente.py, backend/app/api/routes/auth.py, backend/app/api/main.py]
- [x] **Backend — tests:** register + hashes-not-plaintext, duplicate→409 problem+json, recover happy path, wrong code→generic 400, unknown username→same generic 400. [backend/tests/api/test_auth.py]
- [x] **Frontend — registration + recovery screens (AC4 framing, AC5, AC7 lost-code state):** username/password registration form; one-time recovery-code reveal panel with "lo vedrai solo questa volta" framing, copy-to-clipboard, and a "Ho salvato il codice" gate before continuing; recovery form (username + recovery code + new password); and an explicit "senza il codice non è recuperabile" (AC7) note on the recovery screen. [frontend/src/routes/signup.tsx, frontend/src/routes/recover-password.tsx]

## Dev Notes

- Reuses the template's JWT/argon2 scaffold (pwdlib) per architecture; mynance `Utente` (username) is distinct from the template's email `User` (kept only for the seeded superuser/template tests).
- Tables come only from migrations (`init_db` does not `create_all`); CI runs `alembic upgrade head` before pytest, so the migration is load-bearing.
- Constant-time recovery check via a dummy argon2 hash when the username is absent (no existence leak; mirrors `crud.authenticate`).
- Domain/DB conventions honored: Italian noun `Utente`, plural table `utenti`, UUID PK, snake_case, `created_at`/`updated_at`/`deleted_at`, `ix_utenti_username` unique.

### Completion Notes List

_Backend implemented; local verification: ruff check + `ruff format --check` clean (0.15.16), syntax OK. mypy/alembic/pytest verified in CI._

_Frontend completed 2026-06-17 (env restored: native uv + Node 22/npm toolchain, OpenAPI client regenerated). Verified locally: `biome ci .` clean, `tsc` + `vite build` green, and a live end-to-end smoke test against the running backend (register → one-time recovery code shown → login → recover with code → 422 on bad input). One-time-code reveal, copy + "ho salvato" gate, and AC7 lost-code message all in place._

### Change Log

| Date | Change |
|---|---|
| 2026-06-16 | Backend: Utente model + utenti migration + recovery-code security + register/recover endpoints + problem+json + tests. Frontend auth UI deferred. |
| 2026-06-17 | Frontend: registration form (username/password), one-time recovery-code reveal panel (copy + "ho salvato" gate), recovery form (username + code + new password), AC7 "non recuperabile" note. Story done. |

### File List

**Added:** `backend/app/crud_utente.py`, `backend/app/api/routes/auth.py`, `backend/app/alembic/versions/c1d2e3f4a5b6_add_utenti_table.py`, `backend/tests/api/test_auth.py`
**Modified:** `backend/app/models.py` (Utente domain), `backend/app/core/security.py` (recovery-code helpers), `backend/app/api/main.py` (auth router), `frontend/src/routes/signup.tsx` (registration + one-time recovery-code panel), `frontend/src/routes/recover-password.tsx` (recovery flow + AC7 note), `_bmad-output/implementation-artifacts/sprint-status.yaml`
