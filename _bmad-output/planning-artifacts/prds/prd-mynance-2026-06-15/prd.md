---
title: mynance
status: final
created: 2026-06-15
updated: 2026-06-15
---

# PRD: mynance
*Working title — confirm.*

## 0. Document Purpose

This PRD is for the builder of mynance (acting as PM, architect, and developer) and any future contributor or downstream workflow (UX, architecture, epics). It builds directly on `brief-mynance-2026-06-12/brief.md` and does not duplicate it — the brief carries the strategic "why"; this document specifies the product's capabilities so they can be designed and built. It is structured around a Glossary that fixes the domain vocabulary (Italian domain terms kept verbatim — *Secchiello*, *Liquidità*, etc.), with features grouped and Functional Requirements (FRs) nested and globally numbered. Decisions taken during drafting and finalize are recorded in §8 (Resolved Decisions); items carried to downstream workflows are listed in §9 (Deferred Items). Technical "how" (stack, transport, schema) is intentionally excluded and routed to `addendum.md` / downstream architecture.

## 1. Vision

mynance answers one question that mainstream personal-finance apps answer badly: *of everything I have, how much is already committed, how much is free savings, and how much am I investing?* It is built on a deliberate mental model — **accumulate before you spend** — and on the conviction that for someone who runs multiple real accounts and moves money between them, manual entry plus an honest drift-correction mechanism beats automatic bank aggregation that inflates volumes and quietly lies.

The product organizes financial life around three pillars plus a net-worth view, tied together by a single idea: always know how every euro is allocated. Money for known recurring expenses is set aside *in advance* through predictive amortization buckets (*Secchielli*); liquidity is always split into the part already committed and the part that is genuinely free; and because there is no bank link to keep the books honest, mynance actively chases **drift** — periodically prompting the user to confirm reality and reconcile the gap.

mynance is free, tailored, and Italian-context-native by design — born from its author's own need, but engineered from day one as a multi-user SaaS on a frontend-agnostic API. V1 ships the web frontend; native apps follow later on the same core. Success is not feature parity with YNAB or Monarch; it is being a tool the author (and people like him) actually keep using, and trust, month after month.

## 2. Target User

### 2.1 Jobs To Be Done

- **Functional — "Set aside before I spend."** Pre-fund known recurring costs (insurance, road tax, taxes) so they arrive already covered, never as a shock.
- **Functional — "Tell me what's actually free."** At any moment, distinguish committed liquidity, free savings, and the state of my safety buffer, without doing math by hand.
- **Functional — "Don't let me lie to myself."** Catch the divergence that builds up when I forget to log expenses, and give me an honest way to close it.
- **Functional — "Show me my whole net worth on my terms."** Liquidity, invested capital, properties, and depreciating movable goods, valued the way I think about them (contributed capital, price paid, simple depreciation).
- **Emotional — control and clarity over automation.** I am technically capable and willing to type entries manually in exchange for a model that mirrors how I actually reason about money.
- **"This is for me, the builder"** — a free tool that does things my way, with no subscription and no imposed model.

### 2.2 Non-Users (v1)

- People who want fully automatic, zero-effort tracking via bank aggregation. mynance is deliberately manual — that audience will be disappointed.
- People who think in terms of "accounts" and balances per account. mynance has no account concept by design.
- Users needing expense-splitting / social finance (Splitwise-style).
- Users needing live market valuation of their investment portfolio or property.

### 2.3 Key User Journeys

The product is primarily a single-operator tool per user; journeys are scoped accordingly (no multi-stakeholder handoffs). Personas are the builder ("Marco") and a like-minded non-technical adopter ("Elena").

- **UJ-1. Marco sets aside for the car insurance he already knows is coming.**
  - **Persona + context:** Marco, methodical, runs three real bank accounts, wants known costs pre-funded. Authenticated, on web.
  - **Path:** opens mynance → creates a *Secchiello* "Assicurazione auto" with last paid amount €620 and next due date in 8 months → mynance computes the monthly *Quota* and starts crediting it virtually each month.
  - **Climax:** the *Liquidità* view now shows part of his savings as **allocated** to that *Secchiello* and the rest as **free** — he sees, concretely, that €620 of his money is already spoken for.
  - **Resolution:** when the insurance is paid he logs a *Spesa* linked to the *Secchiello*; the leftover balance carries over and lowers next year's *Quota*.

