---
baseline_commit: badb988
---

# Story 4.3: Reconcile real Liquidità and show Drift in € and % (FR-17)

Status: done

## Summary
- POST /riconciliazione/anteprima → DriftPreview { liquidita_calcolata_cents, drift_cents = reale − calcolata (signed), drift_percent = (R−C)/C×100 rounded (null when C=0, no divide-by-zero) }. Computed server-side from cents (API-3).
- Negative computed Liquidità surfaced honestly (drift not clamped).
- POST /riconciliazione persists a Riconciliazione snapshot (reale, calcolata, drift, data=today, esito); the row is the audit record. Per-Utente write only.
- Frontend flow: BalanceBlock(calcolata) + real input (€, Italian comma) + live Drift € and % in warm amber.

## Files
**Modified:** backend/app/api/routes/riconciliazione.py, backend/app/models.py, frontend/src/routes/_layout/riconciliazione.tsx
