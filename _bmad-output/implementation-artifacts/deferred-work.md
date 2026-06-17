# Deferred Work

## Resolved

- ~~**`localStorage` access unguarded in `theme-provider.tsx`**~~ — RESOLVED: access is
  now wrapped in `readStoredTheme`/`writeStoredTheme` with try/catch (no crash in
  private-mode / disabled-storage / SSR). [frontend/src/components/theme-provider.tsx]
- ~~**Movimenti / Secchielli / Beni / Regole had no edit UI**~~ — RESOLVED: inline
  edit (and delete/skip) wired for Movimenti (Home drill-down), Secchielli, Beni
  immobili/mobili, and Regole ricorrenti (backend PATCH already existed).

## Open (non-blocking)

- **Secchiello automatic cycle-advance on payment** (Story 3.3) — when the linked
  payment Spesa is logged, `importo_previsto` should update to the actual paid
  amount and `prossima_scadenza` advance by the Periodicità. Currently done via a
  manual `PATCH /secchielli/{id}`. Needs a product decision on *which* linked Spesa
  counts as "the payment" for a cycle before auto-advancing; the derived Saldo/Quota
  (carryover, negative surfaced) is already correct either way.
- **Egress lint rule absent** [frontend/biome.json] — a rule banning hand-written
  `fetch`/`axios`/`XMLHttpRequest` outside `frontend/src/lib/api`. Low value: the
  boundary is enforced by convention + the generated client. Add when convenient.
- **Pre-deploy hardening** — rotate `SECRET_KEY`, `POSTGRES_PASSWORD`, and the
  template superuser `changethis` (the backend logs a warning at boot) before any
  deployment.
