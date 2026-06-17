---
baseline_commit: e33392a
---

# Story 3.6: Cuscinetto di sicurezza warning with Spesa media mensile (FR-15; UX-DR5 tab A)

Status: done

## Acceptance Criteria (summary)

- **AC1 — Spesa media mensile:** mean of Spese over the last N complete calendar months (current partial month excluded), N default 6, configurable; averages over available months if fewer; "non identificato" Spese included (honesty).
- **AC2 — Cuscinetto:** `N × Spesa media mensile`, integer cents, worked-example tested.
- **AC3/AC4 — card + warning:** the Allocazione tab shows the target floor and whether Risparmio libero sits above/below; below → warm-amber honesty indicator `Risparmio libero sotto il Cuscinetto di sicurezza (N mesi)`, treated as honesty data, not an error.
- **AC5/AC6 — live recompute + new account:** recomputes on invalidation; a brand-new account returns a coherent figure (no div-by-zero) and a calm state.

## Implementation

- Pure `spesa_media_mensile` (mean of provided complete-month totals, 0 when none) + `cuscinetto` (N × media) in `app/calc/allocazione.py`.
- `GET /liquidita/allocazione?mesi=N` (default 6) builds the complete-month Spese totals — last N months before the current, restricted to months at/after the first recorded Spesa (so new accounts average over what exists) — and returns `spesa_media_mensile_cents`, `cuscinetto_cents`, `sotto_cuscinetto`. [backend/app/api/routes/liquidita.py]
- Frontend Cuscinetto card (`liquidita.tsx`): target + spesa media, with a `HonestyBanner` when `sotto_cuscinetto`, else a calm "copre il cuscinetto" note.
- Tests: pure mean/empty/rounding + cuscinetto; API (media over 2 complete months, cuscinetto = 6 × media, sotto flag), calm zeroes on an empty account.

### File List

(Shared with 3.5.) **Modified:** `backend/app/calc/allocazione.py`, `backend/app/api/routes/liquidita.py`, `frontend/src/routes/_layout/liquidita.tsx`, `backend/tests/calc/test_allocazione.py`, `backend/tests/api/test_allocazione.py`
