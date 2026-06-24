# Deferred Work

## Resolved

- ~~**`localStorage` access unguarded in `theme-provider.tsx`**~~ — RESOLVED: access is
  now wrapped in `readStoredTheme`/`writeStoredTheme` with try/catch (no crash in
  private-mode / disabled-storage / SSR). [frontend/src/components/theme-provider.tsx]
- ~~**Movimenti / Secchielli / Beni / Regole had no edit UI**~~ — RESOLVED: inline
  edit (and delete/skip) wired for Movimenti (Home drill-down), Secchielli, Beni
  immobili/mobili, and Regole ricorrenti (backend PATCH already existed).
- ~~**Sub-categories + quick-add note + configurable Cuscinetto (N)**~~ — RESOLVED
  (2026-06-24, branch feat/story-1-1-scaffold): one-level `categorie.parent_id`,
  top-level bilancio aggregation with per-child drill-down split, `/movimenti`
  parent filter includes children, quick-add `note`, and per-Utente
  `mesi_cuscinetto` (GET/PUT + allocazione). See the spec/plan under
  `docs/superpowers/`. Whole-branch review: READY TO MERGE.

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

### Sub-categories feature — follow-ups (from whole-branch review, non-blocking)

- **Quick-add chips don't label children `Padre › Figlia`** — the design spec
  (§Frontend) called for parent-prefixed child labels in the quick-add; the plan's
  Task 7 only mandated the note field, so chips list flat `nome`. Two children with
  the same name under different parents are indistinguishable. [QuickAdd.tsx]
- **Categorie tree renders nested `<li>`** — child rows are an `<li>` indent wrapper
  around `CategoriaRow` (itself an `<li>`); DOM-tolerant but invalid HTML. Clean fix:
  give `CategoriaRow` a className/indent prop so a child is a single
  `<li className="ml-6">`. [frontend/src/routes/_layout/categorie.tsx]
- **Minor test-coverage nits** — tipo-mismatch tested one direction only; a few POST
  responses not status-asserted; cuscinetto-mesi PUT not re-GET'd (covered
  transitively). Add when convenient.
