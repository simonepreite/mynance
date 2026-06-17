---
baseline_commit: 2df118c
---
# Story 5.4: Patrimonio screen — total net worth + per-component breakdown (FR-22, UX-DR7)
Status: done

## Summary
- GET /patrimonio → Patrimonio = Liquidità + Capitale versato totale + Σ Beni immobili + Σ Beni mobili (derived), with per-component values; negative Liquidità summed with sign (never clamped). Per-Utente scoped.
- Reallocation offset (FR-22): a Versamento PAC lowers Liquidità and raises Capitale versato by the same amount → total unchanged (tested). Asset registration adds the asset's Valore while Liquidità is unchanged (no auto-deduct / double-count).
- Frontend Patrimonio screen (replaces the stub): total BalanceBlock + 4 component cards (Liquidità links to the Liquidità screen) + manage sections for Investimenti (with Versa), Beni immobili, Beni mobili; mutations invalidate patrimonio/liquidita/component keys. Note: inline edit forms are a follow-up; create + delete + Versamenti shipped.

## Files
(Shared with 5.1.) **Modified:** backend/app/api/routes/patrimonio.py, frontend/src/routes/_layout/patrimonio.tsx
