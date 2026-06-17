---
baseline_commit: a1e10eb
---

# Story 3.1: Create and edit a Secchiello (any Periodicità) + Categoria→Secchiello link (FR-11, FR-7, FR-5)

Status: done

## Acceptance Criteria (summary)

- **AC1 — table:** `secchielli` (UUID PK, `utente_id` indexed, `nome`, `importo_previsto_cents` BIGINT, `periodicita`, `intervallo_mesi`, `prossima_scadenza` DATE, `data_inizio`, soft-delete); no float money; `ix_secchielli_utente_id`.
- **AC2 — create scoped + cents:** create persists scoped to `utente_id`, money as `*_cents`.
- **AC3 — periodicità:** `monthly|quarterly|semiannual|annual|custom`; `custom` requires an integer interval ≥ 1 (else 422 problem+json).
- **AC4 — validation:** missing `nome`, non-positive `importo`, malformed `prossima_scadenza` → 422, not persisted.
- **AC5 — Categoria→Secchiello link:** nullable `secchiello_id` on Spesa-type Categorie (Entrata → 422); changing the link only affects future Spese.
- **AC6 — Spesa default link:** a Spesa whose Categoria is linked pre-fills its Secchiello, overridable per-Spesa (or cleared).
- **AC7 — isolation + soft-delete:** cross-Utente → 404; delete is a soft-delete and drops from lists/allocation.

## Implementation

- **Models + migration `a5b6c7d8e9f0`:** `Secchiello` + `Periodicita` enum + `periodicita_mesi` helper; `secchiello_id` FK added to `categorie` and `movimenti`. [backend/app/models.py, backend/app/alembic/versions/a5b6c7d8e9f0_add_secchielli_and_links.py]
- **CRUD:** `POST/GET/PATCH/DELETE /api/v1/secchielli` via `UserScopedRepository`; `custom` interval resolved/validated (422). [backend/app/api/routes/secchielli.py, backend/app/api/main.py]
- **Categoria link:** `PATCH /categorie/{id}` now accepts `secchiello_id` (Spesa-only → 422 on Entrata, owned-Secchiello check → 404, null clears). [backend/app/api/routes/categorie.py]
- **Spesa default link:** `POST /movimenti` defaults `secchiello_id` from the Categoria link unless set explicitly; Entrate never link. [backend/app/api/routes/movimenti.py]

### Completion Notes

_Backend verified: ruff/mypy clean, alembic upgrade head, pytest 146 passed / 1 skipped (9 secchielli API tests). Client regenerated (`SecchielliService`); the Secchielli UI is Story 3.4. `data_inizio` is set to the creation date (chronological-replay anchor)._

### File List

**Added:** `backend/app/api/routes/secchielli.py`, `backend/app/alembic/versions/a5b6c7d8e9f0_add_secchielli_and_links.py`, `backend/tests/api/test_secchielli.py`
**Modified:** `backend/app/models.py`, `backend/app/api/main.py`, `backend/app/api/routes/categorie.py`, `backend/app/api/routes/movimenti.py`, `frontend/src/routes/_layout/categorie.tsx` (renameCategoria→updateCategoria), `frontend/src/lib/api/*`, sprint-status
