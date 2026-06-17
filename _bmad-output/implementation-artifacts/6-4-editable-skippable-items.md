---
baseline_commit: 9b21d88
---
# Story 6.4: Generated items editable & skippable, no rule mutation, no Drift (FR-8)
Status: done

## Summary
- Generated items are normal Movimenti / Versamenti PAC, edited via their own endpoints (single-item change; the Regola is untouched; future generation continues from the Regola).
- Skip = deleting a generated item: it is soft-deleted (excluded from Liquidità/Capitale) AND its regole_occorrenze row is marked skipped, so generation never re-materializes it (idempotent skip memory), while later occurrences still generate. Skipping never creates a Drift (the occurrence simply never moved money). Per-Utente isolation (404). Item-level edit/skip never mutates the Regola.

## Files
(Shared.) **Modified:** backend/app/api/routes/movimenti.py (skip on delete of a generated Entrata), backend/app/api/routes/patrimonio.py (skip on delete of a generated Versamento), backend/app/crud_ricorrenza.py (mark_skipped)
