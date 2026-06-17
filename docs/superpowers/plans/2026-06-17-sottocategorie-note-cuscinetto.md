# Sub-categories + quick-add note + configurable Cuscinetto — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add one-level Categoria sub-categories, a note field in the quick-add, and a per-Utente configurable Cuscinetto horizon (N months), on top of the shipped mynance MVP.

**Architecture:** Self-referential `categorie.parent_id` (adjacency, one level); a Spesa may reference a parent or a child; Home/Statistiche aggregate spend at the top-level ancestor with a server-computed per-child drill-down split; `mesi_cuscinetto` becomes a stored `Utente` field (precedent: `intervallo_riconciliazione_giorni`). One Alembic migration adds both columns.

**Tech Stack:** Backend FastAPI + SQLModel + Alembic (run via `uv`, gates: `ruff check` · `ruff format --check` · `mypy app` · `pytest`). Frontend React 19 + Vite + TanStack Router/Query + Morbido (run via Node 22/npm, gates: `biome ci .` · `tsc -p tsconfig.build.json` · `vite build`). Spec: `docs/superpowers/specs/2026-06-17-sottocategorie-and-spesa-note-design.md`.

## Global Constraints

- Money is always integer cents (`*_cents`, BIGINT); never float; never recomputed on the client (API-3). Reuse `app.calc.money.add`.
- Every owned read/write goes through `UserScopedRepository` (per-Utente choke point); cross-Utente → 404.
- Errors are RFC 9457 `application/problem+json` (handlers already registered); validation failures and raised `HTTPException` both surface as problem+json.
- One level of hierarchy only; no re-parenting; no Movimenti reassignment on delete (out of scope).
- Backend env: `export PATH="$HOME/.local/bin:$PATH"` for `uv`; Postgres DB up via `docker compose up -d db`.
- Frontend env: `export NVM_DIR="$HOME/.nvm"; . "$NVM_DIR/nvm.sh"; nvm use 22.12`; `export VITE_API_URL=http://localhost:8000`. After any backend schema/endpoint change, regenerate the client: `( cd backend && uv run python -c "import app.main, json; print(json.dumps(app.main.app.openapi()))" > ../openapi.json ) && cp openapi.json frontend/openapi.json && npm run generate-client --workspace frontend`.
- Do NOT commit `package-lock.json` (repo is bun-canonical; CI uses bun). Pin biome to the lockfile version if it drifts: `npm i -D @biomejs/biome@2.3.14 --no-save`.
- Commit after each task; push at the end of the backend batch and again after the frontend batch so CI runs.

---

### Task 1: Schema & models (parent_id + mesi_cuscinetto)

**Files:**
- Modify: `backend/app/models.py` (Categoria, CategoriaPublic, CategoriaCreate, Utente)
- Create: `backend/app/alembic/versions/e9f0a1b2c3d4_add_parent_id_and_mesi_cuscinetto.py`

**Interfaces:**
- Produces: `Categoria.parent_id: uuid.UUID | None`; `CategoriaPublic.parent_id`; `CategoriaCreate.parent_id`; `Utente.mesi_cuscinetto: int` (default 6). Migration revision `e9f0a1b2c3d4`, down_revision `d8e9f0a1b2c3`.

- [ ] **Step 1: Add `parent_id` to the `Categoria` table model.** In `backend/app/models.py`, in `class Categoria`, after the `secchiello_id` field add:

```python
    parent_id: uuid.UUID | None = Field(
        default=None, foreign_key="categorie.id", nullable=True, index=True
    )
```

- [ ] **Step 2: Add `parent_id` to `CategoriaPublic` and `CategoriaCreate`.** In `CategoriaPublic` add `parent_id: uuid.UUID | None = None`. In `CategoriaCreate` add `parent_id: uuid.UUID | None = None`.

- [ ] **Step 3: Add `mesi_cuscinetto` to `Utente`.** In `class Utente`, after `intervallo_riconciliazione_giorni` add:

```python
    mesi_cuscinetto: int = Field(default=6)
```

- [ ] **Step 4: Write the migration.** Create `backend/app/alembic/versions/e9f0a1b2c3d4_add_parent_id_and_mesi_cuscinetto.py`:

