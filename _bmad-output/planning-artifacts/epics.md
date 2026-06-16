---
stepsCompleted: [1, 2, 3, 4]
inputDocuments:
  - prds/prd-mynance-2026-06-15/prd.md
  - architecture.md
  - ux-designs/ux-mynance-2026-06-15/EXPERIENCE.md
  - ux-designs/ux-mynance-2026-06-15/DESIGN.md
---

# mynance - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for mynance, decomposing the requirements from the PRD, UX Design, and Architecture into implementable stories.

## Requirements Inventory

### Functional Requirements

FR-1: Self-service registration — an anonymous visitor creates an Utente with username + password; new account starts empty; unique usernames; passwords stored salted-hashed only.
FR-2: Authentication & session — login with username + password; session expires after 30 days idle (configurable); explicit logout; invalid credentials don't reveal username existence.
FR-3: Password recovery — one-time recovery code issued at registration (shown once, salted-hash stored, regeneratable while authenticated); no email; recovery never exposes the password.
FR-4: Data isolation — an Utente can read/write only their own data; cross-Utente access returns not-found/forbidden.
FR-5: Record a Spesa — amount, date, Spesa-type Categoria, optional note, link to one Secchiello (defaults from the Categoria, overridable per-Spesa); decrements linked Secchiello Saldo; affects Liquidità; editable/deletable with recompute.
FR-6: Record an Entrata — amount, date, Entrata-type Categoria, optional note; increases Liquidità.
FR-7: Categorization (typed) + Categoria→Secchiello link — create/rename/reuse Categorie typed as Spesa or Entrata (distinct backend spaces); starter set per type; a Spesa-type Categoria may link to one Secchiello to default attribution; delete-in-use prompts reassignment.
FR-8: Recurring income & contribution rules — define a Regola ricorrente (amount, cadence, day) that auto-generates Entrate or Versamenti PAC up to today only (no future/phantom items); generated items editable/skippable.
FR-9: Auto-computed Quota — `Quota = max(0, (Importo previsto − Saldo) / mesi_alla_Prossima_scadenza)` with `mesi = max(1, ceil((scadenza−today)/30.44))`; recomputed on input change; 0 if funded; rises to recover negative Saldo.
FR-10: Funding, payment & carryover lifecycle — virtual monthly crediting computed derived-on-read (chronological); linked Spesa settles and sets carryover; Importo previsto updated to actual paid; Prossima scadenza advances; negative Saldo surfaced, never clamped.
FR-11: Any periodicità — monthly/quarterly/semiannual/annual/custom interval; `mesi_alla_Prossima_scadenza` derived from date, independent of the label.
FR-12: Set initial liquidity — set Liquidità iniziale once; later changes allowed but flagged/logged as re-baselining.
FR-13: Derived liquidity — `Liquidità = Liquidità iniziale + Σ Entrate − Σ Spese − Σ Capitale versato`, recomputed on every relevant change.
FR-14: Allocation breakdown — `Liquidità allocata = Σ max(0, Saldo)`, `Risparmio libero = Liquidità − allocata`, both live.
FR-15: Safety-buffer warning — `Cuscinetto = N × Spesa media mensile` (default N=6, configurable); Spesa media = mean over last N complete calendar months incl. "non identificato"; non-blocking in-app indicator when Risparmio libero falls below.
FR-16: Periodic reconciliation reminder (in-app) — computed from `today − last Riconciliazione` (default weekly, configurable); surfaced in-app on access; no scheduler, no email/push.
FR-17: Reconcile real liquidity — enter actual observed liquidity; show Drift (`reale − calcolata`) with sign, magnitude and % of Liquidità; confirming sets last Riconciliazione date to today.
FR-18: Close the gap with "non identificato" — create a "non identificato" Spesa/Entrata for the difference (dedicated system Categoria per type), or acknowledge-and-leave-open (resets timer, gap stays visible).
FR-19: Investimenti (PAC) at contributed capital — create an Investimento, record Versamenti PAC (manual or via Regola); value = Σ Capitale versato (never market value); each Versamento reduces Liquidità.
FR-20: Beni immobili at price paid — register a property valued statically at price paid (no market estimate).
FR-21: Beni mobili with depreciation — purchase price/date + Svalutazione%; `Valore = max(0, prezzo × (1 − Svalutazione × anni_trascorsi))` (linear, floored at 0, anni fractional); suggested default rates (auto ~15-20%, moto ~8-12%), overridable.
FR-22: Net-worth total — `Patrimonio = Liquidità + Capitale versato totale + Σ Valore beni immobili + Σ Valore beni mobili`; asset registration does not auto-deduct Liquidità (no double-count).
API-1: Contract independence — no business logic only in the frontend; the API is complete and usable headless.
API-2: Documentation & versioning — machine-readable OpenAPI contract, path-versioned (`/api/v1`).
API-3: Same logic, all clients — derived values computed server-side and returned, never recomputed divergently per client.

### NonFunctional Requirements

NFR-1: Calculation correctness & determinism — all derived figures deterministic and reproducible from stored inputs; dedicated tests against worked examples; negative Saldo never silently clamped.
NFR-2: Security & data isolation — authorization on every entity access against the owning Utente; passwords (and recovery code) salted-hashed only; financial data treated as sensitive.
NFR-3: Single currency / Italian context — EUR only in V1; Italian date/number conventions; money as integer minor units (cents), never float.
NFR-4: Data durability & integrity — no financial Movimento lost silently; edits/deletes recompute consistently (soft-delete + audit log).
NFR-5: Performance — personal-scale; derived views compute interactively (sub-second over a year+ of Movimenti).
NFR-6: Privacy — minimize stored data; no third-party sharing; no analytics that exfiltrate financial detail.
NFR-7: Cost — near-zero operating budget (free-tier PaaS + Neon); free to users.
NFR-8: Honesty principle (product tone) — uncomfortable truths (negative Saldo, growing Drift, buffer breach) surfaced plainly, in warm amber, never hidden, never alarm-red.

### Additional Requirements

(From Architecture — `architecture.md`. The starter init is the first story.)
- **AR-Init (Epic 1, Story 1):** initialize from the official `fastapi/full-stack-fastapi-template`; wire **Neon PostgreSQL**; restyle the frontend to the "Morbido" design system. First implementation story.
- AR-Calc: a **pure, framework-independent calculation engine** module (`app/calc/`, no DB/IO) implementing derived-on-read chronological replay; money helpers in integer cents with canonical rounding; covered by worked-example unit tests.
- AR-AuthZ: a **user-scoped repository / dependency** choke point that always filters by `utente_id`; routers never query models directly.
- AR-API: REST under `/api/v1`; OpenAPI is the canonical contract; **auto-generated TypeScript client** as the only frontend egress; errors as `application/problem+json` (RFC 9457).
- AR-Data: PostgreSQL via SQLAlchemy 2 / SQLModel; Alembic migrations; UUID PKs; `*_cents` BIGINT money; soft-delete (`deleted_at`); **audit log** for re-baselining (FR-12), Riconciliazione (FR-17), recovery-code regeneration.
- AR-Aggregation: **server-side period-aggregation endpoints** for Home (period balance + per-Categoria breakdown sorted desc) and Statistiche (trends + pie); the client never aggregates money.
- AR-Regole-Lazy: recurring-rule generation is **lazy & idempotent on access** (no scheduler) — materialize generated items up to today when the relevant period is read / on login.
- AR-PWA: installable PWA (vite-plugin-pwa); **online-first capture** with optimistic UI; offline/stale states handled (true offline queue deferred).
- AR-Infra: GitHub Actions CI/CD (ruff/eslint, mypy/tsc, pytest + Playwright, build, deploy); app on Render/Fly, DB on Neon; backup = Neon snapshots + scheduled `pg_dump`; structured logging (+ optional free Sentry).
- AR-Consistency: Italian domain nouns verbatim in code; snake_case DB/JSON; PascalCase React components; no client-side recompute of derived money.

### UX Design Requirements

(From `EXPERIENCE.md` + `DESIGN.md`. Each is specific enough to seed a story.)
- UX-DR1: Implement the **"Morbido" design tokens** (DESIGN.md) as CSS custom properties — full color set light + dark, typography scale, radii, spacing — with theme defaulting to the device/system setting and a manual override.
- UX-DR2: Build the **shared component set** (behavioral + visual specs): `balance-block`, `category-row` (proportional bar), `honesty-banner`, `bottom-nav` (5 slots + central ＋ FAB), `bottom-sheet`, `chip`, numeric `keypad`, `list-row`, `secchiello-badge`, `period-selector`.
- UX-DR3: **Home "Mese"** — period selector (Giorno/Settimana/Mese/Anno) + in-period nav; balance block (Netto hero, Entrate, Spese); Spese grouped by Categoria sorted largest→smallest with proportional bars; tap category → its Spese detail.
- UX-DR4: **Quick-add bottom sheet** — amount-first numeric keypad, Spesa/Entrata toggle (default Spesa), recent/most-used category chips, date=today default, Secchiello auto-set from linked Categoria (overridable), optimistic save + confirmation toast.
- UX-DR5: **Liquidità screen** — two tabs: Allocazione (Liquidità total, allocata vs Risparmio libero, Cuscinetto status incl. breach) and Secchielli (list with Saldo/Quota/Prossima scadenza + under-funding warning; create/edit; detail).
- UX-DR6: **Statistiche** — charts only (cross-period trend lines + period category-share pie), no lists; shares the period selector.
- UX-DR7: **Patrimonio screen** — total + per-component cards (Liquidità, Investimenti at Capitale versato, Beni immobili, Beni mobili depreciated); asset registration must not imply a Liquidità deduction.
- UX-DR8: **Riconciliazione flow + contextual honesty banner** — banner when reminder due / buffer breached; flow: enter real liquidity → show Drift (€ and %) → close with "non identificato" or acknowledge-and-leave-open.
- UX-DR9: **Impostazioni** — Categorie (typed + Categoria→Secchiello link), Regole ricorrenti, Liquidità iniziale, account + recovery-code.
- UX-DR10: **Onboarding (minimal)** — required: account + recovery-code saved; one skippable "Imposta Liquidità iniziale" step; pre-seeded starter Categorie per type; land on empty Home with gentle nudges (respect entry-burden).
- UX-DR11: **State patterns** — loading (skeletons/inline spinners), empty (new account, no Spese this period, insufficient-data charts), error, honesty states (warm amber), offline/stale, auth failure + lost-recovery-code.
- UX-DR12: **Accessibility floor** — warm-but-legible: text-safe `-ink` token variants (AA contrast in both themes), ≥44px tap targets, visible `{color.focus}` ring, focus-trap + restore on the bottom-sheet, non-color signifiers for honesty states and Netto sign.
- UX-DR13: **Adaptive responsive / PWA** — mobile-first; detail/management screens reachable everywhere but richer on desktop (e.g. Secchiello create = full-screen form on mobile / inline panel on desktop); installable PWA shell.
- UX-DR14: **Voice & tone microcopy** — calm, honest, plain Italian, encouraging-not-nagging; consistent strings for banners, warnings, empty states, toasts.

### FR Coverage Map