- **UJ-2. Marco reconciles after a forgetful fortnight.**
  - **Persona + context:** Marco hasn't logged a few small expenses in two weeks. Authenticated, on web.
  - **Path:** on opening mynance an in-app reminder tells him it's time to confirm real liquidity → he checks his actual bank balances, types the real total → mynance shows the divergence vs its computed *Liquidità* (e.g. −€87).
  - **Climax:** he closes the gap with one action — a *"non identificato"* *Spesa* of €87 — and the books are honest again.
  - **Resolution:** the reconciliation timestamp resets; the drift reminder won't fire again until the next interval.

- **UJ-3. Elena understands, for the first time, how much is really free.**
  - **Persona + context:** Elena, non-technical but shares the accumulate-first philosophy. New self-service account.
  - **Path:** registers (username + password) → sets her initial *Liquidità* → logs her monthly income rule and a few *Spese* → adds two *Secchielli*.
  - **Climax:** the allocation view answers her question — committed vs free vs the safety-buffer status (is free saving above 6 months of expenses?) — at a glance.
  - **Resolution:** she returns weekly, nudged by the in-app reminder, and the numbers stay trustworthy.

- **UJ-4. Marco reviews his whole net worth at year-end.** *(lighter)*
  Marco, planning for the year, opens the *Patrimonio* view and sees liquidity + invested capital (contributed, not market) + properties (price paid) + movable goods (auto-depreciated) summed into one total he believes.

## 3. Glossary

*Downstream workflows and readers must use these terms exactly. FRs, UJs, and SMs use these terms verbatim; introducing a synonym is a discipline violation.*

