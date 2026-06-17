---
baseline_commit: badb988
---

# Story 4.5: Acknowledge and leave the Drift open (FR-18)

Status: done

## Summary
- Confirm with esito=acknowledged_open: no Movimento, computed Liquidità unchanged; data_riconciliazione=today (timer resets) and the open drift_cents snapshotted.
- The reconcile-due banner does NOT re-fire (timer reset, SM-C2), but the open Drift stays visible as a quiet warm-amber indicator (promemoria.drift_aperto_cents) until a later close clears it.
- Per-Utente isolation: another Utente's open Drift is never surfaced.

## Files
**Modified:** backend/app/api/routes/riconciliazione.py, frontend/src/components/Common/ReconcileBanner.tsx, frontend/src/routes/_layout/riconciliazione.tsx
