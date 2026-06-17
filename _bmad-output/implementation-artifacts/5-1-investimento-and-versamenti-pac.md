---
baseline_commit: 2df118c
---
# Story 5.1: Investimento + Versamenti PAC at Capitale versato (FR-19)
Status: done

## Summary
- investimenti + versamenti_pac tables (migration c7d8e9f0a1b2). Investimento value = Σ Versamenti PAC (Capitale versato), starts at 0; **no market-value field** anywhere.
- POST/GET/PATCH/DELETE /investimenti and nested versamenti (POST/GET under /investimenti/{id}/versamenti, PATCH/DELETE /versamenti/{id}); importo_cents gt 0 → 422 otherwise.
- A Versamento PAC lowers derived Liquidità (FR-13 capitale_versato term) — wired via crud_liquidita.compute_current_liquidita, the single source now used by the Liquidità read, allocation, reconciliation, and Patrimonio. Edit/delete recompute consistently.
- Per-Utente isolation (404 cross-Utente).

## Files
**Added:** backend/app/api/routes/patrimonio.py, backend/app/calc/patrimonio.py, backend/app/alembic/versions/c7d8e9f0a1b2_*.py, backend/tests/api/test_patrimonio.py, backend/tests/calc/test_patrimonio.py, frontend/src/routes/_layout/patrimonio.tsx
**Modified:** backend/app/models.py, backend/app/crud_liquidita.py (compute_current_liquidita), backend/app/api/routes/{liquidita,riconciliazione}.py (use the shared helper), backend/app/api/main.py, frontend/src/lib/api/*