- **Utente** — An authenticated person with an isolated dataset. Self-registers with username + password. Owns all entities below; no data is shared between Utenti.
- **Movimento** — A real cash flow recorded manually by the Utente. Two kinds: *Spesa* and *Entrata*. Internal transfers between the Utente's own accounts are never recorded.
- **Spesa** — An outflow Movimento, categorized with a Spesa-type *Categoria*, optionally linked to one *Secchiello* (the link may be inherited from its *Categoria* and overridden per-Spesa). May be of special type *"non identificato"*.
- **Entrata** — An inflow Movimento, typically monthly, optionally generated by a *Regola ricorrente*; categorized with an Entrata-type *Categoria*.
- **Categoria** — A free-form label grouping Movimenti, **typed** as either Spesa or Entrata — the two spaces are distinct at the data-model level (not merely a UI filter). User-defined; a starter set is suggested per type. A Spesa-type Categoria may be linked to one *Secchiello* to default the Secchiello attribution of its Spese.
- **Regola ricorrente** — A rule (amount, cadence, day) that auto-generates *Entrata* Movimenti or *Versamento PAC* entries; generated items are editable and skippable.
- **Secchiello** *(amortization bucket)* — A virtual accumulation envelope for one known recurring expense. Holds a *Saldo*, a *Quota* (monthly), an *Importo previsto*, a *Periodicità*, and a *Prossima scadenza*. The money is virtual — no real cash moves into it.
- **Quota** — The monthly amount mynance recommends setting aside into a *Secchiello*, auto-computed (see FR-9). Not a real transfer; a virtual allocation.
- **Importo previsto** — The expected next payment for a *Secchiello*: the last amount actually paid, or the Utente's estimate on first setup.
- **Saldo (del Secchiello)** — The accumulated virtual balance of a *Secchiello*. May go negative (under-funding), which is surfaced, not hidden. *Carryover* is the *Saldo* that remains after a payment and carries into the next cycle.
- **Periodicità** — A *Secchiello*'s recurrence: monthly, quarterly, semiannual, annual, or custom interval in months.
- **Prossima scadenza** — The date of a *Secchiello*'s next expected payment.
- **Liquidità** — Derived spendable money. `Liquidità = Liquidità iniziale + Σ Entrate − Σ Spese − Σ Capitale versato`. Set the initial value once; thereafter computed.
- **Liquidità iniziale** — The one-time starting liquidity value set by the Utente.
- **Liquidità allocata** — The portion of *Liquidità* committed to *Secchielli*: `Σ max(0, Saldo del Secchiello)`.
- **Risparmio libero** — `Liquidità − Liquidità allocata`. The genuinely uncommitted money.
- **Cuscinetto di sicurezza** *(safety buffer)* — A target floor for *Risparmio libero*: `N × Spesa media mensile`, default N = 6. mynance warns when *Risparmio libero* falls below it.
- **Spesa media mensile** — Average monthly *Spese* over a trailing window (default 6 months, configurable), used to size the *Cuscinetto di sicurezza*.
- **Drift** — The divergence between mynance's computed *Liquidità* and the Utente's actual observed liquidity.
- **Riconciliazione** — The act of confirming real liquidity and closing the *Drift*, optionally via a *"non identificato"* Movimento.
- **Patrimonio** *(net worth)* — `Liquidità + Capitale versato totale + Σ Valore beni immobili + Σ Valore beni mobili` (identical to FR-22).
- **Investimento / PAC** — A recurring investment plan, tracked at *Capitale versato* (contributed capital), not market value.
- **Capitale versato** — Total money contributed to an *Investimento*; the only investment figure mynance tracks.
- **Versamento PAC** — A single contribution to an *Investimento*, manual or generated by a *Regola ricorrente*; reduces *Liquidità*.
- **Bene immobile** — A property asset; its *Valore* is the price paid (static, no market estimate).
- **Bene mobile** — A movable asset (car, motorcycle…); its *Valore* is the purchase price decayed linearly by a *Svalutazione* (see FR-21).
- **Svalutazione** — A simple annual depreciation percentage applied linearly to a *Bene mobile* (see FR-21); suggested defaults provided, fully overridable.

## 4. Features

### 4.1 Account & Authentication

**Description:** Multi-user SaaS with open self-service registration using username + password. Each Utente's data is fully isolated. Authentication is intentionally simple — no 2FA, no social login in V1 (see §5). Password recovery is included so a self-service user is never locked out. Realizes UJ-3.

**Functional Requirements:**

#### FR-1: Self-service registration
An anonymous visitor can create an Utente account with a username and password.
**Consequences (testable):**
- A new account starts with an empty dataset and no Liquidità iniziale set.
- Usernames are unique; duplicate registration is rejected with a clear message.
- Passwords are stored only as a salted hash; the plaintext is never persisted or logged.

#### FR-2: Authentication & session
An Utente can log in with username + password and stays authenticated across a session.
**Consequences (testable):**
- Invalid credentials are rejected without revealing whether the username exists.
- A session expires after 30 days of inactivity (configurable per Utente) and can be ended by explicit logout.

#### FR-3: Password recovery
An Utente can recover access if they forget their password. Recovery uses a one-time **recovery code** issued at registration (the Utente saves it), not an email reset — there is no email infrastructure in V1 and notifications are in-app only (see §5).
**Consequences (testable):**
- Recovery never exposes the existing password.
- A failed recovery attempt does not reveal account existence.
- The recovery code is shown once at registration and stored only as a salted hash; it can be regenerated while authenticated.

#### FR-4: Data isolation
An Utente can read and write only their own data.
**Consequences (testable):**
- Any request for another Utente's entity returns not-found/forbidden, never the data.

**Feature-specific NFRs:** Auth is the security boundary for all financial data; treat authorization checks as mandatory on every entity access (see §10).

### 4.2 Movimenti — Expenses & Income

