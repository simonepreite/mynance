---
baseline_commit: e33392a
---

# Story 3.5: Allocation breakdown — Liquidità allocata vs Risparmio libero (FR-14; UX-DR5 tab A)

Status: done

## Acceptance Criteria (summary)

- **AC1 — server-side split:** `Liquidità allocata = Σ max(0, Saldo)`, `Risparmio libero = Liquidità − allocata`, integer cents in `app/calc/allocazione.py`; a negative Saldo contributes 0 to the allocation total (bucket still shows its own negative Saldo).
- **AC2 — tab A Allocazione:** a balance-block with total Liquidità, then the allocata / libero split; this split appears only here (never Home).
- **AC3 — live reconcile:** invalidating the affected keys updates allocata/libero.
- **AC4 — stale marking / AC5 isolation:** scoped by `utente_id`; never another Utente's figures.

## Implementation

- Pure `liquidita_allocata` / `risparmio_libero` in `app/calc/allocazione.py`.
- `GET /api/v1/liquidita/allocazione` composes the derived Liquidità (Story 2.4), each Secchiello Saldo (Story 3.2 engine), and the split, scoped per-Utente. [backend/app/api/routes/liquidita.py, backend/app/models.py AllocazionePublic]
- Frontend Allocazione tab (`liquidita.tsx`): total `BalanceBlock` + allocata/libero cards; secchiello mutations invalidate `['allocazione']`.
- Tests: pure (allocata clamps negatives, libero can be negative) + API (allocata == max(0, secchiello saldo), libero == liquidità − allocata, isolation/401).

### File List

**Added:** `backend/app/calc/allocazione.py`, `backend/tests/calc/test_allocazione.py`, `backend/tests/api/test_allocazione.py`
**Modified:** `backend/app/api/routes/liquidita.py`, `backend/app/models.py`, `frontend/src/routes/_layout/liquidita.tsx`, `frontend/src/lib/api/*`, sprint-status
