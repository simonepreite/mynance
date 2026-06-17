---
baseline_commit: 2df118c
---
# Story 5.3: Register a Bene mobile with linear Svalutazione (FR-21)
Status: done

## Summary
- beni_mobili table (prezzo_cents, data_acquisto, svalutazione_percentuale). Pure engine app/calc/patrimonio.valore_bene_mobile = max(0, prezzo × (1 − s × anni_trascorsi)) with anni fractional (days/365.25), centralized rounding, floored at 0 (never negative). Worked-example tests.
- Suggested rates offered in the UI (Auto 18%, Moto 10%) and fully editable. Registration never changes Liquidità (FR-22). Per-Utente isolation.

## Files
(Shared with 5.1.) **Added:** backend/app/calc/patrimonio.py, backend/tests/calc/test_patrimonio.py
**Modified:** backend/app/api/routes/patrimonio.py, backend/app/models.py, frontend/src/routes/_layout/patrimonio.tsx