- FR-1: Epic 1 — Self-service registration
- FR-2: Epic 1 — Authentication & session
- FR-3: Epic 1 — Password recovery (recovery code)
- FR-4: Epic 1 — Data isolation
- FR-5: Epic 2 — Record a Spesa (Secchiello link added in Epic 3, Story 3.1)
- FR-6: Epic 2 — Record an Entrata
- FR-7: Epic 2 — Typed Categorie; Categoria→Secchiello link in Epic 3 (Story 3.1)
- FR-8: Epic 6 — Regole ricorrenti (Entrate + Versamenti PAC)
- FR-9: Epic 3 — Auto-computed Quota
- FR-10: Epic 3 — Funding/payment/carryover lifecycle
- FR-11: Epic 3 — Any periodicità
- FR-12: Epic 2 — Set initial liquidity
- FR-13: Epic 2 — Derived liquidity
- FR-14: Epic 3 — Allocation breakdown (allocata/libera)
- FR-15: Epic 3 — Safety-buffer warning (Cuscinetto)
- FR-16: Epic 4 — Periodic reconciliation reminder
- FR-17: Epic 4 — Reconcile real liquidity / Drift
- FR-18: Epic 4 — "non identificato" / acknowledge-and-leave-open
- FR-19: Epic 5 — Investimenti (PAC) at contributed capital
- FR-20: Epic 5 — Beni immobili at price paid
- FR-21: Epic 5 — Beni mobili with linear depreciation
- FR-22: Epic 5 — Net-worth total (Patrimonio)
- API-1 / API-2 / API-3: Cross-cutting — API contract surface established in Epic 1, upheld across all epics.

## Epic List

### Epic 1: Account & Access (Foundation)
A new Utente can register (username + password), save a one-time recovery code, log in, and land in an empty, themed app with their data fully isolated. Establishes the project scaffold (init from `full-stack-fastapi-template` + Neon Postgres + "Morbido" restyle), the design-token system + base components, the `/api/v1` contract surface, and the per-Utente authZ boundary.
**FRs covered:** FR-1, FR-2, FR-3, FR-4 (+ AR-Init first story; API-1/2/3 foundation; UX-DR1/2/10/12; NFR-2)

### Epic 2: Track my money (the daily loop)
An Utente can capture Spese and Entrate "al volo", organize them with typed Categorie, set their Liquidità iniziale, and see the Home "Mese" — the current-period balance (Netto/Entrate/Spese) with Spese broken down by Categoria — plus Statistiche charts (trends + period pie). Liquidità is derived. Establishes the pure calculation engine (Liquidità).
**FRs covered:** FR-5, FR-6, FR-7, FR-12, FR-13 (+ AR-Calc Liquidità; UX-DR3/4/6)

### Epic 3: Set aside & know what's free (Secchielli + allocation)
An Utente can create Secchielli for known recurring costs, get an auto-computed monthly Quota for any periodicità, fund them over time with honest carryover (negative Saldo surfaced), link Spesa-categories to Secchielli, and see Liquidità split into allocata vs Risparmio libero against the Cuscinetto di sicurezza. The signature accumulate-first payoff.
**FRs covered:** FR-9, FR-10, FR-11, FR-14, FR-15 (consumes FR-7 link; + Secchiello calc; UX-DR5)

### Epic 4: Keep it honest (Drift & Reconciliation)
An Utente is reminded in-app to confirm real liquidity, sees the Drift vs the computed figure (€ and %), and closes the gap with a "non identificato" Movimento or acknowledges it — honest books without any bank link.
**FRs covered:** FR-16, FR-17, FR-18 (+ UX-DR8)

### Epic 5: My whole net worth (Patrimonio)
An Utente censuses their net worth on their own terms — Investimenti at Capitale versato, Beni immobili at price paid, Beni mobili linearly depreciated — and sees the total Patrimonio, without assets distorting Liquidità.
**FRs covered:** FR-19, FR-20, FR-21, FR-22 (+ UX-DR7)

### Epic 6: Automate recurring money (Regole ricorrenti)
An Utente can define Regole ricorrenti that auto-generate recurring Entrate and Versamenti PAC (up to today, lazily and idempotently), each editable and skippable — cutting manual entry (the SM-C1 lever).
**FRs covered:** FR-8 (+ AR-Regole-Lazy; UX-DR9 settings)


## Epic 1: Account & Access (Foundation)

This epic establishes the entire scaffold on which mynance is built: the project initialized from `fastapi/full-stack-fastapi-template` with Neon Postgres, a `/api/v1` REST surface emitting `application/problem+json`, the "Morbido" design tokens (light/dark) and accessibility floor, and a Docker/CI baseline (AR-Init). On top of that scaffold it delivers the complete account-and-access boundary: a new Utente can self-register with username + password (FR-1), save a one-time recovery code shown only once and stored as a salted hash (FR-3), log in and stay authenticated across a 30-day idle session (FR-2), and land in an empty themed app whose data is rigorously isolated per-Utente through a single authorization choke point so that no Utente can ever read or write another's data (FR-4, AR-AuthZ). By the end of the epic the design system, the API contract, the authZ boundary, and a minimal onboarding shell all exist — the foundation every later epic builds on.

### Story 1.1: Initialize project scaffold, Morbido theme, API contract, and CI baseline (AR-Init)

As the builder,
I want the mynance monorepo initialized from the official full-stack template, wired to Neon Postgres, restyled to the "Morbido" design tokens, and running under a `/api/v1` + `problem+json` + Docker/CI baseline,
So that every later story builds on a consistent, deployable scaffold with the API-as-product contract already in place.

**Acceptance Criteria:**

**Given** a clean working directory
**When** the project is initialized from `https://github.com/fastapi/full-stack-fastapi-template.git` into the monorepo
**Then** the repo has separate `backend/` (FastAPI, SQLModel/SQLAlchemy 2, Alembic, pydantic v2) and `frontend/` (React 19 + Vite 8 + TypeScript + TanStack Query/Router) trees
**And** `docker compose up` starts api + postgres + frontend locally with hot reload on both sides.

**Given** the backend application factory
**When** routers are mounted
**Then** all API routes are served under the path prefix `/api/v1` and the OpenAPI schema is generated and reachable
**And** the OpenAPI → TypeScript client generation pipeline (`scripts/generate_client.sh`) emits a typed client under `frontend/src/lib/api/` that is the only egress to the backend.

**Given** any backend endpoint that raises a domain or validation error
**When** the error is handled
**Then** the response body is `application/problem+json` (RFC 9457) with fields `{type, title, status, detail, instance}`
**And** a Pydantic validation failure returns HTTP 422 in that same problem+json shape.

**Given** the database configuration
**When** the app connects in any environment
**Then** it connects to a Neon-provided PostgreSQL instance via env-var connection string (no secrets committed)
**And** the initial Alembic migration runs successfully against it.

**Given** the frontend
**When** it renders any screen
**Then** all visual styling derives from the "Morbido" design tokens (`{color.*}`, `{type.*}`, `{radius.*}`) exposed as CSS custom properties under `frontend/src/theme/`, replacing the template's default styling
**And** both a light and a dark theme are defined, with the active theme following the device/system setting and a manual override available.

**Given** a push to the main branch
**When** CI runs
**Then** the pipeline executes lint (ruff/eslint), type-check (mypy/tsc), tests (pytest + Playwright), and build, and fails the pipeline if any step fails.

**Given** the money-handling convention is established at init
**When** any monetary field is defined in the DB schema, API schema, or domain code
**Then** it is an integer in minor units (cents) on a BIGINT column suffixed `_cents`, never a float or a localized string — formatting to `€ 1.234,56` happens only at the frontend display layer.

### Story 1.2: Base shared component library and theme tokens with accessibility floor (UX-DR1, UX-DR2, UX-DR12)

As the builder,
I want the shared "Morbido" components and theme tokens implemented with the accessibility floor baked in,
So that all later screens compose from one consistent, accessible, light/dark-ready component set rather than ad-hoc styling.

**Acceptance Criteria:**

**Given** the theme layer from Story 1.1
**When** the app loads in light or dark
**Then** the documented token set is available as CSS custom properties — including `{color.accent}`/`{color.accent-ink}`, `{color.positive}`/`{color.positive-ink}`, `{color.negative}`, `{color.honesty}`/`{color.honesty-bg}`, `{color.ink}`/`{color.ink-soft}`, `{color.surface}`/`{color.surface-2}`, `{color.bg}`, `{color.bar-track}`, `{color.focus}`, `{radius.card}`, and the `{type.display}`/`{type.body}`/`{font.sans}` typography tokens
**And** switching theme re-resolves every component's appearance without a reload.

**Given** the shared component namespace
**When** the library is built
**Then** the base behavioral components exist and are reusable: `card`, `balance-block`, `bottom-nav`, `honesty-banner`, `list-row`, `chip`, and a generic button/input set
**And** each is styled solely from theme tokens (no inlined colors, radii, or fonts).

**Given** any interactive element (button, input, nav slot, chip, list row)
**When** it receives keyboard focus
**Then** it shows a visible 2px focus ring using the dedicated `{color.focus}` token (never the soft `{color.accent}`)
**And** focus traversal follows reading order on the surface.

**Given** the accessibility floor
**When** text is rendered in either theme
**Then** normal body text meets WCAG AA contrast (≥ 4.5:1) against its surface, using the text-safe `-ink` variants for accent/positive figures and `{color.ink-soft}` (`#6D6A63` light) for secondary text
**And** every tap target (chip, nav slot, list row, button) is ≥ 44px.

**Given** the honesty color rule
**When** a component renders a warning or surfaced truth
**Then** it uses warm amber `{color.honesty}` on `{color.honesty-bg}`, never alarm-red, and `{color.negative}` is reserved only for negative signed figures
**And** sign is never conveyed by color alone — a `+`/`−` plus the figure always accompanies it.

**Given** a user with Reduce Motion enabled
**When** an animated component (e.g. a rising sheet or fading toast) would appear
**Then** the animation is skipped and the end state is shown immediately.

### Story 1.3: Self-service registration with one-time recovery code (FR-1, FR-3)

As an anonymous visitor,
I want to create an account with a username and password and be shown a one-time recovery code to save,
So that I get an isolated, empty dataset and a way to regain access if I forget my password.

**Acceptance Criteria:**

**Given** the registration capability requires persistence
**When** this story is implemented
**Then** an Alembic migration creates the `utenti` table (UUID PK `id`, unique `username`, `password_hash`, `recovery_code_hash`, `session_timeout_days` defaulting to 30, `created_at`/`updated_at`/`deleted_at`) — and no other epic entity tables are created here.

**Given** an anonymous visitor on the registration screen
**When** they submit a unique username and a password
**Then** a new Utente is created with an empty dataset and no Liquidità iniziale set
**And** the password is stored only as an argon2 salted hash; the plaintext is never persisted or logged.

**Given** a username that already exists
**When** registration is attempted with it
**Then** the request is rejected with a clear, plain Italian message that the username is taken (problem+json), and no Utente is created.

**Given** a successful registration
**When** the account is created
**Then** a one-time recovery code is generated and shown to the Utente exactly once, with explicit "save this now" framing
**And** the recovery code is stored only as a salted hash — the plaintext is never persisted, logged, or retrievable afterward.

