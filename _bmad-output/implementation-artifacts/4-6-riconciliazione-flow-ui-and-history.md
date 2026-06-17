---
baseline_commit: badb988
---

# Story 4.6: Riconciliazione flow UI and reconciliation history (UX-DR8)

Status: done

## Summary
- /riconciliazione screen (reached via the honesty banner or TopBar → Riconciliazione): Liquidità calcolata, real-Liquidità input (€), live Drift € and %, two calm actions — "Chiudi lo scostamento" (4.4) and "Lascia aperto" (4.5) — warm/honesty register, never alarm-red, never modal.
- On confirm: quiet toast, returns to Home, the now-reset reminder no longer shows due, closed gap reflected immediately (invalidates liquidita/promemoria/bilancio/allocazione/secchielli/riconciliazioni).
- History list (GET /riconciliazione, most-recent first): data, reale/calcolata snapshot, Drift € and %, esito; calm empty state when none.
- Save failure: non-optimistic, warm retry, no data dropped.

## Files
**Added:** frontend/src/routes/_layout/riconciliazione.tsx, frontend/src/components/Common/ReconcileBanner.tsx
**Modified:** frontend/src/routes/_layout.tsx, frontend/src/components/Common/TopBar.tsx, frontend/src/lib/api/*