**Description:** The factual ledger. The Utente records real cash flows only — *Spese* and *Entrate* — and never internal transfers between their own accounts, which is what eliminates the inflated-volume problem at the root. *Spese* are categorized with Spesa-type *Categorie* and may be linked to one *Secchiello* (directly or inherited from the Categoria). *Entrate* are typically monthly and can be auto-generated from a *Regola ricorrente*. Realizes UJ-1, UJ-2, UJ-3.

**Functional Requirements:**

#### FR-5: Record a Spesa
An Utente can record a Spesa with amount, date, Categoria (a Spesa-type Categoria), optional note, and a link to one Secchiello. The Secchiello link defaults from the chosen Categoria when that Categoria is linked to a Secchiello (FR-7), and can be overridden — to a different Secchiello or to none — on the individual Spesa.
**Consequences (testable):**
- Choosing a Categoria that is linked to a Secchiello pre-fills the Spesa's Secchiello link; the Utente can override it per-Spesa.
- A Spesa linked to a Secchiello decrements that Secchiello's Saldo by the Spesa amount (see FR-10).
- A Spesa immediately affects computed Liquidità (FR-13).
- Spese can be edited and deleted; recomputed values update accordingly.

#### FR-6: Record an Entrata
An Utente can record an Entrata with amount, date, Categoria, and optional note.
**Consequences (testable):**
- An Entrata immediately increases computed Liquidità.

#### FR-7: Categorization (typed, user-defined) and Categoria→Secchiello link
An Utente can create, rename, and reuse Categorie; a starter set is suggested on a new account. Each Categoria is **typed** as either Spesa or Entrata — the two spaces are distinct at the data-model level, not merely filtered in the UI. A Spesa-type Categoria may optionally be linked to one Secchiello.
**Consequences (testable):**
- A Categoria belongs to exactly one type (Spesa or Entrata) and can only be applied to Movimenti of that type; the distinction is enforced in the backend, not just the UI.
- The starter set is suggested separately per type (Spesa categories and Entrata categories).
- A Spesa-type Categoria may be linked to at most one Secchiello; linking is optional and only some Spesa categories are linked. The link drives the default Secchiello attribution on new Spese (FR-5).
- Changing or removing a Categoria→Secchiello link affects only the default for future Spese; already-recorded Spese keep their own link.
- Deleting a Categoria in use prompts reassignment rather than silently orphaning Movimenti.

#### FR-8: Recurring income & contribution rules
An Utente can define a Regola ricorrente (amount, cadence — see Periodicità, day-of-period) that auto-generates Entrate or Versamenti PAC; generated items are editable and skippable.
**Consequences (testable):**
- Each generated item is materialized as a normal Movimento / Versamento that the Utente can edit or skip without affecting the rule.
- Skipping a generated item does not generate a Drift by itself.
- Generation horizon is **up to today**: a Regola materializes items only with date ≤ today, never future-dated ones, so Liquidità always reflects only money that has actually moved (no projected/phantom future Movimenti).

### 4.3 Secchielli — Predictive Amortization Buckets

**Description:** The signature feature, born from the author's mental model and rarely done well elsewhere. For each known recurring expense the Utente creates a *Secchiello*; mynance recommends a monthly *Quota* to set aside virtually (no real money moves), and the *Liquidità allocata* view reflects it. The *Secchiello* has **memory** (carryover lowers next cycle's *Quota*) and **honesty** (a negative *Saldo* from an over-optimistic forecast is shown, not hidden). Supports any *Periodicità* — annual is just one case. Realizes UJ-1, UJ-4.

**Functional Requirements:**

#### FR-9: Auto-computed Quota
mynance computes each Secchiello's recommended monthly Quota.
**Consequences (testable):**
- `Quota = max(0, (Importo previsto − Saldo) / mesi_alla_Prossima_scadenza)`, recomputed when inputs change.
- On first setup with no payment history, Importo previsto is the Utente's estimate.
- If Saldo ≥ Importo previsto, Quota is 0 (already funded).
- If Saldo is negative, Quota rises to recover the shortfall over the remaining months.

