---
baseline_commit: 9b21d88
---
# Story 6.3: Extend generation to Versamenti PAC (FR-8)
Status: done

## Summary
- The same lazy idempotent pass materializes Versamenti PAC for versamento_pac Regole (importo + linked Investimento + regola_id), idempotent. Generated Versamenti reduce computed Liquidità and raise Capitale versato → total Patrimonio unchanged (reallocation, no double-count). Both kinds generate in one pass, each routed correctly, no future-dated items. A Regola whose Investimento was soft-deleted generates nothing and never errors the run.

## Files
(Shared with 6.1/6.2.) **Modified:** backend/app/crud_ricorrenza.py, backend/tests/api/test_regole.py