```python
"""add categorie.parent_id + utenti.mesi_cuscinetto (sub-categories, cuscinetto N)

Revision ID: e9f0a1b2c3d4
Revises: d8e9f0a1b2c3
Create Date: 2026-06-17 00:00:07.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'e9f0a1b2c3d4'
down_revision = 'd8e9f0a1b2c3'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('categorie', sa.Column('parent_id', sa.Uuid(), nullable=True))
    op.create_index(
        op.f('ix_categorie_parent_id'), 'categorie', ['parent_id'], unique=False
    )
    op.create_foreign_key(
        'fk_categorie_parent_id', 'categorie', 'categorie', ['parent_id'], ['id']
    )
    op.add_column(
        'utenti',
        sa.Column('mesi_cuscinetto', sa.Integer(), nullable=False, server_default='6'),
    )


def downgrade():
    op.drop_column('utenti', 'mesi_cuscinetto')
    op.drop_constraint('fk_categorie_parent_id', 'categorie', type_='foreignkey')
    op.drop_index(op.f('ix_categorie_parent_id'), table_name='categorie')
    op.drop_column('categorie', 'parent_id')
```

- [ ] **Step 5: Apply and round-trip the migration.**

Run: `cd backend && export PATH="$HOME/.local/bin:$PATH" && uv run alembic upgrade head && uv run alembic downgrade -1 && uv run alembic upgrade head`
Expected: three "Running upgrade/downgrade" lines, no error; final state at `e9f0a1b2c3d4`.

- [ ] **Step 6: Gate + commit.**

Run: `cd backend && uv run ruff check . && uv run ruff format --check . && uv run mypy app && uv run python -c "import app.models"`
Expected: all pass, import OK.

```bash
git add backend/app/models.py backend/app/alembic/versions/e9f0a1b2c3d4_add_parent_id_and_mesi_cuscinetto.py
git commit -m "feat(cat): schema for sub-categories (parent_id) + mesi_cuscinetto"
```

---

### Task 2: Sub-category create + validation + parent_id in projections

**Files:**
- Modify: `backend/app/api/routes/categorie.py`
- Test: `backend/tests/api/test_categorie.py`

**Interfaces:**
- Consumes: `Categoria.parent_id`, `CategoriaCreate.parent_id`, `CategoriaPublic.parent_id` (Task 1).
- Produces: `POST /categorie` accepts `parent_id`; `_public` returns `parent_id`. Validation order: owned (404) → top-level (422) → tipo match (422) → non-system (422).

- [ ] **Step 1: Write failing tests.** Append to `backend/tests/api/test_categorie.py`:

```python
def test_create_subcategoria(client: TestClient) -> None:
    headers = _auth(client)
    parent = client.post(
        BASE, headers=headers, json={"nome": "Casa", "tipo": "spesa"}
    ).json()
    sub = client.post(
        BASE,
        headers=headers,
        json={"nome": "Mutuo", "tipo": "spesa", "parent_id": parent["id"]},
    )
    assert sub.status_code == 201
    assert sub.json()["parent_id"] == parent["id"]
    # GET carries parent_id on the child.
    listed = client.get(BASE, headers=headers).json()
    child = next(c for c in listed["spesa"] if c["nome"] == "Mutuo")
    assert child["parent_id"] == parent["id"]


def test_subcategoria_one_level_only(client: TestClient) -> None:
    headers = _auth(client)
    parent = client.post(BASE, headers=headers, json={"nome": "Casa", "tipo": "spesa"}).json()
    child = client.post(
        BASE, headers=headers, json={"nome": "Mutuo", "tipo": "spesa", "parent_id": parent["id"]}
    ).json()
    # A child cannot be a parent.
    r = client.post(
        BASE, headers=headers, json={"nome": "Rata", "tipo": "spesa", "parent_id": child["id"]}
    )
    assert r.status_code == 422
    assert r.headers["content-type"].startswith(PROBLEM_JSON)


def test_subcategoria_tipo_must_match_parent(client: TestClient) -> None:
    headers = _auth(client)
    parent = client.post(BASE, headers=headers, json={"nome": "Casa", "tipo": "spesa"}).json()
    r = client.post(
        BASE, headers=headers, json={"nome": "X", "tipo": "entrata", "parent_id": parent["id"]}
    )
    assert r.status_code == 422


def test_subcategoria_parent_must_be_owned_and_non_system(client: TestClient) -> None:
    headers_a = _auth(client)
    headers_b = _auth(client)
    parent_a = client.post(BASE, headers=headers_a, json={"nome": "Casa", "tipo": "spesa"}).json()
    # B cannot parent under A's categoria.
    assert client.post(
        BASE, headers=headers_b, json={"nome": "x", "tipo": "spesa", "parent_id": parent_a["id"]}
    ).status_code == 404
    # System "non identificato" cannot be a parent.
    sys_cat = next(c for c in client.get(BASE, headers=headers_a).json()["spesa"] if c["is_system"])
    assert client.post(
        BASE, headers=headers_a, json={"nome": "x", "tipo": "spesa", "parent_id": sys_cat["id"]}
    ).status_code == 422
```

