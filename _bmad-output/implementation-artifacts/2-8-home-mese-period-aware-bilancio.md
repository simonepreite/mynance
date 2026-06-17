---
baseline_commit: af4d658
---

# Story 2.8: Home "Mese" — period-aware Bilancio + server-aggregated per-Categoria breakdown with drill-down (FR-13, UX-DR3)

Status: done

## Story

As an Utente, I want the Home to show a period-scoped Bilancio and a per-Categoria spend breakdown I can drill into, so that I see my month at a glance and can inspect any Categoria's Spese.

## Acceptance Criteria

- **AC1 — server aggregation:** Home requests a server-side period aggregation (`GET /api/v1/bilancio?period=&anchor=`) scoped by `utente_id`; the client never sums money (API-3).
- **AC2 — Bilancio + breakdown:** the endpoint returns Netto/Entrate/Spese (integer cents) and a per-Categoria Spese breakdown sorted largest→smallest (decision #14); boundaries are calendar dates (Europe/Rome).
- **AC3 — drill-down:** tapping a `category-row` opens that Categoria's Spese detail for the period; closing returns to Home.
- **AC4 — period-aware:** changing the granularity (Giorno/Settimana/Mese/Anno) or navigating with ‹ › re-fetches for the new period; the allocated/free split is NOT on Home (decision #12).
- **AC5 — empty/loading:** an empty period shows the calm "Ancora nessuna spesa…" state (no false bars); loading shows skeletons, not a blocking spinner.
- **AC6 — isolation:** only my Movimenti are aggregated (scoped by `utente_id`); unauthenticated → 401 (FR-4).

## Tasks / Subtasks

- [x] **Pure period math (AC2):** `app/calc/periodo.py` — `period_bounds(period, anchor)` half-open `[start,end)` (week=Mon), `month_anchors_back`. [backend/app/calc/periodo.py, backend/tests/calc/test_periodo.py]
- [x] **Bilancio endpoint (AC1, AC2, AC6):** `GET /api/v1/bilancio` loads Movimenti via the repository, filters to the period, sums per tipo via the calc helpers, groups Spese per Categoria sorted desc. [backend/app/api/routes/riepilogo.py, backend/app/models.py]
- [x] **Drill-down filters (AC3):** `GET /movimenti` gains optional `categoria_id` + `start`/`end` filters. [backend/app/api/routes/movimenti.py]
- [x] **Frontend Home (AC1–AC5):** `PeriodSelector` (granularity chips + ‹ › nav) + Netto `BalanceBlock` + Entrate/Spese + per-Categoria rows with proportional bars; tap → drill-down `Sheet` listing that Categoria's Spese; empty state + skeletons. [frontend/src/components/Common/PeriodSelector.tsx, frontend/src/lib/periodo.ts, frontend/src/routes/_layout/index.tsx]
- [x] **Tests:** empty period, aggregation + sort, period exclusion, invalid period→422, drill-down filter, isolation, 401. [backend/tests/api/test_riepilogo.py]

## Dev Notes

- `Movimento.data` is a date, so period bounds are timezone-free calendar dates (Europe/Rome calendar, no instant shift). The client computes only the anchor; the server owns the boundaries and all sums (API-3).
- Drill-down is a bottom `Sheet` (focus trap + restore) listing the Categoria's Spese for the active `[start,end)`; it lists (does not sum) so client filtering would also be safe, but the server filters.
- Home shows the period Netto, not total Liquidità (that lives on the Liquidità screen, UX-DR5/Epic 3); quick-add invalidates `["bilancio"]` so the Home refreshes after a capture.

### Completion Notes List

_Backend + frontend verified locally: ruff/mypy clean, pytest 133 passed / 1 skipped; `biome ci` clean, `tsc` + `vite build` green. The per-period charts/bars are rendered from server cents (no client math)._

### Change Log

| Date | Change |
|---|---|
| 2026-06-17 | Period calc + `GET /bilancio` aggregation + movimenti drill-down filters; Home "Mese" with PeriodSelector, Netto/Entrate/Spese, per-Categoria bars + drill-down. Story done. |

### File List

**Added:** `backend/app/calc/periodo.py`, `backend/app/api/routes/riepilogo.py`, `backend/tests/calc/test_periodo.py`, `backend/tests/api/test_riepilogo.py`, `frontend/src/lib/periodo.ts`, `frontend/src/components/Common/PeriodSelector.tsx`
**Modified:** `backend/app/models.py` (aggregation models), `backend/app/api/main.py` (riepilogo router), `backend/app/api/routes/movimenti.py` (drill-down filters), `frontend/src/routes/_layout/index.tsx` (Home Mese), `frontend/src/components/Common/QuickAdd.tsx` (invalidate bilancio), `frontend/src/lib/api/*` (regenerated client), `_bmad-output/implementation-artifacts/sprint-status.yaml`
