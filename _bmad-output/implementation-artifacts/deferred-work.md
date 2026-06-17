# Deferred Work

## Resolved

- ~~**`localStorage` access unguarded in `theme-provider.tsx`**~~ — RESOLVED: access is
  now wrapped in `readStoredTheme`/`writeStoredTheme` with try/catch (no crash in
  private-mode / disabled-storage / SSR). [frontend/src/components/theme-provider.tsx]
- ~~**Movimenti / Secchielli / Beni / Regole had no edit UI**~~ — RESOLVED: inline
  edit (and delete/skip) wired for Movimenti (Home drill-down), Secchielli, Beni
  immobili/mobili, and Regole ricorrenti (backend PATCH already existed).

## Open (non-blocking)

- ~~**Secchiello cycle-advance on payment** (Story 3.3)~~ — RESOLVED via the explicit
  `POST /secchielli/{id}/pagamento` "Registra pagamento" action (creates the linked
  Spesa, sets importo_previsto to the paid amount, advances prossima_scadenza by the
  Periodicità). Surfaced in the Secchielli UI.
- **Egress lint rule absent** [frontend/biome.json] — a rule banning hand-written
  `fetch`/`axios`/`XMLHttpRequest` outside `frontend/src/lib/api`. Low value: the
  boundary is enforced by convention + the generated client. Add when convenient.
- **Pre-deploy hardening** — rotate `SECRET_KEY`, `POSTGRES_PASSWORD`, and the
  template superuser `changethis` (the backend logs a warning at boot) before any
  deployment.
