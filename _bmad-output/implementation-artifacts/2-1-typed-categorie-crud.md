---
baseline_commit: df5d591
---

# Story 2.1: Typed Categorie CRUD (FR-7)

Status: done

## Story

As an Utente, I want to create, rename, and reuse my own type-scoped Categorie, so that I can organize my Movimenti by Spesa and Entrata categories.

## Acceptance Criteria

- **AC1 — create typed:** create a Categoria with nome + tipo (Spesa|Entrata), persisted scoped to `utente_id`; tipo enforced backend-side as a distinct space; response returns the object (snake_case).
- **AC2 — rename + list split:** rename persists; list returns Spesa and Entrata split; only my Categorie returned.
- **AC3 — starter set:** a per-tipo starter set provisioned on account creation.
- **AC4 — delete in-use:** deleting a Categoria used by Movimenti prompts reassignment (not silent orphaning). *(Deferred: Movimenti arrive in Story 2.5.)*
- **AC5 — isolation:** another Utente's Categoria id → 404, never its data.

## Tasks / Subtasks

- [x] **Model + migration (AC1):** `CategoriaTipo` enum; `Categoria` (`categorie` table, FK `utenti.id`, `tipo` varchar, soft-delete) + migration `d2e3f4a5b6c7`. [backend/app/models.py, backend/app/alembic/versions/d2e3f4a5b6c7_add_categorie_table.py]
- [x] **CRUD via the choke point (AC1, AC2, AC5):** `POST/GET/PATCH/DELETE /api/v1/categorie` through `UserScopedRepository[Categoria]` scoped to `current_utente`; list split per tipo; cross-Utente → 404. [backend/app/api/routes/categorie.py, backend/app/api/main.py]
- [x] **Starter set (AC3):** `provision_starter_categorie` (7 Spesa + 3 Entrata, Italian) invoked on register. [backend/app/crud_categoria.py, backend/app/api/routes/auth.py]
- [x] **Tests:** starter set per tipo, create+list split, invalid tipo→422, rename, delete, cross-Utente→404. [backend/tests/api/test_categorie.py]
- [ ] **Delete-in-use reassignment (AC4):** deferred to Story 2.5 (no Movimenti table yet); current delete is a scoped soft-delete.
- [x] **Frontend — Categorie management UI:** authenticated `/categorie` route — list split into Spese / Entrate, create dialog (nome + tipo Select), inline rename dialog, delete confirm dialog, empty-state per tipo, query invalidation on mutate; "Categorie" added to the sidebar nav. [frontend/src/routes/_layout/categorie.tsx, frontend/src/components/Sidebar/AppSidebar.tsx]

## Dev Notes

- First real entity exercising the Story 1.5 `UserScopedRepository` end-to-end; the cross-Utente 404 test is the per-entity isolation case AC5 of Story 1.5 calls for.
- `tipo` stored as a validated string (`spesa`/`entrata`); the enum (`CategoriaTipo`) validates input → invalid tipo is 422 problem+json. Distinct spaces enforced server-side (list split per tipo, not a UI filter).
- Conventions: plural table `categorie`, FK `utente_id` (+ `ix_categorie_utente_id`), snake_case, soft-delete.

### Completion Notes List

_Backend implemented; ruff check + `ruff format --check` clean locally; mypy/alembic/pytest in CI (89 passed, 1 skipped re-verified locally 2026-06-17 against Docker Postgres). Delete-in-use guard still pends Movimenti (2.5); current delete is a scoped soft-delete._

_Frontend completed 2026-06-17: `/categorie` management route (list split per tipo, create/rename/delete via the regenerated `CategorieService`), sidebar nav entry. Verified locally: `biome ci .` clean, `tsc` + `vite build` green, and a live smoke test against the backend (starter set 7 Spese / 3 Entrate provisioned on register; create → rename → delete; invalid tipo → 422)._

### Change Log

| Date | Change |
|---|---|
| 2026-06-16 | Backend: Categoria model + categorie migration + CRUD via UserScopedRepository + per-tipo starter set on register + isolation tests. |
| 2026-06-17 | Frontend: `/categorie` route (split Spese/Entrate, create/rename/delete dialogs, empty states) + sidebar nav. Story done. |

### File List

**Added:** `backend/app/crud_categoria.py`, `backend/app/api/routes/categorie.py`, `backend/app/alembic/versions/d2e3f4a5b6c7_add_categorie_table.py`, `backend/tests/api/test_categorie.py`, `frontend/src/routes/_layout/categorie.tsx`
**Modified:** `backend/app/models.py` (Categoria domain), `backend/app/api/main.py` (categorie router), `backend/app/api/routes/auth.py` (starter provisioning), `frontend/src/components/Sidebar/AppSidebar.tsx` (Categorie nav), `_bmad-output/implementation-artifacts/sprint-status.yaml`
