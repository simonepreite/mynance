---
baseline_commit: e33392a
---

# Story 3.4: Secchielli list and detail on the Liquidità screen (FR-9/10/11; UX-DR5 tab B)

Status: done

## Acceptance Criteria (summary)

- **AC1 — two tabs, tab B = Secchielli:** one row per Secchiello with Saldo, recommended Quota, Prossima scadenza, formatted from server cents at the display layer.
- **AC2 — negative Saldo:** shown in `{color.honesty}` (warm amber, never clamped), sign paired to the figure (not colour alone).
- **AC3 — empty state:** `Nessun Secchiello. Crea il primo per mettere da parte in anticipo.`
- **AC4 — detail/edit:** Importo previsto, Periodicità, read-only Quota; create/edit form capturing nome, importo, periodicità, prossima scadenza, Quota shown read-only.
- **AC5 — failed save:** no silent data loss; warm error + retry (mutations are non-optimistic, so there is nothing to leave stale).
- **AC6 — reconcile:** create/edit/delete invalidates `['secchielli']` + `['allocazione']` (+ `['liquidita']`) so derived values re-fetch.

## Implementation

- `routes/_layout/liquidita.tsx` — `Tabs` (Allocazione + Secchielli). Secchielli tab: list of `Card` rows (Saldo with `−`/honesty colour when negative + a `HonestyBanner` "in rosso di X €", Quota/mese, scadenza, periodicità), empty state, create/edit `Sheet` form (nome, importo €→cents, periodicità `Select`, conditional intervallo for custom, `prossima_scadenza` date input, read-only Quota when editing), delete. Mutations via `SecchielliService`, invalidating the derived keys.

### Completion Notes

_Frontend; `biome ci` + `tsc`/`vite build` green. A separate full detail view was folded into the inline row + edit form (the row already surfaces Saldo/Quota/scadenza); the linked-Spese history list is a later refinement._

### File List

**Modified:** `frontend/src/routes/_layout/liquidita.tsx` (replaces the ComingSoon stub), `frontend/src/lib/api/*`, sprint-status