#### FR-10: Funding, payment, and carryover lifecycle
An Utente can fund a Secchiello over time and settle it at payment, with the leftover carried to the next cycle.
**Consequences (testable):**
- Each elapsed period credits the Quota to the Saldo as a virtual allocation. Crediting is monthly and virtual (it never moves Liquidità) and is computed **derived-on-read** from (start date, Quota history, linked Spese) rather than written by a scheduled job — deterministic, robust to back-dated edits, and free of a background scheduler (see §11 / architecture).
- The derived-on-read computation is evaluated **chronologically**: from the Secchiello's start date, each elapsed month credits that month's Quota (computed from the Saldo and months-remaining as of that month) and each linked Spesa is applied on its date. This sequential order makes Saldo and Quota deterministic despite their mutual dependence; the worked reference example is carried to architecture.
- Logging the linked Spesa (the actual payment) decrements Saldo by the actual amount; the resulting Saldo (positive or negative) becomes the carryover.
- After a payment, Importo previsto is updated to the actual amount paid (memory), and Prossima scadenza advances by the Periodicità.
- A negative Saldo is displayed as an explicit under-funding warning, never clamped to zero in the bucket's own view.

#### FR-11: Any periodicity
An Utente can set a Secchiello's Periodicità to monthly, quarterly, semiannual, annual, or a custom interval in months.
**Consequences (testable):**
- `mesi_alla_Prossima_scadenza = max(1, ceil((Prossima scadenza − today) / 30.44 days))`, derived from Prossima scadenza and today, independent of the Periodicità label. The `max(1, …)` floor means a due-or-overdue Secchiello surfaces its full outstanding `(Importo previsto − Saldo)` in a single Quota rather than dividing by zero or a negative — under-funding is never silently spread away (honesty principle).

**Notes:** Crediting model **decided: derived-on-read** — Saldo is computed from (start date, Quota history, linked Spese), not written by a scheduled job. Carried to architecture as a binding constraint.

### 4.4 Liquidità & Allocation View

**Description:** Liquidity is *derived*, never entered as a running balance: the Utente sets *Liquidità iniziale* once, and mynance computes the rest. The core payoff is the allocation view — at any moment, how much *Liquidità* is **allocated** (in *Secchielli*) vs **free**, and whether *Risparmio libero* sits above the *Cuscinetto di sicurezza* (default 6 months of expenses). Realizes UJ-1, UJ-3, UJ-4.

**Functional Requirements:**

#### FR-12: Set initial liquidity
An Utente can set Liquidità iniziale once.
**Consequences (testable):**
- Changing Liquidità iniziale later is possible but flagged as a re-baselining action (logged), since it shifts all derived figures.

#### FR-13: Derived liquidity
mynance computes current Liquidità from flows.
**Consequences (testable):**
- `Liquidità = Liquidità iniziale + Σ Entrate − Σ Spese − Σ Capitale versato`, recomputed on every relevant change.

#### FR-14: Allocation breakdown
An Utente can see Liquidità split into allocated and free.
**Consequences (testable):**
- `Liquidità allocata = Σ max(0, Saldo del Secchiello)`.
- `Risparmio libero = Liquidità − Liquidità allocata`.
- Both update live as Secchielli and Movimenti change.

#### FR-15: Safety-buffer warning
mynance warns when Risparmio libero falls below the Cuscinetto di sicurezza.
**Consequences (testable):**
- `Cuscinetto = N × Spesa media mensile`, default N = 6, N configurable.
- `Spesa media mensile` is the mean of Spese over the last N **complete** calendar months (the current partial month is excluded), N default 6 and configurable; if fewer complete months of history exist, it averages over those available.
- "non identificato" Spese **are included** in Spesa media mensile — they are real outflows, so they contribute to buffer sizing (honesty principle).
- The warning is a non-blocking in-app indicator, surfaced on access like the reconciliation reminder (FR-16).

### 4.5 Drift Detection & Reconciliation

**Description:** The honest, manual alternative to open banking — not a poor surrogate for it. Because mynance has no bank link, it actively chases the divergence (*Drift*) that accrues when the Utente forgets entries. A periodic **in-app** reminder invites the Utente to confirm real liquidity; mynance shows the divergence against its computed *Liquidità* and lets them close it, including via a *"non identificato"* Movimento when the missing flow can't be traced. Realizes UJ-2.