**Given** an Utente who provides their username and the correct recovery code
**When** they complete the recovery flow
**Then** they regain access and can set a new password, and the existing password is never exposed at any point.

**Given** a recovery attempt with a wrong username or wrong recovery code
**When** it is submitted
**Then** it is rejected with a plain message that does not reveal whether the account exists.

**Given** a lost or unavailable recovery code
**When** the Utente seeks recovery
**Then** the UI states plainly that, by design, the account cannot be recovered without it (no false promise of a back channel), per the lost-recovery-code state pattern.

### Story 1.4: Login, 30-day session, and logout (FR-2)

As a registered Utente,
I want to log in with my username and password and stay authenticated across a 30-day session that I can also end explicitly,
So that I have secure, persistent access to my data without re-authenticating constantly.

**Acceptance Criteria:**

**Given** a registered Utente on the login screen
**When** they submit their correct username and password
**Then** they are authenticated and issued a JWT access token used as a Bearer token in the `Authorization` header for subsequent API calls.

**Given** invalid credentials (wrong username or wrong password)
**When** login is attempted
**Then** the request is rejected with a single plain, non-blaming message that does not reveal whether the username exists.

**Given** an authenticated Utente
**When** 30 days of inactivity elapse (the per-Utente `session_timeout_days`, default 30, configurable)
**Then** the session is no longer valid and the next protected request returns 401, redirecting the Utente to login.

**Given** an authenticated Utente
**When** they choose explicit logout
**Then** their session ends immediately and protected requests thereafter return 401.

**Given** any request to a protected endpoint without a valid token
**When** it is received
**Then** it returns 401 in problem+json, and the frontend route guard redirects to login.

**Given** the login and recovery endpoints are auth-sensitive
**When** repeated attempts are made from the same origin
**Then** rate limiting is applied to those endpoints to resist brute-force attempts.

### Story 1.5: Per-Utente authorization choke point and data isolation (FR-4, AR-AuthZ)

As an authenticated Utente,
I want every read and write to be automatically scoped to my own data,
So that no other Utente can ever read or write my financial information and I can never see theirs.

**Acceptance Criteria:**

**Given** the service layer
**When** any data access is performed
**Then** it goes through the user-scoped base repository (`services/repository.py`) that always filters by `utente_id` — routers never query models directly, making the repository the single authZ choke point.

**Given** the API dependency layer
**When** a protected endpoint is invoked
**Then** the current Utente is resolved from the validated JWT via the `current_utente` dependency, and that identity scopes every downstream query.

