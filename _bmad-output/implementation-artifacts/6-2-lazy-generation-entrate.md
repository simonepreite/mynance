---
baseline_commit: 9b21d88
---
# Story 6.2: Lazy idempotent generation of recurring Entrate up-to-today (FR-8, AR-Regole-Lazy)
Status: done

## Summary
- Pure app/calc/ricorrenza.occorrenze_due: occurrences from start_date to today only (no future), day clamped to short months, custom intervals; deterministic. Worked-example tests.
- crud_ricorrenza.run_generation materializes one Entrata Movimento per due occurrence (Regola importo + Categoria + date + regola_id back-ref); idempotent via the regole_occorrenze ledger (already-materialized/skipped never regenerated); back-fills all past occurrences in one pass. Triggered on access (GET /movimenti and GET /liquidita) — no scheduler. Generated Entrate feed derived-on-read Liquidità. Per-Utente scoped.

## Files
(Shared with 6.1.) **Added:** backend/app/calc/ricorrenza.py, backend/app/crud_ricorrenza.py
**Modified:** backend/app/api/routes/{movimenti,liquidita}.py (generation trigger)