**Functional Requirements:**

#### FR-16: Periodic reconciliation reminder (in-app)
mynance reminds the Utente to reconcile after a configurable interval since the last Riconciliazione.
**Consequences (testable):**
- Default interval is weekly; configurable per Utente.
- The reminder is surfaced in-app on access (banner/indicator); there is no email or push in V1 (see §5).
- The reminder is computed from `today − last Riconciliazione date`; it does not require a background scheduler.

#### FR-17: Reconcile real liquidity
An Utente can enter their actual observed liquidity and see the Drift.
**Consequences (testable):**
- Drift = `Liquidità reale inserita − Liquidità calcolata`, shown with sign and magnitude.
- Confirming reality sets the last Riconciliazione date to today.

#### FR-18: Close the gap with a "non identificato" Movimento
An Utente can close a Drift by creating a "non identificato" Spesa (or Entrata) for the difference.
**Consequences (testable):**
- Creating the "non identificato" Movimento brings computed Liquidità to match the entered real figure.
- "non identificato" Movimenti are distinguishable and can be reported on separately, via a dedicated system Categoria "non identificato" provided in each Categoria type (Spesa and Entrata).
- The Utente may also choose to leave the Drift open (acknowledge without adjusting): acknowledging confirms reality and resets the last Riconciliazione date, while the gap stays visible as an indicator until it is closed (honesty principle).

### 4.6 Patrimonio — Net Worth

**Description:** Beyond liquidity, the Utente censuses the rest of their net worth on their own valuation terms: *Investimenti* tracked at *Capitale versato* (what was put in, not market value), *Beni immobili* at price paid, and *Beni mobili* depreciated by a simple annual *Svalutazione* with suggested defaults. The total *Patrimonio* sums all components. Realizes UJ-4.

**Functional Requirements:**

#### FR-19: Investimenti (PAC) at contributed capital
An Utente can create an Investimento and record Versamenti PAC (manual or via Regola ricorrente).
**Consequences (testable):**
- The Investimento's value equals Σ Versamenti PAC (Capitale versato); market value is never requested or shown.
- Each Versamento PAC reduces computed Liquidità (FR-13).

#### FR-20: Beni immobili at price paid
An Utente can register a Bene immobile valued at the price paid.
**Consequences (testable):**
- Value is static at price paid; no automatic market estimate (see §5).

#### FR-21: Beni mobili with depreciation
An Utente can register a Bene mobile with purchase price, purchase date, and a Svalutazione percentage; a default rate is suggested by asset type.
**Consequences (testable):**
- Current value = `max(0, prezzo × (1 − Svalutazione × anni_trascorsi))` — linear / straight-line depreciation, floored at 0 so the value never goes negative.
- `anni_trascorsi` is the fractional time in years from purchase date to today (not rounded to whole years).
- Suggested default Svalutazione rates are indicative and fully overridable — e.g. car ≈ 15–20%/yr, motorcycle ≈ 8–12%/yr.

#### FR-22: Net-worth total
An Utente can see total Patrimonio.
**Consequences (testable):**
- `Patrimonio = Liquidità + Capitale versato totale + Σ Valore beni immobili + Σ Valore beni mobili`.
- Registering a Bene immobile/mobile does not by itself deduct from Liquidità; recording the purchase as a Spesa (which does reduce Liquidità) is a separate, explicit choice by the Utente. Asset registration and cash flows are independent, so a purchase is never double-counted.
- A Versamento PAC reduces Liquidità (FR-19) and raises Capitale versato totale by the same amount, leaving total Patrimonio unchanged — an investment is a reallocation within net worth, not a loss. This offset is intentional, not a double-count.

## 5. Non-Goals (Explicit)

