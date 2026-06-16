---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8]
lastStep: 8
status: 'complete'
completedAt: '2026-06-16'
inputDocuments:
  - prds/prd-mynance-2026-06-15/prd.md
  - ux-designs/ux-mynance-2026-06-15/DESIGN.md
  - ux-designs/ux-mynance-2026-06-15/EXPERIENCE.md
  - briefs/brief-mynance-2026-06-12/brief.md
  - briefs/brief-mynance-2026-06-12/addendum.md
workflowType: 'architecture'
project_name: 'mynance'
user_name: 'Simone'
date: '2026-06-15'
---

# Architecture Decision Document

_This document builds collaboratively through step-by-step discovery. Sections are appended as we work through each architectural decision together._

## Project Context Analysis

### Requirements Overview

**Functional Requirements:**
22 FRs + 3 API requirements across six capability areas, reducible to four architectural jobs:
1. A multi-tenant **ledger** of manually-entered Movimenti (Spese/Entrate) with typed Categorie and recurring-rule generation (FR-5–8) — write-heavy, mobile-first, low-latency capture.
2. A deterministic **calculation engine** deriving every figure on read — Liquidità (FR-13), Quota/Saldo via chronological derived-on-read (FR-9–10), allocata/libera (FR-14), Cuscinetto (FR-15), linear depreciation (FR-21), Patrimonio (FR-22). No scheduled jobs; Saldo/Quota computed by replaying inputs in date order.
3. **Drift & Riconciliazione** computed from `today − last Riconciliazione`, closed via a "non identificato" plug Movimento (FR-16–18) — no scheduler, no notification infrastructure.
4. **Patrimonio** aggregation at the user's own valuation terms — contributed capital, price paid, linear depreciation (FR-19–22).
All exposed through a **frontend-agnostic, documented, versioned API** computing derived values server-side (API-1–3); clients never recompute divergently.

**Non-Functional Requirements (architecture-driving):**
- **Calculation correctness & determinism** — the core. Every derived figure reproducible from stored inputs; dedicated tests against worked examples; negative Saldo never silently clamped. Implies a pure, isolated calc module and exact money handling.
- **Security & per-Utente data isolation** — authorization on every entity access; salted-hash passwords + one-time recovery code; financial data treated as sensitive.
- **Data durability & integrity** — no Movimento lost; edits/deletes recompute consistently.
- **Performance** — personal-scale; derived views sub-second over a year+ of Movimenti (interactive period aggregations + charts).
- **Cost** — near-zero operating budget; low-cost/self-hosted; free product.
- **Privacy** — minimal stored data, no third-party sharing, no exfiltrating analytics; GDPR (account deletion deferred).

**Scale & Complexity:**
- Primary domain: full-stack web — mobile-first adaptive frontend + API backend; the API is the product surface.
- Complexity level: **medium** — no real-time collaboration, no external integrations, single operator per Utente, EUR-only. Concentrated complexity = the deterministic derived-on-read financial engine + multi-tenant isolation.
- Estimated architectural components: ~6–8 (API/service layer, calc engine, persistence, auth, web client, API contract/docs, optional offline-sync).

### Technical Constraints & Dependencies
- **Derived-on-read is binding** (PRD finalize): Saldo/Quota and all derived figures computed chronologically on read; no scheduler.
- **Near-zero cost**: hosting/stack must respect a tiny operating budget (self-hosted / low-cost) — to be decided in this workflow.
- **No external service dependencies** in V1: no bank aggregation, no market quotes, no email/push, no analytics SaaS.
- **EUR-only, Italian context**: single currency; period and date semantics in the Italian locale.
- **In-app notifications only**: reminders computed on access, not pushed.

### Cross-Cutting Concerns Identified
- **Determinism & money representation** — integer minor units (cents) / exact decimal, never float; canonical rounding; calc engine as a pure, independently-testable core.
- **Authorization on every access** — per-Utente isolation as a mandatory boundary across all endpoints.
- **API contract** — machine-readable (e.g. OpenAPI), versioned, documented; single source of derived truth.
- **Time & period semantics** — calendar-month boundaries, trailing windows, fractional `anni_trascorsi`, timezone — centralized.
- **Data model & history** — mutable-with-recompute vs append-only/event-style for derived-on-read robustness to back-dated edits; auditing of re-baselining and reconciliation events.
- **Offline capture & sync** — mobile quick-capture should tolerate flaky connectivity; conflict handling on sync (UX defines offline/stale states).