- [ ] **Step 2: Run to verify they fail.**

Run: `cd backend && export PATH="$HOME/.local/bin:$PATH" && uv run pytest tests/api/test_categorie.py -q`
Expected: the 4 new tests FAIL (parent_id ignored / not validated).

- [ ] **Step 3: Add `parent_id` to `_public`.** In `categorie.py` `_public`, add `parent_id=categoria.parent_id,` to the `CategoriaPublic(...)` call.

- [ ] **Step 4: Validate + persist `parent_id` on create.** Replace the body of `create_categoria` with:

```python
@router.post("/", status_code=201)
def create_categoria(
    body: CategoriaCreate, session: SessionDep, current_utente: CurrentUtente
) -> CategoriaPublic:
    repo = _repo(session, current_utente)
    if body.parent_id is not None:
        parent = repo.get(body.parent_id)
        if parent is None:
            raise HTTPException(status_code=404, detail="Categoria padre non trovata.")
        if parent.parent_id is not None:
            raise HTTPException(
                status_code=422,
                detail="Le sottocategorie possono avere un solo livello.",
            )
        if parent.tipo != body.tipo.value:
            raise HTTPException(
                status_code=422,
                detail="La sottocategoria deve essere dello stesso tipo della categoria padre.",
            )
        if parent.is_system:
            raise HTTPException(
                status_code=422,
                detail="Le categorie di sistema non possono avere sottocategorie.",
            )
    categoria = repo.add(
        Categoria(
            utente_id=current_utente.id,
            nome=body.nome,
            tipo=body.tipo.value,
            parent_id=body.parent_id,
        )
    )
    return _public(categoria)
```

- [ ] **Step 5: Run tests to verify they pass.**

Run: `cd backend && uv run pytest tests/api/test_categorie.py -q`
Expected: all PASS (incl. the pre-existing categorie tests).

- [ ] **Step 6: Gate + commit.**

Run: `cd backend && uv run ruff format . >/dev/null && uv run ruff check . && uv run mypy app`
```bash
git add backend/app/api/routes/categorie.py backend/tests/api/test_categorie.py
git commit -m "feat(cat): create sub-categories with one-level/tipo/owner/system validation"
```

---

### Task 3: Cascade soft-delete of children

**Files:**
- Modify: `backend/app/api/routes/categorie.py` (`delete_categoria`)
- Test: `backend/tests/api/test_categorie.py`

**Interfaces:**
- Consumes: `_repo` (Categoria repository), `Categoria.parent_id`.
- Produces: deleting a parent soft-deletes its children too.

- [ ] **Step 1: Write the failing test.** Append to `test_categorie.py`:

```python
def test_delete_parent_cascades_children(client: TestClient) -> None:
    headers = _auth(client)
    parent = client.post(BASE, headers=headers, json={"nome": "Casa", "tipo": "spesa"}).json()
    client.post(BASE, headers=headers, json={"nome": "Mutuo", "tipo": "spesa", "parent_id": parent["id"]})
    assert client.delete(f"{BASE}{parent['id']}", headers=headers).status_code == 200
    names = [c["nome"] for c in client.get(BASE, headers=headers).json()["spesa"]]
    assert "Casa" not in names and "Mutuo" not in names
```

- [ ] **Step 2: Run to verify it fails.**

Run: `cd backend && uv run pytest tests/api/test_categorie.py::test_delete_parent_cascades_children -q`
Expected: FAIL (child "Mutuo" still listed).

- [ ] **Step 3: Cascade in `delete_categoria`.** After the `is_system` guard and before `repo.delete(categoria_id)`, soft-delete children:

```python
    for child in repo.list():
        if child.parent_id == categoria_id:
            repo.delete(child.id)
    repo.delete(categoria_id)
```