- **Not a bank-aggregation app.** No open banking, no automatic account linking, ever — this is the founding decision, not a missing feature.
- **No "account" concept and no internal-transfer tracking.** Only real external flows are recorded.
- **No expense-splitting / social finance** (Splitwise-style).
- **No live market valuation** of the investment portfolio (quotes) — investments are tracked at contributed capital only.
- **No automatic property market-value estimation** via external APIs in V1 (nice-to-have later, possibly as a note).
- **No advanced authentication** (2FA, social login) in V1.
- **No email / push notification infrastructure** in V1 — notifications are in-app only.
- **Not competing on feature count** with YNAB/Monarch, and not claiming a defensible technical moat.
- **Not a paid product.** Free; no monetization, no ads.

## 6. MVP Scope

### 6.1 In Scope
- Multi-user accounts, open self-service registration (username + password) with password recovery, full data isolation.
- Manual Spese and Entrate with user-defined, type-scoped categorization; recurring Entrate and Versamenti PAC via editable Regole ricorrenti.
- Secchielli: auto-computed Quota, any Periodicità, carryover/memory, honest negative-Saldo tracking, payment-linked settlement.
- Derived Liquidità with allocated / free breakdown and Cuscinetto di sicurezza warning (≥ 6 months).
- Drift detection: in-app periodic reminder, reconciliation, "non identificato" Movimento.
- Patrimonio: Liquidità + Investimenti (PAC at Capitale versato) + Beni immobili (price paid) + Beni mobili (depreciated).
- **Frontend-agnostic, documented backend API as the product core**, exposing the same logic/data to any client; **V1 delivers the web frontend**. Native apps follow on a separate track against the same contract (see §11).

### 6.2 Out of Scope for MVP
- Native mobile apps (separate development track, same project/core).
- Bank aggregation / open banking — permanent non-goal, not a deferral.
- Live investment market value — emotionally adjacent ("but is my PAC up?") but deliberately excluded to preserve the contributed-capital model; revisit post-V1 only if it can be added without corrupting the core view.
- Automatic property valuation via public services — deferred to v2+ as a possible note field.
- Advanced auth (2FA, social login) — deferred.
- Email/push notifications — deferred; gated on building notification infrastructure.

### 6.3 Direction beyond V1 (non-binding)
Captured from the brief to orient downstream thinking — not commitments:
- **Reduce manual entry** over time (e.g. movement import), without abandoning the manual-first, honest-by-design model.
- **Smarter allocation / buffer suggestions** building on the Cuscinetto and Secchielli data.
- **Optional property market-value estimate** via free public services (see §5 — only if it can be added without corrupting the contributed-capital / price-paid model).

## 7. Success Metrics

Stakes are personal-but-SaaS-quality, so metrics are usage-and-trust based, not market based.

**Primary**
- **SM-1 — Sustained real use.** The author still has mynance updated and trusts its numbers after 3+ months. Validates the product as a whole; depends on FR-5/6, FR-16–18.
- **SM-2 — Drift stays small.** Median reconciliation Drift stays within a low, acceptable threshold (e.g. ≤ a few % of Liquidità). Validates FR-16, FR-17, FR-18.
- **SM-3 — Allocation answer is always available.** The Utente can state allocated vs free vs buffer status without manual math at any time. Validates FR-14, FR-15.
- **SM-4 — Secchielli hold.** Known recurring expenses arrive already funded; over-runs are visible *before* the due date, not after. Validates FR-9, FR-10, FR-15.

**Secondary**
- **SM-5 — At least one other Utente** beyond the author adopts mynance and finds it useful. Validates FR-1, FR-2 (self-service onboarding).

**Counter-metrics (do not optimize)**
- **SM-C1 — Entry burden.** Do not drive "engagement" by increasing how much the Utente must type. Counterbalances SM-1: more manual logging is a cost, not a win; auto-generation rules (FR-8) exist to reduce it.
- **SM-C2 — Reminder frequency.** Do not maximize reconciliation reminders; over-prompting trains the Utente to dismiss them. Counterbalances SM-2.

## 8. Resolved Decisions

The questions raised during fast-path drafting were resolved at finalize (2026-06-15; full audit in `.decision-log.md`):