**Given** Utente A is authenticated
**When** A requests, edits, or deletes an entity that belongs to Utente B (by guessing or supplying B's entity id)
**Then** the response is 404 (or 403) in problem+json and never returns or mutates B's data.

**Given** a request for an entity id that does not exist at all
**When** it is made by any authenticated Utente
**Then** the response is the same not-found shape used for cross-Utente access, so existence of another Utente's data is never leaked through differing responses.

**Given** an automated test suite
**When** authZ isolation tests run
**Then** there is at least one test per protected resource asserting that cross-Utente access returns 404/403 and never the data, covering the choke point for every entity type introduced.

**Given** any new endpoint added in later epics
**When** it queries persisted data
**Then** it must do so through the user-scoped repository — a query missing the `utente_id` scope is treated as a defect (enforced in review/CI per the architecture anti-patterns).

### Story 1.6: Minimal onboarding shell and empty themed Home (UX-DR10)

As a newly registered Utente,
I want a minimal onboarding that lands me in an empty, themed app with gentle first-run guidance,
So that I can start using mynance immediately without a heavy setup burden (respecting SM-C1).

**Acceptance Criteria:**

**Given** a just-registered Utente who has saved their recovery code
**When** onboarding continues
**Then** they are offered one light, skippable step — `Imposta la tua Liquidità iniziale per cominciare.` — which is recommended but skippable and settable later from Impostazioni (the Liquidità iniziale value itself is wired to persistence in a later epic; this story delivers only the skippable shell and copy).

**Given** a new Utente completing or skipping onboarding
**When** they land in the app
**Then** they arrive on an empty Home ("Mese") rendered with the Morbido components and the `bottom-nav` shell (the five slots present, even if their destinations are stubbed for later epics).

**Given** the empty Home with no data
**When** it renders
**Then** it shows the calm first-run empty state with gentle, non-nagging Italian microcopy (e.g. `Imposta la tua Liquidità iniziale per cominciare.` and `Ancora nessuna spesa questo mese.`), with no false bars, no zero-state chart noise, and no streaks/badges/exclamation marks.

**Given** the account is brand new
**When** the Home and any summary surface load
**Then** they reflect an empty, isolated dataset (no other Utente's data is ever visible), consistent with the per-Utente isolation from Story 1.5.

**Given** the onboarding and Home shell
**When** navigated by keyboard or screen reader
**Then** the focus ring, ≥44px tap targets, reading-order traversal, and AA contrast from Story 1.2 hold throughout, and every interactive element is labeled with role + state.

## Epic 2: Track my money (the daily loop)

This epic builds the daily tracking loop on top of the Epic 1 foundation (project init, auth, per-Utente isolation, Categorie scaffolding if any). It delivers typed Categorie CRUD with an optional Categoria->Secchiello link, the one-time Liquidità iniziale baseline with a re-baseline audit, a pure derived-on-read calculation engine for Liquidità (AR-Calc) covered by worked-example tests, the derived Liquidità read endpoint, recording a Spesa (with the Secchiello default-from-Categoria, overridable per-Spesa) and an Entrata, an online-first optimistic quick-add bottom sheet, the period-aware Home "Mese" with a server-aggregated per-Categoria breakdown and drill-down, and the Statistiche charts (cross-period trends + per-period Spese pie). All money is integer cents, all derived figures are computed server-side and never recomputed divergently by the client, and Liquidità is always derived, never stored as a running balance. Stories are ordered so each builds only on earlier work (and Epic 1); no story depends on a later one.

### Story 2.1: Typed Categorie CRUD (FR-7)

As an Utente,
I want to create, rename, and reuse my own type-scoped Categorie,
So that I can organize my Movimenti by Spesa and Entrata categories.

**Acceptance Criteria:**

**Given** I am an authenticated Utente
**When** I create a Categoria with a name and a tipo of either Spesa or Entrata
**Then** the Categoria is persisted scoped to my `utente_id` with that tipo
**And** the tipo is enforced backend-side as a distinct space (Spesa and Entrata Categorie are separate, not merely a UI filter)
**And** the response returns the created Categoria object directly (snake_case fields).

**Given** I have an existing Categoria
**When** I rename it or fetch the list of my Categorie
**Then** the rename persists and the list is returned split/identifiable per tipo (Spesa list and Entrata list)
**And** only Categorie owned by my `utente_id` are ever returned.

**Given** a new account with no Categorie yet
**When** the starter set is applied (on account creation or first read, per Epic 1 onboarding)
**Then** a starter set of Categorie is suggested separately per tipo (Spesa categories and Entrata categories)
**And** the system "non identificato" Categorie (one per tipo) are provisioned separately in Epic 4 (Story 4.1) — not duplicated here.

> Note: the **Categoria→Secchiello link** (FR-7) is introduced in Epic 3 (Story 3.1), once Secchielli exist; Epic 2 builds typed Categorie only.

**Given** a Categoria of mine that is in use by existing Movimenti
**When** I attempt to delete it
**Then** I am prompted to reassign the affected Movimenti rather than silently orphaning them (deletion does not proceed until reassignment is resolved).

**Given** another Utente's Categoria id
**When** I request, rename, or delete it
**Then** the response is 404/403 and never that Categoria's data (per-Utente isolation, FR-4).

### Story 2.2: Set Liquidità iniziale once with re-baseline audit (FR-12)

As an Utente,
I want to set my Liquidità iniziale a single time and have any later change recorded as an audited re-baselining,
So that all derived figures start from an honest baseline and any shift of that baseline is traceable.

**Acceptance Criteria:**

**Given** a new account with no Liquidità iniziale set
**When** I read my Liquidità iniziale
**Then** it reports as unset (the account starts with no baseline, per FR-1).

**Given** my Liquidità iniziale is unset
**When** I set it to an integer cents value
**Then** the value is stored in cents (BIGINT, `*_cents`), scoped to my `utente_id`
**And** a non-positive or non-integer-cents input that is invalid (e.g. a float string) is rejected with 422 problem+json (zero is permitted; negative is rejected).

**Given** my Liquidità iniziale is already set
**When** I change it to a different value
**Then** the change is allowed but recorded in the audit log as a re-baselining event (old value, new value, timestamp, `utente_id`)
**And** the UI/response flags it as a re-baselining action because it shifts all derived figures.

**Given** another Utente's account
**When** I attempt to read or change their Liquidità iniziale
**Then** the response is 404/403 and never their value (FR-4).

### Story 2.3: Pure derived-on-read calc engine for Liquidità (AR-Calc) with worked-example tests (FR-13, NFR-1)

As a developer,
I want a pure, framework-independent calculation module that derives Liquidità from stored inputs in integer cents,
So that the core financial figure is deterministic, reproducible, isolated from DB/IO, and covered by worked-example tests before any endpoint depends on it.

**Acceptance Criteria:**

**Given** the calc module lives in `backend/app/calc/` (e.g. `money.py`, `liquidita.py`)
**When** it is imported and used
**Then** it contains no DB access, no FastAPI imports, and no IO — it operates only on plain input values passed in (pure functions, unit-testable in isolation).

**Given** a Liquidità iniziale and collections of Entrate, Spese, and Capitale versato amounts (all in integer cents)
**When** the engine computes Liquidità
**Then** it returns `Liquidità = Liquidità iniziale + Σ Entrate − Σ Spese − Σ Capitale versato`, all arithmetic performed in integer cents (never float)
**And** for this epic, Capitale versato may be empty (no Investimenti yet); the formula still holds with an empty set summing to 0.

**Given** an unset Liquidità iniziale
**When** the engine computes Liquidità
**Then** it treats the baseline as 0 cents (or an explicit "unset" sentinel the caller surfaces), deterministically, without throwing.

**Given** a worked reference example with known inputs (e.g. iniziale 100000 cents, two Entrate 250000 + 50000, three Spese 45000 + 1299 + 90000)
**When** the engine computes Liquidità
**Then** the result equals the hand-computed expected cents value exactly
**And** dedicated unit tests in `backend/tests/calc/` assert this and additional worked examples, including a case whose computed Liquidità is negative (negative result surfaced, never clamped).

**Given** the same stored inputs supplied in different ordering
**When** the engine computes Liquidità
**Then** the result is identical (order-independent for the pure sum) and reproducible across runs (determinism, NFR-1).

**Given** a rounding-sensitive scenario
**When** money helpers convert or aggregate
**Then** rounding is centralized in `money.py` and all values remain exact integer cents with no float drift.

### Story 2.4: Derived Liquidità read endpoint (FR-13)

As an Utente,
I want an API endpoint that returns my current Liquidità computed server-side,
So that every client shows the same derived-on-read value and never recomputes money locally.

**Acceptance Criteria:**

**Given** I am authenticated
**When** I GET `/api/v1/liquidita`
**Then** the service loads my stored inputs (Liquidità iniziale, my Entrate, my Spese — Capitale versato empty for now), scoped by `utente_id`, and calls the pure calc engine from Story 2.3
**And** the response returns the current Liquidità as integer cents (`*_cents`), computed entirely server-side (API-3: client never recomputes).

**Given** I record, edit, or delete a Spesa or Entrata (Stories 2.5/2.6)
**When** I GET `/api/v1/liquidita` again
**Then** the returned value reflects the change immediately (derived-on-read recompute, no stale running balance).

**Given** my flows produce a negative derived value
**When** I GET `/api/v1/liquidita`
**Then** the negative Liquidità is returned with sign, never clamped to zero (honesty principle).

**Given** my Liquidità iniziale is unset
**When** I GET `/api/v1/liquidita`
**Then** the endpoint responds deterministically (baseline treated as 0 / surfaced as unset) without error.

**Given** I request the endpoint without a valid token
**When** the request is made
**Then** it returns 401 and no data; and a request can never return another Utente's Liquidità (queries scoped by `utente_id`, FR-4).

### Story 2.5: Record a Spesa (FR-5)

As an Utente,
I want to record a Spesa with amount, date, a Spesa-type Categoria, and optional note,
So that I capture an outflow correctly and it immediately affects my derived Liquidità.

**Acceptance Criteria:**

**Given** I am authenticated and the Movimento (Spesa) entity/table is created in this story (`movimenti`, money in `*_cents` BIGINT, UUID PK, `utente_id`, soft-delete `deleted_at`)
**When** I POST a Spesa with amount in integer cents, a date, and a Spesa-type Categoria
**Then** the Spesa is persisted scoped to my `utente_id` and the amount is stored in cents (never float).

> Note: linking a Spesa to a Secchiello (Categoria default + per-Spesa override, FR-5/FR-7) is added in Epic 3 (Story 3.1), once Secchielli exist.

**Given** I attempt to attach an Entrata-type Categoria to a Spesa
**When** the request is validated
**Then** it is rejected with 422 problem+json (a Categoria can only apply to Movimenti of its own tipo, FR-7).

**Given** an existing Spesa of mine
**When** I edit its amount/date/Categoria/note, or delete it (soft-delete)
**Then** the change persists, no Movimento is silently lost, and the derived Liquidità (Story 2.4) recomputes accordingly on next read.

**Given** another Utente's Categoria id, or another Utente's Spesa id
**When** I reference it on create, or attempt to read/edit/delete it
**Then** the response is 404/403 and never their data (FR-4).

### Story 2.6: Record an Entrata (FR-6)

As an Utente,
I want to record an Entrata with amount, date, an Entrata-type Categoria, and optional note,
So that my inflows immediately increase my derived Liquidità.

**Acceptance Criteria:**

**Given** I am authenticated
**When** I POST an Entrata with amount in integer cents, a date, and an Entrata-type Categoria
**Then** the Entrata is persisted as a Movimento scoped to my `utente_id`, amount in `*_cents` (never float).

**Given** I attempt to attach a Spesa-type Categoria to an Entrata
**When** the request is validated
**Then** it is rejected with 422 problem+json (tipo mismatch, FR-7).

**Given** I record a new Entrata
**When** I subsequently GET `/api/v1/liquidita`
**Then** the derived Liquidità has increased by exactly that Entrata's cents (FR-13 recompute).

**Given** an existing Entrata of mine
**When** I edit or delete (soft-delete) it
**Then** the change persists with no silent loss, and derived Liquidità recomputes on next read.

**Given** another Utente's Entrata id
**When** I attempt to read/edit/delete it
**Then** the response is 404/403 and never their data (FR-4).

### Story 2.7: Quick-add bottom sheet — online-first optimistic capture (FR-5, FR-6, UX-DR4)

As an Utente,
I want a one-handed quick-add bottom sheet to capture a Spesa or Entrata "al volo" with optimistic UI,
So that capture is fast and frictionless, lowering the chance a forgotten entry becomes Drift.

**Acceptance Criteria:**

**Given** I tap the central ＋ in the `bottom-nav`
**When** the quick-add `bottom-sheet` rises
**Then** the numeric `keypad` is already up with the amount focused, the Spesa/Entrata toggle defaults to Spesa, and the date defaults to Oggi (today)
**And** amount entry uses the Italian decimal comma `,` and is converted to integer cents before submission.

**Given** the sheet is open with an amount typed
**When** I pick a Categoria via a recent/most-used `chip` (or open `＋ altre…` for the full type-scoped list)
**Then** for a Spesa, the `secchiello-badge` updates from the chosen Categoria's linked Secchiello (FR-5), and I can tap it to override or clear the Secchiello per-Spesa before saving.

**Given** I have entered amount + Categoria
**When** I tap `Salva`
**Then** the Movimento is created via the generated API client (Story 2.5/2.6 endpoints), the UI updates optimistically (the new Movimento appears in Home Bilancio and the relevant `category-row` before the server confirms), the sheet falls away, and a quiet `Spesa aggiunta` / `Entrata aggiunta` toast appears.

**Given** the save request fails (network/server error)
**When** the error returns
**Then** the optimistic update is rolled back so no phantom Movimento or wrong balance lingers, and a plain warm message with retry is shown (no raw error exposed); affected TanStack Query keys (`movimenti`, `liquidita`, period aggregates) are reconciled with server truth.

**Given** the optimistic mutation is in flight
**When** it succeeds
**Then** the affected TanStack Query keys are invalidated and re-fetched so derived figures come from the server (client never recomputes money — UX-DR4 / API-3).

**Given** the bottom sheet is open
**When** I swipe down to dismiss
**Then** the sheet closes without saving and focus returns to the ＋ trigger (accessibility: focus trap + restore).

### Story 2.8: Home "Mese" — period-aware Bilancio + server-aggregated per-Categoria breakdown with drill-down (FR-13, UX-DR3)

As an Utente,
I want the Home to show a period-scoped Bilancio and a per-Categoria spend breakdown that I can drill into,
So that I see my month at a glance and can inspect any Categoria's Spese.

**Acceptance Criteria:**

**Given** I am authenticated on the Home "Mese"
**When** the screen loads with the default period (Mese / current month) via the `period-selector` (Giorno / Settimana / Mese / Anno)
**Then** it requests a server-side period aggregation endpoint (e.g. GET `/api/v1/...?period=month&anchor=2026-06`) scoped by `utente_id`, and the client never sums money itself (API-3).

**Given** the period aggregation endpoint
**When** it computes the response for my account
**Then** it returns the period Bilancio (Netto, plus Entrate and Spese totals) in integer cents and a per-Categoria Spese breakdown, with category boundaries computed in `Europe/Rome`
**And** the per-Categoria list is sorted largest → smallest by total spend (decision #14).

**Given** the per-Categoria breakdown is displayed
**When** I tap a `category-row`
**Then** I drill into that Categoria's Spese detail list (pushed one level), showing the individual Spese for the selected period, and Back returns to Home.

**Given** I change the period granularity or navigate within the period with `‹ ›`
**When** the period changes
**Then** the Bilancio and breakdown re-fetch the server aggregation for the new period (period-aware), and the allocated/free split is NOT shown on Home (it lives only on Liquidità, decision #12).

**Given** a period with no Spese
**When** the Home renders
**Then** it shows the calm empty state `Ancora nessuna spesa questo mese.` with no false bars or zero-state chart noise.

**Given** the derived data is loading or stale/offline
**When** the Home renders
**Then** loading shows skeletons (not a blocking spinner) and stale/offline derived values are marked plainly ("dati non aggiornati") with retry, never presented as confidently current.

**Given** another Utente's data
**When** the aggregation endpoint is called
**Then** only my Movimenti are aggregated (queries scoped by `utente_id`); a request for another Utente's data returns 404/403 (FR-4).

### Story 2.9: Statistiche charts — cross-period trends + per-period Spese pie (UX-DR6)

As an Utente,
I want a charts-only Statistiche screen showing how my money moves over time and a per-period Spese share by Categoria,
So that I understand trends and where my spending concentrates without manual math.

**Acceptance Criteria:**

**Given** I am authenticated on Statistiche
**When** the screen loads
**Then** it shows charts only — no lists (the per-Categoria list is Home's job) — using the same `period-selector` as Home to set the reference period.

**Given** the Statistiche data
**When** it is fetched
**Then** it comes from a server-side aggregation endpoint (e.g. GET `/api/v1/statistiche?period=...&anchor=...`) scoped by `utente_id`, returning all monetary aggregates in integer cents; the client renders charts but never aggregates money itself (API-3).

**Given** sufficient history exists
**When** the trends layer renders
**Then** it shows cross-period line charts (Spese / Entrate / Netto month-over-month) computed server-side with month boundaries in `Europe/Rome`.

**Given** the selected period has Spese
**When** the pie layer renders
**Then** it shows a pie of that period's Spese share by Categoria, computed server-side, with the system "non identificato" Categoria surfaced like any other Categoria (not hidden).

**Given** there is not enough history to chart a trend, or no Spese in the period for the pie
**When** Statistiche renders
**Then** it shows the calm `Servono più dati per i grafici` message instead of an empty or fabricated/misleading chart (no false trend lines).

**Given** the data is loading or stale/offline
**When** Statistiche renders
**Then** loading shows skeletons and stale data is marked plainly with retry, never shown as confidently current.

**Given** another Utente's data
**When** the Statistiche endpoint is called
**Then** only my Movimenti are aggregated (scoped by `utente_id`); cross-Utente access returns 404/403 (FR-4).

## Epic 3: Set aside & know what’s free (Secchielli + allocation)

This epic delivers mynance's signature capability: the *Secchiello* (predictive amortization bucket) and the allocation answer it enables. The Utente can create and edit a *Secchiello* for any *Periodicità*, mynance auto-computes a recommended monthly *Quota* and a chronologically derived-on-read *Saldo* (no scheduler), the full funding→payment→carryover lifecycle keeps the bucket honest by surfacing a negative *Saldo* (under-funding) rather than hiding it, and the **Liquidità** screen's two tabs answer the north-star question — how much *Liquidità* is *allocata* vs how much is *Risparmio libero*, and whether *Risparmio libero* sits above the *Cuscinetto di sicurezza* (default N=6 months of *Spesa media mensile*, including *"non identificato"*). It consumes the Categoria→Secchiello link established in Epic 2 and builds strictly on the derived *Liquidità* engine from Epic 2's Liquidità work; all money is integer cents, all derived values are computed server-side per-Utente.

### Story 3.1: Create and edit a Secchiello (any Periodicità) + Categoria→Secchiello link (FR-11, FR-7, FR-5)

As an Utente,
I want to create and edit a *Secchiello* with a name, *Importo previsto*, *Periodicità*, and *Prossima scadenza*,
So that I can set aside money in advance for any known recurring expense, not just annual ones.

**Acceptance Criteria:**

**Given** I am an authenticated Utente
**When** the migration for this epic runs
**Then** a `secchielli` table exists with snake_case columns: `id` (UUID PK), `utente_id` (UUID FK, indexed), `nome`, `importo_previsto_cents` (BIGINT), `periodicita`, `prossima_scadenza` (DATE), `created_at`, `updated_at`, `deleted_at` (soft-delete)
**And** there is an index `ix_secchielli_utente_id` and no money column is stored as a float

**Given** I am authenticated
**When** I create a *Secchiello* with `nome` "Assicurazione auto", `importo_previsto_cents` 62000, `periodicita` `annual`, and a *Prossima scadenza* 8 months from today
**Then** the *Secchiello* is persisted scoped to my `utente_id`
**And** the response returns money as integer `*_cents`, never a float or localized string

**Given** I am creating or editing a *Secchiello*
**When** I set its `periodicita`
**Then** the accepted values are `monthly`, `quarterly`, `semiannual`, `annual`, or `custom` with an integer interval in months (≥ 1)
**And** a `custom` *Periodicità* without a positive integer interval is rejected with a 422 `application/problem+json` validation error

**Given** I submit a *Secchiello* with a missing `nome`, a non-positive `importo_previsto_cents`, or a malformed `prossima_scadenza`
**When** the request is validated at the API boundary
**Then** it is rejected with 422 `application/problem+json` and the *Secchiello* is not persisted

**Given** Secchielli now exist (this epic) and the typed Categorie from Epic 2
**When** the Categoria→Secchiello link is introduced
**Then** a nullable `secchiello_id` link is added to Spesa-type Categorie (at most one Secchiello per Categoria, optional; an Entrata-type Categoria cannot be linked → 422), and changing/removing a Categoria's link affects only the default for future Spese (already-recorded Spese keep their own link)

**Given** a Spesa (Story 2.5) whose chosen Spesa-type Categoria is linked to a Secchiello
**When** the Spesa is created without an explicit Secchiello
**Then** its Secchiello link is pre-filled (defaulted) from the Categoria, and the Utente can override it per-Spesa (a different Secchiello or none) — fulfilling the FR-5/FR-7 link deferred from Epic 2

**Given** another Utente owns a *Secchiello*
**When** I request, edit, or delete it by its `id`
**Then** the response is 404/403 and never that Utente's data

**Given** I delete a *Secchiello* I own
**When** the delete succeeds
**Then** the row is soft-deleted (`deleted_at` set) so no data is silently lost, and it no longer appears in my *Secchielli* list or allocation calculations

### Story 3.2: Derived-on-read Quota & Saldo engine (FR-9, FR-11)

As an Utente,
I want mynance to recommend a monthly *Quota* and compute the *Secchiello*'s *Saldo* deterministically from my inputs,
So that I always know how much to set aside, without any manual math or a background job.

**Acceptance Criteria:**

**Given** a *Secchiello* with stored inputs (start date, *Importo previsto*, *Prossima scadenza*, *Periodicità*, and any linked *Spese*)
**When** the engine computes its *Quota* and *Saldo*
**Then** the computation lives in the pure `app/calc/secchiello.py` module with no DB or framework imports, and is exercised by dedicated worked-example unit tests in `tests/calc/`

**Given** a *Secchiello*
**When** the months-to-due is computed
**Then** `mesi_alla_Prossima_scadenza = max(1, ceil((Prossima scadenza − today) / 30.44 days))`, derived from *Prossima scadenza* and today independently of the *Periodicità* label
**And** a due-or-overdue *Secchiello* yields `mesi = 1`, so its full outstanding `(Importo previsto − Saldo)` surfaces in a single *Quota* rather than dividing by zero or a negative

**Given** a *Secchiello* with current *Saldo* and *Importo previsto*
**When** the *Quota* is computed
**Then** `Quota = max(0, (Importo previsto − Saldo) / mesi_alla_Prossima_scadenza)` in integer cents with centralized rounding, recomputed on every read when inputs change
**And** if `Saldo ≥ Importo previsto` the *Quota* is 0 (already funded)
**And** if *Saldo* is negative the *Quota* rises to recover the shortfall over the remaining months

**Given** a *Secchiello* is created with no payment history
**When** the *Quota* is first computed
**Then** *Importo previsto* is the Utente's estimate provided at setup, and the *Quota* derives from it

**Given** the same stored inputs are read twice
**When** the engine recomputes
**Then** the *Quota* and *Saldo* are identical (deterministic and reproducible), and the *Quota* is returned read-only via the API — clients never recompute it

**Given** I request a *Secchiello* I do not own
**When** the engine would be invoked
**Then** the service rejects at the authZ boundary (404/403) before any computation

### Story 3.3: Funding, payment & carryover lifecycle with negative Saldo surfaced (FR-10)

As an Utente,
I want the *Secchiello* to accumulate its *Quota* each elapsed month, settle when I log the linked *Spesa*, and carry the leftover into the next cycle,
So that known expenses arrive already covered and any under-funding is shown to me honestly, never hidden.

**Acceptance Criteria:**

**Given** a *Secchiello* with a start date and *Quota* history
**When** the *Saldo* is computed
**Then** it is derived-on-read by replaying inputs **chronologically** from the start date — each elapsed month credits that month's *Quota* (computed from the *Saldo* and months-remaining as of that month) and each linked *Spesa* is applied on its date — with no scheduled write and no background job
**And** crediting the *Quota* is virtual: it changes the *Secchiello* *Saldo* but never moves *Liquidità*

**Given** elapsed months and chronological replay where *Saldo* and *Quota* are mutually dependent
**When** the engine evaluates each month in date order (credit then apply that month's linked *Spese*)
**Then** the resulting *Saldo* and *Quota* are deterministic, and a back-dated *Spesa* edit recomputes correctly because order is by date, not by insertion

**Given** a *Spesa* (consuming the Categoria→Secchiello link from Story 3.1, overridable per-Spesa) linked to a *Secchiello*
**When** I log it as the actual payment
**Then** the *Secchiello* *Saldo* decrements by the actual *Spesa* amount in cents
**And** the resulting *Saldo*, positive or negative, becomes the carryover into the next cycle

**Given** I log the linked payment *Spesa*
**When** the lifecycle advances
**Then** *Importo previsto* is updated to the actual amount paid (memory) and *Prossima scadenza* advances by the *Periodicità*
**And** the next cycle's *Quota* reflects the carried-over *Saldo* (a positive carryover lowers it; a negative carryover raises it)

**Given** an over-optimistic forecast leaves a *Secchiello* with a negative *Saldo*
**When** I view the *Secchiello* row or detail
**Then** the negative *Saldo* is displayed as an explicit under-funding warning in `{color.honesty}` (warm amber, never alarm-red) with copy `Secchiello in rosso di X € — la Quota salirà per recuperare`
**And** the *Saldo* is never clamped to zero in the bucket's own view

**Given** I delete or edit the linked payment *Spesa*
**When** the engine recomputes
**Then** the *Secchiello* *Saldo*, carryover, and *Quota* update consistently, with no *Movimento* silently lost

### Story 3.4: Secchielli list and detail on the Liquidità screen (FR-9, FR-10, FR-11; UX-DR5 tab B)

As an Utente,
I want a Secchielli tab listing each *Secchiello* with its *Saldo*, recommended *Quota*, and *Prossima scadenza*, with a detail view and the create/edit form,
So that I can manage my buckets and see their funding state at a glance.

**Acceptance Criteria:**

**Given** I open the **Liquidità** screen
**When** it renders
**Then** it shows two tabs and tab B is **Secchielli**, presenting one `list-row` per *Secchiello* with its `secchiello-badge`, current *Saldo*, recommended monthly *Quota*, and *Prossima scadenza*, all formatted from server-supplied cents to `€ 1.234,56` Italian locale at the display layer only

**Given** a *Secchiello* row has a negative *Saldo*
**When** the row renders
**Then** the under-funding is shown in `{color.honesty}` (never clamped, never alarm-red), with sign paired to the figure (not color alone)

**Given** I have no *Secchielli*
**When** tab B renders
**Then** it shows the empty state `Nessun Secchiello. Crea il primo per mettere da parte in anticipo.` with no false rows or bars

**Given** I tap a *Secchiello* row
**When** the detail opens
**Then** it shows *Importo previsto*, *Periodicità*, the *Quota* (read-only, auto-computed per FR-9), the carryover, and the linked *Spese* history

**Given** I create or edit a *Secchiello* from this screen
**When** the form opens
**Then** it is a pushed full-screen form on mobile and an inline panel on desktop, capturing `nome`, *Importo previsto* / last-paid amount, *Periodicità*, and *Prossima scadenza*, with *Quota* shown read-only

**Given** I save a *Secchiello* edit and the save fails (e.g. network/validation error)
**When** the mutation rejects
**Then** any optimistic UI update is rolled back, the prior value is restored, and a plain warm error message with retry is shown — financial data is never silently dropped

**Given** a *Secchiello* mutation succeeds (create/edit/delete) or a linked *Spesa* changes
**When** TanStack Query reconciles
**Then** the `['secchielli']` and `['liquidita']` keys are invalidated and the list, allocation, and *Cuscinetto* re-fetch to reflect recomputed derived values

### Story 3.5: Allocation breakdown — Liquidità allocata vs Risparmio libero (FR-14; UX-DR5 tab A)

As an Utente,
I want the Allocazione tab to split my *Liquidità* into the part committed to *Secchielli* and the part that is genuinely free,
So that I can always see, at a glance, how much of my money is already spoken for and how much is truly free savings.

**Acceptance Criteria:**

**Given** I have *Liquidità* and one or more *Secchielli*
**When** the allocation is computed server-side
**Then** `Liquidità allocata = Σ max(0, Saldo del Secchiello)` and `Risparmio libero = Liquidità − Liquidità allocata`, both in integer cents in `app/calc/allocazione.py`
**And** a *Secchiello* with a negative *Saldo* contributes 0 to *Liquidità allocata* (the `max(0, …)` clamp applies to the allocation total only — the bucket's own view still surfaces the negative *Saldo* per Story 3.3)

**Given** I open the **Liquidità** screen
**When** it renders
**Then** tab A is **Allocazione**, showing a `balance-block` with total *Liquidità*, then the split into **Liquidità allocata** and **Risparmio libero**, formatted from cents at the display layer
**And** this allocation split appears only here, never on the Home

**Given** my *Secchielli* *Saldi* or my *Movimenti* change
**When** the affected TanStack Query keys are invalidated
**Then** *Liquidità allocata* and *Risparmio libero* update live to reflect the recomputed figures, never showing a stale value as current

**Given** the connection drops or a derived value is stale
**When** the Allocazione tab renders
**Then** the affected figure is marked plainly (e.g. a quiet "dati non aggiornati" note) with retry, rather than presenting a confidently wrong number

**Given** I request another Utente's allocation data
**When** the endpoint is called
**Then** the request is scoped to my `utente_id` and never returns another Utente's figures

### Story 3.6: Cuscinetto di sicurezza warning with Spesa media mensile (FR-15; UX-DR5 tab A)

As an Utente,
I want mynance to warn me when my *Risparmio libero* falls below the *Cuscinetto di sicurezza*,
So that I know honestly whether my free savings still cover several months of expenses.

**Acceptance Criteria:**

**Given** my *Spese* history
**When** *Spesa media mensile* is computed in `app/calc/allocazione.py`
**Then** it is the mean of *Spese* over the last N **complete** calendar months (the current partial month excluded), N default 6 and configurable
**And** if fewer complete months of history exist it averages over those available
**And** *"non identificato"* *Spese* **are included** because they are real outflows (honesty principle)

**Given** *Spesa media mensile* and a configurable N (default 6)
**When** the *Cuscinetto di sicurezza* is computed
**Then** `Cuscinetto = N × Spesa media mensile`, in integer cents, deterministic from stored inputs and covered by worked-example tests in `tests/calc/`

**Given** the Allocazione tab (tab A)
**When** the *Cuscinetto* card renders
**Then** it shows the target floor (`N × Spesa media mensile`, default N=6) and whether *Risparmio libero* sits above or below it

**Given** *Risparmio libero* falls below the *Cuscinetto di sicurezza*
**When** the card renders
**Then** a non-blocking indicator surfaces in `{color.honesty}` (warm amber, never alarm-red) with copy `Risparmio libero sotto il Cuscinetto di sicurezza (N mesi)`, and it is treated as honesty data, not an error

**Given** my N or the *Spesa media mensile* trailing window is reconfigured, or my *Spese* / *Secchielli* change
**When** the relevant query keys are invalidated
**Then** the *Cuscinetto* target and the above/below status recompute live

**Given** a brand-new account with no complete months of *Spese* history
**When** the *Cuscinetto* would be computed
**Then** the engine returns a coherent figure over the available (possibly zero) months without dividing by zero, and the tab shows a calm state rather than a misleading warning

## Epic 4: Keep it honest (Drift & Reconciliation)

This epic delivers mynance's honest, manual answer to having no bank link: a self-computed reconciliation reminder (from `today − last Riconciliazione`, no scheduler) that surfaces in-app as a warm-amber `honesty-banner`; a Riconciliazione flow where the Utente confirms real Liquidità and sees the resulting **Drift** in both € and %; and two honest ways to resolve it — close the gap with a *"non identificato"* system `Categoria` plug Movimento that brings computed Liquidità to match reality, or acknowledge-and-leave-open, which resets the reminder timer while keeping the gap visible as a quiet indicator. All honesty states are surfaced warmly (amber), never as alarm-red errors. Covers FR-16, FR-17, FR-18 and realizes UX-DR8.

### Story 4.1: Riconciliazione entity, "non identificato" system Categorie, and reminder-interval setting (FR-16)
As an Utente,
I want mynance to persist my Riconciliazioni and provision the honesty primitives my reconciliation needs,
So that the rest of the reconciliation flow has a place to store events, a configurable cadence, and the dedicated buckets that keep my books honest.

**Acceptance Criteria:**

**Given** the database migrations run on a fresh environment
**When** the schema is created
**Then** a `riconciliazioni` table exists with `id` (UUID PK), `utente_id` (UUID FK, indexed), `liquidita_reale_cents` (BIGINT), `liquidita_calcolata_cents` (BIGINT, snapshot at reconcile time), `drift_cents` (BIGINT, signed), `data_riconciliazione` (DATE), an `esito` enum distinguishing `chiusa` (closed via Movimento) vs `acknowledged_open`, plus `created_at`/`updated_at`/`deleted_at`
**And** an index `ix_riconciliazioni_utente_id_data_riconciliazione` exists for fast "last Riconciliazione" lookups
**And** all money columns are integer cents (BIGINT), never float

**Given** a new Utente account is created
**When** the account is provisioned
**Then** exactly one system `Categoria` named "non identificato" of type Spesa AND exactly one system `Categoria` named "non identificato" of type Entrata are created for that Utente
**And** both are flagged as system categories (a `sistema`/`is_system` boolean true) so they cannot be renamed or deleted by the Utente
**And** they appear in the relevant typed Categoria list like any other Categoria (not hidden buckets)

**Given** the Utente's account settings
**When** the reconciliation interval is read or written
**Then** a per-Utente `intervallo_riconciliazione_giorni` setting exists, defaulting to 7 (weekly)
**And** updating it to a positive integer persists; a non-positive or non-integer value is rejected with a clear validation message (problem+json)

**Given** an authenticated Utente A and an existing Riconciliazione belonging to Utente B
**When** Utente A requests, edits, or deletes B's Riconciliazione (or B's system Categorie) by id
**Then** the response is 404/403 and never leaks B's data, because every query is scoped by `utente_id`

### Story 4.2: Computed reconciliation reminder (no scheduler) (FR-16)
As an Utente,
I want mynance to tell me when it is time to reconcile, computed on access from how long it has been,
So that I keep my books honest without relying on background jobs, email, or push.

**Acceptance Criteria:**

**Given** the Utente has a last Riconciliazione on date D and an interval of N days
**When** the reminder status is requested (computed on read)
**Then** the response returns `due = (today − D) ≥ N`, the integer `giorni_dall_ultima` (`today − D`), and `data_ultima_riconciliazione = D`
**And** no background scheduler, cron, or stored "due" flag is involved — the value is derived purely from `today − last Riconciliazione` evaluated at request time

**Given** the Utente has never reconciled (no Riconciliazione exists)
**When** the reminder status is requested
**Then** the reminder is `due = true` and `data_ultima_riconciliazione = null`, using account creation / first-data date as the baseline so a never-reconciled account is honestly flagged
**And** `giorni_dall_ultima` is computed from that baseline, not returned as an error

**Given** the reminder is `due`
**When** the Utente loads any primary screen
**Then** a non-blocking `honesty-banner` is shown in warm amber (`{color.honesty}` on `{color.honesty-bg}`), reading `È ora di riconciliare — ultima volta: N gg fa`, never alarm-red and never modal (UX-DR8)
**And** the banner is the primary tap target into the Riconciliazione flow, and is dismissible-to-later without resetting the timer

**Given** `(today − D) < N`
**When** any screen loads
**Then** no reconciliation banner is shown (respecting the over-prompting counter-metric SM-C2)

**Given** date boundaries are evaluated
**When** `today` and `D` are compared
**Then** the day delta is computed using calendar days in the `Europe/Rome` context, so a reconciliation late in the day and a check early the next day count consistently

### Story 4.3: Reconcile real Liquidità and show Drift in € and % (FR-17)
As an Utente,
I want to enter my actual observed Liquidità and immediately see the Drift against what mynance computed,
So that I can see plainly how far my books have diverged from reality.

**Acceptance Criteria:**

**Given** the Utente opens the Riconciliazione flow
**When** the flow loads
**Then** mynance shows the current **Liquidità calcolata** (derived on read as `Liquidità iniziale + Σ Entrate − Σ Spese − Σ Capitale versato`), and provides a single input for the real observed Liquidità entered in € (Italian decimal comma) and stored as integer cents

**Given** the Utente enters a real Liquidità of R cents and the computed Liquidità is C cents
**When** the Drift is computed
**Then** `Drift = R − C` is shown with sign and magnitude in € (e.g. `Scostamento: −87 € rispetto al calcolato`) in warm amber, never alarm-red
**And** the Drift is also shown as a percentage `Drift% = (R − C) / C × 100`, signed, displayed alongside the € figure
**And** both figures are computed server-side from integer cents; the client never recomputes money

**Given** the computed Liquidità C is exactly 0 cents
**When** the Drift percentage is computed
**Then** the percentage is suppressed / shown as not-applicable (no divide-by-zero), while the € Drift is still shown normally

**Given** the computed Liquidità is negative (e.g. over-spent baseline) and the real figure differs
**When** the Drift is shown
**Then** the signed € Drift is surfaced honestly and is never silently clamped to zero

**Given** the Utente confirms reality (with or without closing the gap, per Story 4.4/4.5)
**When** the confirmation is saved
**Then** the last `data_riconciliazione` is set to today and a Riconciliazione row is persisted snapshotting `liquidita_reale_cents`, `liquidita_calcolata_cents`, and `drift_cents`
**And** an audit-log entry is written for the Riconciliazione event

**Given** Utente A is authenticated
**When** A submits a reconciliation
**Then** the Riconciliazione is created under A's `utente_id` only; A can never write a Riconciliazione attributable to another Utente (cross-Utente write → 404/403)

### Story 4.4: Close the Drift with a "non identificato" Movimento (FR-18)
As an Utente,
I want to close the Drift in one action by creating a "non identificato" Spesa or Entrata for the difference,
So that my computed Liquidità matches what I really have, with the unexplained flow surfaced rather than swept aside.

**Acceptance Criteria:**

**Given** a confirmed Drift of `R − C` cents during the Riconciliazione flow
**When** the Utente chooses "close the gap"
**Then** mynance creates a single plug Movimento for the absolute difference attributed to the matching "non identificato" system Categoria: a **Spesa** when `R < C` (real is lower, money left unexplained) and an **Entrata** when `R > C` (real is higher), so the sign self-selects the type
**And** the Movimento amount in cents equals `|R − C|` exactly

**Given** the plug "non identificato" Movimento has been created
**When** Liquidità is next derived on read
**Then** computed Liquidità now equals the entered real figure R (the gap is closed), because the plug Movimento exactly offsets the prior Drift
**And** the same confirmation sets the last `data_riconciliazione` to today and records the Riconciliazione with `esito = chiusa`

**Given** the closing Movimento exists
**When** the Utente views Home's per-Categoria breakdown and the Statistiche Spese pie
**Then** the "non identificato" Movimento appears under its "non identificato" Categoria like any other Categoria (it is reportable, not hidden) and is included in Spesa media mensile

**Given** the Drift is exactly 0 cents
**When** the Utente confirms
**Then** no plug Movimento is created (nothing to close); the Riconciliazione is still recorded and the timer resets

**Given** the plug Movimento creation fails (e.g. server/network error) after the Utente taps "close the gap"
**When** the error is returned
**Then** any optimistic UI update (closed-gap state) is rolled back, the original Drift is shown again in warm amber, no partial Riconciliazione is committed, and a plain warm retry message is surfaced (financial data is never silently dropped)

### Story 4.5: Acknowledge and leave the Drift open (resets timer, gap stays visible) (FR-18)
As an Utente,
I want to confirm reality without adjusting and leave the Drift open,
So that I reset the reminder when I'm not ready to attribute the gap, while mynance still honestly shows the gap until I close it.

**Acceptance Criteria:**

**Given** a confirmed non-zero Drift during the Riconciliazione flow
**When** the Utente chooses "acknowledge and leave open"
**Then** no Movimento is created and computed Liquidità is unchanged
**And** the last `data_riconciliazione` is set to today (the reminder timer resets) and a Riconciliazione is recorded with `esito = acknowledged_open`, snapshotting the open `drift_cents`

**Given** an acknowledged-but-open Drift exists and the configured interval has not yet elapsed
**When** the Utente loads any screen
**Then** the reconciliation-due banner does NOT fire (timer was reset), but the open Drift stays visible as a quiet warm-amber indicator (not a "due" banner), per the honesty principle (UX-DR8)
**And** the indicator persists across sessions until the gap is closed

**Given** an acknowledged-open Drift indicator is showing
**When** the Utente later closes that gap (via Story 4.4) in a subsequent reconciliation
**Then** the open-Drift indicator clears, and the next reconciliation reminder is governed only by `today − last Riconciliazione` and the interval

**Given** the open-Drift indicator and a due-reminder could both be relevant over time
**When** both conditions are evaluated on read
**Then** they are distinguishable: the open Drift is a standing quiet indicator of magnitude/sign, while the "due" banner is gated strictly by the interval (SM-C2 over-prompting is respected — acknowledging does not re-nag before the interval)

**Given** Utente A acknowledges an open Drift
**When** the open-Drift indicator is requested
**Then** it is derived only from A's own latest Riconciliazione and subsequent Movimenti; another Utente's open Drift is never surfaced to A (per-Utente isolation)

### Story 4.6: Riconciliazione flow UI and reconciliation history (UX-DR8)
As an Utente,
I want a calm, warm reconciliation screen and a record of past Riconciliazioni,
So that reconciling feels honest and non-alarming, and I can review how my Drift has trended over time.

**Acceptance Criteria:**

**Given** the Utente taps the `honesty-banner` or opens Altro → Riconciliazione
**When** the Riconciliazione flow opens
**Then** it presents, in order: the computed **Liquidità calcolata**, the real-Liquidità input (€, Italian decimal comma), the live **Drift** in € and %, and two clear resolution actions — "close the gap" (Story 4.4) and "acknowledge and leave open" (Story 4.5) — all in the warm/calm register, honesty figures in `{color.honesty}`, never alarm-red, never modal-blocking (UX-DR8)

**Given** the Utente confirms a Riconciliazione (either resolution)
**When** the action succeeds
**Then** a quiet confirmation is shown, the flow returns to where the Utente came from, the now-reset reminder no longer shows a "due" banner, and any closed gap is reflected immediately in derived Liquidità

**Given** the Utente has past Riconciliazioni
**When** they open the reconciliation history (richer on desktop per the responsive spine)
**Then** each entry shows its `data_riconciliazione`, the snapshot Liquidità reale and calcolata, the Drift in € and %, and the esito (`chiusa` vs `acknowledged_open`), sorted most-recent first and paginated

**Given** the Utente has never reconciled
**When** the history is opened
**Then** a calm empty-state message is shown (no fabricated rows), and the flow still offers a first reconciliation

**Given** a save action is in flight on the reconciliation screen
**When** the request fails
**Then** any optimistic state is rolled back, the prior Drift/figures are restored, and a single plain warm retry message is shown — raw errors are never exposed and financial data is never silently dropped

**Given** Utente A opens the reconciliation history
**When** the list is fetched
**Then** only A's own Riconciliazioni are returned (scoped by `utente_id`); requesting another Utente's history or entry by id returns 404/403

## Epic 5: My whole net worth (Patrimonio)

This epic lets an Utente census their entire net worth on their own valuation terms, beyond derived Liquidità: Investimenti (PAC) tracked at Capitale versato (contributed capital, never market value) with each Versamento PAC reducing Liquidità (FR-19), Beni immobili held static at the price paid (FR-20), and Beni mobili decayed by a simple linear Svalutazione floored at zero with suggested per-type defaults (FR-21). It culminates in the Patrimonio screen (UX-DR7) that sums Liquidità + Capitale versato totale + Σ Valore beni immobili + Σ Valore beni mobili into one total the Utente believes, with a per-component breakdown — and it enforces that asset registration is independent of cash so a purchase is never auto-deducted nor double-counted (FR-22). It builds on the derived Liquidità engine and per-Utente authZ from earlier epics; recurring (auto-generated) Versamenti PAC are handled later in Epic 6 (Regole ricorrenti), keeping Epic 5 standalone with manual Versamenti PAC.

### Story 5.1: Create an Investimento and record Versamenti PAC at Capitale versato (FR-19)

As an Utente,
I want to create an Investimento and record manual Versamenti PAC against it,
So that I can track my recurring investing at the contributed capital I put in, without any market-value noise.

**Acceptance Criteria:**

**Given** I am an authenticated Utente
**When** I create an Investimento with a name
**Then** an `investimenti` row is persisted scoped to my `utente_id` (UUID PK, soft-delete columns, created_at/updated_at)
**And** its value is derived as `Σ Versamenti PAC` (Capitale versato) and starts at 0 cents with no Versamenti
**And** no field for market value, price, or quote is ever requested, stored, or returned by the API.

**Given** an existing Investimento I own
**When** I record a Versamento PAC with an amount and a date
**Then** a `versamenti_pac` row is persisted in integer cents (`importo_cents` BIGINT, never float) linked to that Investimento and scoped to my `utente_id`
**And** the Investimento's Capitale versato increases by exactly that amount on the next derived-on-read computation
**And** my computed Liquidità decreases by the same Versamento amount per FR-13 (`Liquidità = Liquidità iniziale + Σ Entrate − Σ Spese − Σ Capitale versato`).

**Given** a Versamento PAC I recorded
**When** I edit its amount or date, or soft-delete it
**Then** both the Investimento's Capitale versato and my computed Liquidità recompute consistently from stored inputs (derived-on-read, no stale value).

**Given** a Versamento PAC amount of zero or negative cents
**When** I attempt to save it
**Then** the API rejects it with a `422 application/problem+json` validation error and nothing is persisted.

**Given** an Investimento or Versamento PAC owned by a different Utente
**When** I request, edit, or delete it by id
**Then** the API returns 404/403 and never the other Utente's data.

### Story 5.2: Register a Bene immobile at price paid (FR-20)

As an Utente,
I want to register a property valued at the price I paid,
So that my net worth reflects my real properties without any automatic market estimate I don't trust.

**Acceptance Criteria:**

**Given** I am an authenticated Utente
**When** I register a Bene immobile with a name and a price paid
**Then** a `beni_immobili` row is persisted scoped to my `utente_id` with `prezzo_cents` (BIGINT integer cents, never float), UUID PK, and soft-delete columns
**And** its Valore is static at the price paid, with no automatic market estimate ever requested, computed, or returned.

**Given** a Bene immobile I own
**When** I edit its price paid or soft-delete it
**Then** the stored value updates and the Patrimonio total recomputes accordingly on read.

**Given** I register a Bene immobile
**When** the registration is saved
**Then** my computed Liquidità is NOT changed by the registration itself (FR-22) — the UI must not imply a cash deduction; recording the purchase as a Spesa is a separate explicit choice.

**Given** a Bene immobile owned by a different Utente
**When** I request, edit, or delete it by id
**Then** the API returns 404/403 and never the other Utente's data.

### Story 5.3: Register a Bene mobile with linear Svalutazione and suggested rates (FR-21)

As an Utente,
I want to register a depreciating movable asset with a suggested-but-overridable annual Svalutazione,
So that its current value reflects how a car or motorcycle actually loses worth over time, honestly floored at zero.

**Acceptance Criteria:**

**Given** I am an authenticated Utente
**When** I register a Bene mobile with a name, purchase price, purchase date, and a Svalutazione percentage
**Then** a `beni_mobili` row is persisted scoped to my `utente_id` with `prezzo_cents` (BIGINT integer cents), purchase date, and the Svalutazione rate.

**Given** I am choosing the Svalutazione for an asset type
**When** I pick a known type (e.g. car, motorcycle)
**Then** a suggested default rate is offered (car ≈ 15–20%/yr, motorcycle ≈ 8–12%/yr) and is fully editable; my override is what gets persisted.

**Given** a Bene mobile with purchase price `prezzo`, Svalutazione `s`, and purchase date
**When** its current Valore is computed derived-on-read
**Then** `Valore = max(0, prezzo_cents × (1 − s × anni_trascorsi))` (linear/straight-line) in integer cents with centralized rounding
**And** `anni_trascorsi` is the fractional time in years from purchase date to today (not rounded to whole years)
**And** once `s × anni_trascorsi ≥ 1` the Valore is floored at exactly 0 cents and never goes negative.

**Given** I register a Bene mobile
**When** the registration is saved
**Then** my computed Liquidità is NOT changed by the registration itself (FR-22).

**Given** a Bene mobile owned by a different Utente
**When** I request, edit, or delete it by id
**Then** the API returns 404/403 and never the other Utente's data.

### Story 5.4: Patrimonio screen — total net worth and per-component breakdown (FR-22, UX-DR7)

As an Utente,
I want a Patrimonio screen showing my total net worth and each component,
So that at year-end I see Liquidità, invested capital, properties, and depreciating goods summed into one number I believe.

**Acceptance Criteria:**

**Given** I have Liquidità, Investimenti, Beni immobili, and Beni mobili
**When** I open the Patrimonio screen under Altro
**Then** a `balance-block` shows total `Patrimonio = Liquidità + Capitale versato totale + Σ Valore beni immobili + Σ Valore beni mobili`, computed server-side in integer cents and formatted only at the display layer (`€ 1.234,56`, Italian locale)
**And** a `card` per component is shown: Liquidità (linking to the Liquidità screen), Investimenti (each at Capitale versato — never market value), Beni immobili (price paid, static), Beni mobili (current depreciated value).

**Given** the Patrimonio total and components are derived
**When** I add/edit/delete any underlying input (a Versamento PAC, a Bene immobile/mobile, or any Movimento affecting Liquidità)
**Then** the affected TanStack Query keys are invalidated and the Patrimonio recomputes on re-fetch (derived-on-read), never showing a stale total.

**Given** I record a Versamento PAC
**When** the Patrimonio is recomputed
**Then** Liquidità falls by the amount and Capitale versato totale rises by the same amount, leaving total Patrimonio unchanged (intentional reallocation offset, FR-22) — not a double-count.

**Given** I register a Bene immobile or Bene mobile
**When** the Patrimonio is recomputed
**Then** the asset's Valore is added to total Patrimonio while Liquidità is unchanged by the registration alone (no auto-deduct); a separately recorded purchase Spesa is the only thing that lowers Liquidità, so a purchase is never double-counted (FR-22)
**And** the screen UI never implies that registering an asset deducts cash.

**Given** my Liquidità is negative (derived from flows)
**When** the Patrimonio total is computed
**Then** the negative Liquidità is surfaced with its sign and summed into Patrimonio honestly, never clamped or hidden.

**Given** the Patrimonio data is loading or a derived value is stale (e.g. connection dropped)
**When** the screen renders
**Then** it shows a skeleton/quiet "dati non aggiornati" note with retry rather than a confidently wrong total.

**Given** another Utente's Patrimonio
**When** I attempt to access it
**Then** every component query is scoped by my `utente_id` and cross-Utente access returns 404/403, never their data.

## Epic 6: Automate recurring money (Regole ricorrenti)

Recurring money — monthly salary Entrate, scheduled Versamenti PAC — is the predictable part of an Utente's finances and the single biggest source of repetitive manual entry (counter-metric SM-C1). This epic lets an Utente define a Regola ricorrente (amount in integer cents, Periodicità, day-of-period) that auto-generates the matching Entrate or Versamenti PAC up to today only — never future-dated phantom items — using lazy, idempotent generation triggered on access (no scheduler, per AR-Regole-Lazy / architecture gap-analysis). Each generated Movimento or Versamento is a normal materialized record the Utente can edit or skip independently of the rule, and skipping never manufactures a Drift. The epic delivers the RegolaRicorrente model and CRUD, the generation engine for both Entrate and Versamenti PAC, the skip/edit semantics, and the Impostazioni → Regole ricorrenti management UI (UX-DR9), all fulfilling FR-8. It depends on Entrate existing (Epic 2) and Versamenti PAC existing (Epic 5).

### Story 6.1: Create the RegolaRicorrente model and CRUD endpoints (FR-8)

As an Utente,
I want to define and manage rules that describe my recurring money (amount, Periodicità, day-of-period, target kind),
So that mynance knows what to auto-generate and I never have to type predictable Entrate or Versamenti PAC by hand.

**Acceptance Criteria:**

**Given** the migration for this story has run
**When** the schema is inspected
**Then** a `regole_ricorrenti` table exists with `id` (UUID PK), `utente_id` (FK, indexed), an `importo_cents` BIGINT (integer minor units, never float), a `periodicita` (monthly, quarterly, semiannual, annual, or custom interval in months — same vocabulary as Periodicità), a `day_of_period` integer, a `kind` discriminator restricted to `entrata` or `versamento_pac`, a nullable `categoria_id` (required when `kind = entrata`, referencing an Entrata-type Categoria), a nullable `investimento_id` (required when `kind = versamento_pac`), a `start_date`, optional `note`, and `created_at` / `updated_at` / `deleted_at` (soft-delete) columns, with index `ix_regole_ricorrenti_utente_id`.

**Given** an authenticated Utente
**When** they POST a Regola ricorrente with a valid `importo_cents`, `periodicita`, `day_of_period`, `kind = entrata`, and an Entrata-type Categoria they own
**Then** the Regola is persisted scoped to their `utente_id` and returned as the resource object directly (no `{data}` wrapper) with money as integer `*_cents`.

**Given** an authenticated Utente
**When** they POST a Regola with `kind = versamento_pac` referencing one of their own Investimenti
**Then** the Regola is created and linked to that Investimento via `investimento_id`.

**Given** a create request whose `kind = entrata` references an Entrata-type Categoria
**When** validated, but the referenced Categoria is a Spesa-type Categoria (wrong type) or `categoria_id` is missing
**Then** the request is rejected with `422` `application/problem+json` and no Regola is created.

**Given** a create request with a non-positive `importo_cents`, or a `day_of_period` outside the valid range for the chosen Periodicità (e.g. day 0 or day 32 for monthly)
**When** validated
**Then** it is rejected with `422` problem+json and no row is written.

**Given** Utente A owns a Regola
**When** Utente B issues GET / PUT / DELETE on that Regola's id
**Then** the response is `404` (not-found, never the data), enforced by the user-scoped repository.

**Given** an Utente edits a Regola's `importo_cents`, `periodicita`, `day_of_period`, or target
**When** they PUT the change
**Then** the Regola row is updated and `updated_at` advances; previously generated items are NOT retroactively rewritten by the edit (their independence is verified in Story 6.4).

**Given** an Utente lists their Regole
**When** they GET the collection
**Then** only their own non-soft-deleted Regole are returned as `{items, total, limit, offset}`, each scoped to their `utente_id`.

### Story 6.2: Lazy idempotent generation of recurring Entrate up-to-today (FR-8, AR-Regole-Lazy)

As an Utente,
I want each income Regola to auto-create the Entrate it owes me whenever I open mynance, but only up to today,
So that my recurring income appears without manual entry and my Liquidità only ever reflects money that has actually arrived.

**Acceptance Criteria:**

**Given** an `entrata` Regola with `start_date` in the past and no items yet generated
**When** the generation service runs on access (e.g. on login or when the relevant period / Movimenti list is read — no scheduler exists)
**Then** one materialized Entrata Movimento is created for every due occurrence with date ≤ today, each a normal Entrata carrying the Regola's `importo_cents`, the Regola's Categoria, the computed occurrence date, and a back-reference to the originating Regola.

**Given** a Regola whose next due occurrence date is strictly after today
**When** generation runs
**Then** no Entrata is materialized for that future occurrence (generation horizon is up-to-today only; no projected / phantom future Movimenti), so Liquidità reflects only money that has actually moved.

**Given** generation has already created the Entrate for a Regola up to today
**When** generation runs again on a subsequent access on the same day
**Then** it is idempotent — no duplicate Entrate are created (occurrences already materialized for that Regola+date are detected and skipped).

**Given** a Regola with `periodicita = monthly` and `day_of_period = 31`
**When** an occurrence falls in a month with fewer days (e.g. February)
**Then** the occurrence date is clamped to the last valid day of that period deterministically (the same input always yields the same date), and exactly one Entrata is generated for it.

**Given** a custom-interval-in-months Periodicità (e.g. every 2 months)
**When** generation runs from `start_date` to today
**Then** occurrences are spaced by that interval and only those with date ≤ today are materialized.

**Given** an Utente accesses mynance after several elapsed periods with no prior generation
**When** generation runs once
**Then** all owed past occurrences up to today are back-filled in chronological order, and the resulting Entrate immediately participate in derived-on-read Liquidità (recomputed on read, not via a scheduled write).

**Given** generation runs for an Utente
**When** it executes
**Then** it only ever reads and writes that Utente's own Regole and Movimenti (scoped by `utente_id`), never another Utente's data.

### Story 6.3: Extend generation to Versamenti PAC (FR-8)

As an Utente,
I want a PAC Regola to auto-create my scheduled Versamenti PAC up to today,
So that my recurring investment contributions are tracked without manual entry and feed Capitale versato and Liquidità correctly.

**Acceptance Criteria:**

**Given** a `versamento_pac` Regola linked to an Investimento the Utente owns
**When** the same lazy idempotent generation runs on access
**Then** one Versamento PAC is materialized for every due occurrence with date ≤ today, each carrying the Regola's `importo_cents`, linked to the Regola's Investimento, with a back-reference to the originating Regola.

**Given** a PAC Regola has already generated its Versamenti up to today
**When** generation runs again
**Then** it is idempotent — no duplicate Versamenti PAC are created.

**Given** newly generated Versamenti PAC exist
**When** Liquidità and Patrimonio are computed on read
**Then** each generated Versamento PAC reduces computed Liquidità (FR-19) and raises Capitale versato totale by the same amount, leaving total Patrimonio unchanged (the intentional reallocation offset, not a double-count).

**Given** a single access by an Utente who owns both `entrata` and `versamento_pac` Regole
**When** generation runs
**Then** both kinds are generated in one pass, each routed to its correct target (Entrata Movimento vs Versamento PAC), and no future-dated occurrence of either kind is created.

**Given** a `versamento_pac` Regola whose linked Investimento has since been soft-deleted
**When** generation runs
**Then** no Versamento PAC is generated for that Regola and no orphaned record is created (the run does not error out for the Utente's other Regole).

### Story 6.4: Make generated items editable and skippable without affecting the rule, and without creating Drift (FR-8)

As an Utente,
I want to edit or skip any single generated Entrata or Versamento PAC independently of its Regola,
So that I can correct a one-off amount or omit a missed occurrence without breaking the rule and without producing a false Drift.

**Acceptance Criteria:**

**Given** a materialized item (Entrata or Versamento PAC) created by a Regola
**When** the Utente edits its amount, date, or (for an Entrata) its Categoria
**Then** the change is saved on that single item only; the Regola is unchanged, and future generation continues from the Regola's own definition.

**Given** a generated item edited optimistically in the UI
**When** the save request fails
**Then** the optimistic update is rolled back to the previous state and the error is surfaced (the affected TanStack Query keys — e.g. `movimenti` + `liquidita`, or PAC + `liquidita` + `patrimonio` — are reconciled to server truth).

**Given** an Utente skips a generated item
**When** the skip is recorded
**Then** that occurrence is marked skipped (the materialized record is removed or flagged as skipped) and it no longer contributes to Liquidità / Capitale versato.

**Given** an occurrence has been skipped
**When** generation runs again on a later access
**Then** the skipped occurrence is NOT re-materialized (skip is remembered idempotently), while subsequent due occurrences of the same Regola are still generated normally.

**Given** an Utente skips a generated Entrata or Versamento PAC
**When** Drift is computed on read
**Then** skipping does not by itself generate a Drift (FR-8 consequence): the skipped occurrence simply never moved money, so computed Liquidità stays consistent with reality.

**Given** an Utente edits or skips a generated item
**When** the Regola is later inspected or used for the next generation pass
**Then** the Regola's `importo_cents`, `periodicita`, `day_of_period`, and target are exactly as defined (an item-level edit/skip never mutates the rule).

**Given** Utente A owns a generated item
**When** Utente B attempts to edit or skip it
**Then** the response is `404`, enforced by user-scoped access.

### Story 6.5: Regole ricorrenti settings UI (UX-DR9, FR-8)

As an Utente,
I want a Regole ricorrenti management surface under Impostazioni where I create, edit, and review my rules,
So that I can set up automation for anything predictable and reduce my entry burden (SM-C1).

**Acceptance Criteria:**

**Given** the Utente opens Impostazioni → Regole ricorrenti
**When** the screen renders
**Then** their Regole are shown as `list-row` items (per UX component rules), each showing the amount formatted `€ 1.234,56` (Italian locale, formatted at the display layer only — never localized money from the API), the Periodicità, the day-of-period, and the target (Entrata Categoria or Investimento for a Versamento PAC).

**Given** the Utente taps to create a Regola
**When** the form opens
**Then** they can enter amount, choose Periodicità, set day-of-period, and choose the kind (auto-generate Entrate or Versamenti PAC) with the corresponding target (Entrata-type Categoria, or an Investimento) — matching the Impostazioni → Regole spec (UX-DR9).

**Given** the create/edit form
**When** the Utente enters money via the keypad
**Then** the amount uses the decimal comma `,` (Italian convention) in the UI and is sent to the API as integer `*_cents`.

**Given** the Regole list and detail
**When** the screen is shown
**Then** copy reflects that generated items are auto-created up to today only (no future/phantom items) and are editable and skippable, with skipping stated as not creating a Drift — in calm, honest microcopy (never nagging), consistent with the voice/tone rules.

**Given** the Utente saves a new or edited Regola
**When** the mutation succeeds
**Then** the Regole list updates (its TanStack Query key is invalidated) and the save is confirmed via the standard toast.

**Given** the Utente saves a Regola and the request fails
**When** the error returns
**Then** the optimistic change is rolled back and the error is surfaced inline / via the single toast pattern, leaving the previously persisted Regole intact.

**Given** the desktop layout
**When** the Utente opens Regole ricorrenti
**Then** the management surface renders richer / more comfortably editable than on mobile (per the responsive Impostazioni behavior), while remaining reachable on mobile.

**Given** an empty state (no Regole yet)
**When** the screen renders
**Then** it invites the Utente to set up a Regola for anything predictable (steering toward automation per UX-DR9 / SM-C1), without manufacturing engagement pressure (no streaks, no gamification).
