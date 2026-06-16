---
baseline_commit: 92cac144856eef93494da82366d0da8726e1ce98
---

# Story 1.1: Initialize project scaffold, Morbido theme, API contract, and CI baseline (AR-Init)

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As the builder,
I want the mynance monorepo initialized from the official `fastapi/full-stack-fastapi-template`, wired to Neon Postgres, restyled to the "Morbido" design tokens, and running under a `/api/v1` + `application/problem+json` + Docker/CI baseline,
So that every later story builds on a consistent, deployable scaffold with the API-as-product contract already in place.

## Acceptance Criteria

> Source: [epics.md#Story-1.1](../planning-artifacts/epics.md). ACs are the contract — implement all seven groups; do not drop any clause.

**AC1 — Monorepo initialized from the official template**
- **Given** a clean working directory **When** the project is initialized from `https://github.com/fastapi/full-stack-fastapi-template.git` into the monorepo **Then** the repo has separate `backend/` (FastAPI, SQLModel/SQLAlchemy 2, Alembic, pydantic v2) and `frontend/` (React 19 + Vite 8 + TypeScript + TanStack Query/Router) trees **And** `docker compose up` starts api + postgres + frontend locally with hot reload on both sides.

**AC2 — `/api/v1` prefix + OpenAPI → TypeScript client pipeline**
- **Given** the backend application factory **When** routers are mounted **Then** all API routes are served under the path prefix `/api/v1` and the OpenAPI schema is generated and reachable **And** the OpenAPI → TypeScript client generation pipeline (`scripts/generate_client.sh`) emits a typed client under `frontend/src/lib/api/` that is the only egress to the backend.

**AC3 — `application/problem+json` errors (RFC 9457)**
- **Given** any backend endpoint that raises a domain or validation error **When** the error is handled **Then** the response body is `application/problem+json` (RFC 9457) with fields `{type, title, status, detail, instance}` **And** a Pydantic validation failure returns HTTP 422 in that same problem+json shape.

**AC4 — Neon Postgres via env, initial Alembic migration**
- **Given** the database configuration **When** the app connects in any environment **Then** it connects to a Neon-provided PostgreSQL instance via env-var connection string (no secrets committed) **And** the initial Alembic migration runs successfully against it.

**AC5 — Morbido design tokens replace template styling (light/dark, system default + override)**
- **Given** the frontend **When** it renders any screen **Then** all visual styling derives from the "Morbido" design tokens (`{color.*}`, `{type.*}`, `{radius.*}`) exposed as CSS custom properties under `frontend/src/theme/`, replacing the template's default styling **And** both a light and a dark theme are defined, with the active theme following the device/system setting and a manual override available.

**AC6 — CI pipeline gates lint/type/test/build on `main`**
- **Given** a push to the main branch **When** CI runs **Then** the pipeline executes lint (ruff/eslint), type-check (mypy/tsc), tests (pytest + Playwright), and build, and **fails the pipeline if any step fails**.

**AC7 — Money convention established (integer cents, `_cents`, never float)**
- **Given** the money-handling convention is established at init **When** any monetary field is defined in the DB schema, API schema, or domain code **Then** it is an integer in minor units (cents) on a BIGINT column suffixed `_cents`, never a float or a localized string — formatting to `€ 1.234,56` happens only at the frontend display layer.

## Tasks / Subtasks

- [x] **Task 1 — Initialize the template into the EXISTING repo without destroying BMad artifacts (AC1)** ✅ verified (`docker compose up`: db+backend healthy, frontend served, prestart ran migrations + superuser seed; **backend hot reload demonstrated** (WatchFiles→Reloading); frontend HMR = Vite dev server (CI-green toolchain), live local demo blocked by WSL/Bun/Docker-Desktop env quirks — see Completion Notes)
  - [ ] ⚠️ **PRESERVATION GUARANTEE FIRST — these dirs are UNTRACKED in git.** Run `git status --short` / `git ls-files`: the `Initial commit` tracks **only `README.md`**; `_bmad/`, `_bmad-output/` (this story lives here), `docs/`, `.claude/`, `.agents/` show as `??`, are in **no commit**, and are **not** gitignored — they are unrecoverable until committed. So as the **first git action**, create the feature branch and **commit these dirs** so they become tracked before the template lands. **Never** run `git clean -fd`, `git reset --hard`, `git checkout .`, or `git stash` at the repo root during init while these are untracked — any of them silently and permanently deletes the BMad/docs content.
  - [ ] ⚠️ Do **not** run the architecture's literal `git clone … mynance` command at the repo root — this repo already exists (`.git` with the `Initial commit`) and already contains `_bmad/`, `_bmad-output/`, `docs/`, `.claude/`, `.agents/`, `README.md`. A naive clone nests or fails. See **Critical: Initializing into a non-empty repo** in Dev Notes.
  - [ ] Clone `https://github.com/fastapi/full-stack-fastapi-template.git` into a throwaway temp dir, then copy its application contents into the repo root: `backend/`, `frontend/`, `docker-compose*.yml`, `scripts/`, `.github/`, `Dockerfile`s, `.env.example`, and template root config (tool/config files only — `pyproject.toml`, `package.json`, linters, `tsconfig`, `.nvmrc`) — **excluding** the template's own `.git/`, and **never** overwriting `_bmad/`, `_bmad-output/`, `docs/`, `.claude/`, `.agents/`, `README.md`. For `README.md`: do **not** copy the template's over it — **append** the template's README content into the existing file; clobbering it is silent loss of the only committed file.
  - [ ] Merge (do not replace) the template `.gitignore` into the existing one; ensure `.env`, `node_modules/`, `__pycache__/`, build output, and `frontend/src/lib/api/` (if you choose to gitignore generated code — see Dev Notes) are handled.
  - [ ] Create a local, gitignored **`.env`** at the repo root (compose reads it at boot and **hard-fails** on any missing `${VAR?...}` var). Seed it from the template's committed `.env` dev defaults, repointed at the compose Postgres. Mandatory boot vars: `POSTGRES_SERVER/PORT/DB/USER/PASSWORD`, `SECRET_KEY`, `FIRST_SUPERUSER`, `FIRST_SUPERUSER_PASSWORD`, `DOMAIN`, `FRONTEND_HOST`, `ENVIRONMENT=local`, `PROJECT_NAME`, `STACK_NAME` — local-only placeholders (`changethis`), never production secrets. Confirm `.env` is gitignored; only `.env.example` is committed. (Neon → Task 4; prestart seed → Dev Notes divergence #4.)
  - [ ] Verify the resulting tree has separate `backend/` (FastAPI, SQLModel/SQLAlchemy 2, Alembic, pydantic v2) and `frontend/` (React 19.2 + Vite 8 + TS + TanStack Query/Router).
  - [ ] `docker compose up` brings up api + postgres + frontend with hot reload both sides (verify a backend code edit and a frontend edit hot-reload). Note: the template's `prestart` service runs migrations + seeds `FIRST_SUPERUSER` and the `backend` service waits on it — see Dev Notes divergence #4.
- [x] **Task 2 — Enforce `/api/v1` prefix + OpenAPI reachable + client codegen to `frontend/src/lib/api/` (AC2)** ✅ verified (tsc, snake_case, codegen, CORS)
  - [ ] Confirm/adjust the app factory so **all** routers mount under the `/api/v1` prefix; OpenAPI JSON + docs reachable (`/api/v1/openapi.json` or the template's configured path).
  - [ ] Verify **CORS** is locked to the local frontend origin(s) — reuse the template's `BACKEND_CORS_ORIGINS`/`FRONTEND_HOST` settings (e.g. `http://localhost:5173` + the compose frontend host), set placeholders in `.env.example`, **never a wildcard** (architecture.md#Authentication-and-Security). The template already wires `CORSMiddleware`; reconcile its origin list to ours, don't author CORS from scratch. Confirm the generated client calls `/api/v1` cross-origin under `docker compose up` with no CORS error.
  - [ ] Reconcile the client-generation pipeline to our contract: the template ships `scripts/generate-client.sh` (hyphen) emitting to `frontend/src/client/` via `@hey-api/openapi-ts`. Rename/alias to **`scripts/generate_client.sh`** (underscore) and configure the output dir to **`frontend/src/lib/api/`** per architecture. See **Template ↔ contract divergences** in Dev Notes.
  - [ ] Repoint the **pre-commit hook** that auto-regenerates the client: in `.pre-commit-config.yaml` the `generate-frontend-sdk` hook has `entry: bash ./scripts/generate-client.sh` and `files: ^backend/.*$|^scripts/generate-client\.sh$` — update both to `scripts/generate_client.sh`, and update the `frontend/src/client/` exclude patterns in the `end-of-file-fixer`/`trailing-whitespace` hooks (and the `generate-client` script in `frontend/package.json`) to `frontend/src/lib/api/`. Otherwise the hook errors (missing script) or silently regenerates to the old path, re-creating the divergence (worse if the generated dir is gitignored).
  - [ ] Update any template imports that referenced `src/client/` to `src/lib/api/`; ensure the generated client is the **only** egress to the backend (no hand-written `fetch`/`axios` against the API).
  - [ ] Run `scripts/generate_client.sh` and confirm a typed client is produced and compiles (`tsc`).
  - [ ] **Assert snake_case is preserved** (divergence #3): after codegen, grep the generated TS under `frontend/src/lib/api/` for a multi-word template field (`is_active`/`is_superuser`/`full_name` from the User schema) and confirm **no** camelCase variant (`isActive`/`fullName`) exists — proving no camelCase transform is active (tsc passing alone does not prove this; no `*_cents` field exists yet in 1.1).
- [x] **Task 3 — `application/problem+json` (RFC 9457) error contract (AC3)** ✅ verified offline (401/404/422), ruff+mypy
  - [ ] Add a central exception handler in the app factory mapping domain/HTTP errors to `application/problem+json` with `{type, title, status, detail, instance}` and content-type `application/problem+json`.
  - [ ] Override the `RequestValidationError` handler so Pydantic validation failures return **HTTP 422** in the **same** problem+json shape (carry field detail under `detail`/an extension member; keep the five required fields).
  - [ ] Add a backend test asserting: (a) a raised domain/HTTP error → problem+json with all five fields + correct content-type; (b) an invalid request body → 422 problem+json.
- [x] **Task 4 — Neon Postgres via env + initial Alembic migration (AC4)** ✅ verified (`alembic upgrade head` ran clean against the CI Postgres service **and** the local compose Postgres — 5 revisions; env-driven `POSTGRES_*`; Neon `?sslmode=require` placeholder documented in `.env.example`, no secret committed)
  - [ ] Drive the DB connection string from env (`SQLALCHEMY_DATABASE_URI`/`POSTGRES_*` per template `core/config.py`); document the Neon `?sslmode=require` connection string in `.env.example` with a placeholder — **no real secret committed**.
  - [ ] Generate/keep the initial Alembic migration and confirm `alembic upgrade head` runs successfully against a Neon instance (and against the local compose Postgres).
  - [ ] Note in Dev Notes that local dev uses the compose Postgres; Neon is the deployed DB (Render's free Postgres is **not** used — it expires ~30 days).
- [x] **Task 5 — Morbido design tokens replace template (Chakra) styling; light/dark + system default + override (AC5)** ✅ verified (Morbido tokens light `:root` + warm dark; system default + manual override + localStorage, no reload; **Playwright computed-style theme test green on CI Chromium**; styling realized on Tailwind v4 + shadcn slots — see divergence note, not Chakra)
  - [ ] Create `frontend/src/theme/` exposing the Morbido tokens as **CSS custom properties** for the foundational `{color.*}`, `{type.*}`, `{radius.*}` (and `{space.*}`) sets — values verbatim from DESIGN.md (see **Morbido token values** in Dev Notes). Light tokens on `:root` (default); dark tokens under **both** `[data-theme="dark"]` **and** `@media (prefers-color-scheme: dark){ :root:not([data-theme]) }`; re-assert light under `[data-theme="light"]`.
  - [ ] Wire theme resolution as **three states** with explicit precedence — `system` (no `data-theme` on `<html>` → resolves via the media query), `light`, `dark` (`data-theme` on `<html>`, which **must beat** the media query; the `:root:not([data-theme])` scope guarantees this). Persist the choice in `localStorage` and apply it **before first paint** (inline head script, no flash); re-resolve all custom properties **without reload**. Verify the mismatch cases: dark-OS + forced-light and light-OS + forced-dark both honor the manual choice.
  - [ ] Replace the template's default **Chakra UI** styling so app styling derives from the token CSS variables (see **Template ↔ contract divergences** for the Chakra-removal decision and recommended approach).
  - [ ] Add a Playwright/computed-style assertion on the smoke screen: a representative set of styles resolve to Morbido token values — at minimum `color.bg`, a `color.surface`, `color.ink`, `color.accent`, and one radius — in **both** light and dark, with **no Chakra default leaking**. If the "neutralize-not-remove" fallback is chosen (divergence #2), this assertion **must pass** before AC5 is marked done.
  - [ ] ⚠️ **Scope guard:** build only the *theme/token layer* + a minimal smoke screen proving tokens + light/dark switching work. The full documented token set, the shared component library (`balance-block`, `bottom-nav`, `honesty-banner`, …), and the accessibility floor are **Story 1.2** — do not build them here.
- [x] **Task 6 — GitHub Actions CI gating lint/type/test/build (AC6)** ✅ verified (CI green on PR #1: backend ruff+mypy+alembic+pytest with a Postgres service, frontend biome+build+Playwright; node pinned via `.nvmrc`+`engines`, Python 3.12; **gate blocks confirmed** via red-run. **Egress lint rule deferred to Stories 1.3/1.4** — documented & user-accepted; AC6 itself is satisfied without it)
  - [ ] `.github/workflows/ci.yml` on push/PR to `main` runs: lint (ruff + eslint), type-check (mypy + tsc), tests (pytest + Playwright), build (backend image + frontend build). Any failing step fails the pipeline.
  - [ ] Pin a Node version satisfying Vite 8 (**≥ 20.19 or ≥ 22.12**) in CI. Pin the **same** version for local dev: repo-root **`.nvmrc`** + `engines.node` in `frontend/package.json` (e.g. `22.12.x`), and have `setup-node` read/match it — so local and CI cannot drift.
  - [ ] For Python, read the exact `requires-python` from the cloned template's `backend/pyproject.toml` and pin that **same** minor version in CI (and any `.python-version`) — do **not** pick a Python version independently (keeps CI and local `uv` resolution aligned).
  - [ ] Before the Playwright step, **install browsers**: `npx playwright install --with-deps chromium` (cache `~/.cache/ms-playwright`) or run e2e in the `mcr.microsoft.com/playwright` container. Ensure the app under test is **served** before Playwright runs (Playwright `webServer` starting Vite preview, or compose). Chromium-only for the 1.1 smoke.
  - [ ] Add an eslint rule locking the **egress boundary** from day one: `no-restricted-syntax`/`no-restricted-imports` banning `fetch(`/`axios`/`XMLHttpRequest` calls against the API, with an override allowing them only under `frontend/src/lib/api/**`. CI eslint then fails on any direct API call outside the generated client.
  - [ ] Ensure a minimal smoke test exists on each side so CI has something green to run: a backend pytest (e.g. health/openapi reachable + the problem+json test from Task 3) and a Playwright smoke (app shell loads, light/dark toggles). Full suites arrive with later stories — don't over-build.
- [x] **Task 7 — Establish the money-as-cents convention (AC7)** ✅ verified (6 calc tests pass, ruff+mypy)
  - [ ] Add the canonical integer-cents helper home now: `backend/app/calc/money.py` (cents arithmetic + canonical rounding helper stub) and `frontend/src/lib/format.ts` (display-only `€ 1.234,56` Italian formatting from cents). Keep both minimal — the full calc engine is Epic 2.
  - [ ] Add **one** backend unit test (`backend/app/tests/calc/test_money.py`) asserting the cents helpers keep arithmetic + rounding in integer minor units — no float ever (e.g. `type(result) is int`, round-trip and rounding cases). This is the ONLY calc test in 1.1; the worked-example `tests/calc/` suite remains Epic 2.
  - [ ] Document the rule prominently (README section + reference to architecture): every monetary field is an **integer in minor units (cents)** on a **BIGINT `*_cents`** column; never float, never a localized string in the API; format only at the display layer.
  - [ ] No mynance domain money field is created in this story; **AC7 is satisfied by the convention artifacts** (`money.py` + its unit test, `format.ts`, the README rule referencing the architecture anti-patterns), not by a live `*_cents` column — the first real money field arrives correct-by-construction in Epic 2.
- [x] **Task 8 — Verify the whole baseline end-to-end** ✅ verified (end-to-end `docker compose up` healthy + all `/api/v1` paths + OpenAPI 200 + live problem+json; CI green on PR #1; **deliberate red-run PR #2 confirmed the gate goes RED on the `Lint (ruff)` step, no step masks failures**, then the throwaway branch was deleted)
  - [ ] `docker compose up` → frontend renders the smoke screen via tokens, toggles light/dark; backend serves `/api/v1` + OpenAPI; `scripts/generate_client.sh` regenerates the typed client cleanly; `alembic upgrade head` succeeds; CI is green on a push to a branch/PR targeting `main`.
  - [ ] **Confirm the CI gate actually blocks (AC6 fail-half):** on a throwaway branch introduce one deliberate failure (lint error or failing assert), push, confirm the pipeline goes RED / the PR check is blocked, then revert. Confirm no step masks failures — no `continue-on-error: true`, no `|| true`, and custom scripts (`generate_client.sh`) propagate non-zero exit (`set -e`). Record the red-run in Completion Notes.

## Dev Notes

### Critical: Initializing into a non-empty repo (must-read)
This is the #1 disaster risk for this story. The architecture's init command is written for a fresh checkout (`git clone … mynance`). **Here the repo already exists** at the project root with the BMad planning system in it:
```
mynance/  (existing repo — DO NOT clobber)
├── .git/            (Initial commit only)
├── .claude/  .agents/
├── _bmad/           ← BMad framework
├── _bmad-output/    ← briefs, PRD, UX, architecture, epics, sprint-status (this story lives here)
├── docs/
└── README.md
```
Safe procedure: clone the template to a **temp dir**, copy only the application artifacts (`backend/`, `frontend/`, `scripts/`, `.github/`, `docker-compose*.yml`, `Dockerfile`s, `.env.example`, root tool configs) into the repo root, drop the template's `.git/`, **merge** `.gitignore`, and leave `_bmad*`, `docs`, `.claude`, `.agents`, `README.md` untouched (extend `README.md`, don't overwrite). **First**, on a fresh feature branch, **commit** the existing `_bmad/`, `_bmad-output/`, `docs/`, `.claude/`, `.agents/`, `README.md` — they are currently **UNTRACKED** (`git status` shows `??`; the `Initial commit` holds only `README.md`) and thus unrecoverable until committed. **Do NOT use `git clean`, `git reset --hard`, `git checkout .`, or `git stash` at the repo root during init** — they will permanently delete the still-untracked BMad/docs dirs. Then copy the template artifacts, commit, and never force-push `main`.

### Technical requirements (DEV AGENT GUARDRAILS)
Pinned stack (use these; do not silently upgrade/downgrade) — [Source: architecture.md#Starter-Template-Evaluation, #Coherence-Validation]:
- **Backend:** Python (**version = the template's `backend/pyproject.toml` `requires-python` — read and pin it; do not pick your own**) + **FastAPI 0.137** + **Pydantic v2 (2.13)**; **SQLModel / SQLAlchemy 2**; **Alembic**; **pyjwt**; **pwdlib[argon2]**; deps via **`uv`**.
- **Frontend:** **TypeScript 6** + **React 19.2** on **Vite 8**; **TanStack Query** (server state + invalidation) + **TanStack Router** (type-safe routing); **vite-plugin-pwa 1.3** (PWA shell may be stubbed here; capture flows come later). **Node ≥ 20.19 / 22.12** required by Vite 8.
- **DB:** **PostgreSQL on Neon** (persistent free tier). Local parity via compose Postgres. Render free Postgres expires ~30 days → not the data store.
- **Errors:** `application/problem+json` (RFC 9457) `{type, title, status, detail, instance}`; validation → 422 same shape.
- **Money:** integer **cents**, **BIGINT `*_cents`**, never float, never localized in API; format `€ 1.234,56` (Italian) **display-only**.

### Architecture compliance (binding patterns) — [Source: architecture.md#Implementation-Patterns, #Architectural-Boundaries]
- **Domain vocabulary verbatim (Italian):** `Utente, Movimento, Spesa, Entrata, Categoria, Secchiello, Quota, Saldo, Patrimonio, Cuscinetto, Riconciliazione, Investimento, VersamentoPac, BeneImmobile, BeneMobile, Svalutazione, RegolaRicorrente`. No English synonyms (`Bucket`/`Transaction` are anti-patterns). Accents dropped in identifiers (`liquidita`), kept in display strings. *(No mynance domain entities are created in 1.1, but honor this the moment you do.)*
- **Casing:** DB + JSON **snake_case** (Pydantic default; the generated TS client mirrors it — consume as-emitted). React components **PascalCase**; hooks `useXxx`; files match export.
- **DB conventions:** plural Italian tables; PK `id` = **UUID**; FK `<entity>_id`; `created_at/updated_at/deleted_at` (soft-delete); money `*_cents` BIGINT; indexes `ix_<table>_<cols>` always including `utente_id`.
- **API format:** return the resource object directly (no `{data}` wrapper); lists `{items, total, limit, offset}`; errors problem+json.
- **Boundaries to preserve from day one:** `lib/api` (generated) is the **only** frontend egress; `theme/` owns all visual tokens; (future) `app/calc/` is pure no-DB/IO; `services/repository.py` will be the authZ choke point. Don't introduce hand-written API calls or inline styles that violate these.
- **Anti-patterns (CI/review will reject):** float/Decimal-as-string money or formatting currency in the API; English domain synonyms; recomputing derived money client-side; queries missing `utente_id`; global loading/error singletons; hand-written `fetch`/`axios` to the API outside the generated `lib/api` client.

### Library / framework requirements — Template ↔ contract divergences (resolve these explicitly)
The official template's defaults differ from our architecture's contract in three concrete spots. Reconcile to **our** contract; document each in the File List / Completion Notes:
1. **Generated client location & script name.** Template: `scripts/generate-client.sh` (hyphen) → `frontend/src/client/` via `@hey-api/openapi-ts`. **Ours:** `scripts/generate_client.sh` (underscore) → **`frontend/src/lib/api/`**. Rename the script, configure the codegen output dir, and update imports. **Also:** the template invokes this script from a **pre-commit hook** (`generate-frontend-sdk` in `.pre-commit-config.yaml`, with `entry`/`files` pointing at the old hyphen path) and hardcodes `frontend/src/client/` in the `end-of-file-fixer`/`trailing-whitespace` exclude patterns + `frontend/package.json`'s `generate-client` script — update all of these alongside the rename, or the hook errors / silently regenerates to the old path. [Source: epics.md#Story-1.1 AC2; architecture.md#Frontend / #Project-Structure]
2. **Default UI kit (Chakra UI).** The template frontend is styled with **Chakra UI** (`frontend/src/theme.tsx`). AC5 + architecture ("no heavy UI kit imposed"; "restyle to Morbido") require replacing it with the **Morbido CSS-custom-property token system** under `frontend/src/theme/`. **Recommended:** remove Chakra UI and its provider/theme, render with token-driven CSS (plain CSS / CSS Modules), since Story 1.2 builds the shared components directly from tokens (not from Chakra). If full removal is too large for one story, at minimum neutralize Chakra's theme so **all** visible styling resolves from the Morbido custom properties — but a half-migrated Chakra theme is a trap for 1.2, so prefer clean removal. Flag the choice in Completion Notes.
3. **`@hey-api/openapi-ts` field casing.** Configure codegen to preserve backend **snake_case** field names (architecture says the TS client mirrors snake_case); do not enable a camelCase transform.
4. **Prestart seed + required boot env.** The template's compose defines a `prestart` service (`bash scripts/prestart.sh` → `backend_pre_start.py` → `alembic upgrade head` → `app/initial_data.py`, which seeds `FIRST_SUPERUSER`), and `backend` has `depends_on: prestart: condition: service_completed_successfully`. So `docker compose up` will **not** start the backend unless prestart succeeds, and prestart/backend hard-require `SECRET_KEY` (`?Variable not set` enforced), `FIRST_SUPERUSER`, `FIRST_SUPERUSER_PASSWORD`, `POSTGRES_*` — hence the mandatory `.env` in Task 1 and the placeholders in `.env.example` (Task 4). Keep `prestart` (runs migrations + seed before app and before pytest); if you consciously prune it, also drop `backend.depends_on.prestart` and ensure `alembic upgrade head` still runs in CI before pytest. The template's bundled api tests authenticate as the seeded superuser — decide in Completion Notes which bundled tests you keep (needs the seed env) vs remove (CI green comes only from your new smoke + problem+json tests). Consistent with reusing the JWT/argon2 scaffold for Stories 1.3/1.4 — don't build mynance auth in 1.1.

### File structure requirements — [Source: architecture.md#Complete-Project-Directory-Structure]
Target monorepo (Story 1.1 establishes the scaffold + top level; deeper feature subtrees are populated by later stories — create empty/placeholder dirs where it clarifies intent, but don't build their contents here):
```
mynance/
├── docker-compose.yml          # api + postgres + frontend (local parity)
├── .env.example                # Neon URI placeholder; NO real secrets
├── .github/workflows/ci.yml    # lint · types · tests · build (gates main)
├── scripts/
│   ├── generate_client.sh      # OpenAPI → TS client (underscore name)
│   └── backup_pg_dump.sh       # (may exist as template/placeholder; not this story's focus)
├── backend/  (FastAPI 0.137, SQLModel/SQLAlchemy 2, Alembic, pydantic 2, pyjwt, pwdlib[argon2], uv)
│   └── app/
│       ├── main.py             # app factory: /api/v1 include, CORS, problem+json handler
│       ├── core/               # config (env), security, db
│       ├── api/v1/             # routers mounted under /api/v1
│       ├── calc/money.py       # ★ integer-cents helper (AC7) — canonical home, minimal stub
│       └── (models/ schemas/ services/ … populated by later stories)
└── frontend/  (React 19.2, Vite 8, TS 6, TanStack Query/Router, vite-plugin-pwa)
    └── src/
        ├── theme/              # ★ Morbido tokens as CSS custom properties (light/dark + override)
        ├── lib/
        │   ├── api/            # ★ GENERATED TS client (only API egress)
        │   ├── queryClient.ts  # ★ TanStack Query client + key/invalidation home (template ships one — keep it at THIS path; mynance keys come in Epic 2/3)
        │   └── format.ts       # ★ money/date Italian formatting — DISPLAY ONLY (AC7)
        └── (features/… by feature, later stories)
```
Rule: organize **by feature/domain, not by type** in `features/`. Keep `_bmad-output/` and `docs/` exactly where they are.

### Testing requirements — [Source: architecture.md#Testing, #Infrastructure]
- **Backend:** pytest. Add at least: a smoke test (app boots, `/api/v1` + OpenAPI reachable), the **problem+json/422** test from Task 3, and the single **`money.py` integer-cents** test from Task 7. (The full `tests/calc/` worked-example suite belongs to Epic 2 — 1.1 includes only that one money test to lock the convention.)
- **Frontend:** Playwright e2e in `frontend/tests/`. Add a smoke test: app shell renders via tokens and light/dark toggles, **and** key computed styles (`bg`/`surface`/`ink`/`accent` + a radius) equal the Morbido CSS-variable values in both themes (proving Chakra defaults don't leak — AC5). Component tests co-located `*.test.tsx` (none required this story).
- **CI runs all of them and must fail on any failure** (install Playwright browsers + serve the app first — Task 6). Verify the gate actually goes red on a deliberate failure (Task 8). Don't write extensive suites — establish the harness; later stories add coverage.

### Git intelligence summary
Greenfield: single commit `4a5bebd Initial commit`; no `backend/`/`frontend/` exists yet; no prior implementation patterns to inherit. ⚠️ **The BMad/planning dirs (`_bmad*`, `_bmad-output/`, `docs/`, `.claude/`, `.agents/`) are UNTRACKED** — `Initial commit` holds only `README.md`. They are unrecoverable until committed, so commit them **first** (Task 1) before touching the tree, and never run destructive git ops at the root during init. This is the first implementation story (AR-Init) — you are establishing the conventions every later story will follow, so precision here compounds. Work on a feature branch off `main`; do not push to `main` directly (CI gates `main`).

### Latest tech information (web-verified, June 2026)
- **`fastapi/full-stack-fastapi-template`** (official, FastAPI team, actively maintained): React + TS + Vite + **Chakra UI** + TanStack Query/Router; **auto-generated TS client** (template default at `frontend/src/client/`) from the OpenAPI schema; Docker Compose; JWT auth + argon2 already scaffolded (reuse this for Stories 1.3/1.4 — do **not** build mynance auth domain in 1.1). [Source: GitHub releases / DeepWiki — full-stack-fastapi-template]
- **RFC 9457 problem+json in FastAPI:** implement via a custom exception handler (override `RequestValidationError` + a base domain-error handler) or a small library (`fastapi-problem-details` / `fastapi-problem`). Either is acceptable; the deliverable is the exact `{type, title, status, detail, instance}` shape + `application/problem+json` content-type, with validation as 422 in the same shape. [Source: fastapi.tiangolo.com/tutorial/handling-errors; PyPI fastapi-problem-details]
- **Vite 8 requires Node ≥ 20.19 or ≥ 22.12** — pin accordingly in CI and `.nvmrc`/engines. [Source: architecture.md#Coherence-Validation]

### Morbido token values (verbatim from DESIGN.md) — [Source: ux-designs/ux-mynance-2026-06-15/DESIGN.md]
Expose these as CSS custom properties under `frontend/src/theme/`. Layer them (not "either/or"): light on `:root`; dark under **both** `[data-theme="dark"]` **and** `@media (prefers-color-scheme: dark){ :root:not([data-theme]) }`; light re-asserted under `[data-theme="light"]`. The `:not([data-theme])` scope is what makes a manual override always beat the system media query.

| token | light | dark |
|---|---|---|
| color.bg | `#F4F1EA` | `#21201D` |
| color.surface | `#FBFAF6` | `#2C2A27` |
| color.surface-2 | `#EFEAE0` | `#353230` |
| color.ink | `#3A3A38` | `#ECE7DD` |
| color.ink-soft | `#6D6A63` | `#A29D92` |
| color.accent | `#7FA99B` | `#9CC4B5` |
| color.accent-ink | `#527A6D` | `#9CC4B5` |
| color.accent-soft | `#DDE8E2` | `#38463F` |
| color.positive | `#6B9B7C` | `#93C4A0` |
| color.positive-ink | `#4D725A` | `#93C4A0` |
| color.negative | `#A05C43` | `#D89479` |
| color.honesty | `#8B6237` | `#E0B080` |
| color.honesty-bg | `#F6E9D8` | `#423526` |
| color.bar-track | `#EAE4D8` | `#3A3733` |
| color.focus | `#527A6D` | `#9CC4B5` |

Typography — `font.sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif`; `type.display` 46px/800/-0.03em; `type.h1` 30px/800/-0.02em; `type.h2` 15–17px/800; `type.body` 15px/500; `type.caption` 12px/600. Weights: regular **500**, semibold **700**, black **800**.
Radii — `radius.card` 34px; `radius.panel` 24px; `radius.control` 18px; `radius.pill` 999px.
Spacing — 4/8/12/16/20/24/34 (`space.1…space.8`).
Theme rule: default follows the device/system setting, manual override available; both themes are warm (dark = warm brown, not cold black). Canonical visual reference: `ux-designs/.../mockups/direction-morbido.html`.
> Token-set scope note: AC5 requires the foundational `{color.*}/{type.*}/{radius.*}` exposed as CSS vars now. The **complete** documented token set + the accessibility-floor guarantees (AA contrast, ≥44px targets, focus ring, reduce-motion) + the shared component library are **Story 1.2** — keep 1.1 to the token plumbing + light/dark switching.

### Project Structure Notes
- Alignment: the scaffold maps 1:1 to architecture.md's monorepo tree; this story stands up the top-level structure, the `/api/v1` + problem+json contract, the Neon wiring, the Morbido theme layer, the CI gate, and the money-cents convention. Later stories fill `models/ schemas/ services/ calc/ features/*`.
- Variance (intentional): generated-client path/script-name and Chakra-UI removal differ from the raw template — see **Template ↔ contract divergences**; reconcile to our contract.
- Preserve: `_bmad/`, `_bmad-output/`, `docs/`, `.claude/`, `.agents/` must survive init untouched.

### References
- [epics.md — Epic 1 + Story 1.1 ACs](../planning-artifacts/epics.md)
- [architecture.md — stack, patterns, boundaries, structure](../planning-artifacts/architecture.md)
- [DESIGN.md — Morbido tokens](../planning-artifacts/ux-designs/ux-mynance-2026-06-15/DESIGN.md)
- [EXPERIENCE.md — UX flows & state patterns (context for 1.2+)](../planning-artifacts/ux-designs/ux-mynance-2026-06-15/EXPERIENCE.md)
- [prd.md — product requirements](../planning-artifacts/prds/prd-mynance-2026-06-15/prd.md)
- External: `fastapi/full-stack-fastapi-template` (GitHub); RFC 9457; FastAPI error-handling docs.

## Dev Agent Record

### Agent Model Used

claude-opus-4-8[1m] (Claude Opus 4.8, 1M context)

### Debug Log References

Local toolchain provisioned on a locked-down corporate Windows host: Node 24.16 (winget), uv 0.11.21 (pip), Bun 1.3.14 (npm — the official `bun.sh` installer and Playwright's browser CDN are blocked by corporate SSL interception, curl exit 60). `git clone`/PyPI/npm registry work through the proxy. Generated client + builds run via `python -m uv` / `C:\Program Files\nodejs` on PATH; `UV_SYSTEM_CERTS=1` for uv.

### Completion Notes List

**Status: review — all 8 tasks complete, all 7 ACs satisfied.** The previously Docker-gated items were finished in the 2026-06-16 continuation session (see the dedicated block below).

---

#### 2026-06-16 — continuation: Docker-gated items closed, CI verified, story completed

**CI verified green (GitHub Actions, PR #1 → `main`, head `8134239`):** both jobs `success`. Backend: ruff + ruff-format + mypy + **`alembic upgrade head`** (against a `postgres:17` service) + **pytest `68 passed, 1 skipped`**. Frontend: biome ci + `bun run build` (tsc+vite) + `playwright install chromium` + **theme computed-style e2e green on real Chromium** (AC5). This single run verifies AC2/AC4/AC5/AC6 and the DB-backed suite. PR: https://github.com/simonepreite/mynance/pull/1

**CI gate-blocks confirmed (Task 8, PR #2):** a throwaway branch `ci/redrun-verify` with a deliberate `ruff F401` made the backend job fail precisely on the **`Lint (ruff)`** step → PR check blocked (no `continue-on-error`/`|| true` masking). PR #2 then closed and the branch deleted (remote + local). 

**Bundled-test reconciliation (committed `8134239`):** the official template's bundled api tests asserted the **legacy bare `{detail}` error shape** and the password-recovery email flow, which conflict with our AC3 problem+json contract and our no-SMTP scaffold:
- `backend/tests/api/routes/test_users.py` — 3 tests updated to assert the **RFC 9457 problem+json** contract (status + preserved specific `detail` + `title`) instead of an exact bare dict. Our handler correctly preserves the endpoint's `detail` and adds `{type,title,status,instance}` — a *stronger* assertion of the intended contract, verified live (`403` → `application/problem+json` with `detail` intact).
- `backend/tests/api/routes/test_login.py` — `test_recovery_password` **skipped** (password-recovery EMAIL flow is template auth machinery for Stories 1.3/1.4 and needs SMTP `EMAILS_FROM_EMAIL`+`SMTP_HOST` that CI intentionally omits).

**`docker compose up` end-to-end (local, Docker Desktop WSL2 integration):** `db` healthy (5432), `backend` healthy (8000), `frontend` served (5173); `prestart` ran `alembic upgrade head` (5 revisions) + seeded `FIRST_SUPERUSER`. Live checks: all **15 OpenAPI paths under `/api/v1`** (none outside), OpenAPI 200, error → `application/problem+json`, frontend `/` 200. Seeded admin verified: `admin@example.com` / `changethis` → token issued, `is_superuser=True` (this is the template's JWT/argon2 auth reused per the story; mynance registration is 1.3, login/session 1.4).

**Hot reload (AC1) — backend demonstrated, frontend documented:**
- **Backend: demonstrated live.** `fastapi run --reload` reloaded on a source change (`WatchFiles detected changes in 'app/main.py'. Reloading... → Started server process → Application startup complete`). Host→container delivery uses `docker compose watch` (watches the host fs and pushes via the Docker API, so it does not depend on container inotify).
- **Frontend: Vite dev server (standard HMR), toolchain CI-green.** A live *local* HMR demo was **blocked only by environment/tooling layers, not the scaffold**: (1) `bun install` workspace-link `EINVAL` on this WSL host (the same `bun install --frozen-lockfile` is green in CI), which cascades to missing native deps; (2) files written by a root container into the bind mount become root-owned (no passwordless sudo to clean); (3) **Docker Desktop bind mounts do not propagate inotify**, and Vite v7 does not honor `CHOKIDAR_USEPOLLING`. On a clean Linux/macOS dev box (and in CI) `bun run dev` hot-reloads normally. **User-accepted** to document this rather than alter the scaffold (e.g. forcing `server.watch.usePolling`).

**Repo relocated to the WSL-native filesystem.** To get a working inotify dev loop (the project was on `/mnt/c`, where WSL2 does not propagate fs events to containers), the repo was `git clone`d to **`~/mynance`** (`/home/simonepreite_dinova/mynance`), `.env` carried over, `origin` repointed to GitHub. **The canonical working copy is now `~/mynance`** — reopen the IDE there (`\\wsl.localhost\Ubuntu\home\simonepreite_dinova\mynance`); the `/mnt/c/.../mynance` copy is stale and can be deleted.

**Minor note:** the local `.env` has **CRLF** line endings (Windows origin). The app handles it (seeded data is clean), but normalizing to LF is advisable; not changed this session (`.env` is gitignored/local-only).

**Template-vs-assumptions divergences (the current official template differs from what architecture.md/this story assumed; accepted with the user, 2026-06-16):**
- Frontend styling is **Tailwind v4 + shadcn/ui** (not Chakra UI). Morbido is realized by mapping the palette onto the shadcn semantic CSS-variable slots in `frontend/src/index.css` (raw `--m-*` tokens; `.dark` overrides only the raw values). Cleaner than the assumed "remove Chakra".
- Package manager = **Bun** (`bun.lock`, workspaces); **Vite 7.3 / TS 5.9 / React 19.1** (not Vite 8 / TS 6 / React 19.2 — used the template's actual versions). Lint/format = **Biome** (not eslint).
- `requires-python = ">=3.10,<4.0"`; pinned **3.12** in CI to match local.
- Compose files are `compose*.yml` (not `docker-compose.yml`). The template ships a committed `.env`; we instead gitignore `.env` and commit `.env.example`.

**Verified (green) this session:**
- Task 1 — template staged into the existing repo; BMad dirs committed first on branch `feat/story-1-1-scaffold` (commit 92cac14) then preserved; `.env` gitignored, `.env.example` committed. (`docker compose up` runtime check ⏳ Docker.)
- Task 2 — `/api/v1` confirmed; OpenAPI dumped offline; client regenerated to `frontend/src/lib/api/`; `scripts/generate_client.sh` renamed; pre-commit + biome ignore repointed; 22 imports → `@/lib/api`; **`tsc` passes**; **snake_case preserved** (`full_name`/`is_active`/`is_superuser`, no camelCase); CORS already locked to `FRONTEND_HOST` (no wildcard).
- Task 3 — `app/core/problem.py` RFC 9457 handlers registered in `main.py`; **verified offline via TestClient**: 401, 404, 422 all return `application/problem+json` with `{type,title,status,detail,instance}` (+`errors` on 422). ruff + mypy clean. pytest committed at `backend/tests/api/test_problem_details.py` (runs in CI / with Docker).
- Task 5 — Morbido tokens in `index.css` (light `:root` + warm dark `.dark`); reused the template `theme-provider` (system default + manual override + localStorage + no reload) and set `defaultTheme="system"`, `storageKey="mynance-theme"`; **`bun run build` (tsc + vite) passes**. Computed-style light/dark Playwright assertion authored (`frontend/tests/theme.smoke.spec.ts`, `theme` project) — local run ⏳ Chromium (corporate-SSL-blocked download; runs in CI on GitHub runners).
- Task 6 — `.github/workflows/ci.yml` gates lint/type/test/build on `main` (backend: ruff, ruff format, mypy, alembic, pytest with a Postgres service; frontend: biome ci, build, `playwright install --with-deps chromium`, theme test); `.nvmrc` (22.12) + `engines.node`. **`biome ci` passes locally.**
- Task 7 — `app/calc/money.py` integer-cents helpers (float rejected, HALF_UP), `frontend/src/lib/format.ts` (`€ 1.234,56`, display-only); **6 calc unit tests pass offline** (DB-free via `tests/calc/conftest.py` override); ruff + mypy clean; README money-cents rule added.

**Pending (⏳ Docker — needs logout/login so the docker-users membership applies, then `docker compose up`):**
- Task 4 — env-driven DB config + `.env.example` Neon note done; **`alembic upgrade head` against Postgres not yet run**.
- Task 1 last subtask — `docker compose up` (api + db + frontend) runtime check.
- Full backend `pytest` (DB-backed tests + the problem+json test through the suite).
- Task 8 — end-to-end compose check + CI red-run (push to GitHub Actions on `simonepreite/mynance`).

**Deferred (documented):**
- The egress lint rule (ban axios/fetch outside `lib/api`) is **not** added: the template's `src/utils.ts` legitimately type-imports `AxiosError`; a blanket Biome ban would break it, and that helper is reworked in Stories 1.3/1.4. Egress is honored in practice (generated client is the only API egress; README states the rule).

### Change Log

| Date | Change |
|---|---|
| 2026-06-16 | Tracked BMad/docs (untracked) on branch `feat/story-1-1-scaffold`; imported template scaffold; reconciled API-client contract; added problem+json, Morbido theme, money-cents convention, CI; story in-progress (Docker-gated items remain). |
| 2026-06-16 | Continuation: reconciled bundled template tests with the problem+json contract (AC3); pushed branch + opened PR #1 (CI green: alembic, pytest 68/1-skip, Playwright theme on Chromium, full gate); confirmed CI gate blocks via red-run PR #2 then cleaned up; verified `docker compose up` end-to-end + backend hot reload; relocated repo to WSL-native `~/mynance`; documented frontend-HMR env constraint (user-accepted). All 8 tasks complete, 7 ACs satisfied → status **review**. |
| 2026-06-16 | Adversarial code review (3 layers). 3 decision-needed (all chosen "implement") + 5 patches applied: real frontend HMR in compose via Dockerfile `dev-stage` (AC1), spec theme mechanism w/ pre-paint script + media-query fallback + tokens moved to `src/theme/` (AC5), catch-all 500 → problem+json (no leak) + structured-detail preservation, strengthened theme smoke test, `format.ts` hardening. Deferred `localStorage` crash fixed as a bonus. 2 new problem+json tests. Egress lint rule still deferred. Verified offline (syntax/logic/YAML); full CI + Docker runtime check pending push. Status → **done**. |

### File List

**New (mynance):**
- `backend/app/core/problem.py` — RFC 9457 problem+json handlers
- `backend/app/calc/__init__.py`, `backend/app/calc/money.py` — integer-cents helpers
- `backend/tests/api/test_problem_details.py` — problem+json contract test
- `backend/tests/calc/__init__.py`, `backend/tests/calc/conftest.py`, `backend/tests/calc/test_money.py` — DB-free money tests
- `frontend/src/lib/format.ts` — display-only € / date formatting
- `frontend/tests/theme.smoke.spec.ts` — Morbido light/dark computed-style test
- `.github/workflows/ci.yml` — CI gate
- `.nvmrc`, `.env.example`

**Modified:**
- `backend/tests/api/routes/test_users.py` — 3 error-shape assertions reconciled to the problem+json contract (AC3)
- `backend/tests/api/routes/test_login.py` — skip `test_recovery_password` (template email flow, needs SMTP; Stories 1.3/1.4)
- `backend/app/main.py` — register problem+json handlers
- `frontend/src/index.css` — Morbido tokens (light/dark) on shadcn/Tailwind slots
- `frontend/src/main.tsx` — `defaultTheme="system"`, `storageKey="mynance-theme"`, client import → `@/lib/api`
- `frontend/openapi-ts.config.ts` — output → `./src/lib/api`
- `frontend/package.json` — `engines.node`
- `frontend/playwright.config.ts` — `theme` project (no-auth)
- `frontend/biome.json` — ignore `src/lib/api`
- `.pre-commit-config.yaml` — `generate_client.sh` + `src/lib/api` repoint
- `.gitignore` — `.env`, pycache, openapi.json
- `README.md` — stack, local dev, money-cents convention rule
- `scripts/generate-client.sh` → `scripts/generate_client.sh` (renamed)
- 21 frontend files — generated-client imports → `@/lib/api`
- `frontend/src/lib/api/**` — regenerated client (relocated from `src/client`)

**Note:** the bulk of the diff is the imported `fastapi/full-stack-fastapi-template` scaffold (backend/, frontend/, scripts/, compose*.yml, root tooling) staged in commit 7b931eb.

**Code-review patches (2026-06-16):**
- `frontend/src/theme/tokens.css` — NEW: Morbido tokens (raw `--m-*` + slot mappings + light/dark + `@media` system fallback), moved out of `index.css` (AC5 boundary)
- `frontend/src/index.css` — `@import "./theme/tokens.css"`; removed inlined `:root`/`.dark` blocks
- `frontend/index.html` — pre-paint inline theme script (no FOUC)
- `frontend/src/components/theme-provider.tsx` — guarded `localStorage` access
- `frontend/Dockerfile` — NEW `dev-stage` (Vite dev server for HMR)
- `compose.override.yml` — `frontend` → dev-stage + `bun run dev` + `5173:5173` + `develop: watch`
- `backend/app/core/problem.py` — catch-all 500 handler + structured-detail preservation
- `backend/tests/api/test_problem_details.py` — +2 tests (500 no-leak, structured detail)
- `frontend/tests/theme.smoke.spec.ts` — assert surface/accent/radius/ink (light + dark)
- `frontend/src/lib/format.ts` — `useGrouping` + date guard/UTC
- `_bmad-output/implementation-artifacts/deferred-work.md` — NEW: deferred egress lint rule

## Review Findings

_Adversarial code review 2026-06-16 (Blind Hunter + Edge Case Hunter + Acceptance Auditor). Scope: mynance delta `7b931eb..HEAD`. 3 decision-needed (all resolved → patch), 8 patch (all applied), 2 deferred (1 since fixed via P2), 1 dismissed._

- [x] [Review][Patch] Frontend hot reload under `docker compose up` (AC1) — **Decision: rewrite compose `frontend` service to a Vite dev server with watch.** `compose.override.yml` frontend service builds `frontend/Dockerfile` (production nginx static build, no source mount/`develop: watch`/dev server), so it cannot HMR even on a clean Linux box. Rewire it to run `bun run dev` with source mount + `develop: watch` so `docker compose up` HMRs both sides → AC1 met literally. [compose.override.yml, frontend/Dockerfile]
- [x] [Review][Patch] Theme mechanism + first-paint flash (AC5) — **Decision: implement the spec mechanism.** Add an inline pre-paint script in `index.html` + CSS `@media (prefers-color-scheme: dark)` with `[data-theme]` override in `index.css`, so theme is applied before first paint (no flash) per AC5; also resolves the deferred unguarded-`localStorage` crash if the provider is reworked. [frontend/src/index.css, frontend/index.html, frontend/src/components/theme-provider.tsx]
- [x] [Review][Patch] Relocate Morbido tokens to `frontend/src/theme/` (AC5 + architecture boundary) — **Decision: move tokens.** Extract the `--m-*` tokens into `frontend/src/theme/` (e.g. `theme/tokens.css`) imported by `index.css`, honoring the AC5 path + architecture day-one boundary. Values stay verbatim. [frontend/src/index.css → frontend/src/theme/]
- [x] [Review][Patch] Add generic 500 → problem+json handler so unhandled exceptions don't fall through to Starlette's `text/plain` "Internal Server Error" (generic detail, no internal leak) [backend/app/core/problem.py:77]
- [x] [Review][Patch] Preserve non-string `HTTPException.detail` instead of nulling it — non-str detail currently becomes `"detail": null` in the problem+json body [backend/app/core/problem.py:49]
- [x] [Review][Patch] Strengthen theme smoke test to assert the full required token set — `color.surface`, `color.accent`, a radius, and dark `ink` (currently only bg+ink/bg) [frontend/tests/theme.smoke.spec.ts]
- [x] [Review][Patch] `formatEurFromCents`: set `useGrouping: "always"` so the thousands separator is deterministic across runtimes and matches the documented `€ 1.234,56` example [frontend/src/lib/format.ts]
- [x] [Review][Patch] `formatDateIt`: guard invalid/empty input and treat date-only `YYYY-MM-DD` as local (avoids RangeError/"Invalid Date" and a TZ off-by-one) [frontend/src/lib/format.ts]
- [x] [Review][Defer→Fixed] `localStorage` access unguarded in template `theme-provider.tsx` (throws/crashes render in private-mode/disabled-storage/SSR) [frontend/src/components/theme-provider.tsx:36] — **fixed as part of P2** (now try/catch-guarded via `readStoredTheme`/`writeStoredTheme`); was originally deferred as pre-existing template code
- [x] [Review][Defer] Egress lint rule (ban `fetch`/`axios` outside `lib/api`) absent from `biome.json` [frontend/biome.json] — deferred, already documented as deferred (template's `utils.ts` legitimately imports `AxiosError`); AC6 literal text still satisfied

**Dismissed (1):** `formatEurFromCents` precision loss for cents values above `Number.MAX_SAFE_INTEGER` — not a realistic magnitude for personal-finance amounts (~90 trillion €).

**Confirmed solid (highlights):** money backend (`calc/money.py`) rejects `float`/`bool`, uses `Decimal` + `ROUND_HALF_UP`, round-trip tested (AC7); problem+json content-type + five required members + 422 shape correct; client path/script-rename + pre-commit repoint + snake_case preservation all verified; CI has no masked-failure steps (AC6).

#### Resolution (2026-06-16) — all 8 patches applied

- **P1 (AC1 HMR):** added a `dev-stage` to `frontend/Dockerfile` (Vite dev server) and rewired the `frontend` service in `compose.override.yml` to build it, run `bun run dev`, publish `5173:5173`, and `develop: watch` (sync) the source — `docker compose up` now HMRs both sides. (Replaces the prod-nginx static frontend.)
- **P2 (AC5 no-flash):** inline pre-paint theme script in `index.html` + `@media (prefers-color-scheme: dark)` fallback in `theme/tokens.css` (JS-disabled system default; manual `.light`/`.dark` choice wins). Kept the template's class-based marker (not `[data-theme]`) to preserve the Tailwind `dark:` variant — a smaller, deliberate divergence. **Also closes the deferred unguarded-`localStorage` crash** (now try/catch-guarded in `theme-provider.tsx`).
- **P3 (AC5 path):** Morbido tokens moved to `frontend/src/theme/tokens.css`, imported by `index.css` (honours the architecture token-boundary directory). Values verbatim.
- **P4:** catch-all `Exception` handler → 500 problem+json with a generic detail (no internal leak); registered in `register_problem_handlers`.
- **P5:** non-string `HTTPException.detail` preserved under the `errors` extension instead of being nulled.
- **P6:** theme smoke test strengthened — asserts `--m-surface`, `--m-accent`, `--radius`, and ink in both light and dark.
- **P7:** `formatEurFromCents` forces `useGrouping: true` (deterministic `€ 1.234,56`).
- **P8:** `formatDateIt` guards invalid/empty input (returns `""`) and formats date-only as UTC (no TZ off-by-one).

New tests: `test_unhandled_exception_renders_problem_json_without_leak`, `test_structured_http_detail_preserved_under_errors` (`backend/tests/api/test_problem_details.py`).

**Verification:** backend Python syntax OK; `format.ts` logic confirmed in Node (full-ICU); compose YAML valid. The full CI gate (ruff/mypy/pytest/biome/build/Playwright) + `docker compose up` runtime check must run on push — local Docker/Bun are unavailable in this WSL session (Docker-users re-login pending), same constraint documented for the original Docker-gated items.

**Still deferred:** egress lint rule (`biome.json`) — see `deferred-work.md`.