## Starter Template Evaluation

### Primary Technology Domain
Full-stack web with a **separate API service**: a Python **FastAPI** backend (the product's API-as-contract surface, OpenAPI-native) and a **React + Vite** PWA frontend (mobile-first, "Morbido" design system). Persistence in **PostgreSQL**, deployed on a free-tier PaaS.

### Stack Decisions (this step)
- **Backend: FastAPI (Python)** — native OpenAPI (serves API-1/API-2), a pure/testable calculation engine, Pydantic v2 typing.
- **Frontend: React + Vite (SPA/PWA)** — separate from the API; Next.js intentionally not used (no SSR/SEO need for an authenticated personal tool).
- **Database: PostgreSQL** — switched from the initially-considered MySQL/MariaDB because managed MySQL is scarce/costlier on free-tier PaaS (Render is Postgres-only; Railway/Fly lack a real free tier), while Postgres is free and first-class everywhere and is the official template's default. Calc engine + SQLAlchemy are DB-agnostic, so nothing is lost. (MySQL-compatible TiDB Cloud Starter / Aiven were evaluated and set aside.)
- **Hosting: free-tier PaaS** (Render / Railway / Fly) + free Postgres (Render / Neon / Supabase). Near-zero operating budget honored.

### Starter Options Considered
- **`fastapi/full-stack-fastapi-template`** (official, FastAPI team; actively maintained, updated 2026-06) — **selected**. FastAPI + SQLModel/SQLAlchemy 2 + Alembic + JWT auth + an **auto-generated TypeScript client from the OpenAPI schema** + React 19 + Vite + TanStack Router/Query + Docker Compose. Postgres-native.
- `alperencubuk/fastapi-…-postgres-alembic-docker-template` — lighter (plain SQLAlchemy 2 + Alembic + Docker); viable for a thinner base, but lacks the wired frontend + generated client.
- Hand-rolled (structured FastAPI project + standalone `npm create vite` React app) — maximum control, but re-implements what the official template already wires (esp. the OpenAPI→client pipeline).

### Selected Starter: `fastapi/full-stack-fastapi-template`

**Rationale for Selection:**
It encodes exactly the architecture mynance needs and reinforces the PRD's API-as-product principle: the **OpenAPI→TypeScript client generation** means the React app consumes the very contract the API publishes (API-1/2/3 — derived values computed server-side, never recomputed divergently per client). Postgres-native (matches our DB choice), Alembic migrations, JWT auth aligned with FR-1/2/3, Docker Compose for PaaS parity. Its bundled React+Vite+TanStack frontend is our chosen frontend; we **restyle it to the "Morbido" design system** (DESIGN.md) rather than keep its default styling.

**Initialization Command:**
```bash
git clone https://github.com/fastapi/full-stack-fastapi-template.git mynance && cd mynance
# Backend deps via uv; frontend via npm. No DB driver swap — template is PostgreSQL-native.
```

**Architectural Decisions Provided by Starter:**
- **Language & Runtime:** Python + FastAPI 0.137 + Pydantic v2 (2.13) backend; TypeScript 6 + React 19.2 on Vite 8 frontend.
- **Styling:** template default **replaced** by the "Morbido" design system (DESIGN.md tokens, light/dark warm palette); no heavy UI kit imposed.
- **Build Tooling:** Vite 8 (HMR/build); `uv` for Python deps; Docker Compose for local + deploy parity.
- **Testing:** backend pytest; frontend Playwright — aligns with the PRD's "dedicated tests against worked examples" for the calc engine.
- **Code Organization:** separate `backend/` (FastAPI app, models, Alembic) and `frontend/` (React + generated API client); clean API/persistence layering.
- **Development Experience:** auto-generated type-safe API client from OpenAPI; hot reload both sides; one-command Docker Compose env; JWT auth scaffolding.

**Note:** Project initialization with this template (and the frontend restyle to Morbido) should be the **first implementation story**.

## Core Architectural Decisions

### Decision Priority Analysis
**Critical (block implementation):**
- Deterministic calculation engine — pure functions, chronological derived-on-read; money as integer minor units (cents).
- PostgreSQL (Neon) persistence; mutable rows + soft-delete + audit log.
- Per-Utente authorization enforced on every data access (FR-4).
- JWT auth + custom one-time recovery-code (FR-3).

**Important (shape architecture):**
- REST API `/api/v1` with OpenAPI → auto-generated TS client; server-side period-aggregation endpoints.
- Installable PWA (online-first capture); TanStack Query/Router.
- Render/Fly app + Neon Postgres; GitHub Actions CI/CD.

**Deferred (post-MVP):**
- True offline capture queue + sync/conflict resolution.
- Native apps (separate track, same API).
- Derived-value caching/materialization (only if profiling shows need).
- Account deletion / full GDPR tooling (PRD §9).

### Data Architecture
- **Database:** PostgreSQL (recent major, Neon-provided — pin at init), hosted on **Neon** (persistent free tier; Render's free Postgres expires ~30 days, so not used for data). ORM SQLAlchemy 2 / SQLModel; migrations Alembic (starter).
- **Data model:** mutable rows for Utente, Movimento (Spesa/Entrata), Categoria (typed Spesa/Entrata), Secchiello, Regola ricorrente, Investimento/Versamento PAC, Bene immobile/mobile, Liquidità-baseline, Riconciliazione. **Soft-delete** (`deleted_at`) so no Movimento is silently lost (NFR) and recompute stays consistent. **Audit log** for sensitive events: Liquidità iniziale re-baselining (FR-12), Riconciliazione (FR-17), recovery-code regeneration.
- **Money:** integer **minor units (cents)**, BIGINT; never float. All engine arithmetic in cents with centralized rounding; EUR only.
- **Validation:** Pydantic v2 at the API boundary; domain invariants in the service/engine layer.
- **Caching:** none separate — compute-on-read with indexes (`user_id` + date) and per-request memoization; revisit only if profiling misses the sub-second target.

### Calculation Engine (core — derived-on-read)
- A **pure, framework-independent Python module** (no DB/IO) that, from an Utente's stored inputs, computes every derived figure by **replaying Movimenti/credits in date order**: Liquidità (FR-13); per-Secchiello Saldo & Quota chronologically (FR-9/10, `mesi = max(1, ceil(days/30.44))`); allocata/Risparmio libero (FR-14); Cuscinetto & Spesa media (FR-15, last N complete calendar months incl. "non identificato"); linear depreciation `max(0, prezzo×(1−Svalut×anni))` (FR-21); Patrimonio (FR-22); Drift in € and % of Liquidità (FR-17).
- **Deterministic & reproducible** from stored inputs; negative Saldo never clamped. Covered by **dedicated unit tests against worked examples** (NFR), testable in isolation from API/DB.

### Authentication & Security
- **AuthN:** JWT access tokens (pyjwt); password hashing argon2 (pwdlib) — starter. Idle/session expiry **30 days, configurable** (FR-2).
- **Recovery (FR-3, custom):** one-time recovery code at registration, shown once, stored only as a **salted hash**, regeneratable while authenticated. No email.
- **AuthZ / multi-tenant isolation:** every access scoped to the authenticated Utente via a **user-scoped repository/dependency** that always filters by `user_id`; cross-Utente access → 404/403, never data (FR-4).
- **Middleware:** HTTPS (PaaS-terminated), CORS locked to the frontend origin, security headers, rate limiting on auth endpoints; secrets via env; no exfiltrating analytics (privacy).

### API & Communication Patterns
- **Style:** REST, versioned `/api/v1`; OpenAPI is the canonical contract (API-2); **TS client auto-generated** for the frontend (API-1/3 — derived values server-side, never recomputed client-side).
- **Errors:** consistent `application/problem+json` (RFC 9457).
- **Aggregation:** server-side period endpoints for Home (period balance + per-Categoria breakdown sorted desc) and Statistiche (trends + pie); the client never aggregates money.
- **Pagination:** offset/cursor on Movimenti lists. **Versioning:** path-based `/v1`, additive-preferred to protect the web→native contract.

### Frontend Architecture
- **Framework:** React 19.2 + Vite 8 + TypeScript 6 (starter), SPA.
- **State/data:** TanStack Query (server state + invalidation) + TanStack Router (type-safe routing); local UI state via React — no global store at this scale.
- **PWA:** vite-plugin-pwa — installable, app shell + offline/stale states; **capture online-first with optimistic UI** (true offline queue deferred).
- **Design system:** "Morbido" tokens (DESIGN.md) as CSS custom properties; light/dark via system default + override; no heavy UI kit.
- **API client:** generated TS client against `/api/v1` — single contract source.

### Infrastructure & Deployment
- **App:** FastAPI web service on **Render** (free) or **Fly.io**; static frontend as static site/CDN.
- **DB:** **Neon** Postgres (persistent free tier, branching, backups).
- **Containers:** Docker / Compose (starter) for local parity.
- **CI/CD:** **GitHub Actions** — lint (ruff/eslint), type-check (mypy/tsc), tests (pytest + Playwright), build, deploy on main.
- **Config:** env vars per environment; PaaS secrets in prod.
- **Backup/retention (PRD §9):** Neon managed backups/PITR + scheduled `pg_dump` to object storage; documented restore.
- **Monitoring:** structured JSON logs; optional free-tier Sentry. Minimal, cost-aware.
- **Scaling:** single small instance suffices; stateless API allows later horizontal scale — no premature infra.

### Decision Impact Analysis
**Implementation Sequence:**
1. Init from `full-stack-fastapi-template`; wire Neon; restyle to Morbido (first story).
2. Auth + Utente + per-user authZ scoping (security boundary first).
3. Domain models + migrations (Movimento, typed Categoria, Secchiello, …) with soft-delete + audit log.
4. **Calculation engine** as a pure module + worked-example tests (the heart).
5. REST endpoints + OpenAPI + generated client; server-side aggregations.
6. Frontend screens against the generated client (Home, quick-add, Liquidità, Statistiche, …); PWA shell.
7. Drift/Riconciliazione, Patrimonio, Regole ricorrenti.
8. CI/CD, backup, deploy.

**Cross-Component Dependencies:**
- Calc engine depends only on stored inputs (pure) → testable before any API/UI.
- All endpoints depend on the authZ scoping layer.
- Frontend depends on the generated TS client → the API contract is the integration seam.
- Money-as-cents is a cross-cutting invariant binding DB ↔ engine ↔ API ↔ UI formatting.

## Implementation Patterns & Consistency Rules

### Pattern Categories Defined
Key conflict points where independent AI agents could diverge: domain vocabulary, DB/JSON casing, money representation, project structure, API/error formats, cache-invalidation, error/loading handling.

### Naming Patterns
**Domain vocabulary (binding):** code uses the **Italian domain nouns verbatim** from the PRD glossary — `Utente`, `Movimento`, `Spesa`, `Entrata`, `Categoria`, `Secchiello`, `Quota`, `Saldo`, `Patrimonio`, `Cuscinetto`, `Riconciliazione`, `Investimento`, `VersamentoPac`, `BeneImmobile`, `BeneMobile`, `Svalutazione`, `RegolaRicorrente`. No English translations (prevents synonym drift — the glossary is load-bearing). Accents dropped in identifiers (`liquidita`); display strings keep them.

**Database (Postgres):** snake_case; **plural Italian** tables (`utenti`, `movimenti`, `categorie`, `secchielli`, `regole_ricorrenti`, `investimenti`, `versamenti_pac`, `beni_immobili`, `beni_mobili`, `riconciliazioni`); PK `id` = **UUID**; FK `<entity>_id` (`utente_id`, `categoria_id`, `secchiello_id`); `created_at`/`updated_at`/`deleted_at`; money columns suffixed `_cents` (BIGINT); indexes `ix_<table>_<cols>` (always include `utente_id`).

**API (REST):** lowercase plural resources `/api/v1/movimenti`, `/secchielli`, `/categorie`; path param `{id}`; query params snake_case (`from_date`, `to_date`, `period`, `anchor`).

**JSON fields:** **snake_case** (Pydantic default; the generated TS client mirrors it). Money as integer `*_cents`; booleans `true/false`; dates `YYYY-MM-DD`; datetimes ISO 8601 UTC with `Z`.

**Frontend code:** React components PascalCase (`HomeMese.tsx`), hooks `useXxx`, variables/functions camelCase; file name matches export. The generated API client types are consumed as-emitted (snake_case fields); formatting happens at the display layer.

### Structure Patterns
**Backend (`backend/app/`):** `api/` (routers per resource) · `models/` (SQLAlchemy/SQLModel) · `schemas/` (Pydantic) · `services/` (business logic + user-scoped repositories) · `core/` (config, security) · **`calc/` (the pure calculation engine — no DB/IO)** · `alembic/` · `tests/` mirroring structure, with `tests/calc/` for worked-example tests.
**Frontend (`frontend/src/`):** organized **by feature** — `features/{home,movimenti,liquidita,secchielli,statistiche,patrimonio,riconciliazione,impostazioni,auth}/` (components + hooks + queries co-located) · `components/` (shared) · `lib/` (generated api client, utils) · `theme/` (Morbido tokens as CSS vars). Playwright e2e in `frontend/tests/`; component tests co-located `*.test.tsx`.
Rule: organize **by feature/domain, not by type**, mirroring the PRD feature areas.

### Format Patterns
- **API responses:** return the resource object directly (no `{data}` wrapper); paginated lists return `{items, total, limit, offset}`. Errors: **`application/problem+json`** (RFC 9457): `{type, title, status, detail, instance}`.
- **Money:** ALWAYS integer cents in DB + API (`*_cents`); formatted to `€ 1.234,56` (Italian locale) only at the UI display layer. Never float, never localized strings in the API.
- **Dates/times:** dates `YYYY-MM-DD`; datetimes UTC ISO 8601 `Z`; period query `period=month&anchor=2026-06`; boundaries computed in `Europe/Rome`.

### Communication Patterns
- **No event system in V1** — synchronous REST only.
- **TanStack Query keys:** array convention `['movimenti', filters]`, `['liquidita']`, `['secchielli']`, `['statistiche', period]`. Mutations invalidate every affected key (e.g. adding a Spesa invalidates `movimenti` + `liquidita` + `secchielli` + period aggregates).
- **State updates:** immutable; **optimistic** for capture (online-first), rolled back on error.

### Process Patterns
- **Error handling:** backend raises typed domain exceptions → central handler maps to problem+json; frontend surfaces via one toast/inline pattern. **Honesty states are NOT errors** (negative Saldo, Drift, Cuscinetto breach) — normal data rendered in warm amber `{color.honesty}`.
- **Loading:** TanStack Query `isPending`/`isError`; skeletons for lists, inline spinners for actions; per-screen, never global.
- **Validation:** Pydantic at the boundary (→422 problem+json); domain invariants in services/calc; never trust the client.
- **Auth:** JWT Bearer in `Authorization` header; 401 → redirect to login; recovery-code flow per FR-3.

### Enforcement Guidelines
**All AI agents MUST:** use the Italian domain nouns verbatim · represent money as integer `*_cents` (never float) · never recompute derived money client-side (always call the API) · scope every query by `utente_id` · use snake_case for DB/JSON and PascalCase for React components · talk to the API only through the generated TS client.
**Enforcement:** ruff + mypy (backend), eslint + tsc (frontend) in CI; PR review checks domain-term fidelity and the no-client-recompute rule.

### Anti-Patterns (avoid)
- Float/`Decimal`-as-string money, or formatting currency in the API.
- English synonyms for domain entities (`Bucket` for `Secchiello`, `Transaction` for `Movimento`).
- Recomputing Liquidità/Saldo/Quota in the frontend.
- Queries missing the `utente_id` scope.
- Global loading/error singletons.

## Project Structure & Boundaries

### Complete Project Directory Structure
```
mynance/                              # monorepo from full-stack-fastapi-template
├── README.md
├── docker-compose.yml                # local: api + postgres + frontend (parity)
├── .env.example  / .env              # secrets via env (PaaS in prod)
├── .gitignore
├── .github/workflows/
│   └── ci.yml                        # lint (ruff/eslint) · types (mypy/tsc) · tests · build · deploy
├── scripts/
│   ├── backup_pg_dump.sh             # scheduled dump → object storage (PRD §9)
│   └── generate_client.sh            # OpenAPI → TS client codegen
│
├── backend/
│   ├── pyproject.toml  / uv.lock     # FastAPI 0.137, SQLModel/SQLAlchemy 2, Alembic, pydantic 2, pyjwt, pwdlib[argon2]
│   ├── Dockerfile
│   ├── alembic.ini
│   ├── alembic/versions/             # migrations
│   ├── app/
│   │   ├── main.py                   # app factory, router include, CORS, problem+json handler
│   │   ├── core/
│   │   │   ├── config.py             # Settings (env)
│   │   │   ├── security.py           # JWT, argon2 hashing, recovery-code (salted hash)
│   │   │   └── db.py                 # engine + session
│   │   ├── models/                   # ORM — Italian domain nouns, *_cents BIGINT, UUID PKs, soft-delete
│   │   │   ├── utente.py  movimento.py  categoria.py  secchiello.py
│   │   │   ├── regola_ricorrente.py  investimento.py  bene.py
│   │   │   └── riconciliazione.py  audit_log.py
│   │   ├── schemas/                  # Pydantic v2 (snake_case, *_cents) request/response
│   │   ├── calc/                     # ★ PURE calculation engine — NO DB/IO
│   │   │   ├── money.py              # integer-cents helpers + canonical rounding
│   │   │   ├── liquidita.py          # FR-13
│   │   │   ├── secchiello.py         # FR-9/10 chronological Saldo/Quota replay
│   │   │   ├── allocazione.py        # FR-14/15 allocata/libera, cuscinetto, spesa media
│   │   │   ├── patrimonio.py         # FR-21/22 linear depreciation + net worth
│   │   │   └── drift.py              # FR-17 € and % of Liquidità
│   │   ├── services/                 # business logic + user-scoped repositories
│   │   │   ├── repository.py         # base repo — ALWAYS filters utente_id
│   │   │   ├── movimenti.py  secchielli.py  liquidita.py
│   │   │   ├── regole.py             # generation up-to-today
│   │   │   └── patrimonio.py  riconciliazione.py
│   │   └── api/
│   │       ├── deps.py               # current_utente, db session deps
│   │       └── v1/
│   │           ├── router.py
│   │           ├── auth.py  movimenti.py  categorie.py  secchielli.py
│   │           ├── liquidita.py  statistiche.py  patrimonio.py
│   │           └── riconciliazione.py  regole.py
│   └── tests/
│       ├── calc/                     # ★ worked-example determinism tests (the heart, NFR)
│       ├── api/                      # endpoint + authZ-isolation tests
│       └── conftest.py
│
└── frontend/
    ├── package.json                  # React 19.2, Vite 8, TS 6, TanStack Query/Router, vite-plugin-pwa 1.3
    ├── vite.config.ts                # + PWA plugin
    ├── tsconfig.json   Dockerfile
    ├── index.html
    ├── public/                       # manifest.webmanifest, icons (installable PWA)
    ├── tests/                        # Playwright e2e
    └── src/
        ├── main.tsx
        ├── routes/                   # TanStack Router (type-safe)
        ├── lib/
        │   ├── api/                  # ★ GENERATED TS client from OpenAPI (only way to call API)
        │   ├── queryClient.ts        # TanStack Query keys + invalidation
        │   └── format.ts             # money/date Italian formatting — DISPLAY ONLY
        ├── theme/                    # Morbido tokens → CSS custom properties (light/dark, system default)
        ├── components/               # shared: balance-block, category-row, honesty-banner,
        │                             #         bottom-nav, fab, bottom-sheet, chip, keypad, list-row, secchiello-badge
        └── features/
            ├── auth/                 # FR-1/2/3 — register, login, recovery code
            ├── home/                 # FR-13 — Mese: period balance + per-Categoria list
            ├── movimenti/            # FR-5/6 — quick-add bottom sheet, edit
            ├── liquidita/            # FR-14/15 + §4.3 — allocazione + Secchielli tabs
            ├── secchielli/           # FR-9/10/11 — create/edit, detail
            ├── statistiche/          # decision #26 — trends + pie charts
            ├── patrimonio/           # FR-19/20/21/22 — net worth
            ├── riconciliazione/      # FR-16/17/18 — drift flow + honesty banner
            └── impostazioni/         # FR-7/8/12 — Categorie (+Secchiello link), Regole, Liquidità iniziale, account
```

### Architectural Boundaries
- **API boundary:** the FastAPI `/api/v1` surface + its OpenAPI schema is the ONLY contract; the frontend reaches it solely through the generated client. Derived values computed server-side (API-3).
- **Calc boundary:** `app/calc/` is pure (no DB, no FastAPI imports). Services load stored inputs and call it; it is unit-tested in isolation against worked examples.
- **AuthZ boundary:** `services/repository.py` is the choke point — every query filters by `utente_id`; routers never query models directly.
- **Data boundary:** only `services/` touch the DB; `api/` never imports `models/` directly; `calc/` never touches persistence.
- **Frontend boundary:** `lib/api` (generated) is the only egress to the backend; `features/` never recompute derived money; `theme/` owns all visual tokens.

### Requirements → Structure Mapping
| PRD area | Backend | Frontend |
|---|---|---|
| §4.1 Auth (FR-1/2/3) | `api/v1/auth.py`, `core/security.py`, `models/utente.py` | `features/auth/` |
| §4.2 Movimenti (FR-5/6/7/8) | `api/v1/{movimenti,categorie,regole}.py`, `services/{movimenti,regole}.py` | `features/{movimenti,home,impostazioni}/` |
| §4.3 Secchielli (FR-9/10/11) | `calc/secchiello.py`, `services/secchielli.py`, `api/v1/secchielli.py` | `features/{secchielli,liquidita}/` |
| §4.4 Liquidità (FR-12/13/14/15) | `calc/{liquidita,allocazione}.py`, `api/v1/liquidita.py` | `features/{home,liquidita}/` |
| §4.5 Drift (FR-16/17/18) | `calc/drift.py`, `services/riconciliazione.py`, `api/v1/riconciliazione.py` | `features/riconciliazione/` + `honesty-banner` |
| §4.6 Patrimonio (FR-19-22) | `calc/patrimonio.py`, `api/v1/patrimonio.py` | `features/patrimonio/` |
| Statistiche (#26) | `api/v1/statistiche.py` (server-side aggregation) | `features/statistiche/` |
| Cross-cutting: authZ | `services/repository.py`, `api/deps.py` | route guards on 401 |

### Integration Points & Data Flow
- **Internal:** Router → Service (authZ-scoped) → {Repository (DB), Calc (pure)} → Pydantic schema → JSON.
- **External (V1):** none — no bank aggregation, no market data, no email/push (PRD non-goals). Only PaaS-managed Postgres (Neon) and optional Sentry.
- **Data flow (read):** client query → `/api/v1/...` → service loads stored inputs → `calc/` replays in date order → derived figures (cents) → JSON → client formats for display.
- **Data flow (write):** optimistic UI → mutation → service validates + persists (soft-delete/audit where relevant) → client invalidates affected TanStack Query keys → re-fetch recomputes.

### File Organization & Workflow
- **Config:** `pyproject.toml`/`uv.lock` (backend), `package.json` (frontend), `.env(.example)`, `docker-compose.yml`.
- **Tests:** backend `tests/calc` (determinism) + `tests/api` (integration/isolation); frontend Playwright in `tests/`, component tests co-located.
- **Dev:** `docker compose up` (api + postgres + frontend, HMR both sides); `scripts/generate_client.sh` regenerates the TS client after API changes.
- **Build/deploy:** CI builds both; backend image → Render/Fly, frontend static → CDN/static host; migrations via Alembic on deploy; Neon as the managed DB.

## Architecture Validation Results

### Coherence Validation ✅
**Decision Compatibility:** the stack is internally consistent and version-current — FastAPI 0.137 + Pydantic 2.13 + SQLAlchemy 2 + Alembic + Postgres (Neon); React 19.2 + Vite 8 + TS 6 + TanStack + vite-plugin-pwa 1.3 (Vite 8 requires Node ≥20.19/22.12 — noted). No contradictory choices.
**Pattern Consistency:** snake_case JSON ↔ Pydantic default ↔ generated TS client; integer-cents ↔ calc determinism; user-scoped repository ↔ FR-4 isolation; problem+json ↔ central error handler. All aligned.
**Structure Alignment:** the pure `calc/` module supports the determinism NFR and isolated testability; `services/` is the single authZ + DB choke point; `features/` mirror the PRD areas. Structure enables every pattern.

### Requirements Coverage Validation ✅
**Functional Requirements (22/22):**
- FR-1/2/3/4 → `api/v1/auth.py`, `core/security.py`, `services/repository.py` (recovery code custom; 30-day session; user-scoped isolation).
- FR-5/6/7/8 → `services/{movimenti,regole}.py`, typed Categorie + Categoria→Secchiello default, Regole up-to-today.
- FR-9/10/11 → `calc/secchiello.py` (chronological Saldo/Quota replay, `mesi = max(1, ceil(days/30.44))`, any Periodicità, carryover, negative Saldo surfaced).
- FR-12/13/14/15 → `calc/{liquidita,allocazione}.py` (derived Liquidità, allocata/libera, Cuscinetto N=6, Spesa media incl. "non identificato").
- FR-16/17/18 → `services/riconciliazione.py` + `calc/drift.py` (computed reminder, Drift € and %, "non identificato" plug, acknowledge-without-fix).
- FR-19/20/21/22 → `calc/patrimonio.py` (PAC at Capitale versato, price-paid, linear depreciation floored at 0, net-worth sum, no auto-deduct).
**API Requirements (3/3):** API-1 contract independence (server-side calc), API-2 OpenAPI + `/v1` versioning, API-3 single generated client (no client-side recompute).
**Non-Functional Requirements:** determinism (pure `calc/` + worked-example tests), security/isolation (JWT, argon2, scoped repo, CORS, rate-limit), EUR single-currency (integer cents), durability (soft-delete, audit log, recompute), privacy (no exfiltrating analytics), cost (free-tier PaaS + Neon). Performance addressed via compute-on-read + indexes + per-request memoization.

### Implementation Readiness Validation ✅
**Decision Completeness:** all critical decisions documented with current versions; deferred items explicitly listed.
**Structure Completeness:** complete monorepo tree, boundaries, and FR→directory mapping defined.
**Pattern Completeness:** naming, structure, format, communication, and process patterns specified with enforcement + anti-patterns.

### Gap Analysis Results
- **Minor — Recurring-rule materialization trigger:** generation is "up to today" with no scheduler → must be **lazy & idempotent on access** (compute/persist generated items when the relevant period is read / on login). To be made explicit in the `services/regole.py` story. Non-blocking.
- **Watch item — derived-on-read performance at scale:** sub-second is expected at personal volumes with proper indexes; if a year+ of data ever regresses, introduce per-Secchiello checkpoint snapshots (materialization is the deferred fallback). Non-blocking.
- **Deferred (by design):** true offline capture queue + sync; native apps; account deletion / full GDPR tooling (PRD §9); backup restore drill.

### Architecture Completeness Checklist
**Requirements Analysis**
- [x] Project context thoroughly analyzed
- [x] Scale and complexity assessed
- [x] Technical constraints identified
- [x] Cross-cutting concerns mapped

**Architectural Decisions**
- [x] Critical decisions documented with versions
- [x] Technology stack fully specified
- [x] Integration patterns defined
- [x] Performance considerations addressed

**Implementation Patterns**
- [x] Naming conventions established
- [x] Structure patterns defined
- [x] Communication patterns specified
- [x] Process patterns documented

**Project Structure**
- [x] Complete directory structure defined
- [x] Component boundaries established
- [x] Integration points mapped
- [x] Requirements to structure mapping complete

### Architecture Readiness Assessment
**Overall Status:** READY FOR IMPLEMENTATION (all 16 checklist items confirmed; no Critical Gaps — only one minor clarification and one watch item, both non-blocking).
**Confidence Level:** high.
**Key Strengths:** the pure, isolated derived-on-read calc engine (testable, deterministic); API-as-product reinforced by OpenAPI→TS client; strict per-Utente isolation choke point; warm honesty surfacing baked into patterns; near-zero-cost hosting.
**Areas for Future Enhancement:** derived-value checkpoints if scale grows; offline capture queue; full GDPR/account-deletion tooling; backup restore drill.

### Implementation Handoff
**AI Agent Guidelines:** follow all architectural decisions and patterns exactly; money always integer `*_cents`; never recompute derived money client-side; scope every query by `utente_id`; use the Italian domain nouns verbatim; reach the API only via the generated client.
**First Implementation Priority:** initialize from `fastapi/full-stack-fastapi-template`, wire Neon Postgres, restyle the frontend to the "Morbido" design system — then build the security/authZ boundary and the pure `calc/` engine (with worked-example tests) before the feature endpoints.
