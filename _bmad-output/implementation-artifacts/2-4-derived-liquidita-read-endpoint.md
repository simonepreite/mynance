---
baseline_commit: e2a1470
---

# Story 2.4: Derived Liquidità read endpoint (FR-13)

Status: done

## Story

As an Utente, I want an API endpoint that returns my current Liquidità computed server-side, so that every client shows the same derived-on-read value and never recomputes money locally.

## Acceptance Criteria

- **AC1 — derived server-side:** `GET /api/v1/liquidita` loads my stored inputs (Liquidità iniziale, my Entrate, my Spese — Capitale versato empty for now), scoped by `utente_id`, calls the pure calc engine (Story 2.3), and returns current Liquidità as integer cents (API-3: client never recomputes).
- **AC2 — reflects changes:** once Spese/Entrate exist (2.5/2.6), re-reading reflects them immediately (derived-on-read; no stale running balance).
- **AC3 — negative surfaced:** a negative derived value is returned with sign, never clamped to zero.
- **AC4 — unset baseline:** an unset Liquidità iniziale responds deterministically (baseline treated as 0 / surfaced via `iniziale_is_set`) without error.
- **AC5 — auth + isolation:** no valid token → 401, no data; a request can never return another Utente's Liquidità (inputs scoped by `utente_id`, FR-4).

## Tasks / Subtasks

- [x] **Endpoint (AC1, AC3, AC4):** `GET /api/v1/liquidita/` on the `liquidita` router → reads `current_utente.liquidita_iniziale_cents`, feeds the pure `compute_liquidita` engine (empty Entrate/Spese for now), returns `LiquiditaPublic {value_cents, iniziale_is_set}`. Negative values pass through unclamped; unset baseline → 0. [backend/app/api/routes/liquidita.py, backend/app/models.py]
- [x] **Tests (AC1, AC4, AC5):** unset → 0 / `iniziale_is_set=false`; reflects a set baseline; unauthenticated → 401; isolation (B never sees A's value). [backend/tests/api/test_liquidita_read.py]
- [x] **Client regen:** `LiquiditaService.readLiquidita()` available for the Home "Mese" (2.8) / Liquidità screen (Epic 3). [frontend/src/lib/api/*]

## Dev Notes

- The endpoint stays read-only and side-effect free; it composes the Story 2.3 pure engine with scoped inputs. The only stored input today is the per-Utente baseline (already scoped via `current_utente`), so no extra DB query is needed yet — Stories 2.5/2.6 will load Movimenti through the `UserScopedRepository` and pass them to the same engine (AC2 then becomes observable).
- UI consumption is deferred to the Home "Mese" (Story 2.8); 2.4 ships the endpoint + typed client only. The Liquidità bottom-nav tab remains a calm stub until its Epic 3 screen.
- `GET /liquidita/` and `GET|PUT /liquidita/iniziale` coexist on the same router.

### Completion Notes List

_Backend-only (+ client regen). Verified locally: ruff + `ruff format --check` clean, mypy clean, pytest 110 passed / 1 skipped; frontend `biome ci` + `tsc`/`vite build` green after client regen._

### Change Log

| Date | Change |
|---|---|
| 2026-06-17 | `GET /liquidita/` derived read endpoint composing the pure engine + tests; regenerated typed client. Story done. |

### File List

**Added:** `backend/tests/api/test_liquidita_read.py`
**Modified:** `backend/app/api/routes/liquidita.py` (derived read), `backend/app/models.py` (LiquiditaPublic), `frontend/src/lib/api/*` (regenerated client), `_bmad-output/implementation-artifacts/sprint-status.yaml`
