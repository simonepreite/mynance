---
title: mynance — Experience (EXPERIENCE.md)
status: final
created: 2026-06-15
updated: 2026-06-15
sources:
  - {planning_artifacts}/prds/prd-mynance-2026-06-15/prd.md
  - .decision-log.md (24 entries — canonical UX decisions)
  - wireframes/home-mese.v2.md
  - wireframes/quick-add.v1.md
---

# mynance — Experience Spine

> How mynance behaves. `DESIGN.md` is the visual identity (the "Morbido" direction — pillowy cards, airy spacing, warm sage accent); this spine is the experience. Every visual token is referenced by name — `{color.*}`, `{type.*}`, `{radius.*}` — and never inlined. Italian domain terms (Secchiello, Liquidità, Quota, Saldo, Patrimonio…) and Italian UI microcopy are verbatim and load-bearing; they are the product's vocabulary, not translatable strings. The spine wins on any conflict with wireframes.

## Foundation

**Form-factor: mobile-first, adaptive / progressive disclosure** (decision #2, #7). The primary daily act is quick "al volo" capture of a *Spesa* on a phone, one-handed — every forgotten entry becomes *Drift*, so lowering capture friction directly serves the entry-burden counter-metric (SM-C1). The surface strategy is *adaptive*, not split: **everything is reachable everywhere**. Mobile prioritizes capture and at-a-glance summaries; detail and management screens (Categorie, Regole ricorrenti, Patrimonio editing, reconciliation history) are reachable but secondary on mobile, and become richer and more comfortably editable on desktop. Nothing is excluded from any surface (decision #7 supersedes the earlier open question #6).

**Design system: the mynance "Morbido" system** (decision #23, #24), defined in `DESIGN.md`. The register is calm, trustworthy, soft and "comfortable" — warm and welcoming, explicitly **not** bank-like or cold (decision #20). Very rounded cards (`{radius.card}`), airy spacing, a muted sage/teal accent (`{color.accent}`), large friendly sans (`{font.sans}`), and hero numbers carrying weight (`{type.display}`). Light and dark themes both ship; the default **follows the device/system setting** with a manual override (decision #21). Contrast must stay legible without going harsh — the warm palette is the point (decision #20, #22); see Accessibility Floor for how that tension is resolved.

**Guiding principle — allocation awareness is the north star.** The product's core payoff is that the Utente can *always know how every euro is allocated: committed vs free* — *Liquidità allocata* vs *Risparmio libero*. This is the answer mynance exists to give (UJ-1, UJ-3). It does **not** displace the calm month snapshot as the default Home (decision #12): the Home stays the clean period view, and the allocation answer lives on **Liquidità**. The experience's job is to make sure the Utente always knows that answer is one tap away.

**Regole ricorrenti are the primary entry-burden reducer** (counter-metric SM-C1). Beyond quick "al volo" capture, the biggest lever against entry burden is automation: a *Regola ricorrente* means recurring *Entrate* and *Versamenti PAC* are auto-generated rather than manually typed (FR-8). Less manual typing is the point — the spine should steer toward setting up Regole for anything predictable.

`DESIGN.md` owns color, type, radius, and component visual specs. This document owns behavior. Where a screen is not yet wireframed, its behavior here is derived strictly from the PRD's FRs and glossary.

## Information Architecture

Mobile bottom navigation (`bottom-nav`) — five destinations, the centre one a hero action (decision #9):

| Nav slot | Surface | PRD feature / FR | Purpose |
|---|---|---|---|
| 🏠 **Mese** | Home (period budget + Spese list) | §4.2, §4.4 (display); FR-13 | Default landing. Period-scoped Bilancio + Spese grouped by Categoria. |
| 📊 **Statistiche** | Charts only (line trends + period pie) | §4.2/§4.4 (read views) | Cross-period trends over time + a period category-share pie. **No lists** (decisions #17, #26). |
| ＋ **Aggiungi** | Quick-add bottom sheet (`bottom-sheet`) | FR-5, FR-6 | Central hero action. Capture a *Spesa* or *Entrata* al volo. |
| 💧 **Liquidità** | Allocation + Secchielli (two tabs) | FR-12, FR-14, FR-15; §4.3 | Allocata/libera + *Cuscinetto di sicurezza*, and the *Secchielli* list (decision #10). |
| ⋯ **Altro** | Patrimonio · Riconciliazione · Impostazioni | §4.5, §4.6, §4.1, FR-7, FR-8, FR-12 | Hub for net worth, reconciliation, and all management/settings. |

**Riconciliazione has no nav icon.** It lives under **Altro** as a destination *and* surfaces as a contextual `honesty-banner` wherever the Utente is when it comes due (decision #11; FR-16). The banner is the primary entry to the reconcile flow; the Altro entry is the deliberate/manual path.

Modal depth: the quick-add `bottom-sheet` is one level deep and dismissible by swipe-down (decision #18). Detail drill-downs (e.g. a Categoria's Spese list) push one level and return with Back. Never stack two modals.

→ Composition & visual references — **the spine wins on any conflict with a mock or wireframe:**
- Home "Mese": mockup [`mockups/direction-morbido.html`](mockups/direction-morbido.html), wireframe [`wireframes/home-mese.v2.md`](wireframes/home-mese.v2.md).
- Quick-add: wireframe [`wireframes/quick-add.v1.md`](wireframes/quick-add.v1.md).
- Liquidità: mockup [`mockups/mock-liquidita.html`](mockups/mock-liquidita.html).
- Statistiche: mockup [`mockups/mock-statistiche.html`](mockups/mock-statistiche.html).

### Screen-by-screen behavioral spine

Screens already wireframed (Home "Mese", quick-add) are detailed in their own sections below. The following are specified here at spine level, behavior **derived strictly from the PRD** — they are not yet wireframed.

**Liquidità — tab A: Allocazione** (FR-14, FR-15). A `balance-block` showing the answer to the product's core question (UJ-3 climax): *Liquidità* total, then the split into **Liquidità allocata** (`Σ max(0, Saldo del Secchiello)`) and **Risparmio libero** (`Liquidità − Liquidità allocata`), shown live. A `card` for the **Cuscinetto di sicurezza**: the target floor (`N × Spesa media mensile`, default N=6) and whether *Risparmio libero* sits above or below it. A breach renders in `{color.honesty}` (see State Patterns), never alarm-red. This split lives **only here**, never on the Home (decision #12).

**Liquidità — tab B: Secchielli** (§4.3; FR-9, FR-10, FR-11). A `list-row` per *Secchiello* with its `secchiello-badge`, current *Saldo*, recommended *Quota* (monthly), and *Prossima scadenza*. A negative *Saldo* is shown as an explicit under-funding warning in `{color.honesty}`, never clamped to zero (FR-10, honesty principle). Tap → detail: *Importo previsto*, *Periodicità*, *Quota* derivation, carryover, and the linked Spese history. Create/edit a *Secchiello* here (name, *Importo previsto* / last-paid amount, *Periodicità*, *Prossima scadenza*); *Quota* is auto-computed and read-only (FR-9). Create/edit of a Secchiello is a pushed full-screen form on mobile and an inline panel on desktop (decision #25, adaptive strategy #7).

**Statistiche** (decisions #17, #26). Charts only — no lists (the per-category list is Home's job). Two complementary layers: **cross-period trends** as line charts (Spese / Entrate / netto month-over-month; *Risparmio libero* vs *Cuscinetto di sicurezza* over time) and a **pie of the selected period's Spese share by Categoria**. The same `period-selector` as Home sets the reference period; Home is the single-period snapshot (list), Statistiche is how things move over time (charts).

**Patrimonio** (§4.6; FR-19–22; UJ-4). A `balance-block` for total *Patrimonio* (`Liquidità + Capitale versato totale + Σ Valore beni immobili + Σ Valore beni mobili`), then a `card` per component: *Liquidità* (links to the Liquidità screen), *Investimenti* (each at *Capitale versato* — never market value), *Beni immobili* (price paid, static), *Beni mobili* (current depreciated value, `max(0, prezzo × (1 − Svalutazione × anni))`). Management (add an *Investimento* and its *Versamenti PAC*, register a *Bene immobile/mobile*, set/override *Svalutazione*) is reachable on mobile but richer on desktop. Registering an asset never deducts *Liquidità* by itself (FR-22) — the UI must not imply it does.

**Riconciliazione flow** (§4.5; FR-16–18; UJ-2). Entered from the `honesty-banner` or from Altro. Steps: (1) prompt to enter actual observed liquidity; (2) show **Drift** = `Liquidità reale − Liquidità calcolata`, **both** as a signed € amount **and** as a **% of Liquidità** (SM-2 frames acceptable Drift as a small percentage, so the percentage is what tells the Utente whether the gap is small or worrying), in `{color.honesty}`; (3) offer to close the gap with a *"non identificato"* *Spesa* or *Entrata* for the difference (FR-18), **or** acknowledge-and-leave-open (FR-18 — resets the reconciliation timer, gap stays visible as an indicator). Confirming reality sets the last *Riconciliazione* date to today (FR-17). Respect SM-C2: the reminder fires only after the configured interval (default weekly), never more.

**Impostazioni** (under Altro). Houses all management surfaces, richer on desktop (decision #7):
- **Categorie** (FR-7) — create/rename/reuse, type-scoped (Spesa vs Entrata are distinct spaces, enforced backend-side; the UI presents two separate lists). A starter set is suggested per type on a new account. **Categoria → Secchiello link**: on a Spesa-type Categoria, optionally link one *Secchiello* to default the attribution of its Spese (FR-5, FR-7). Deleting an in-use Categoria prompts reassignment, never silent orphaning.
- **Regole ricorrenti** (FR-8) — define amount, cadence (*Periodicità*), day-of-period; auto-generate *Entrate* or *Versamenti PAC* up to today only (no future/phantom items). Generated items are editable and skippable; skipping does not create *Drift*.
- **Liquidità iniziale** (FR-12) — set once; changing it later is allowed but flagged as a logged re-baselining action.
- **Account & recovery** (FR-1, FR-2, FR-3) — username, password, session, theme override (decision #21), *Cuscinetto* N and *Spesa media mensile* window config (FR-15), reconciliation interval (FR-16). The one-time **recovery code** is shown once at registration with explicit "save this now" framing, regeneratable while authenticated (FR-3).

**Onboarding / registration** (FR-1, FR-3; UJ-3; decision #27). Deliberately minimal to respect entry-burden (SM-C1). **Required:** username + password → the one-time recovery code shown once with explicit "save this now" framing (FR-3). **Then one light, skippable step:** *Imposta la tua Liquidità iniziale* (FR-12) — recommended but skippable, settable later from Impostazioni. Starter *Categorie* are pre-seeded per type (FR-7). *Secchielli*, *Regole ricorrenti* and everything else are entirely optional, added later when wanted. The Utente lands on an empty Home whose empty states (see State Patterns) carry gentle first-run nudges. A new account starts empty (FR-1).

**First-run nudge toward the allocation answer.** Because allocation awareness is the north-star payoff but the Home stays the clean month snapshot (decision #12), a gentle one-time nudge surfaces the allocation answer **once the Utente has enough data** (a *Liquidità iniziale* set, or a first *Secchiello*): a soft pointer routes them toward **Liquidità → Allocazione** to see committed vs free for the first time. It is a quiet suggestion, not a forced step, and it never clutters the Home — it respects the calm snapshot while making sure the core payoff is discovered.

## Voice and Tone

Microcopy. Calm, honest, plain Italian. Encouraging — never nagging. The honesty principle (PRD §12) is a tone rule, not just a UX preference: where the system could hide an uncomfortable truth (negative *Saldo*, growing *Drift*, buffer breach), it states it plainly and warmly. And it respects the reminder counter-metric (SM-C2): do not over-prompt, do not gamify, no streaks or "engagement" pressure (SM-C1).

| Do | Don't |
|---|---|
| `Spesa aggiunta` (save toast) | `✓ Spesa salvata con successo!` |
| `È ora di riconciliare — ultima volta: 9 gg fa` | `Non riconcili da troppo tempo! Fallo subito.` |
| `Risparmio libero sotto il Cuscinetto di sicurezza` | `ATTENZIONE: fondo di emergenza insufficiente!` |
| `Questo Secchiello è in rosso di 40 € — la Quota salirà per recuperare` | `Errore: saldo negativo` |
| `Ancora nessuna spesa questo mese` | `Inizia subito a tracciare! 🎉` |
| Plain Italian, complete sentences. | Exclamation marks, badges, streak counters, guilt. |

Sample microcopy (verbatim seeds — `DESIGN.md` owns nothing here, this section owns the words):
- **Empty — new account:** `Imposta la tua Liquidità iniziale per cominciare.`
- **Empty — no Spese this period:** `Ancora nessuna spesa questo mese.`
- **Empty — no Secchielli:** `Nessun Secchiello. Crea il primo per mettere da parte in anticipo.`
- **Reconciliation banner:** `È ora di riconciliare — ultima volta: N gg fa` (→ tap to start).
- **Under-funding (negative Saldo):** `Secchiello in rosso di X € — la Quota salirà per recuperare.`
- **Cuscinetto breach:** `Risparmio libero sotto il Cuscinetto di sicurezza (N mesi).`
- **Drift shown:** `Scostamento: −87 € rispetto al calcolato.`
- **Save toast:** `Spesa aggiunta` / `Entrata aggiunta`.

## Component Patterns

Behavioral. Visual specs live in `DESIGN.md`. Components named here come from the `DESIGN.md` component namespace.

| Component | Use | Behavioral rules |
|---|---|---|
| `period-selector` | Home, Statistiche | Segmented Giorno / Settimana / Mese / Anno (default Mese / current month, decision #13). Below it, `‹ ›` in-period navigation. Both screens share it for consistency. |
| `balance-block` | Home (Bilancio), Liquidità, Patrimonio | One hero number in `{type.display}`: *Netto* on Home (large display, `{color.positive}` / `{color.negative}` by sign), total *Liquidità*, or total *Patrimonio*. Supporting figures in `{type.body}`; small positive figures (e.g. the *Entrate* value) use `{color.positive-ink}`. |
| `category-row` | Home Spese list | One per *Categoria*, sorted **largest → smallest** by total spend (decision #14). Icon + name + total + a proportional progress bar (fill in `{color.accent}`, unfilled track in `{color.bar-track}`). Tap → that Categoria's Spese detail. No other sort/filter on Home (decision #15). |
| `list-row` | Spese detail, Secchielli, Regole, Categorie, assets | Tap → detail or edit. Swipe action reserved for native edit/delete where applicable. |
| `secchiello-badge` | Quick-add 🎟 chip, Secchielli list | Shows the linked *Secchiello* (e.g. `🎟 Assic. auto`). In quick-add, auto-set from the chosen Categoria (FR-5); tappable to override or clear per-Spesa. |
| `chip` | Quick-add Categoria picker | Recent / most-used *Categorie* as one-tap chips; `＋ altre…` opens the searchable full list. |
| `keypad` | Quick-add | Numeric keypad, raised on sheet open (decision #18); amount is the focus. Decimal comma `,` (Italian convention). |
| `fab` / centre nav | ＋ Aggiungi | Central hero in `bottom-nav`; raises the quick-add `bottom-sheet`. |
| `bottom-sheet` | Quick-add | Rises from ＋, one-handed; swipe-down to dismiss (decision #18). |
| `honesty-banner` | Any screen (contextual) | Reconciliation-due / buffer / drift surfacing in `{color.honesty}` on `{color.honesty-bg}`. Non-blocking, dismissible-to-later, never modal. |
| `period-selector`, `card` | All summary screens | `card` is the base container at `{radius.card}`; airy padding per the Morbido system. |
| `bottom-nav` | All primary screens | Five slots (decision #9). Persistent on mobile. On desktop, becomes a side/top nav (adaptive). |

## State Patterns

| State | Surface | Treatment |
|---|---|---|
| Loading | Any derived view | Skeleton in `{color.surface-2}`; never a blocking spinner over content. Derived figures (Liquidità, Quota, Saldo, Patrimonio) compute sub-second (NFR §10) — loading is rare and brief. |
| Offline / stale derived data | Any screen (responsive web) | Since every figure is live-derived, when the connection drops or a derived value is stale, mark it plainly (e.g. a quiet "dati non aggiornati" note) rather than showing a confidently wrong number; offer retry. Never present stale liquidity as current. |
| Empty — new account | Home / Liquidità | First-run guidance: `Imposta la tua Liquidità iniziale per cominciare.` Routes into onboarding/Impostazioni. |
| Empty — no Spese this period | Home Spese list | `Ancora nessuna spesa questo mese.` No false bars, no zero-state chart noise. |
| Empty — no Secchielli | Liquidità tab B | `Nessun Secchiello. Crea il primo per mettere da parte in anticipo.` |
| Empty — Statistiche / insufficient data | Statistiche | When there is not enough history to chart a trend (or no Spese in the period for the pie), show a calm "Servono più dati per i grafici" message instead of an empty or misleading chart. No fabricated trend lines. |
| Error | Any | Plain warm message in `{color.honesty}`, with a retry where it applies. Never expose raw errors. Financial data is never silently dropped (NFR §10). |
| Auth failure / lost recovery code | Login, recovery (FR-1..FR-3) | Wrong credentials get a plain, non-blaming message and a retry. Account recovery uses the one-time **recovery code** (FR-3); if it is lost or unavailable, state plainly that — by design — the account cannot be recovered without it, with no false promise of a back channel. Offer to regenerate the code while still authenticated (FR-3). |
| **Honesty — under-funding** | Secchiello row/detail, Liquidità | Negative *Saldo* shown explicitly in `{color.honesty}`, never clamped (FR-10). Message: `Secchiello in rosso di X € — la Quota salirà per recuperare.` |
| **Honesty — Drift / reconciliation due** | `honesty-banner` anywhere | `È ora di riconciliare — ultima volta: N gg fa`. Fires only after the configured interval (FR-16, SM-C2). An acknowledged-but-open Drift stays visible as a quiet indicator (FR-18). |
| **Honesty — Cuscinetto breach** | Liquidità (Cuscinetto card) | `Risparmio libero sotto il Cuscinetto di sicurezza (N mesi).` Non-blocking indicator (FR-15). |
| Focus | Inputs | Native focus + keyboard; visible focus ring (see Accessibility). |

**Honesty states use warm amber `{color.honesty}` on `{color.honesty-bg}`, never alarm-red.** This is the deliberate reconciliation of the honesty principle (PRD §12) with the calm/warm register (decision #20): truths are surfaced plainly but without alarm. `{color.negative}` (the warm red) is reserved for a negative *Netto* / negative signed figure, not for warnings.

## Interaction Primitives

- **Tap to act.** The quick-add optimal path is amount → category `chip` → `Salva` (decision #18) — three taps, keypad already up.
- **Swipe-down** dismisses the quick-add `bottom-sheet` (decision #18).
- **Tap a `category-row`** drills into that Categoria's Spese detail (decision #14); Back returns.
- **`‹ ›`** navigates within the selected period; the `period-selector` switches granularity (decision #13).
- **Amount-first entry:** the `keypad` is up on open, Italian decimal comma, *Spesa*/*Entrata* toggle defaults to *Spesa* (decision #19).
- **Banned:** streaks, badge counts, engagement nudges, push/email re-engagement (none exist in V1 anyway — notifications are in-app only, PRD §5), gamification, alarm-red warnings, blocking modals over financial content. These violate SM-C1, SM-C2, and the calm register.

## Accessibility Floor

Warm but legible — the tension between "no harsh contrast" (decision #20, #22) and accessibility is resolved by treating WCAG AA as a **floor on text legibility**, met *within* the warm palette rather than by cranking contrast to harsh black-on-white. `{color.ink}` is a warm near-black (not pure `#000`) and clears AA comfortably. Secondary text uses `{color.ink-soft}`, which was **darkened** in `DESIGN.md` (light `#6D6A63`) so it now clears AA — the *original* lighter `#807C74` did **not** clear AA and that earlier assumption was wrong. For accent-colored text, icons and small figures the palette splits into text-safe `-ink` variants — `{color.accent-ink}` and `{color.positive-ink}` — while the softer `{color.accent}` / `{color.positive}` are kept for fills and large display only. Harshness is avoided by softness of hue, not by lowering contrast below the floor.

Concrete contrast (against `{color.surface}` / `{color.bg}`):
- **Light:** `{color.accent-ink}` text ≈ 4.6:1; `{color.positive-ink}` ≈ 4.5:1; `{color.honesty}` `#8B6237` ≈ 4.5:1; `{color.ink-soft}` `#6D6A63` ≈ 4.5:1 — all clearing the 4.5:1 AA floor for normal text.
- **Dark:** the corresponding `-ink` / soft tokens land in the **4.7–13.2:1** range — comfortably above AA throughout (the dark theme was already AA, so its values are unchanged).

- Tap targets ≥ 44px — confirmed for every `chip`, `keypad` key, `bottom-nav` slot, and the `period-selector` buttons (and every list row).
- Visible focus indicator on every interactive element: a **2px `{color.focus}` ring** (a dedicated token, never the soft `{color.accent}`). Focus traversal follows reading order on every surface.
- The quick-add `bottom-sheet` **traps focus** while open and **restores focus** to the ＋ trigger on dismiss, so keyboard/screen-reader users are never stranded behind the scrim.
- Text contrast meets WCAG AA in both light and dark themes; honesty amber `{color.honesty}` is validated against its background `{color.honesty-bg}` for legibility (warnings must be readable, that is the whole point).
- Sign is never conveyed by color alone — `{color.positive}` / `{color.positive-ink}` / `{color.negative}` always pair with a `+`/`−` and the figure.
- Screen-reader labels: every interactive element labeled with role + state; the save toast and honesty banners announce on appearance. Italian domain terms are read as-is (they are the labels).
- Honor system text-size / dynamic type via `DESIGN.md` typography tokens; controls must not truncate at the largest setting.
- Reduce Motion: skip sheet-rise and toast fades; show end state immediately.

## Honesty & Surfacing

A product-specific section, because honesty is a stated product value (PRD §12), not only UX polish. The rule across every surface: **where mynance could hide an uncomfortable truth, it shows it plainly and warmly.**

- A negative *Saldo del Secchiello* is shown as under-funding, never clamped to zero in the bucket's own view (FR-10).
- Growing *Drift* surfaces via the `honesty-banner`; an acknowledged-but-unclosed gap stays visible as a quiet indicator (FR-18).
- A *Risparmio libero* below the *Cuscinetto di sicurezza* is flagged (FR-15).
- *"non identificato"* is a **dedicated system *Categoria*** (not a hidden bucket): the *Spesa*/*Entrata* created to close a Drift is attributed to it, so it surfaces like any other *Categoria* — in the Home per-category breakdown and in the **Statistiche** Spese pie. It **is** reportable (FR-18), counted in *Spesa media mensile* — real outflows surfaced, not swept aside (FR-15, FR-18).
- All of this in `{color.honesty}`, never alarm-red — surfaced, not weaponized (respecting SM-C2 and the calm register).

## Responsive & Platform

Adaptive, single codebase, per decision #7. V1 ships the **web frontend** (PRD §6.1); native apps follow later on the same API (PRD §11) — so this spine targets responsive web that is mobile-first.

- **Mobile (primary):** `bottom-nav` persistent; quick-add as `bottom-sheet`; capture + summaries foregrounded; management/detail reachable but secondary.
- **Desktop (companion):** nav becomes side/top; management surfaces (Categorie, Regole, Patrimonio editing, Secchielli forms, reconciliation history) become richer and more comfortably editable; the quick-add may render as a centred panel rather than a rising sheet. [ASSUMPTION: desktop quick-add as a panel rather than a sheet — derived from #7's "richer on desktop", not separately decided.]
- Theme follows system, manual override (decision #21); both light and dark are first-class.

## Key Flows

Named-protagonist journeys mirroring the PRD's UJ names and protagonists verbatim (Marco, Elena), plus the hero quick-capture flow.

### Flow 0 — Quick capture "al volo" (Marco, in line at the supermarket, one hand)

The hero daily action; realizes the entry-burden counter-metric (SM-C1).

1. Marco taps the central ＋ in `bottom-nav`.
2. The quick-add `bottom-sheet` rises; the numeric `keypad` is already up, *Spesa* toggle active (decision #18, #19).
3. He types `45,00`.
4. He taps the `🛒 Alimentari` `chip` (recent/most-used).
5. The `secchiello-badge` updates from the Categoria's link if any; date is `Oggi` by default (FR-5).
6. He taps `Salva`.
7. **Climax:** a quiet `Spesa aggiunta` toast, the sheet falls away, and Home already reflects the new *Spesa* in the Bilancio and the *Alimentari* `category-row` — three taps, no friction, nothing forgotten to become *Drift*.

Failure path: linked *Secchiello* is wrong → he taps the `secchiello-badge` to override or clear before `Salva` (FR-5 per-Spesa override).

### Flow 1 (UJ-1) — Marco sets aside for the car insurance he already knows is coming

1. Marco goes to **Liquidità → Secchielli** and creates a *Secchiello* `Assicurazione auto`, *Importo previsto* €620, *Prossima scadenza* in 8 months (§4.3).
2. mynance computes the monthly *Quota* (`max(0, (620 − Saldo) / mesi)`, FR-9) and begins crediting it virtually each elapsed month (derived-on-read, FR-10).
3. He switches to the **Allocazione** tab.
4. **Climax:** the view shows part of his savings as **Liquidità allocata** to that *Secchiello* and the rest as **Risparmio libero** — €620 of his money is concretely, visibly already spoken for (UJ-1 climax verbatim).
5. **Resolution:** when the insurance is paid he logs a *Spesa* linked to the *Secchiello*; *Saldo* decrements by the actual amount, the leftover carries over and lowers next year's *Quota*, *Prossima scadenza* advances by the *Periodicità* (FR-10).

### Flow 2 (UJ-2) — Marco reconciles after a forgetful fortnight

1. On opening mynance, the `honesty-banner` reads `È ora di riconciliare — ultima volta: 14 gg fa` (FR-16).
2. He taps it; the Riconciliazione flow opens.
3. He checks his actual bank balances and types the real total.
4. mynance shows the **Drift**: `Scostamento: −87 € rispetto al calcolato` (FR-17), in `{color.honesty}`.
5. **Climax:** he closes the gap with one action — a *"non identificato"* *Spesa* of €87 (FR-18) — and the books are honest again (UJ-2 climax verbatim).
6. **Resolution:** the *Riconciliazione* timestamp resets; the banner won't fire again until the next interval (FR-16, SM-C2). (Alternatively he acknowledges and leaves it open — timer resets, gap stays a quiet indicator.)

### Flow 3 (UJ-3) — Elena understands, for the first time, how much is really free

1. Elena registers (username + password); the recovery code is shown once and she saves it (FR-1, FR-3).
2. She sets her *Liquidità iniziale* (FR-12).
3. She adds a monthly income *Regola ricorrente* and logs a few *Spese* (FR-8, FR-5); she adds two *Secchielli* (§4.3).
4. She opens **Liquidità → Allocazione**.
5. **Climax:** the allocation view answers her question — **committed vs free vs the Cuscinetto status** (is *Risparmio libero* above 6 months of *Spese*?) — at a glance (UJ-3 climax verbatim).
6. **Resolution:** she returns weekly, nudged by the in-app reminder, and the numbers stay trustworthy.

### Flow 4 (UJ-4) — Marco reviews his whole net worth at year-end *(lighter)*

1. Marco opens **Altro → Patrimonio** (§4.6).
2. **Climax:** he sees *Liquidità* + invested capital (*Capitale versato*, contributed not market) + *Beni immobili* (price paid) + *Beni mobili* (auto-depreciated by *Svalutazione*) summed into one total *Patrimonio* he believes (UJ-4 verbatim; FR-19–22).

---

### Coverage self-check

- **Every nav/IA surface has a section:** Mese (Home), Statistiche, Aggiungi (quick-add), Liquidità (Allocazione + Secchielli), Altro → Patrimonio / Riconciliazione / Impostazioni (Categorie, Regole, Liquidità iniziale, Account+recovery), Onboarding — all present.
- **Every PRD feature has a surface:** §4.1 Auth → Onboarding + Account/recovery; §4.2 Movimenti → quick-add + Home + Categorie/Regole; §4.3 Secchielli → Liquidità tab B; §4.4 Liquidità → Liquidità tab A; §4.5 Drift → Riconciliazione flow + honesty-banner; §4.6 Patrimonio → Patrimonio screen. FR-1..FR-22 each mapped above.
- **Counter-metrics honored:** SM-C1 (entry burden) via quick-capture; SM-C2 (reminder frequency) via interval-gated, non-nagging banners.
