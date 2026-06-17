# Design — Categoria sub-categories + note in quick-add

**Date:** 2026-06-17 · **Project:** mynance · **Author:** Simone (+ AI dev)
**Status:** Approved — ready for implementation plan.

## Goal

Two related additions, on top of the shipped MVP:

1. **Sub-categories** — one level of hierarchy under a Categoria
   (e.g. *Casa* → *Mutuo*, *Condominio*).
2. **Note field in the quick-add** — expose the already-existing
   `MovimentoCreate.note` in the add-Spesa/Entrata bottom sheet.

"Adding categories" already exists (Impostazioni → Categorie, create/rename/
delete); this design extends it with hierarchy. No change to the Secchielli,
Riconciliazione, Patrimonio, or Regole engines.

## Decisions (from brainstorming)

- **Depth:** exactly one level (parent → children). A child cannot have children.
- **Spesa attachment:** free — a Movimento may reference a parent *or* a child.
  Logging directly on a parent that has children is allowed.
- **Breakdown (Home + Statistiche pie):** aggregated at the **top-level** parent
  (parent total = its own direct spese + all children's spese). Drill-down shows
  the per-child split (plus a "(diretto)" bucket) and the individual spese.
- **Data model:** self-referential `parent_id` on the existing `categorie` table
  (adjacency list). No separate table, no free-text tag.

## Out of scope (YAGNI)

- Multi-level nesting (sub-sub-categories).
- Re-parenting an existing Categoria (parent set at creation only).
- Movimenti reassignment on Categoria delete (pre-existing deferred item, Story 2.1 AC4).

## Data model

`Categoria` (table `categorie`) gains:

- `parent_id: uuid.UUID | None` — FK → `categorie.id`, nullable, **indexed**
  (`ix_categorie_parent_id`). `NULL` = top-level; set = sub-category.

Projections / inputs:

- `CategoriaPublic` gains `parent_id: uuid | None`.
- `CategoriaCreate` gains `parent_id: uuid | None` (optional).
- `CategoriaUpdate` — **unchanged** (no re-parenting in v1; `nome` and
  `secchiello_id` remain editable).

**Migration** (`e9f0a1b2c3d4`): add the nullable `parent_id` column + self-FK +
index. No backfill (existing categorie are all top-level).

## Validation rules (API boundary → problem+json)

On `POST /categorie` with `parent_id` set:

1. **Owned + exists:** parent resolved through `UserScopedRepository` → 404 if
   missing/foreign.
2. **One level:** parent must be top-level (`parent.parent_id is None`), else 422.
3. **Same tipo:** request `tipo` must equal `parent.tipo`, else 422.
4. **Not system:** parent must not be `is_system`; a created sub is never
   `is_system`, else 422.

The system "non identificato" Categorie stay flat, top-level, childless.

## API surface

### Categorie
- `POST /api/v1/categorie` — accepts optional `parent_id`; validates as above;
  returns `CategoriaPublic` (now with `parent_id`).
- `GET /api/v1/categorie` — unchanged shape `{spesa: [...], entrata: [...]}`,
  flat, each item carrying `parent_id`. The client builds the parent→children
  tree from the flat lists.
- `PATCH /api/v1/categorie/{id}` — unchanged (rename + Secchiello link); system
  guard unchanged.
- `DELETE /api/v1/categorie/{id}` — if the target is a top-level parent with
  children, **cascade soft-delete** the children too (set `deleted_at` on parent
  + each child). System guard unchanged (system categorie can't be deleted).

### Movimenti
- No schema change. `categoria_id` may reference a parent or a child.
- `GET /api/v1/movimenti?categoria_id=X` — **extended**: if `X` is a top-level
  Categoria, the result includes Movimenti whose `categoria_id` is `X` *or* whose
  Categoria's `parent_id` is `X` (parent + children). If `X` is a child, only
  `X`. (Powers the Home drill-down for a parent.) Existing `start`/`end` filters
  still compose.

### Bilancio (Home / Statistiche aggregation)
`GET /api/v1/bilancio` response `spese_per_categoria`:

- Aggregated at **top-level**: each spesa is attributed to its top-level ancestor
  (its `parent_id`, or itself). One entry per top-level Categoria, `total_cents` =
  own + children, sorted largest→smallest.
- Each entry gains an optional `sottocategorie: list[CategoriaSpesa] | None` —
  present only when that parent has children with spend in the period. It lists
  one `CategoriaSpesa` per child (with spend) **plus** a synthetic
  `(diretto)` entry for spese booked directly on the parent (when > 0). All
  amounts computed server-side.
- `GET /api/v1/statistiche` pie uses the same top-level aggregation (no
  `sottocategorie` needed — charts stay at parent level).

`CategoriaSpesa` is reused as-is (`categoria_id`, `nome`, `total_cents`); the
synthetic "(diretto)" entry uses the parent's `categoria_id` and a "(diretto)"
nome.

## Frontend

- **Impostazioni → Categorie** ([categorie.tsx](frontend/src/routes/_layout/categorie.tsx)):
  render each tipo as parents with their children nested/indented; the create
  dialog gains an optional "Sottocategoria di…" parent select (filtered to
  top-level, same-tipo, non-system). Existing rename/delete per row unchanged
  (delete on a parent cascades server-side; copy warns it removes the children).
- **Quick-add** ([QuickAdd.tsx](frontend/src/components/Common/QuickAdd.tsx)):
  category chips list parents and children; children labelled `Padre › Figlia`.
  **Add a `note` text input** (optional) and pass `note` in `createMovimento`.
- **Home** ([index.tsx](frontend/src/routes/_layout/index.tsx)): top-level rows as
  today (server already aggregates to parent). The drill-down sheet first shows
  the `sottocategorie` split (server totals) when present, then the individual
  spese (fetched via `/movimenti?categoria_id=<parent>`, now including children),
  each editable/deletable as today.
- **Statistiche** — no change (already consumes the bilancio/pie top-level data).

## Testing

**Backend**
- Create sub: success; one-level violation (parent is a child) → 422; tipo
  mismatch → 422; system parent → 422; cross-Utente parent → 404.
- `GET /categorie` returns `parent_id` on children.
- Bilancio: a parent's `total_cents` includes children's spese; `sottocategorie`
  lists children + "(diretto)"; a parent with no children has `sottocategorie`
  null/absent.
- `GET /movimenti?categoria_id=<parent>` includes children's movimenti; with a
  child id returns only that child's.
- Delete parent → children soft-deleted (drop from `GET /categorie`).
- All scoped per-Utente (404 cross-Utente).

**Frontend**
- `biome ci` + `tsc` + `vite build` green.
- Categorie tree + parent select; quick-add note persists; drill-down sub-split
  renders.

## Risks / notes

- Bilancio aggregation changes from "group by categoria_id" to "group by
  top-level ancestor" — must not double-count and must keep integer-cents sums
  server-side (reuse `money.add`). Covered by the parent-total test.
- The "(diretto)" synthetic entry reuses the parent's `categoria_id`; the client
  must treat it as a label, not a drill target.
- Cascade soft-delete only touches children; Movimenti on deleted (sub)categorie
  keep their `categoria_id` (resolve to "—" in views) — same pre-existing
  behaviour as deleting any Categoria; full reassignment stays the tracked
  follow-up.