1. **Password recovery (FR-3)** — one-time recovery code issued at registration; no email reset.
2. **Secchiello crediting (FR-10)** — derived-on-read (computed from start date, Quota history, linked Spese); no scheduled write. Binding constraint for architecture.
3. **Beni mobili depreciation (FR-21)** — linear / straight-line, floored at 0: `max(0, prezzo × (1 − Svalutazione × anni))`.
4. **Spesa media mensile (FR-15)** — trailing window default 6 months (configurable); "non identificato" Spese are included.
5. **Categorie (FR-7)** — separate, backend-typed spaces for Spese and Entrate.
6. **Categoria→Secchiello link (FR-5 / FR-7)** — the link lives on the Spesa-type Categoria and defaults the Spesa's Secchiello attribution, overridable per-Spesa.
7. **Recurrence horizon (FR-8)** — generation up to today only; no future-dated / phantom items.
8. **Drift acknowledge-without-fix (FR-18)** — allowed; resets the reconciliation timer while leaving the gap visible.
9. **Session timeout (FR-2)** — 30 days idle, configurable.
10. **Currency** — EUR only in V1.

## 9. Deferred Items

Carried to downstream workflows; none blocks UX / architecture / epics planning.

- **Backup / retention policy** (§10) — owner: architecture; revisit during data-durability design.
- **Hosting model** (self-hosted / low-cost) (§12) — owner: architecture; revisit during infrastructure design.
- **Personal-but-SaaS-quality posture** (§2.3) — standing framing from the brief: V1 optimizes for the primary user; opening to others is real but secondary. No action.
- **Privacy policy text & account deletion (GDPR)** (§12) — owner: architecture / legal; revisit before any non-author Utente onboards. (Early-use data may be fictitious, per the brief.)

---

## 10. Cross-Cutting NFRs

- **Security & data isolation.** Every entity access is authorized against the owning Utente (FR-4). Passwords stored salted-hashed only. Financial data is sensitive personal data — treat accordingly even at personal scale.
- **Calculation correctness & determinism.** All derived figures (Liquidità, Quota, Saldo, allocated/free, Patrimonio, depreciation) must be deterministic and reproducible from stored inputs. The calculation engine is the heart of the product; it warrants dedicated tests against worked examples. Negative Saldo must never be silently clamped.
- **Single currency / Italian context.** EUR only in V1 (decided); Italian-context conventions (date formats, terminology).
- **Data durability & integrity.** No financial Movimento is lost silently; edits/deletes recompute consistently. Backup/retention specifics deferred to architecture (§9).
- **Performance.** Personal-scale data volumes; derived views should compute interactively (sub-second on a year+ of Movimenti).

## 11. API as Product Surface

mynance's backend is a **frontend-agnostic, documented API** that is the product's core, not an implementation detail of the web app. It exposes the full domain logic and data (auth, Movimenti, Secchielli with computed Quota/Saldo, derived Liquidità and allocation, Drift/Riconciliazione, Patrimonio) so that the V1 web frontend, future native apps, and even a hypothetical third-party client all consume the same contract.

- **API-1 — Contract independence.** No business logic lives only in the frontend; the API is complete and usable headless.
- **API-2 — Documentation.** The API is documented (machine-readable contract) and versioned so clients can depend on it across the web→native expansion.
- **API-3 — Same logic, all clients.** Derived values are computed server-side and returned via the API, never recomputed divergently per client.

*Transport, framework, schema, auth-token mechanics, and versioning specifics belong to architecture / `addendum.md`.*

## 12. Constraints & Guardrails

- **Privacy.** Personal financial data; minimize what's stored, no third-party data sharing, no analytics that exfiltrate financial detail.
- **Cost.** Built and run cheaply by the author; free to users. Architectural choices should respect a near-zero operating budget. Hosting model (self-hosted / low-cost) deferred to architecture (§9).
- **Honesty principle (product tone).** Where the system could hide an uncomfortable truth (negative Saldo, growing Drift, buffer breach), it must surface it plainly. This is a product value, not just a UX preference.
