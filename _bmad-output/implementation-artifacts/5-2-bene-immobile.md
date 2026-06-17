---
baseline_commit: 2df118c
---
# Story 5.2: Register a Bene immobile at price paid (FR-20)
Status: done

## Summary
- beni_immobili table; prezzo_cents BIGINT; Valore static at price paid, no market estimate. POST/GET/PATCH/DELETE /beni-immobili.
- Registration never changes Liquidità (FR-22) — the UI states the purchase Spesa is recorded separately. Per-Utente isolation.

## Files
(Shared with 5.1.) **Modified:** backend/app/api/routes/patrimonio.py, backend/app/models.py, frontend/src/routes/_layout/patrimonio.tsx
