---
baseline_commit: badb988
---

# Story 4.2: Computed reconciliation reminder, no scheduler (FR-16)

Status: done

## Summary
- GET /riconciliazione/promemoria computes on read: due = (no Riconciliazione yet) OR (today − last ≥ N); returns giorni_dall_ultima, data_ultima_riconciliazione (null if never), intervallo_giorni, and drift_aperto_cents (the snapshot Drift of the latest acknowledged-open Riconciliazione, else null). No scheduler/stored flag.
- Never-reconciled accounts are honestly flagged due (baseline = account creation). Day delta uses calendar dates.
- Frontend ReconcileBanner (warm-amber HonestyBanner) on every primary screen when due, or a quiet open-Drift indicator; taps into the flow; dismiss-to-later does not reset the timer (timer only resets on confirm).

## Files
**Modified:** backend/app/api/routes/riconciliazione.py, frontend/src/components/Common/ReconcileBanner.tsx, frontend/src/routes/_layout.tsx