(`repo.list()` returns only this Utente's non-deleted rows; `repo.delete` soft-deletes via `deleted_at`.)

- [ ] **Step 4: Run to verify it passes.**

Run: `cd backend && uv run pytest tests/api/test_categorie.py -q`
Expected: PASS.

- [ ] **Step 5: Gate + commit.**

```bash
git add backend/app/api/routes/categorie.py backend/tests/api/test_categorie.py
git commit -m "feat(cat): cascade soft-delete of sub-categories when deleting a parent"
```

---

### Task 4: Bilancio top-level aggregation + sottocategorie split

**Files:**
- Modify: `backend/app/models.py` (`CategoriaSpesa`)
- Modify: `backend/app/api/routes/riepilogo.py`
- Test: `backend/tests/api/test_riepilogo.py`

**Interfaces:**
- Consumes: `Categoria.parent_id`; `app.calc.money` (sums via plain `sum`, integer cents).
- Produces: `CategoriaSpesa.sottocategorie: list[CategoriaSpesa] | None`; `_spese_per_categoria` aggregates at the top-level ancestor, attaching `sottocategorie` (children with spend + a `(diretto)` entry) for parents that have children.

- [ ] **Step 1: Add the recursive field to `CategoriaSpesa`.** In `models.py`, change `CategoriaSpesa` to:

```python
class CategoriaSpesa(SQLModel):
    categoria_id: uuid.UUID
    nome: str
    total_cents: int
    sottocategorie: list["CategoriaSpesa"] | None = None
```

- [ ] **Step 2: Write the failing test.** Append to `test_riepilogo.py` (helpers `_auth`, `_cat`, `_spesa` already exist):

```python
def test_bilancio_aggregates_at_top_level_with_subsplit(client: TestClient) -> None:
    headers = _auth(client)
    casa = client.post(f"{CAT}", headers=headers, json={"nome": "Casa", "tipo": "spesa"}).json()
    mutuo = client.post(
        f"{CAT}", headers=headers, json={"nome": "Mutuo", "tipo": "spesa", "parent_id": casa["id"]}
    ).json()
    _spesa(client, headers, casa["id"], 10000, "2026-06-05")   # direct on parent
    _spesa(client, headers, mutuo["id"], 40000, "2026-06-06")  # on child

    body = client.get(
        BILANCIO, headers=headers, params={"period": "month", "anchor": "2026-06-15"}
    ).json()
    casa_row = next(c for c in body["spese_per_categoria"] if c["categoria_id"] == casa["id"])
    assert casa_row["total_cents"] == 50000  # parent + child
    subs = {s["nome"]: s["total_cents"] for s in casa_row["sottocategorie"]}
    assert subs["Mutuo"] == 40000
    assert subs["(diretto)"] == 10000
    # Child is not also a separate top-level row.
    assert all(c["categoria_id"] != mutuo["id"] for c in body["spese_per_categoria"])
```

(`CAT = f"{settings.API_V1_STR}/categorie/"` — add this module constant if missing.)

- [ ] **Step 2b: Run to verify it fails.**

Run: `cd backend && uv run pytest tests/api/test_riepilogo.py::test_bilancio_aggregates_at_top_level_with_subsplit -q`
Expected: FAIL.

- [ ] **Step 3: Rewrite `_spese_per_categoria` to aggregate at top-level.** Replace the function in `riepilogo.py` with:

```python
def _spese_per_categoria(
    movimenti: Sequence[Movimento],
    nomi: dict[uuid.UUID, str],
    parent_of: dict[uuid.UUID, uuid.UUID | None],
) -> list[CategoriaSpesa]:
    # direct spend per categoria (leaf or parent)
    direct: dict[uuid.UUID, int] = {}
    for m in movimenti:
        if m.tipo == CategoriaTipo.spesa.value:
            direct[m.categoria_id] = direct.get(m.categoria_id, 0) + m.amount_cents

    def top(cid: uuid.UUID) -> uuid.UUID:
        return parent_of.get(cid) or cid

    # group totals by top-level ancestor
    totals: dict[uuid.UUID, int] = {}
    for cid, amt in direct.items():
        totals[top(cid)] = totals.get(top(cid), 0) + amt

    items: list[CategoriaSpesa] = []
    for parent_cid, total in totals.items():
        sotto: list[CategoriaSpesa] | None = None
        children = {
            cid: amt
            for cid, amt in direct.items()
            if cid != parent_cid and top(cid) == parent_cid
        }
        if children:
            sotto = [
                CategoriaSpesa(categoria_id=cid, nome=nomi.get(cid, "—"), total_cents=amt)
                for cid, amt in children.items()
            ]
            if direct.get(parent_cid):
                sotto.append(
                    CategoriaSpesa(
                        categoria_id=parent_cid, nome="(diretto)", total_cents=direct[parent_cid]
                    )
                )
            sotto.sort(key=lambda x: x.total_cents, reverse=True)
        items.append(
            CategoriaSpesa(
                categoria_id=parent_cid,
                nome=nomi.get(parent_cid, "—"),
                total_cents=total,
                sottocategorie=sotto,
            )
        )
    items.sort(key=lambda x: x.total_cents, reverse=True)
    return items
```

- [ ] **Step 4: Build `parent_of` in `_load` and pass it through.** Change `_load` to also return the parent map, and update both call sites (`bilancio`, `statistiche`):

```python
def _load(
    session: SessionDep, current_utente: CurrentUtente
) -> tuple[Sequence[Movimento], dict[uuid.UUID, str], dict[uuid.UUID, uuid.UUID | None]]:
    mov_repo = UserScopedRepository(session=session, model=Movimento, utente_id=current_utente.id)
    cat_repo = UserScopedRepository(session=session, model=Categoria, utente_id=current_utente.id)
    cats = cat_repo.list()
    nomi = {c.id: c.nome for c in cats}
    parent_of = {c.id: c.parent_id for c in cats}
    return mov_repo.list(), nomi, parent_of
```

In `bilancio`: `movimenti, nomi, parent_of = _load(...)` and `spese_per_categoria=_spese_per_categoria(in_period, nomi, parent_of)`.
In `statistiche`: `movimenti, nomi, parent_of = _load(...)`; the pie uses `_spese_per_categoria(in_period, nomi, parent_of)` (top-level too — chart stays at parent level; ignore the `sottocategorie` field client-side).

- [ ] **Step 5: Run tests to verify they pass.**

Run: `cd backend && uv run pytest tests/api/test_riepilogo.py -q`
Expected: PASS (existing + new). Confirm the prior `test_bilancio_aggregates_and_sorts_breakdown` still holds (no sub-categories → `sottocategorie` is null, totals unchanged).

- [ ] **Step 6: Gate + commit.**

```bash
git add backend/app/models.py backend/app/api/routes/riepilogo.py backend/tests/api/test_riepilogo.py
git commit -m "feat(home): aggregate Spese at top-level Categoria + sotto-split drill-down"
```

---

### Task 5: `GET /movimenti` includes children for a parent

**Files:**
- Modify: `backend/app/api/routes/movimenti.py` (`list_movimenti`)
- Test: `backend/tests/api/test_movimenti.py`

**Interfaces:**
- Consumes: `Categoria.parent_id`, the Categoria repository.
- Produces: `GET /movimenti?categoria_id=X` returns Movimenti for X plus its children when X is top-level.

- [ ] **Step 1: Write the failing test.** Append to `test_movimenti.py`:

```python
def test_list_filter_includes_children(client: TestClient) -> None:
    headers = _auth(client)
    casa = client.post(CAT, headers=headers, json={"nome": "Casa", "tipo": "spesa"}).json()
    mutuo = client.post(
        CAT, headers=headers, json={"nome": "Mutuo", "tipo": "spesa", "parent_id": casa["id"]}
    ).json()
    client.post(MOV, headers=headers, json={"tipo": "spesa", "amount_cents": 10000, "data": "2026-06-05", "categoria_id": casa["id"]})
    client.post(MOV, headers=headers, json={"tipo": "spesa", "amount_cents": 40000, "data": "2026-06-06", "categoria_id": mutuo["id"]})
    # Parent filter → parent + child movimenti.
    rows = client.get(MOV, headers=headers, params={"categoria_id": casa["id"]}).json()
    assert len(rows) == 2
    # Child filter → only the child's.
    rows_child = client.get(MOV, headers=headers, params={"categoria_id": mutuo["id"]}).json()
    assert len(rows_child) == 1 and rows_child[0]["amount_cents"] == 40000
```

- [ ] **Step 2: Run to verify it fails.**

Run: `cd backend && uv run pytest tests/api/test_movimenti.py::test_list_filter_includes_children -q`
Expected: FAIL (parent filter returns only 1).

- [ ] **Step 3: Expand the `categoria_id` filter to include children.** In `list_movimenti`, replace the `if categoria_id is not None:` filter block with:

```python
    if categoria_id is not None:
        cat_ids = {categoria_id}
        for c in _cat_repo(session, current_utente).list():
            if c.parent_id == categoria_id:
                cat_ids.add(c.id)
        items = [m for m in items if m.categoria_id in cat_ids]
```

- [ ] **Step 4: Run tests to verify they pass.**

Run: `cd backend && uv run pytest tests/api/test_movimenti.py -q`
Expected: PASS (existing drill-down test still passes — a categoria with no children yields `cat_ids == {id}`).

- [ ] **Step 5: Gate + commit.**

```bash
git add backend/app/api/routes/movimenti.py backend/tests/api/test_movimenti.py
git commit -m "feat(movimenti): drill-down filter includes a parent Categoria's children"
```

---

### Task 6: Configurable Cuscinetto months — endpoints + allocazione uses stored N

**Files:**
- Modify: `backend/app/models.py` (add `CuscinettoMesi` model)
- Modify: `backend/app/api/routes/liquidita.py`
- Test: `backend/tests/api/test_allocazione.py`

**Interfaces:**
- Consumes: `Utente.mesi_cuscinetto` (Task 1).
- Produces: `GET /liquidita/cuscinetto-mesi` → `CuscinettoMesi{mesi_cuscinetto}`; `PUT /liquidita/cuscinetto-mesi`; `allocazione` effective N = `mesi` query param if given, else `current_utente.mesi_cuscinetto`.

- [ ] **Step 1: Add the model.** In `models.py`, after `AllocazionePublic` add:

```python
class CuscinettoMesi(SQLModel):
    mesi_cuscinetto: int = Field(ge=1)
```

- [ ] **Step 2: Write failing tests.** Append to `test_allocazione.py`:

```python
CUSC = f"{settings.API_V1_STR}/liquidita/cuscinetto-mesi"


def test_cuscinetto_mesi_default_and_update(client: TestClient) -> None:
    headers = _auth(client)
    assert client.get(CUSC, headers=headers).json()["mesi_cuscinetto"] == 6
    ok = client.put(CUSC, headers=headers, json={"mesi_cuscinetto": 3})
    assert ok.status_code == 200 and ok.json()["mesi_cuscinetto"] == 3
    bad = client.put(CUSC, headers=headers, json={"mesi_cuscinetto": 0})
    assert bad.status_code == 422


def test_allocazione_uses_stored_mesi(client: TestClient) -> None:
    headers = _auth(client)
    cat = _spesa_cat(client, headers)
    for data in ("2026-04-10", "2026-05-12"):
        client.post(MOV, headers=headers, json={"tipo": "spesa", "amount_cents": 100000, "data": data, "categoria_id": cat})
    client.put(CUSC, headers=headers, json={"mesi_cuscinetto": 3})
    a = client.get(ALLOC, headers=headers).json()  # no mesi override
    assert a["mesi_cuscinetto"] == 3
    assert a["cuscinetto_cents"] == 300000  # 3 × media(100000)
```

(`MOV = f"{settings.API_V1_STR}/movimenti/"` — add the constant if missing.)

- [ ] **Step 3: Run to verify they fail.**

Run: `cd backend && uv run pytest tests/api/test_allocazione.py -q`
Expected: the 2 new tests FAIL (404 on cuscinetto-mesi; allocazione default still 6).

- [ ] **Step 4: Add endpoints + import.** In `liquidita.py` add `CuscinettoMesi` to the `app.models` import, then add:

```python
@router.get("/cuscinetto-mesi")
def get_cuscinetto_mesi(current_utente: CurrentUtente) -> CuscinettoMesi:
    return CuscinettoMesi(mesi_cuscinetto=current_utente.mesi_cuscinetto)


@router.put("/cuscinetto-mesi")
def set_cuscinetto_mesi(
    body: CuscinettoMesi, session: SessionDep, current_utente: CurrentUtente
) -> CuscinettoMesi:
    current_utente.mesi_cuscinetto = body.mesi_cuscinetto
    session.add(current_utente)
    session.commit()
    return CuscinettoMesi(mesi_cuscinetto=current_utente.mesi_cuscinetto)
```

- [ ] **Step 5: Make `allocazione` use the stored value.** Change the signature default from `mesi: int = Query(6, ge=1, le=60)` to `mesi: int | None = Query(None, ge=1, le=60)` and, at the top of the body, add:

```python
    mesi = mesi if mesi is not None else current_utente.mesi_cuscinetto
```

(Everything downstream already uses the local `mesi`.)

- [ ] **Step 6: Run tests to verify they pass.**

Run: `cd backend && uv run pytest tests/api/test_allocazione.py -q`
Expected: PASS (the prior `test_cuscinetto_from_complete_months_and_below_flag` passes `mesi=6` explicitly, still valid as an override).

- [ ] **Step 7: Gate + commit + push backend batch.**

Run: `cd backend && uv run ruff format . >/dev/null && uv run ruff check . && uv run mypy app && uv run pytest -q`
Expected: full suite green.

```bash
git add backend/app/models.py backend/app/api/routes/liquidita.py backend/tests/api/test_allocazione.py
git commit -m "feat(cuscinetto): per-Utente configurable mesi_cuscinetto (GET/PUT) + allocazione uses it"
git push origin <branch>
```

Then watch CI green before starting the frontend batch.

---

### Task 7: Client regen + quick-add note field

**Files:**
- Modify: `frontend/src/lib/api/*` (regenerated)
- Modify: `frontend/src/components/Common/QuickAdd.tsx`

**Interfaces:**
- Consumes: regenerated `MovimentiService.createMovimento` (request already has optional `note`), new `LiquiditaService.getCuscinettoMesi/setCuscinettoMesi`, `CategoriaPublic.parent_id`.
- Produces: quick-add sends `note`.

- [ ] **Step 1: Regenerate the client** (backend running or importable). Run the regen command from Global Constraints. Verify: `grep -c "getCuscinettoMesi" frontend/src/lib/api/sdk.gen.ts` ≥ 1.

- [ ] **Step 2: Add a note input to QuickAdd.** In `QuickAdd.tsx`, add `const [note, setNote] = useState("")`; reset it in `reset()`; add `note: note.trim() === "" ? undefined : note` to the `createMovimento` request body; and render an input after the Categoria chips:

```tsx
<Input
  placeholder="Nota (facoltativa)"
  value={note}
  onChange={(e) => setNote(e.target.value)}
  data-testid="quick-add-note"
/>
```

(`Input` is already imported.)

- [ ] **Step 3: Verify build/lint.**

Run: `cd frontend && export NVM_DIR="$HOME/.nvm" && . "$NVM_DIR/nvm.sh" && nvm use 22.12 >/dev/null && export VITE_API_URL=http://localhost:8000 && npm run lint && npm run build && npx biome ci .`
Expected: lint ok, BUILD OK, biome ci clean.

- [ ] **Step 4: Commit.**

```bash
git add frontend/src/lib/api frontend/src/components/Common/QuickAdd.tsx frontend/openapi.json
git commit -m "feat(fe): note field in quick-add + regenerated client"
```

(Note: `openapi.json`/`frontend/openapi.json` may be gitignored — `git add` is a no-op then; the `lib/api` gen files are tracked.)

---

### Task 8: Categorie screen — tree + sub-category create

**Files:**
- Modify: `frontend/src/routes/_layout/categorie.tsx`

**Interfaces:**
- Consumes: `CategoriaPublic.parent_id`; `CategorieService.createCategoria` (now with `parent_id`).
- Produces: parents render with nested children; create dialog has an optional parent select.

- [ ] **Step 1: Render children under parents.** In `CategoriaGroup`, split `categorie` into parents (`parent_id == null`) and children (grouped by `parent_id`); render each parent row, then its children indented beneath (reuse `CategoriaRow`, add a `className="ml-6"` wrapper for children). A child row shows its `nome`; rename/delete unchanged.

```tsx
const parents = categorie.filter((c) => c.parent_id == null)
const childrenOf = (id: string) => categorie.filter((c) => c.parent_id === id)
// render: parents.map(p => <><CategoriaRow categoria={p}/> {childrenOf(p.id).map(ch => <div className="ml-6"><CategoriaRow categoria={ch}/></div>)}</>)
```

- [ ] **Step 2: Add a parent select to the create dialog.** In `CreateCategoria`, add `const [parentId, setParentId] = useState<string>("")`; after the tipo field, render a `Select` (optional, label "Sottocategoria di…") listing top-level, same-tipo, non-system categorie from `useQuery(["categorie"])`; include the parent_id in the create body (`parent_id: parentId || null`). When tipo changes, clear `parentId`.

- [ ] **Step 3: Verify build/lint.**

Run: `cd frontend && npm run lint && npm run build && npx biome ci .`
Expected: green.

- [ ] **Step 4: Commit.**

```bash
git add frontend/src/routes/_layout/categorie.tsx
git commit -m "feat(fe): Categorie tree view + create sub-category (parent select)"
```

---

### Task 9: Home drill-down sub-split + Allocazione cuscinetto control

**Files:**
- Modify: `frontend/src/routes/_layout/index.tsx` (drill-down)
- Modify: `frontend/src/routes/_layout/liquidita.tsx` (Allocazione tab)

**Interfaces:**
- Consumes: `CategoriaSpesa.sottocategorie`; `LiquiditaService.getCuscinettoMesi/setCuscinettoMesi`; `AllocazionePublic.mesi_cuscinetto`.
- Produces: drill-down shows the sub-split; Allocazione tab edits N.

- [ ] **Step 1: Show `sottocategorie` in the Home drill-down.** The drill-down sheet receives the tapped `CategoriaSpesa`. If `categoria.sottocategorie` is non-empty, render a small list (nome + `formatEurFromCents(total_cents)`) above the individual movimenti list. (Pass the full `CategoriaSpesa` into `CategoriaDrillDown` — `drill` already is one.)

```tsx
{categoria?.sottocategorie?.length ? (
  <ul className="mb-3 flex flex-col gap-1">
    {categoria.sottocategorie.map((s) => (
      <li key={`${s.categoria_id}-${s.nome}`} className="flex justify-between type-caption text-ink-soft">
        <span>{s.nome}</span><span className="tabular-nums">{formatEurFromCents(s.total_cents)}</span>
      </li>
    ))}
  </ul>
) : null}
```

- [ ] **Step 2: Add the cuscinetto-mesi control to the Allocazione tab.** In `liquidita.tsx` `AllocazioneTab`, add a small numeric input next to the Cuscinetto card bound to a query `["cuscinetto-mesi"]` (`LiquiditaService.getCuscinettoMesi`), with a `useMutation` calling `setCuscinettoMesi` on change/blur that invalidates `["allocazione"]` and `["cuscinetto-mesi"]`:

```tsx
const { data: cusc } = useQuery({ queryKey: ["cuscinetto-mesi"], queryFn: () => LiquiditaService.getCuscinettoMesi() })
const [mesi, setMesi] = useState("")
// seed from cusc?.mesi_cuscinetto; on blur, if valid int >=1, PUT then invalidate
```

Render: `Cuscinetto: [input] mesi` with a "Salva" affordance or save-on-blur; show validation (>=1).

- [ ] **Step 3: Verify build/lint.**

Run: `cd frontend && npm run lint && npm run build && npx biome ci .`
Expected: green.

- [ ] **Step 4: Commit + push frontend batch.**

```bash
git add frontend/src/routes/_layout/index.tsx frontend/src/routes/_layout/liquidita.tsx
git commit -m "feat(fe): Home sub-category drill-down split + configurable Cuscinetto months"
git push origin <branch>
```

Then watch CI green.

---

### Task 10: Final verification + demo refresh

- [ ] **Step 1: Full backend gate.** Run: `cd backend && uv run ruff check . && uv run ruff format --check . && uv run mypy app && uv run pytest -q` — expect all green (≈ +12 tests).
- [ ] **Step 2: Full frontend gate.** Run: `cd frontend && npm run lint && npm run build && npx biome ci .` — green.
- [ ] **Step 3: Confirm CI green** on the pushed branch (backend + frontend jobs).
- [ ] **Step 4: Restart the demo backend** so the new endpoints are live: `pkill -9 -f "uvicorn app.main:app"; (cd backend && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000)` (background), then optionally seed a sub-category on `demo` (e.g. Casa → Mutuo) for a visible demo.
- [ ] **Step 5: Update docs** — mark the design spec implemented; note the three features in `deferred-work.md`/sprint-status if tracked.

## Self-Review

- **Spec coverage:** parent_id model+migration (T1); create+validation+projections (T2); cascade delete (T3); top-level aggregation + sotto-split (T4); /movimenti children (T5); configurable cuscinetto endpoints + allocazione (T6); quick-add note (T7); Categorie tree+create UI (T8); Home sub-split + cuscinetto UI (T9); verification+demo (T10). All spec sections covered.
- **Placeholders:** none — every backend step has real test + impl code + exact commands; frontend steps give the concrete code blocks and the build/lint gate (this repo has no FE unit-test framework beyond the CI Playwright theme suite — FE tasks are verified by tsc/biome/build + CI, matching existing practice).
- **Type consistency:** `CategoriaSpesa.sottocategorie` (T4) consumed in T9; `CuscinettoMesi{mesi_cuscinetto}` (T6) consumed in T9; `categorie.parent_id` (T1) used by T2/T3/T4/T5/T8; migration `e9f0a1b2c3d4`/down `d8e9f0a1b2c3` consistent.
- **Ordering:** backend T1→T6 (push+CI), then frontend T7→T9 (push+CI), then T10. Frontend depends on the regenerated client from T7.
