---
baseline_commit: cd898b8
---

# Story 1.4: Login, 30-day session, and logout (FR-2)

Status: done

## Story

As a registered Utente, I want to log in with my username and password and stay authenticated across a 30-day session that I can also end explicitly, so that I have secure, persistent access without re-authenticating constantly.

## Acceptance Criteria

- **AC1 — login → JWT:** correct username+password → authenticated, JWT issued, used as a Bearer token.
- **AC2 — invalid credentials:** single plain non-blaming message that does not reveal whether the username exists.
- **AC3 — 30-day session:** token valid for the per-Utente `session_timeout_days` (default 30); after expiry the next protected request is 401.
- **AC4 — logout:** explicit logout ends the session immediately; protected requests thereafter return 401.
- **AC5 — unauthenticated:** any protected request without a valid token → 401 problem+json; frontend route guard redirects to login.
- **AC6 — rate limiting:** repeated attempts on login/recovery from the same origin are rate-limited to resist brute force.

## Tasks / Subtasks

- [x] **Backend — login (AC1, AC2, AC3):** `POST /api/v1/auth/login` (JSON username+password) → `crud_utente.authenticate` (constant-time miss) → JWT with `jti`, expiry = `timedelta(days=session_timeout_days)`. Invalid creds → single generic 400 problem+json. [backend/app/api/routes/auth.py, backend/app/crud_utente.py]
- [x] **Backend — session dependency + protected route (AC5):** `get_current_utente`/`CurrentUtente` in `deps.py` (decode JWT, denylist check, load Utente, 401 problem+json on any failure); `GET /api/v1/auth/me` protected. [backend/app/api/deps.py]
- [x] **Backend — logout (AC4):** `POST /api/v1/auth/logout` revokes the token `jti` via an in-memory denylist; subsequent requests with that token → 401. [backend/app/core/auth_state.py]
- [x] **Backend — rate limiting (AC6):** in-memory sliding-window limiter on login + recover (keyed by client host + username), → 429 over threshold. [backend/app/core/auth_state.py]
- [x] **Backend — tests:** login→token + `/me`; wrong password→generic 400; `/me` without token→401 problem+json; logout→`/me` 401; rate-limit→429. [backend/tests/api/test_auth_login.py]
- [x] **Frontend — login screen + route guard + logout (AC1/AC4/AC5 UI):** `useAuth` rewired to `/auth/login` (JSON username+password → Bearer token in localStorage), `/auth/me` (`UtentePublic`), and `/auth/logout` (server revocation, then local clear + redirect); login form switched from email to username; the `_layout` `beforeLoad` guard redirects unauthenticated users to `/login` (AC5) and the global 401/403 handler clears the token and bounces to login. [frontend/src/hooks/useAuth.ts, frontend/src/routes/login.tsx, frontend/src/main.tsx, frontend/src/components/Sidebar/User.tsx]

## Dev Notes

- Stateless JWT (pyjwt, reused). Logout/denylist + rate-limiter are **in-memory** (`app/core/auth_state.py`): process-local, reset on restart — adequate for the single-instance MVP; a Redis-backed store is the documented upgrade for horizontal scaling. "30-day idle" is implemented as a 30-day token lifetime (configurable per-Utente).
- Invalid-credential and recovery messages are intentionally identical/non-revealing; `authenticate` runs a dummy argon2 verify on miss (constant-time).
- 401s and 429s surface as problem+json via the Story 1.1 handlers.

### Completion Notes List

_Backend implemented and locally verified (ruff check + `ruff format --check` clean; syntax OK). mypy/pytest run in CI._

_Frontend completed 2026-06-17 once the env was restored (Docker DB + native uv; Node 22/npm toolchain since native bun is blocked by the corporate Cisco proxy on the github asset CDN — see story note). OpenAPI client regenerated against the live `/auth` + `/categorie` spec. Verified locally: `biome ci .` clean, `tsc` + `vite build` green, plus a live smoke test — login issues a 30-day Bearer token, `/auth/me` returns the Utente, logout revokes the token and a subsequent `/auth/me` with the same token returns 401 (AC4)._

### Change Log

| Date | Change |
|---|---|
| 2026-06-16 | Backend: username login + JWT(jti) + session expiry + current_utente dep + /me + logout denylist + in-memory rate limiting + tests. Frontend login UI deferred (env-blocked). |
| 2026-06-17 | Frontend: `useAuth` rewired to `/auth/login`/`/auth/me`/`/auth/logout`; login form username-based; route guard + 401 redirect confirmed. Live smoke test confirms 30-day token + logout revocation. Story done. |

### File List

**Added:** `backend/app/core/auth_state.py`, `backend/tests/api/test_auth_login.py`
**Modified:** `backend/app/api/routes/auth.py` (login/logout/me), `backend/app/api/deps.py` (current_utente), `backend/app/core/security.py` (jti), `backend/app/crud_utente.py` (authenticate), `backend/app/models.py` (UtenteLogin, TokenPayload.jti), `frontend/src/hooks/useAuth.ts` (auth wiring), `frontend/src/routes/login.tsx` (username login), `frontend/src/components/Sidebar/User.tsx` (username display + logout), `_bmad-output/implementation-artifacts/sprint-status.yaml`
