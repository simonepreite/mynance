---
baseline_commit: 9b21d88
---
# Story 6.1: RegolaRicorrente model + CRUD (FR-8)
Status: done

## Summary
- regole_ricorrenti table (importo_cents, periodicita, intervallo_mesi, day_of_period 1–31, kind entrata|versamento_pac, nullable categoria_id/investimento_id, start_date, note, soft-delete) + regole_occorrenze ledger; regola_id back-ref added to movimenti & versamenti_pac. Migration d8e9f0a1b2c3.
- POST/GET/PATCH/DELETE /regole-ricorrenti; entrata requires an owned Entrata-type Categoria (422/404 otherwise), versamento_pac requires an owned Investimento; day_of_period out of 1–31 → 422; custom periodicità needs an interval. List returns {items,total,limit,offset}. Editing a Regola never rewrites already-generated items. Per-Utente isolation (404).

## Files
**Added:** backend/app/api/routes/regole.py, backend/app/crud_ricorrenza.py, backend/app/calc/ricorrenza.py, backend/app/alembic/versions/d8e9f0a1b2c3_*.py, backend/tests/api/test_regole.py, backend/tests/calc/test_ricorrenza.py, frontend/src/routes/_layout/regole.tsx
**Modified:** backend/app/models.py, backend/app/api/main.py, frontend/src/routes/_layout/settings.tsx, frontend/src/lib/api/*
