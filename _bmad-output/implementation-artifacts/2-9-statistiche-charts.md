---
baseline_commit: af4d658
---

# Story 2.9: Statistiche charts — cross-period trends + per-period Spese pie (UX-DR6)

Status: done

## Story

As an Utente, I want a charts-only Statistiche screen showing how my money moves over time and a per-period Spese share by Categoria, so that I understand trends and where my spending concentrates without manual math.

## Acceptance Criteria

- **AC1 — charts only:** Statistiche shows charts (no lists) and shares the Home `period-selector`.
- **AC2 — server aggregation:** data comes from `GET /api/v1/statistiche?period=&anchor=` scoped by `utente_id`, all aggregates in integer cents; the client renders but never sums (API-3).
- **AC3 — trends:** cross-period line charts (Spese / Entrate / Netto month-over-month) computed server-side with month boundaries on the calendar (Europe/Rome).
- **AC4 — pie:** the selected period's Spese share by Categoria, computed server-side.
- **AC5 — insufficient data:** with too little history (or no Spese in the period) it shows the calm "Servono più dati per i grafici" message — never a fabricated/empty chart.
- **AC6 — loading + isolation:** loading shows skeletons; only my Movimenti are aggregated; unauthenticated → 401 (FR-4).

## Tasks / Subtasks

- [x] **Statistiche endpoint (AC2, AC3, AC4, AC6):** `GET /api/v1/statistiche` returns a 6-month month-over-month `trend` (entrate/spese/netto cents) + the selected period's `pie` (Spese per Categoria), with `has_trend` (≥2 months with data) / `has_pie` flags. [backend/app/api/routes/riepilogo.py, backend/app/models.py]
- [x] **Frontend charts (AC1, AC3, AC4, AC5, AC6):** charts-only screen sharing `PeriodSelector`; hand-rolled SVG line chart (entrate/spese/netto with a zero baseline + legend) and SVG pie with a percentage legend; "Servono più dati" empty state; skeletons. [frontend/src/routes/_layout/statistiche.tsx]
- [x] **Tests:** pie + 6-point trend, `has_pie`/`has_trend` flags (sufficient & insufficient), isolation/401. [backend/tests/api/test_riepilogo.py]

## Dev Notes

- Charts are **hand-rolled SVG** — no charting dependency. A new npm dependency can't be added here because CI runs `bun install --frozen-lockfile` and the `bun.lock` can't be regenerated in this environment (native bun is blocked by the corporate proxy). SVG keeps it dependency-free and theme-token styled.
- Colour is never the only signifier: every series/slice has a text legend (UX-DR12). The "non identificato" system Categoria (Epic 4) will appear in the pie like any other once it exists.
- The trend is always the last 6 months regardless of the selected granularity (month-over-month is the meaningful trend unit); the pie follows the selected period.

### Completion Notes List

_Backend + frontend verified locally: ruff/mypy clean, pytest 133 passed / 1 skipped; `biome ci` clean, `tsc` + `vite build` green. Browser e2e for the charts is not run locally (Playwright blocked by the proxy); the theme e2e runs in CI._

### Change Log

| Date | Change |
|---|---|
| 2026-06-17 | `GET /statistiche` (trend + pie + flags) + charts-only Statistiche screen (SVG trend lines + pie, calm insufficient-data state). Story done — Epic 2 complete. |

### File List

**Added:** (shared with 2.8) `backend/app/api/routes/riepilogo.py`, `backend/tests/api/test_riepilogo.py`
**Modified:** `backend/app/models.py` (Statistiche/TrendPunto models), `frontend/src/routes/_layout/statistiche.tsx` (charts), `frontend/src/lib/api/*` (regenerated client), `_bmad-output/implementation-artifacts/sprint-status.yaml`
